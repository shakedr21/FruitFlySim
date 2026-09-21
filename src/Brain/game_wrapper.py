import torch
import numpy as np
from src.Game import Game

from src.common.consts import neurons_per_group

def encode_distances_to_current(distances: np.ndarray) -> torch.Tensor:
    """
    Encodes 4 distance scalars into an 80-element population current array using overlapping Gaussians.
    Assumes distances are normalized to [0, 1].
    """
    currents = []
    sigma = 0.1  # Width of tuning curves

    for dist in distances:
        # Centers spaced evenly across [0, 1]
        centers = np.linspace(0.0, 1.0, neurons_per_group)
        # Compute Gaussian current injection for each neuron in the array
        var_currents = np.exp(-((dist - centers) ** 2) / (2 * sigma ** 2))
        currents.extend(var_currents)

    return torch.tensor(currents, dtype=torch.float32)


class GameWrapperObject:
    def __init__(self):
        self._game = Game()
        self._score = 0

    def get_input_currents(self) -> torch.Tensor:
        observation = self._game.observe()
        distances = observation.as_array()
        return encode_distances_to_current(distances)

    def reset(self) -> None:
        self._game.reset()
        self._score = 0

    def step(self, should_jump: bool) -> tuple[float, bool] :
        self._game.step(should_jump)

        reward = 0.1
        done = not self._game.alive

        if self._game.score > self._score:
            self._score = self._game.score
            reward = 1

        return reward, done
