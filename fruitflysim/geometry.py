from dataclasses import dataclass
from typing import Annotated, Literal, Tuple

import numpy as np
import numpy.typing as npt
import pygame

Vector = Annotated[npt.NDArray[np.float64], Literal[2]]


def make_vector(x: float, y: float) -> Vector:
    return np.array([x, y], dtype=np.float64)


@dataclass(frozen=True)
class Hitbox:
    """Axis-aligned box in screen-fraction space. Location is the top-left corner."""

    location: Vector
    dimensions: Vector

    @property
    def left(self) -> float:
        return float(self.location[0])

    @property
    def top(self) -> float:
        return float(self.location[1])

    @property
    def right(self) -> float:
        return float(self.location[0] + self.dimensions[0])

    @property
    def bottom(self) -> float:
        return float(self.location[1] + self.dimensions[1])

    def overlaps(self, other: "Hitbox") -> bool:
        return (
            self.left < other.right
            and other.left < self.right
            and self.top < other.bottom
            and other.top < self.bottom
        )

    def to_pygame_rect(self, screen_size: Tuple[int, int]) -> pygame.Rect:
        screen_width, screen_height = screen_size
        width_px = max(1, int(round(self.dimensions[0] * screen_width)))
        height_px = max(1, int(round(self.dimensions[1] * screen_height)))
        left = int(round(self.location[0] * screen_width))
        top = int(round(self.location[1] * screen_height))
        return pygame.Rect(left, top, width_px, height_px)
