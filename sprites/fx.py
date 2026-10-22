"""Tiny feedback effects: floating text, particles, pet poses. Pygame-side."""
from __future__ import annotations
import math
import random

import pygame

from engine import assets

NEED_COLORS = {
    "hunger": (235, 120, 60), "happiness": (240, 90, 140),
    "energy": (240, 190, 40), "cleanliness": (70, 160, 230), "coins": (230, 180, 40),
}
NEED_SHORT = {"hunger": "Food", "happiness": "Joy", "energy": "Energy",
              "cleanliness": "Clean", "coins": "coins"}


class FloatText:
    __slots__ = ("surf", "x", "y", "t", "life", "vy")

    def __init__(self, text, x, y, color, size=24, life=1.3):
        self.surf = assets.text_outlined(text, size, color)
        self.x, self.y, self.t, self.life, self.vy = x, y, 0.0, life, -38.0


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "t", "life", "color", "kind", "r")

    def __init__(self, x, y, color, kind="dot"):
        self.x, self.y = x, y
        a = random.uniform(-math.pi * 0.9, -math.pi * 0.1)
        sp = random.uniform(40, 120)
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp
        self.t, self.life = 0.0, random.uniform(0.6, 1.1)
        self.color, self.kind, self.r = color, kind, random.randint(3, 5)


def _heart(surf, x, y, r, color):
    pygame.draw.circle(surf, color, (int(x - r * 0.5), int(y)), int(r * 0.6) + 1)
    pygame.draw.circle(surf, color, (int(x + r * 0.5), int(y)), int(r * 0.6) + 1)
    pygame.draw.polygon(surf, color, [(x - r * 1.1, y + 1), (x + r * 1.1, y + 1), (x, y + r * 1.4)])


def _sparkle(surf, x, y, r, color):
    pygame.draw.line(surf, color, (x - r, y), (x + r, y), 2)
    pygame.draw.line(surf, color, (x, y - r), (x, y + r), 2)


class Effects:
    """Owns all transient effects for a scene; capped so it can't grow forever."""
    MAX = 60

    def __init__(self):
        self.texts: list[FloatText] = []
        self.parts: list[Particle] = []

    def clear(self):
        self.texts.clear(); self.parts.clear()

    def float_text(self, text, x, y, color, size=24):
        # stack new popups so simultaneous deltas don't overlap
        y -= 22 * sum(1 for t in self.texts if t.t < 0.4)
        self.texts.append(FloatText(text, x, y, color, size))

    def deltas(self, deltas: dict, x, y):
        for name, v in deltas.items():
            if abs(v) < 0.5:
                continue
            sign = "+" if v > 0 else ""
            col = NEED_COLORS.get(name, (255, 255, 255)) if v > 0 else (200, 90, 90)
            self.float_text(f"{sign}{int(round(v))} {NEED_SHORT.get(name, name)}", x, y, col)

    def burst(self, x, y, color, kind="dot", n=10):
        for _ in range(n):
            if len(self.parts) < self.MAX:
                self.parts.append(Particle(x, y, color, kind))

    def update(self, dt):
        for t in self.texts:
            t.t += dt
            t.y += t.vy * dt
        self.texts = [t for t in self.texts if t.t < t.life]
        for p in self.parts:
            p.t += dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 160 * dt
        self.parts = [p for p in self.parts if p.t < p.life]

    def draw(self, surf):
        for p in self.parts:
            if p.kind == "heart":
                _heart(surf, p.x, p.y, p.r + 1, p.color)
            elif p.kind == "sparkle":
                _sparkle(surf, int(p.x), int(p.y), p.r + 1, p.color)
            else:
                pygame.draw.circle(surf, p.color, (int(p.x), int(p.y)), p.r)
        for t in self.texts:
            fade = 1.0 - max(0.0, (t.t - t.life * 0.6) / (t.life * 0.4))
            t.surf.set_alpha(int(255 * fade))
            surf.blit(t.surf, t.surf.get_rect(center=(int(t.x), int(t.y))))


def pet_pose(action: str | None, p: float) -> dict:
    """Body motion for a care action at progress p in [0, 1]."""
    if not action:
        return {}
    s = math.sin
    if action == "feed":        # three happy chomps
        k = abs(s(p * math.pi * 6)) * (1 - p)
        return {"sx": 1 + 0.10 * k, "sy": 1 - 0.10 * k}
    if action == "play":        # two hops with squash on landing
        hop = abs(s(p * math.pi * 2))
        land = 1 - hop
        return {"dy": -46 * hop, "sx": 1 + 0.14 * land * (1 - p), "sy": 1 - 0.12 * land * (1 - p) + 0.06 * hop}
    if action == "clean":       # wiggle-shake
        return {"angle": 10 * s(p * math.pi * 8) * (1 - p), "dx": 4 * s(p * math.pi * 8) * (1 - p)}
    if action == "rest":        # sink down and breathe slowly
        sink = s(min(1.0, p * 1.3) * math.pi / 2)
        return {"sy": 1 - 0.12 * sink + 0.03 * s(p * math.pi * 3), "sx": 1 + 0.06 * sink}
    if action in ("plant", "harvest", "buy", "decorate"):
        hop = abs(s(p * math.pi))
        return {"dy": -18 * hop, "sx": 1 - 0.05 * hop, "sy": 1 + 0.05 * hop}
    if action == "sad":
        return {"angle": 4 * s(p * math.pi * 2)}
    return {}
