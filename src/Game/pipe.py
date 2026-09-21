import random
from typing import List, Optional

from src.Game.bird import Bird
from src.Game.game_object import GameObject
from src.Game.geometry import Hitbox, make_vector


class Pipe(GameObject):
    PIPE_SPEED = make_vector(-0.22, 0)
    PIPE_WIDTH = 0.08
    PIPE_OPENING_SIZE = Bird.BIRD_SIZE[1] * 3.2
    _MARGIN = 0.08

    def __init__(self, initial_location, speed, gap_top):
        super().__init__(initial_location, speed, make_vector(self.PIPE_WIDTH, 1.0))
        self._gap_top = gap_top

    @classmethod
    def new_pipe(cls, rng: Optional[random.Random] = None):
        rng = rng if rng is not None else random
        max_gap_top = 1.0 - cls.PIPE_OPENING_SIZE - cls._MARGIN
        gap_top = rng.uniform(cls._MARGIN, max(cls._MARGIN, max_gap_top))
        return Pipe(make_vector(1.0, 0.0), cls.PIPE_SPEED, gap_top)

    @property
    def gap_top(self) -> float:
        return self._gap_top

    @property
    def opening_center_y(self) -> float:
        return self._gap_top + self.PIPE_OPENING_SIZE / 2

    def is_offscreen(self) -> bool:
        return self._location[0] + self.PIPE_WIDTH < 0

    def hitboxes(self) -> List[Hitbox]:
        x = float(self._location[0])
        top = Hitbox(make_vector(x, 0.0), make_vector(self.PIPE_WIDTH, self._gap_top))
        bottom_y = self._gap_top + self.PIPE_OPENING_SIZE
        bottom = Hitbox(
            make_vector(x, bottom_y),
            make_vector(self.PIPE_WIDTH, max(0.0, 1.0 - bottom_y)),
        )
        return [top, bottom]
