import pandas as pd
import numpy as np
import torch


def load_connectome_to_tensors(csv_path: str, input_root_ids: list[int], output_root_ids: list[int]):
    df = pd.read_csv(csv_path)

    # 1. Collect all unique nodes in the subnetwork
    all_nodes = sorted(
        list(set(df['pre_id']).union(set(df['post_id'])).union(set(input_root_ids)).union(set(output_root_ids))))
    node_to_idx = {node_id: i for i, node_id in enumerate(all_nodes)}
    N = len(all_nodes)

    # 2. Build initial weight matrix W and structural mask M
    W = np.zeros((N, N), dtype=np.float32)
    M = np.zeros((N, N), dtype=np.float32)

    max_weight = df['weight'].max() if len(df) > 0 else 1.0

    for _, row in df.iterrows():
        u = node_to_idx[row['pre_id']]  # presynaptic
        v = node_to_idx[row['post_id']]  # postsynaptic
        w = row['weight'] / max_weight  # Normalize synapse count to [0, 1]

        W[v, u] = w
        M[v, u] = 1.0

    # 3. Map input and output Root IDs to their subnetwork tensor indices
    input_indices = torch.tensor([node_to_idx[uid] for uid in input_root_ids if uid in node_to_idx], dtype=torch.long)
    output_indices = torch.tensor([node_to_idx[uid] for uid in output_root_ids if uid in node_to_idx], dtype=torch.long)

    return torch.tensor(W), torch.tensor(M), input_indices, output_indices, N