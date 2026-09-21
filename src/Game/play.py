from typing import Tuple

import pygame

from src.Game import colors
from src.Game.bird import Bird
from src.Game.game import Game
from src.Game.geometry import Hitbox
from src.Game.pipe import Pipe
from src.Game.timer import Timer


def hitbox_to_rect(hitbox: Hitbox, screen_size: Tuple[int, int]) -> pygame.Rect:
    screen_width, screen_height = screen_size
    width_px = max(1, int(round(hitbox.dimensions[0] * screen_width)))
    height_px = max(1, int(round(hitbox.dimensions[1] * screen_height)))
    left = int(round(hitbox.location[0] * screen_width))
    top = int(round(hitbox.location[1] * screen_height))
    return pygame.Rect(left, top, width_px, height_px)


def draw_bird(surface: pygame.Surface, bird: Bird):
    rect = hitbox_to_rect(bird.hitboxes()[0], surface.get_size())
    body = rect.inflate(-rect.width * 0.1, -rect.height * 0.25)
    pygame.draw.ellipse(surface, colors.FLY_BODY, body)

    wing = pygame.Rect(0, 0, int(rect.width * 0.7), int(rect.height * 0.45))
    wing.center = (rect.centerx - rect.width * 0.05, rect.top + rect.height * 0.28)
    pygame.draw.ellipse(surface, colors.FLY_WING, wing)
    pygame.draw.ellipse(surface, colors.TEXT, wing, width=1)

    eye_radius = max(2, rect.width // 8)
    eye_center = (int(body.right - body.width * 0.22), int(body.centery - body.height * 0.12))
    pygame.draw.circle(surface, colors.FLY_EYE, eye_center, eye_radius)


def draw_pipe(surface: pygame.Surface, pipe: Pipe):
    screen_size = surface.get_size()
    rim_px = max(6, int(screen_size[1] * 0.02))
    for rect in (hitbox_to_rect(hitbox, screen_size) for hitbox in pipe.hitboxes()):
        pygame.draw.rect(surface, colors.PIPE, rect)
        pygame.draw.rect(surface, colors.PIPE_RIM, rect, width=3)
        rim = pygame.Rect(rect.left - 4, 0, rect.width + 8, rim_px)
        if rect.top <= 0:
            rim.top = rect.bottom - rim_px
        else:
            rim.top = rect.top
        pygame.draw.rect(surface, colors.PIPE_RIM, rim)


class PygameView:
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

    def draw(self, game: Game):
        self._draw_background(game)
        for pipe in game.pipes:
            draw_pipe(self._screen, pipe)
        draw_bird(self._screen, game.bird)
        self._draw_hud(game)
        pygame.display.flip()

    def tick(self):
        self._clock.tick(Timer.TURNS_PER_SECOND)

    def close(self):
        pygame.quit()

    def _draw_background(self, game: Game):
        self._screen.fill(colors.SKY)
        screen_width, screen_height = self._screen.get_size()
        ground_height = int(game.GROUND_HEIGHT * screen_height)
        ground = pygame.Rect(0, screen_height - ground_height, screen_width, ground_height)
        pygame.draw.rect(self._screen, colors.GROUND, ground)
        pygame.draw.rect(self._screen, colors.GROUND_STRIPE, ground, width=3)

    def _draw_hud(self, game: Game):
        score = self._font.render(str(game.score), True, colors.TEXT)
        self._screen.blit(score, score.get_rect(midtop=(self._screen.get_width() // 2, 20)))
        if not game.alive:
            overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
            overlay.fill(colors.OVERLAY)
            self._screen.blit(overlay, (0, 0))
            title = self._font.render("Game over", True, colors.TEXT)
            hint = self._small_font.render("Space to restart  ·  Esc to quit", True, colors.TEXT)
            center_x = self._screen.get_width() // 2
            center_y = self._screen.get_height() // 2
            self._screen.blit(title, title.get_rect(center=(center_x, center_y - 24)))
            self._screen.blit(hint, hint.get_rect(center=(center_x, center_y + 24)))


def run():
    game = Game()
    view = PygameView()
    running = True
    try:
        while running:
            jump = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        if game.alive:
                            jump = True
                        else:
                            game.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and game.alive:
                    jump = True
                elif event.type == pygame.VIDEORESIZE:
                    view._screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if game.alive:
                game.step(jump)
            view.draw(game)
            view.tick()
    finally:
        view.close()
