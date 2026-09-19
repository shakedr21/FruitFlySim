import random
from typing import List

import pygame

from fruitflysim import colors
from fruitflysim.bird import Bird
from fruitflysim.game_object import GameObject
from fruitflysim.geometry import Hitbox, make_vector


class Pipe(GameObject):
    PIPE_SPEED = make_vector(-0.22, 0)
    PIPE_WIDTH = 0.08
    PIPE_OPENING_SIZE = Bird.BIRD_SIZE[1] * 3.2
    _MARGIN = 0.08

    def __init__(self, initial_location, speed, gap_top):
        super().__init__(initial_location, speed, make_vector(self.PIPE_WIDTH, 1.0))
        self._gap_top = gap_top

    @classmethod
    def new_pipe(cls):
        max_gap_top = 1.0 - cls.PIPE_OPENING_SIZE - cls._MARGIN
        gap_top = random.uniform(cls._MARGIN, max(cls._MARGIN, max_gap_top))
        return Pipe(make_vector(1.0, 0.0), cls.PIPE_SPEED, gap_top)

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

    def render(self, surface: pygame.Surface):
        screen_size = surface.get_size()
        rim_px = max(6, int(screen_size[1] * 0.02))
        for rect in (hitbox.to_pygame_rect(screen_size) for hitbox in self.hitboxes()):
            pygame.draw.rect(surface, colors.PIPE, rect)
            pygame.draw.rect(surface, colors.PIPE_RIM, rect, width=3)
            rim = pygame.Rect(rect.left - 4, 0, rect.width + 8, rim_px)
            if rect.top <= 0:
                rim.top = rect.bottom - rim_px
            else:
                rim.top = rect.top
            pygame.draw.rect(surface, colors.PIPE_RIM, rim)
