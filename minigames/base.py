"""Shared minigame base class.

Contract used by ArcadeScene (pause menu + results card live in the scene):
    __init__(screen, clock=None)      build state
    handle_action(action)             "UP"/"DOWN"/"LEFT"/"RIGHT"/"A"/"B" (pad-agnostic)
    update(dt)                        dt in seconds
    draw(surface)                     must fully cover the screen
    score: int, game_over: bool       read by the scene to finish the run
    held: set                         directions currently held (set by the scene)

Fonts returned by ``self.font`` & co. render through the shared LRU text
cache, so "SCORE: 120" is rendered once, not 30 times a second.
Older games written against handle_key(key) keep working: the default
handle_action translates actions to arrow/space keys.
"""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine import assets

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
_ACTION_KEYS = {"UP": pygame.K_UP, "DOWN": pygame.K_DOWN, "LEFT": pygame.K_LEFT,
                "RIGHT": pygame.K_RIGHT, "A": pygame.K_SPACE}


@dataclass
class MinigameResult:
    score: int
    completed: bool
    message: str = ""


class CachedFont:
    """Drop-in for pygame.font.Font.render() backed by engine.assets.text."""

    def __init__(self, size, bold=False):
        self.size_px, self.bold = size, bold
        self._font = assets.font(size, bold)

    def render(self, text, antialias=True, color=(255, 255, 255), background=None):
        return assets.text(str(text), self.size_px, tuple(color), self.bold)

    def size(self, text):
        return self._font.size(text)

    def get_height(self):
        return self._font.get_height()


class MinigameBase:
    FPS = 30

    def __init__(self, screen, clock=None, font_sizes=(31, 62, 23)):
        self.screen = screen
        self.clock = clock or pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.held: set = set()
        f, big, small = font_sizes
        self.font = CachedFont(f)
        self.big_font = CachedFont(big, True)
        self.small_font = CachedFont(small)

    # -- input ---------------------------------------------------------
    def handle_action(self, action: str):
        key = _ACTION_KEYS.get(action)
        if key is not None and not self.game_over:
            self.handle_key(key)

    def handle_key(self, key):
        pass

    # -- loop ----------------------------------------------------------
    def update(self, dt):
        pass

    def draw(self, screen=None):
        pass

    def end(self):
        self.game_over = True

    def hud(self, surface, left, right=None, color=(255, 255, 255), y=8):
        """Standard cached top-line HUD: big left label, small right tag."""
        t = assets.text_outlined(left, 30, color, (20, 20, 30))
        surface.blit(t, (12, y))
        if right:
            r = assets.text_outlined(right, 24, (255, 220, 120), (20, 20, 30))
            surface.blit(r, (SCREEN_WIDTH - r.get_width() - 12, y + 3))

    def run(self):
        """Standalone loop for quick manual testing: python -m minigames.<name>."""
        while self.running and not self.game_over:
            dt = self.clock.tick(self.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return MinigameResult(self.score, False, "quit")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    for a, k in _ACTION_KEYS.items():
                        if k == event.key:
                            self.held.add(a)
                            self.handle_action(a)
                elif event.type == pygame.KEYUP:
                    for a, k in _ACTION_KEYS.items():
                        if k == event.key:
                            self.held.discard(a)
            self.update(dt)
            self.draw(self.screen)
            pygame.display.flip()
        return MinigameResult(self.score, True)
