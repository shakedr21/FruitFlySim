import torch
import torch.nn as nn
import snntorch as snn
from snntorch import surrogate


class FlyBrainSNN(nn.Module):
    def __init__(self, weight_matrix: torch.Tensor, mask_matrix: torch.Tensor,
                 input_indices: torch.Tensor, output_indices: torch.Tensor,
                 beta: float = 0.8):
        super().__init__()
        self.N = weight_matrix.shape[0]

        # Trainable parameters masked by biological topology
        self.weights = nn.Parameter(weight_matrix.clone())
        self.register_buffer('mask', mask_matrix.clone())

        self.register_buffer('input_idx', input_indices)
        self.register_buffer('output_idx', output_indices)

        # Fast sigmoid surrogate gradient allows backpropagation through discrete spikes
        spike_grad = surrogate.fast_sigmoid(slope=25)
        self.lif = snn.Leaky(beta=beta, spike_grad=spike_grad, init_hidden=False)

    def forward(self, input_currents: torch.Tensor, steps: int = 16):
        """
        input_currents: Tensor of shape (80,) containing Gaussian currents for the inputs
        steps: Number of 1ms time steps per game frame
        """
        device = input_currents.device

        # Enforce biological connectivity (non-existent edges remain zero)
        effective_W = self.weights * self.mask

        # Initialize membrane potentials and spike states
        mem = torch.zeros(self.N, device=device)
        spk = torch.zeros(self.N, device=device)

        total_gf_spikes = torch.tensor(0.0, device=device)

        for t in range(steps):
            # 1. Inject Gaussian input current into the 80 Calyx input neurons
            I_ext = torch.zeros(self.N, device=device)
            I_ext[self.input_idx] = input_currents

            # 2. Recurrent current from previous step + external input
            I_syn = torch.matmul(effective_W, spk) + I_ext

            # 3. Update LIF neuron membrane potential and generate spikes
            spk, mem = self.lif(I_syn, mem)

            # 4. Tally spikes from Left and Right Giant Fibers
            total_gf_spikes = total_gf_spikes + spk[self.output_idx].sum()

        return total_gf_spikes