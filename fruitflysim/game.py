import sys
from typing import List

import pygame

from fruitflysim import colors
from fruitflysim.bird import Bird
from fruitflysim.game_object import GameObject
from fruitflysim.geometry import Vector, make_vector
from fruitflysim.pipe import Pipe
from fruitflysim.timer import Timer


class Game:
    PIPE_SPAWN_FREQUENCY_SECONDS = 3
    PIPE_SPAWN_FREQUENCY_TURNS = PIPE_SPAWN_FREQUENCY_SECONDS * Timer.TURNS_PER_SECOND
    GROUND_HEIGHT = 0.06

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fruit Fly Sim")

        display_info = pygame.display.Info()
        width = display_info.current_w or 1280
        height = display_info.current_h or 720
        self._screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        self._font = pygame.font.Font(None, max(24, self._screen.get_height() // 16))
        self._small_font = pygame.font.Font(None, max(18, self._screen.get_height() // 28))
        self._clock = pygame.time.Clock()
        self._score = 0
        self._alive = True

        self._pipes: List[Pipe] = []
        self._unscored_pipes: List[Pipe] = []
        self._turn = 0
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

        self._bird = Bird.new_bird()
        self._spawn_pipe()

    def _get_screen_dimensions(self) -> Vector:
        width, height = self._screen.get_size()
        return make_vector(float(width), float(height))

    def _spawn_pipe(self):
        pipe = Pipe.new_pipe()
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

    def _draw_background(self):
        self._screen.fill(colors.SKY)
        screen_width, screen_height = self._screen.get_size()
        ground_height = int(self.GROUND_HEIGHT * screen_height)
        ground = pygame.Rect(0, screen_height - ground_height, screen_width, ground_height)
        pygame.draw.rect(self._screen, colors.GROUND, ground)
        pygame.draw.rect(self._screen, colors.GROUND_STRIPE, ground, width=3)

    def _draw_hud(self):
        score = self._font.render(str(self._score), True, colors.TEXT)
        self._screen.blit(score, score.get_rect(midtop=(self._screen.get_width() // 2, 20)))
        if not self._alive:
            overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
            overlay.fill(colors.OVERLAY)
            self._screen.blit(overlay, (0, 0))
            title = self._font.render("Game over", True, colors.TEXT)
            hint = self._small_font.render("Space to restart  ·  Esc to quit", True, colors.TEXT)
            center_x = self._screen.get_width() // 2
            center_y = self._screen.get_height() // 2
            self._screen.blit(title, title.get_rect(center=(center_x, center_y - 24)))
            self._screen.blit(hint, hint.get_rect(center=(center_x, center_y + 24)))

    def _render(self):
        self._draw_background()
        for pipe in self._pipes:
            pipe.render(self._screen)
        self._bird.render(self._screen)
        self._draw_hud()
        pygame.display.flip()

    def _reset(self):
        self._score = 0
        self._alive = True
        self._pipes = []
        self._unscored_pipes = []
        self._turn = 0
        self._pipe_spawning_timer.reset()
        self._bird = Bird.new_bird()
        self._spawn_pipe()

    def loop_iteration(self):
        if self._alive:
            self._spawn_pipe_if_due()
            self._update_actors()
            self._remove_offscreen_pipes()
            self._check_bird_collisions()
            self._update_score()
            self._turn += 1
        self._render()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        if self._alive:
                            self._bird.attempt_jump()
                        else:
                            self._reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and self._alive:
                    self._bird.attempt_jump()
                elif event.type == pygame.VIDEORESIZE:
                    self._screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            self.loop_iteration()
            self._clock.tick(Timer.TURNS_PER_SECOND)

        pygame.quit()
        sys.exit(0)
