import pandas as pd


def extract_neuron_data(file_path: str) -> pd.DataFrame:
    # Read the CSV
    df = pd.read_csv(file_path)

    # Extract only the columns we care about
    extracted = df[['root_id', 'side', 'output_synapses', 'nt_type']].copy()

    # Keep only excitatory neurons
    df = df[df.nt_type == "ACH"]

    # Determine if the connection should be negative (inhibitory)
    # GABA and Glutamate (GLUT) act as inhibitory in this context
    # Acetylcholine (ACH) is positive (excitatory)dfs
    extracted['needs_negative_weight'] = extracted['nt_type'].isin(['GABA', 'GLUT'])
    return extracted

def extract_ids_with_most_output_synapses(neuron_data: pd.DataFrame) -> pd.DataFrame:
    sorted_neuron_data = neuron_data.sort_values(by="output_synapses", ascending=False)
    return sorted_neuron_data[:40]["root_id"]

if __name__ == "__main__":
    files: list[str] = [
        "data/search_results_output_neuropils_contains_CA_and_super_class_visual_projection_and_side_left.csv",
        "data/search_results_output_neuropils_contains_CA_and_super_class_visual_projection_and_side_right.csv"
    ]
    output_paths: list[str] = [
        "data/input_neurons_left.csv",
        "data/input_neurons_right.csv"
    ]

    assert len(output_paths) == len(files), "The number of input and output paths is different!"
    for i in range(len(files)):
        neuron_data = extract_neuron_data(files[i])
        extracted_neuron_ids = extract_ids_with_most_output_synapses(neuron_data)
        extracted_neuron_ids.to_csv(output_paths[i], index=False)
