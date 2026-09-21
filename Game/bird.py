from Game.game_object import GameObject
from Game.geometry import make_vector
from Game.timer import Timer


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

    @property
    def center_y(self) -> float:
        return float(self._location[1] + self._dimensions[1] / 2)

    @property
    def top(self) -> float:
        return float(self._location[1])

    @property
    def bottom(self) -> float:
        return float(self._location[1] + self._dimensions[1])

    @property
    def right(self) -> float:
        return float(self._location[0] + self._dimensions[0])

    def attempt_jump(self):
        if self._jump_timeout_timer.status():
            self._speed_per_turn = make_vector(self._speed_per_turn[0], -Bird.JUMP_BOOST_SCREENS_PER_TURN)
            self._jump_timeout_timer.reset()

    def update(self):
        super().update()
        if not self._jump_timeout_timer.status():
            self._jump_timeout_timer.progress()
