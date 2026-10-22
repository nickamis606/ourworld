"""PetSprite: draws the pet with squash/stretch, hop, tilt and fade.

Loads a pre-shrunk PNG from assets/pets/ (see tools/shrink_assets.py) or
falls back to a procedural blob, so a missing file never crashes the game.
Transformed frames are cached by (scale, angle) bucket so idle frames cost
one blit and animated frames reuse recent transforms.
"""
from __future__ import annotations
import math
from collections import OrderedDict

import pygame

from engine import assets

SPRITE_FILES = {0: "bubbles", 1: "milo", 2: "luna", 3: "sprout", 4: "pip", 5: "nova"}


def _procedural(color, h):
    w = int(h * 0.8)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    dark = tuple(max(0, c - 60) for c in color)
    pygame.draw.ellipse(s, color, (4, h * 0.35, w - 8, h * 0.62))
    pygame.draw.ellipse(s, dark, (4, h * 0.35, w - 8, h * 0.62), 3)
    pygame.draw.ellipse(s, color, (w * 0.1, h * 0.05, w * 0.8, h * 0.5))
    pygame.draw.ellipse(s, dark, (w * 0.1, h * 0.05, w * 0.8, h * 0.5), 3)
    for ex in (0.35, 0.65):
        pygame.draw.circle(s, (255, 255, 255), (int(w * ex), int(h * 0.28)), max(3, h // 14))
        pygame.draw.circle(s, (30, 30, 50), (int(w * ex), int(h * 0.29)), max(2, h // 24))
    pygame.draw.arc(s, (60, 40, 40), (w * 0.4, h * 0.33, w * 0.2, h * 0.08), math.pi, math.tau, 2)
    return s


class PetSprite:
    def __init__(self, pet_config: dict, height: int = 128, pos=(320, 330)):
        self.config = pet_config
        self.pet_id = pet_config.get("id", 0)
        self.name = pet_config.get("name", "Pet")
        self.color = pet_config.get("color", (200, 200, 200))
        self.height = height
        self.feet = pygame.Vector2(pos)   # bottom-centre anchor (where the pet stands)
        self.base = self._load()
        self._cache: "OrderedDict" = OrderedDict()
        self._shadows: dict = {}
        self.idle_t = 0.0
        self.rect = self.base.get_rect(midbottom=self.feet)

    def _load(self):
        name = SPRITE_FILES.get(self.pet_id)
        img = assets.image(f"assets/pets/{name}.png") if name else None
        if img is None:
            return _procedural(self.color, self.height)
        if img.get_height() != self.height:
            s = self.height / img.get_height()
            img = pygame.transform.smoothscale(img, (max(1, int(img.get_width() * s)), self.height))
        return img

    def set_feet(self, x, y):
        self.feet.update(x, y)

    def update(self, dt):
        self.idle_t += dt

    def _frame(self, sx, sy, angle):
        key = (round(sx, 2), round(sy, 2), int(angle))
        surf = self._cache.get(key)
        if surf is not None:
            self._cache.move_to_end(key)
            return surf
        surf = self.base
        if key[:2] != (1.0, 1.0):
            w, h = self.base.get_size()
            surf = pygame.transform.scale(surf, (max(1, int(w * key[0])), max(1, int(h * key[1]))))
        if key[2]:
            surf = pygame.transform.rotate(surf, key[2])
        self._cache[key] = surf
        if len(self._cache) > 48:
            self._cache.popitem(last=False)
        return surf

    def draw(self, surface, pose=None, shadow=True, idle=True):
        """pose: dict with optional dx, dy, sx, sy, angle (from fx.pet_pose)."""
        pose = pose or {}
        dx, dy = pose.get("dx", 0.0), pose.get("dy", 0.0)
        sx, sy = pose.get("sx", 1.0), pose.get("sy", 1.0)
        angle = pose.get("angle", 0.0)
        if idle and not pose:
            # gentle breathing: stretch a little instead of a jerky bob
            b = math.sin(self.idle_t * 2.4)
            sy, sx = 1.0 + 0.025 * b, 1.0 - 0.015 * b
        frame = self._frame(sx, sy, angle)
        fx, fy = self.feet.x + dx, self.feet.y
        if shadow:
            lift = max(0.0, -dy)
            sw = int(self.base.get_width() * (0.8 - min(0.4, lift / 200))) // 4 * 4
            sh = self._shadows.get(sw)
            if sh is None:
                sh = pygame.Surface((max(4, sw), 12), pygame.SRCALPHA)
                pygame.draw.ellipse(sh, (30, 20, 10, 70), sh.get_rect())
                self._shadows[sw] = sh
            surface.blit(sh, (fx - sw // 2, fy - 6))
        self.rect = frame.get_rect(midbottom=(int(fx), int(fy + dy)))
        surface.blit(frame, self.rect)

    @property
    def head(self):
        return (int(self.feet.x), int(self.feet.y - self.height))
