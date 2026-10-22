"""Bottom action bar: one D-pad-navigable row of tiles.

Items change with the location (care actions are always first, then the
place's own actions, then Map). The focused tile's full description is
shown on a line above the bar, so tiles can stay short at 640x480.
"""
from __future__ import annotations
from dataclasses import dataclass

import pygame

from engine import assets
from ui.common import FOCUS, panel
from ui.icons import icon


@dataclass
class ActionItem:
    id: str
    label: str
    icon: str
    desc: str = ""
    enabled: bool = True
    badge: str = ""          # e.g. price or count shown in the tile corner
    color: tuple = (110, 100, 150)


class ActionBar:
    Y = 400
    H = 62

    def __init__(self, width=640):
        self.width = width
        self.items: list[ActionItem] = []
        self.focus = 0
        self.pulse = 0.0        # visual press feedback
        self.pulse_id = None
        self.t = 0.0

    def set_items(self, items):
        old = self.items[self.focus].id if self.items and self.focus < len(self.items) else None
        self.items = items
        ids = [i.id for i in items]
        self.focus = ids.index(old) if old in ids else min(self.focus, max(0, len(items) - 1))

    def move(self, d):
        if self.items:
            self.focus = (self.focus + d) % len(self.items)

    def focus_id(self, item_id):
        for i, it in enumerate(self.items):
            if it.id == item_id:
                self.focus = i

    @property
    def current(self):
        return self.items[self.focus] if self.items else None

    def press(self, item_id):
        self.pulse, self.pulse_id = 0.25, item_id

    def update(self, dt):
        self.t += dt
        if self.pulse > 0:
            self.pulse -= dt

    def rects(self):
        n = max(1, len(self.items))
        gap = 6
        w = min(96, (self.width - 16 - gap * (n - 1)) // n)
        total = n * w + gap * (n - 1)
        x0 = (self.width - total) // 2
        return [pygame.Rect(x0 + i * (w + gap), self.Y, w, self.H) for i in range(n)]

    def hit(self, pos):
        for i, r in enumerate(self.rects()):
            if r.collidepoint(pos):
                return i
        return None

    def draw(self, surface, busy=False):
        surface.blit(panel((self.width, self.H + 18), (40, 34, 56, 200), 0, None), (0, self.Y - 9))
        for i, (it, r) in enumerate(zip(self.items, self.rects())):
            focused = i == self.focus
            base = it.color if it.enabled else (90, 86, 100)
            if self.pulse > 0 and self.pulse_id == it.id:
                base = tuple(min(255, c + 70) for c in base)
            rr = r.move(0, -4 if focused else 0)
            pygame.draw.rect(surface, (20, 16, 30), rr.move(0, 3), border_radius=10)
            pygame.draw.rect(surface, base, rr, border_radius=10)
            if focused:
                glow = 3 + int(abs(((self.t * 2) % 2) - 1) * 2)
                pygame.draw.rect(surface, FOCUS, rr.inflate(4, 4), glow, border_radius=12)
            ic = icon(it.icon, 28)
            if not it.enabled:
                ic = ic.copy(); ic.set_alpha(110)
            surface.blit(ic, ic.get_rect(center=(rr.centerx, rr.y + 20)))
            lab = assets.text(it.label, 18, (255, 255, 255) if it.enabled else (170, 165, 180), bold=True)
            if lab.get_width() > rr.width - 6:
                lab = assets.text(it.label, 15, (255, 255, 255) if it.enabled else (170, 165, 180), bold=True)
            surface.blit(lab, lab.get_rect(center=(rr.centerx, rr.bottom - 13)))
            if it.badge:
                b = assets.text(it.badge, 15, (60, 40, 10), bold=True)
                br = pygame.Rect(0, 0, b.get_width() + 8, 15)
                br.topright = (rr.right - 2, rr.y + 2)
                pygame.draw.rect(surface, (255, 220, 110), br, border_radius=7)
                surface.blit(b, b.get_rect(center=br.center))
        if busy:
            veil = panel((self.width, self.H + 18), (40, 34, 56, 90), 0, None)
            surface.blit(veil, (0, self.Y - 9))
