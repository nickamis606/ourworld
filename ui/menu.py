"""Simple vertical menu used for pause / title screens."""
import pygame

from engine import assets
from ui.common import FOCUS, panel


class Menu:
    def __init__(self, title, options, width=300):
        self.title = title
        self.options = list(options)   # list of (id, label)
        self.index = 0
        self.width = width

    def move(self, d):
        self.index = (self.index + d) % len(self.options)

    @property
    def selected(self):
        return self.options[self.index][0]

    def rects(self, center):
        cx, cy = center
        h = 44
        top = cy - (len(self.options) * h) // 2 + 20
        return [pygame.Rect(cx - self.width // 2 + 20, top + i * h, self.width - 40, 38)
                for i in range(len(self.options))]

    def hit(self, pos, center):
        for i, r in enumerate(self.rects(center)):
            if r.collidepoint(pos):
                return i
        return None

    def draw(self, surface, center=(320, 240), veil=True, box=True):
        if veil:
            surface.blit(panel((640, 480), (10, 10, 20, 150), 0, None), (0, 0))
        if box:
            h = len(self.options) * 44 + 80
            rect = pygame.Rect(0, 0, self.width, h)
            rect.center = center
            surface.blit(panel(rect.size, (255, 250, 240, 245), 16, (120, 90, 70)), rect.topleft)
            t = assets.text(self.title, 30, (80, 60, 50), bold=True)
            surface.blit(t, t.get_rect(center=(rect.centerx, rect.y + 26)))
        for i, ((oid, label), r) in enumerate(zip(self.options, self.rects(center))):
            sel = i == self.index
            pygame.draw.rect(surface, (255, 230, 170) if sel else (240, 232, 220), r, border_radius=10)
            if sel:
                pygame.draw.rect(surface, FOCUS, r, 3, border_radius=10)
            lt = assets.text(label, 24, (60, 50, 50), bold=sel)
            surface.blit(lt, lt.get_rect(center=r.center))
