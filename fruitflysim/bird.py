import pygame

from fruitflysim import colors
from fruitflysim.game_object import GameObject
from fruitflysim.geometry import make_vector
from fruitflysim.timer import Timer


class Bird(GameObject):
    BIRD_SIZE = make_vector(0.045, 0.06)
    JUMP_BOOST_SCREENS_PER_SECOND = 0.62
    JUMP_BOOST_SCREENS_PER_TURN = JUMP_BOOST_SCREENS_PER_SECOND / Timer.TURNS_PER_SECOND
    JUMP_TIMEOUT_SECONDS = 0.1
    JUMP_TIMEOUT_TURNS = JUMP_TIMEOUT_SECONDS * Timer.TURNS_PER_SECOND

    def __init__(self, initial_location, acceleration, dimensions):
        super().__init__(initial_location, make_vector(0, 0), dimensions, acceleration)
        self._jump_timeout_timer = Timer(Bird.JUMP_TIMEOUT_TURNS, start_ready=True)

    @classmethod
    def new_bird(cls):
        return Bird(make_vector(1 / 3, 1 / 2), GameObject.GRAVITY, cls.BIRD_SIZE)

    def attempt_jump(self):
        if self._jump_timeout_timer.status():
            self._speed_per_turn = make_vector(self._speed_per_turn[0], -Bird.JUMP_BOOST_SCREENS_PER_TURN)
            self._jump_timeout_timer.reset()

    def update(self):
        super().update()
        if not self._jump_timeout_timer.status():
            self._jump_timeout_timer.progress()

    def render(self, surface: pygame.Surface):
        rect = self.hitboxes()[0].to_pygame_rect(surface.get_size())
        body = rect.inflate(-rect.width * 0.1, -rect.height * 0.25)
        pygame.draw.ellipse(surface, colors.FLY_BODY, body)

        wing = pygame.Rect(0, 0, int(rect.width * 0.7), int(rect.height * 0.45))
        wing.center = (rect.centerx - rect.width * 0.05, rect.top + rect.height * 0.28)
        pygame.draw.ellipse(surface, colors.FLY_WING, wing)
        pygame.draw.ellipse(surface, colors.TEXT, wing, width=1)

        eye_radius = max(2, rect.width // 8)
        eye_center = (int(body.right - body.width * 0.22), int(body.centery - body.height * 0.12))
        pygame.draw.circle(surface, colors.FLY_EYE, eye_center, eye_radius)
