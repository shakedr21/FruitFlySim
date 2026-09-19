import random
from typing import List, Optional

from fruitflysim.bird import Bird
from fruitflysim.game_object import GameObject
from fruitflysim.geometry import make_vector
from fruitflysim.observation import Observation
from fruitflysim.pipe import Pipe
from fruitflysim.timer import Timer


class Game:
    PIPE_SPAWN_FREQUENCY_SECONDS = 3
    PIPE_SPAWN_FREQUENCY_TURNS = PIPE_SPAWN_FREQUENCY_SECONDS * Timer.TURNS_PER_SECOND
    GROUND_HEIGHT = 0.06

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self._pipes: List[Pipe] = []
        self._unscored_pipes: List[Pipe] = []
        self._pipe_spawning_timer = Timer(Game.PIPE_SPAWN_FREQUENCY_TURNS)
        self._ground = GameObject(
            make_vector(0.0, 1.0 - self.GROUND_HEIGHT),
            make_vector(0.0, 0.0),
            make_vector(1.0, self.GROUND_HEIGHT),
        )
        self._ceiling = GameObject(
            make_vector(0.0, -1.0),
            make_vector(0.0, 0.0),
            make_vector(1.0, 1.0),
        )
        self.reset()

    @property
    def bird(self) -> Bird:
        return self._bird

    @property
    def pipes(self) -> List[Pipe]:
        return self._pipes

    @property
    def score(self) -> int:
        return self._score

    @property
    def alive(self) -> bool:
        return self._alive

    @property
    def turn(self) -> int:
        return self._turn

    def reset(self) -> Observation:
        self._score = 0
        self._alive = True
        self._pipes = []
        self._unscored_pipes = []
        self._turn = 0
        self._pipe_spawning_timer.reset()
        self._bird = Bird.new_bird()
        self._spawn_pipe()
        return self.observe()

    def step(self, jump: bool = False) -> Observation:
        if self._alive:
            if jump:
                self._bird.attempt_jump()
            self._spawn_pipe_if_due()
            self._update_actors()
            self._remove_offscreen_pipes()
            self._check_bird_collisions()
            self._update_score()
            self._turn += 1
        return self.observe()

    def observe(self) -> Observation:
        floor_y = 1.0 - self.GROUND_HEIGHT
        pipe = self._nearest_pipe()
        if pipe is None:
            pipe_distance = 1.0 - self._bird.right
            opening_height_distance = 0.0
        else:
            pipe_distance = float(pipe.location[0]) - self._bird.right
            opening_height_distance = float(pipe.opening_center_y - self._bird.center_y)
        return Observation(
            floor_distance=floor_y - self._bird.bottom,
            ceiling_distance=self._bird.top,
            pipe_distance=pipe_distance,
            opening_height_distance=opening_height_distance,
        )

    def _nearest_pipe(self) -> Optional[Pipe]:
        ahead = [pipe for pipe in self._pipes if pipe.location[0] + Pipe.PIPE_WIDTH >= self._bird.location[0]]
        if not ahead:
            return None
        return min(ahead, key=lambda pipe: pipe.location[0])

    def _spawn_pipe(self):
        pipe = Pipe.new_pipe(self._rng)
        self._pipes.append(pipe)
        self._unscored_pipes.append(pipe)

    def _spawn_pipe_if_due(self):
        if self._pipe_spawning_timer.status():
            self._spawn_pipe()
            self._pipe_spawning_timer.reset()
        self._pipe_spawning_timer.progress()

    def _update_actors(self):
        self._bird.update()
        for pipe in self._pipes:
            pipe.update()

    def _remove_offscreen_pipes(self):
        self._pipes = [pipe for pipe in self._pipes if not pipe.is_offscreen()]
        self._unscored_pipes = [pipe for pipe in self._unscored_pipes if not pipe.is_offscreen()]

    def _check_bird_collisions(self):
        obstacles = (*self._pipes, self._ground, self._ceiling)
        if any(self._bird.collides_with(obstacle) for obstacle in obstacles):
            self._alive = False

    def _update_score(self):
        while self._unscored_pipes:
            pipe = self._unscored_pipes[0]
            if self._bird.location[0] <= pipe.location[0] + Pipe.PIPE_WIDTH:
                break
            self._unscored_pipes.pop(0)
            self._score += 1
