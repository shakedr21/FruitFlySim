import polars as pl
import pandas as pd
import rustworkx as rx
import numpy as np
import time

MIN_SYN_THRESHOLD = 12

def extract_subnetwork(connections_file: str, input_ids: list[int], output_ids: list[int], max_hops: int = 4):
    """
    Reads the FlyWire connection list, builds a directed graph, and extracts
    the sub-network between the provided input and output IDs.
    """
    print("1. Loading edge list into memory (Polars)...")
    start_time = time.time()

    # Load the filtered connections CSV
    # Adjust column names if they differ in the downloaded file (e.g., 'pre_id', 'post_id')
    edges_df = pl.read_csv(
        connections_file,
        columns=["pre_root_id", "post_root_id", "syn_count"]
    )
    edges_df = edges_df.filter(edges_df["syn_count"] > MIN_SYN_THRESHOLD)

    print(f"   Loaded {len(edges_df)} edges in {time.time() - start_time:.2f} seconds.")

    print("\n2. Preparing node mapping (64-bit Root ID -> Sequential Integer)...")
    # Extract the raw columns as numpy arrays
    sources = edges_df["pre_root_id"].to_numpy()
    targets = edges_df["post_root_id"].to_numpy()
    weights = edges_df["syn_count"].to_numpy()

    # Combine sources and targets to find all unique nodes in the network
    edge_array = np.column_stack((sources, targets))
    unique_nodes = np.unique(edge_array)

    # Create a dictionary to map 64-bit FlyWire IDs to 0-indexed integers for rustworkx
    root_to_idx = {root_id: i for i, root_id in enumerate(unique_nodes)}
    idx_to_root = {i: root_id for root_id, i in root_to_idx.items()}

    print("\n3. Building the Rustworkx Directed Graph...")
    start_time = time.time()
    G = rx.PyDiGraph()

    # Add nodes (this adds nodes 0 through len(unique_nodes)-1)
    G.add_nodes_from(unique_nodes)

    # Map the 64-bit IDs in our edge array to the new sequential integers
    mapped_sources = np.vectorize(root_to_idx.get)(sources)
    mapped_targets = np.vectorize(root_to_idx.get)(targets)

    # Create a list of tuples: (source_idx, target_idx, synapse_weight)
    mapped_edges = list(zip(mapped_sources, mapped_targets, weights))

    # Add all edges to the graph
    G.extend_from_weighted_edge_list(mapped_edges)
    print(f"   Graph built in {time.time() - start_time:.2f} seconds.")
    print(f"   Total Nodes: {G.num_nodes()} | Total Edges: {G.num_edges()}")

    print("\n4.1 Tracing pathways from Inputs to Outputs...")
    # Convert our target FlyWire IDs to graph indices (ignore if they don't exist in the graph)
    input_indices = [root_to_idx[uid] for uid in input_ids if uid in root_to_idx]
    output_indices = set(root_to_idx[uid] for uid in output_ids if uid in root_to_idx)

    if not input_indices or not output_indices:
        raise ValueError("Missing input or output IDs in the graph! Check your ID lists.")

    forward_nodes = set(input_indices)
    # Find all paths up to max_hops from our inputs
    for start_idx in input_indices:
        # returns dict of {node_index: path_length}
        paths = rx.digraph_dijkstra_shortest_paths(
            G,
            source=start_idx,
            target=None,
            weight_fn=lambda x: 1.0  # Treat all hops equally for distance
        )

        # Check which of the reached nodes actually connect to our Giant Fibers
        # Note: In a real scenario, you'd run a bi-directional search or
        # a backwards search from the outputs to find the intersection.
        # For simplicity here, we keep all nodes within max_hops of the input.
        for node_idx, path in paths.items():
            if len(path) <= max_hops:
                forward_nodes.update(path)

    print("\n4.2. Tracing pathways from Outputs to Inputs...")

    G.reverse()
    backward_nodes = set(output_indices)
    for target_idx in output_indices:
        paths = rx.digraph_dijkstra_shortest_paths(
            G, source=target_idx, target=None, weight_fn=lambda x: 1.0
        )
        for node_idx, path in paths.items():
            if len(path) <= max_hops:
                backward_nodes.update(path)
    G.reverse()

    print("\n4.3. Finding intersection between the two node groups...")
    subgraph_nodes = forward_nodes.intersection(backward_nodes)

    print(f"   Sub-network identified with {len(subgraph_nodes)} nodes.")

    print("\n5. Extracting final edge list...")
    # Create the final subgraph
    sub_G = G.subgraph(list(subgraph_nodes))

    # Format the final output: [Pre_Root_ID, Post_Root_ID, Synapse_Count]
    final_edge_list = []
    for edge in sub_G.edge_list():
        source_idx, target_idx = edge
        weight = sub_G.get_edge_data(source_idx, target_idx)

        final_edge_list.append({
            "pre_id": idx_to_root[source_idx],
            "post_id": idx_to_root[target_idx],
            "weight": weight
        })

    final_df = pl.DataFrame(final_edge_list)
    print("Extraction Complete!")
    return final_df


if __name__ == "__main__":
    # --- YOUR DATA GOES HERE ---

    # 1. The path to the downloaded 68MB CSV
    CONNECTIONS_FILE = "data/connections_princeton.csv"

    input_ids_left = list(pd.read_csv("data/input_neurons_left.csv").root_id)
    input_ids_right = list(pd.read_csv("data/input_neurons_right.csv").root_id)
    input_ids = input_ids_left + input_ids_right

    output_ids = list(pd.read_csv("data/output_neurons.csv").root_id)

    # Run the extraction
    final_subnetwork_df = extract_subnetwork(
        connections_file=CONNECTIONS_FILE,
        input_ids=input_ids,
        output_ids=output_ids,
        max_hops=3
    )

    # Save the final small edge list to feed into snnTorch
    final_subnetwork_df.write_csv("data/flappy_bird_subnetwork.csv")
    print(final_subnetwork_df.head())