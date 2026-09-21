import torch
from FlyBrainSNN import FlyBrainSNN

from src.common.consts import trained_model_output_path, subnetwork_csv_path, model_beta_value
from src.scripts.input_output_ids_helper import get_output_ids, get_inupt_ids
from connectome_to_tensor import load_connectome_to_tensors

# Loading a trained brain
W, M, input_idx, output_idx, N = load_connectome_to_tensors(
    subnetwork_csv_path,
    get_inupt_ids(),
    get_output_ids()
)
brain = FlyBrainSNN(W, M, input_idx, output_idx, beta=model_beta_value)
brain.load_state_dict(torch.load(trained_model_output_path))
brain.eval() # Sets the module to evaluation mode