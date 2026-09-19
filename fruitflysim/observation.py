from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Observation:
    floor_distance: float
    ceiling_distance: float
    pipe_distance: float
    opening_height_distance: float

    def as_array(self) -> np.ndarray:
        return np.array(
            [
                self.floor_distance,
                self.ceiling_distance,
                self.pipe_distance,
                self.opening_height_distance,
            ],
            dtype=np.float64,
        )
