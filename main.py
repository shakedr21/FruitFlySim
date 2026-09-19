import random
from typing import Annotated, Literal, List
import numpy as np
import numpy.typing as npt

Vector = Annotated[npt.NDArray[np.float64], Literal[2]]

def make_vector(x: float, y: float) -> Vector:
    return np.array([x, y])

class Timer:
    TURNS_PER_SECOND = 60

    def __init__(self, frequency_in_turns):
        self._frequency_in_turns = frequency_in_turns
        self._turns_remaining = frequency_in_turns

    def reset(self):
        self._turns_remaining = self._frequency_in_turns

    def progress(self):
        if self._turns_remaining >= 0:
            raise Exception("Timer was expired!")

        self._turns_remaining = self._turns_remaining - 1

    def status(self):
        return self._turns_remaining <= 0

class GameObject:
    GRAVITY = make_vector(0, -10)

    def __init__(
            self,
            initial_location: Vector,
            initial_speed: Vector,
            acceleration : Vector = make_vector(0, 0)
    ):
        """
        :param initial_location: The initial location of the bottom left corner of the object, starting from the bottom
            left corner of the game board
        :param initial_speed: In pixels per second
        :param acceleration: In pixels per second per second
        """
        self._location: Vector = initial_location
        self._speed_per_turn = initial_speed / Timer.TURNS_PER_SECOND
        self._acceleration_per_turn = acceleration / Timer.TURNS_PER_SECOND

    def update(self):
        self._speed_per_turn *= self._acceleration_per_turn
        self._location += self._speed_per_turn

    def render(self):
        pass


class Bird(GameObject):
    BIRD_SIZE = make_vector(50, 50)
    JUMP_BOOST_PIXELS_PER_SECOND = 50
    JUMP_BOOST_PIXELS_PER_TURN = JUMP_BOOST_PIXELS_PER_SECOND / Timer.TURNS_PER_SECOND
    JUMP_TIMEOUT_SECONDS = 1
    JUMP_TIMEOUT_TURNS = JUMP_TIMEOUT_SECONDS * Timer.TURNS_PER_SECOND

    def __init__(
            self,
            initial_location: Vector,
            acceleration: Vector,
            dimensions: Vector
    ):
        super().__init__(initial_location, make_vector(0, 0), acceleration)
        self._dimensions = dimensions
        self._jump_timeout_timer = Timer(Bird.JUMP_TIMEOUT_TURNS)

    @classmethod
    def new_bird(cls, screen_width, screen_height):
        return Bird(make_vector(screen_width / 3, screen_height / 2), GameObject.GRAVITY, cls.BIRD_SIZE)

    def attempt_jump(self):
        if self._jump_timeout_timer.status():
            self._speed_per_turn *= Bird.JUMP_BOOST_PIXELS_PER_TURN
            self._jump_timeout_timer.reset()

    def update(self):
        super().update()
        self._jump_timeout_timer.progress()

    def render(self):
        pass


class Pipe(GameObject):
    PIPE_SPEED = make_vector(50, 0)
    PIPE_OPENING_SIZE = Bird.BIRD_SIZE[0] * 1.5

    def __init__(self, initial_location, speed, opening_height):
        super().__init__(initial_location, speed)
        self._opening_height = opening_height

    @classmethod
    def new_pipe(cls, screen_width, screen_height):
        return Pipe(
            make_vector(screen_width, 0),
            cls.PIPE_SPEED,
            random.randint(0, screen_height - cls.PIPE_OPENING_SIZE)
        )

    def render(self):
        pass

class Game:
    PIPE_SPAWN_FREQUENCY_SECONDS = 5
    PIPE_SPAWN_FREQUENCY_TURNS = PIPE_SPAWN_FREQUENCY_SECONDS * Timer.TURNS_PER_SECOND

    def __init__(self):
        self._pipes = []
        self._turn = 0
        self._pipe_spawning_timer = Timer(Game.PIPE_SPAWN_FREQUENCY_TURNS)

        screen_width, screen_height = self._get_screen_dimensions()
        self._objects: List[GameObject] = [Bird.new_bird(screen_width, screen_height)]

    def _get_screen_dimensions(self) -> Vector:
        pass

    def loop_iteration(self):
        if self._pipe_spawning_timer.status():
            screen_width, screen_height = self._get_screen_dimensions()
            self._objects.append(Pipe.new_pipe(screen_width, screen_height))
            self._pipe_spawning_timer.reset()

        for obj in self._objects:
            obj.update()
            obj.render()

        self._pipe_spawning_timer.progress()
        self._turn += 1


# TODO:
# - All render functions
# - Get screen measurements
# - Make everything relative to screen size instead of in pixels (including sizes, speeds, accelerations, etc)