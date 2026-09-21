import pandas as pd
from src.common.consts import (
    input_neuron_group_names as output_group_names,
    search_result_file_paths as input_file_paths,
    input_output_neuron_data_dir_path,
    csv_column_name,
    neurons_per_group
)


def extract_neuron_data(file_path: str) -> pd.DataFrame:
    # Read the CSV
    df = pd.read_csv(file_path)

    # Keep only excitatory neurons
    df = df[df.nt_type == "ACH"]

    # Extract only the columns we care about
    extracted = df[['root_id', 'side', 'output_synapses', 'nt_type']].copy()
    return extracted

def extract_ids_with_most_output_synapses(neuron_data: pd.DataFrame, count: int) -> list[int]:
    assert count > 0, "Illegal count!"

    sorted_neuron_data = neuron_data.sort_values(by="output_synapses", ascending=False)
    return list(sorted_neuron_data[:count][csv_column_name])

def distribute_neurons_fairly(input_file_paths, output_group_count, neurons_per_group):
    neurons_per_input_file = (neurons_per_group * output_group_count) // len(input_file_paths)

    output_groups = [[0] * neurons_per_group for i in range(output_group_count)]

    for input_file_idx in range(len(input_file_paths)):
        input_file = input_file_paths[input_file_idx]
        extracted_neuron_ids = extract_ids_with_most_output_synapses(
            extract_neuron_data(input_file),
            neurons_per_input_file
        )
        for idx in range(neurons_per_input_file):
            group_index = idx % output_group_count
            neuron_index = input_file_idx + (idx // output_group_count) * len(input_file_paths)
            output_groups[group_index][neuron_index] = extracted_neuron_ids[idx]

    return output_groups

def save_output_group_to_csv(output_group, output_file_path):
    df = pd.DataFrame(output_group, columns=[csv_column_name])
    df.to_csv(output_file_path)

if __name__ == "__main__":
    output_groups = distribute_neurons_fairly(input_file_paths, len(output_group_names), neurons_per_group)
    assert len(output_group_names) == len(output_groups)

    for group_id in range(len(output_groups)):
        save_output_group_to_csv(
            output_groups[group_id],
            f"{input_output_neuron_data_dir_path}/{output_group_names[group_id]}.csv"
        )
