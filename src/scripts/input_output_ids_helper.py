import pandas as pd

from src.common.consts import (
    input_neuron_group_names,
    input_output_neuron_data_dir_path,
    csv_column_name,
    output_neuron_group_name
)

def get_inupt_ids() -> list[int]:
    input_ids = []
    for group_name in input_neuron_group_names:
        fd = pd.read_csv(f"{input_output_neuron_data_dir_path}/{group_name}.csv")
        input_ids += list(fd[csv_column_name])
    return input_ids

def get_output_ids() -> list[int]:
    return list(pd.read_csv(f"{input_output_neuron_data_dir_path}/{output_neuron_group_name}.csv")[csv_column_name])
