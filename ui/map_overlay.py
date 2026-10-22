"""Neighbourhood map: 3x4 grid of place cards, D-pad + mouse. Locked places are dimmed."""
import math

import pygame

from core.world import LOCATIONS, MAP_COLS, MAP_ROWS, location_at
from engine import assets
from sprites import backdrops
from ui.common import FOCUS, hint_bar, panel

CARD_W, CARD_H = 180, 86
GRID_X, GRID_Y = 40, 56
GAP_X, GAP_Y = 10, 8
THUMB_H = 46


class MapOverlay:
    def __init__(self):
        self.open = False
        self.cursor = (0, 0)
        self.t = 0.0
        self._thumbs = {}

    def show(self, current):
        self.open = True
        self.cursor = LOCATIONS[current]["map"]

    def hide(self):
        self.open = False

    def move(self, dx, dy):
        c, r = self.cursor
        self.cursor = ((c + dx) % MAP_COLS, (r + dy) % MAP_ROWS)

    @property
    def selected(self):
        return location_at(*self.cursor)

    def card_rect(self, col, row):
        return pygame.Rect(GRID_X + col * (CARD_W + 10), GRID_Y + row * (CARD_H + GAP_Y), CARD_W, CARD_H)

    def hit(self, pos):
        for key, data in LOCATIONS.items():
            if self.card_rect(*data["map"]).collidepoint(pos):
                return key
        return None

    def _thumb(self, key, locked=False):
        th = self._thumbs.get((key, locked))
        if th is None:
            th = pygame.transform.smoothscale(backdrops.get(key), (CARD_W - 12, THUMB_H))
            if locked:
                th.fill((90, 90, 110), special_flags=pygame.BLEND_MULT)
            self._thumbs[(key, locked)] = th
        return th

    def update(self, dt):
        self.t += dt

    def draw(self, surface, current, labels, locked=(), markers=None):
        markers = markers or {}
        surface.blit(panel((640, 480), (20, 30, 40, 200), 0, None), (0, 0))
        title = assets.text_outlined("Map of Willowby", 32, (255, 240, 200))
        surface.blit(title, title.get_rect(center=(250, 27)))
        sub = assets.text("Where to?", 21, (230, 230, 240))
        surface.blit(sub, sub.get_rect(midleft=(440, 29)))
        # roads between cards
        for row in range(MAP_ROWS):
            y = GRID_Y + row * (CARD_H + GAP_Y) + CARD_H // 2
            pygame.draw.line(surface, (200, 180, 140), (GRID_X, y),
                             (GRID_X + MAP_COLS * CARD_W + (MAP_COLS - 1) * GAP_X, y), 8)
        for col in range(MAP_COLS):
            x = GRID_X + col * (CARD_W + GAP_X) + CARD_W // 2
            pygame.draw.line(surface, (200, 180, 140), (x, GRID_Y + CARD_H // 2),
                             (x, GRID_Y + (MAP_ROWS - 1) * (CARD_H + GAP_Y) + CARD_H // 2), 8)
        for key, data in LOCATIONS.items():
            col, row = data["map"]
            r = self.card_rect(col, row)
            sel = (col, row) == self.cursor
            if sel:
                r = r.inflate(8, 8)
            pygame.draw.rect(surface, (30, 24, 20), r.move(0, 4), border_radius=12)
            is_locked = key in locked
            pygame.draw.rect(surface, (255, 250, 240) if not is_locked else (170, 166, 176), r, border_radius=12)
            surface.blit(self._thumb(key, is_locked), (r.x + 6, r.y + 6))
            name = data.get("short", data["name"]) if not is_locked else "???"
            surface.blit(assets.text(name, 19, data["color"] if not is_locked else (90, 86, 100), bold=True), (r.x + 10, r.y + 52))
            info = labels.get(key, "") if not is_locked else "Locked"
            if info:
                surface.blit(assets.text(info, 15, (110, 100, 100)), (r.x + 10, r.y + 69))
            if is_locked:
                lx, ly = r.centerx, r.y + 28
                pygame.draw.rect(surface, (250, 220, 120), (lx - 12, ly - 4, 24, 18), border_radius=4)
                pygame.draw.arc(surface, (250, 220, 120), (lx - 8, ly - 16, 16, 20), 0, 3.15, 3)
            mk = markers.get(key)
            if mk and not is_locked:
                bc = (240, 150, 40) if mk == "new" else (240, 190, 40)
                bx, by = r.x + 18, r.y + 18
                pygame.draw.circle(surface, (40, 30, 30), (bx, by + 2), 12)
                pygame.draw.circle(surface, bc, (bx, by), 12)
                m = assets.text("!" if mk == "new" else "*", 20, (255, 255, 255), bold=True)
                surface.blit(m, m.get_rect(center=(bx, by + 1)))
            edge = FOCUS if sel else data["color"]
            pygame.draw.rect(surface, edge, r, 5 if sel else 2, border_radius=12)
            if key == current:
                pin_y = r.y - 6 + int(3 * math.sin(self.t * 5))
                pygame.draw.circle(surface, (230, 60, 60), (r.right - 22, pin_y), 11)
                pygame.draw.polygon(surface, (230, 60, 60), [(r.right - 31, pin_y + 4), (r.right - 13, pin_y + 4), (r.right - 22, pin_y + 20)])
                pygame.draw.circle(surface, (255, 255, 255), (r.right - 22, pin_y), 4)
        sel_key = self.selected
        if sel_key:
            d = LOCATIONS[sel_key]["desc"] if sel_key not in locked else \
                "Still asleep... help the townsfolk to wake this place up!"
            t = assets.text(d, 20, (255, 255, 255))
            if t.get_width() > 620:
                t = assets.text(d, 17, (255, 255, 255))
            surface.blit(t, t.get_rect(center=(320, 443)))
        hint_bar(surface, [("D-pad", "Choose"), ("A", "Go"), ("B", "Close")])
