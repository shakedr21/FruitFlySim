data_dir_path = "../../data"

search_result_file_paths: list[str] = [
    f"{data_dir_path}/search_results_output_neuropils_contains_CA_and_super_class_visual_projection_and_side_left.csv",
    f"{data_dir_path}/search_results_output_neuropils_contains_CA_and_super_class_visual_projection_and_side_right.csv"
]

input_neuron_group_names: list[str] = [
    "ceiling_distance",
    "floor_distance",
    "next_pipe_distance",
    "pipe_opening_height_difference",
]
neurons_per_group = 20
output_neuron_group_name = "output_neurons"


input_output_neuron_data_dir_path = f"{data_dir_path}/data/input_output_neurons"
connectome_file = f"{data_dir_path}/data/connections_princeton.csv"
subnetwork_csv_path = f"{data_dir_path}/data/flappy_bird_subnetwork.csv"
trained_model_output_path = f"{data_dir_path}/trained_models/flappy_bird_fly_brain.pth"

csv_column_name = "neuron_id"

model_beta_value = 0.8