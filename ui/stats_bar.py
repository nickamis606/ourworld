"""Top HUD: four need meters with icons + coins. Smoothly animates values."""
import math

import pygame

from engine import assets
from ui.common import draw_progress_bar, panel
from ui.icons import icon

NEEDS = (("hunger", "Food", (235, 130, 60)), ("happiness", "Joy", (240, 90, 140)),
         ("energy", "Energy", (240, 190, 40)), ("cleanliness", "Clean", (70, 160, 230)))


class StatsBar:
    HEIGHT = 44

    def __init__(self, width=640):
        self.width = width
        self.shown = {}      # tweened display values
        self.flash = {}      # need -> seconds of highlight after a change
        self.t = 0.0

    def update(self, dt, needs):
        self.t += dt
        for name, _, _ in NEEDS:
            target = getattr(needs, name)
            cur = self.shown.get(name, target)
            if abs(target - cur) > 2:
                self.flash[name] = 0.6
            cur += (target - cur) * min(1.0, dt * 8)
            self.shown[name] = cur
            if name in self.flash:
                self.flash[name] -= dt
                if self.flash[name] <= 0:
                    del self.flash[name]

    def draw(self, surface, needs, coins):
        surface.blit(panel((self.width, self.HEIGHT), (255, 250, 240, 230), 0, None), (0, 0))
        pygame.draw.line(surface, (200, 180, 160), (0, self.HEIGHT), (self.width, self.HEIGHT), 2)
        seg = 128
        for i, (name, label, color) in enumerate(NEEDS):
            x = 8 + i * seg
            v = self.shown.get(name, getattr(needs, name))
            low = v < 25
            ic = icon(name, 26)
            bob = int(2 * math.sin(self.t * 10)) if low else 0
            surface.blit(ic, (x, 9 + bob))
            surface.blit(assets.text(label, 18, (90, 70, 70)), (x + 30, 4))
            bar = pygame.Rect(x + 30, 21, 88, 14)
            fill = color
            if low and int(self.t * 4) % 2:
                fill = (230, 60, 60)
            draw_progress_bar(surface, bar, v, fill_color=fill, bg_color=(220, 210, 200), border_radius=6)
            if name in self.flash:
                pygame.draw.rect(surface, (255, 255, 255), bar.inflate(4, 4), 2, border_radius=7)
            num = assets.text(str(int(round(v))), 16, (60, 50, 50))
            surface.blit(num, (bar.right - num.get_width() - 3, 4))
        # coins
        x = 8 + 4 * seg
        surface.blit(icon("coin", 24), (x, 10))
        surface.blit(assets.text(str(coins), 26, (170, 110, 20), bold=True), (x + 28, 13))
