from typing import List, Optional

import numpy as np

from fruitflysim.geometry import Hitbox, Vector, make_vector
from fruitflysim.timer import Timer


class GameObject:
    # Screen heights per second squared. Positive Y is toward the ground.
    GRAVITY = make_vector(0, 1.8)

    def __init__(
            self,
            initial_location: Vector,
            initial_speed: Vector,
            dimensions: Vector,
            acceleration: Optional[Vector] = None,
    ):
        """
        :param initial_location: Top-left corner in screen fractions. (0, 0) is the top-left of the board.
        :param initial_speed: In screen fractions per second (x: widths, y: heights)
        :param dimensions: Width and height in screen fractions
        :param acceleration: In screen fractions per second per second
        """
        if acceleration is None:
            acceleration = make_vector(0, 0)
        self._location: Vector = initial_location.astype(np.float64)
        self._dimensions: Vector = dimensions.astype(np.float64)
        self._speed_per_turn = initial_speed / Timer.TURNS_PER_SECOND
        self._acceleration_per_turn = acceleration / (Timer.TURNS_PER_SECOND ** 2)

    @property
    def location(self) -> Vector:
        return self._location

    @property
    def dimensions(self) -> Vector:
        return self._dimensions

    def update(self):
        self._speed_per_turn = self._speed_per_turn + self._acceleration_per_turn
        self._location = self._location + self._speed_per_turn

    def hitboxes(self) -> List[Hitbox]:
        return [Hitbox(self._location.copy(), self._dimensions.copy())]

    def collides_with(self, other: "GameObject") -> bool:
        return any(
            mine.overlaps(theirs)
            for mine in self.hitboxes()
            for theirs in other.hitboxes()
        )
