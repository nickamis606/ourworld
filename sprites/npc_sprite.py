"""Code-drawn townsfolk. Each NPC is rendered once into a small cached surface."""
import math

import pygame

from core.story_data import NPCS

W, H = 110, 120
_cache: dict = {}


def _dark(c, k=40):
    return tuple(max(0, v - k) for v in c)


def _light(c, k=40):
    return tuple(min(255, v + k) for v in c)


def surface(npc: str) -> pygame.Surface:
    s = _cache.get(npc)
    if s is None:
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        _draw(s, NPCS[npc]["kind"], NPCS[npc]["color"])
        _cache[npc] = s
    return s


def _eyes(s, cx, cy, gap=13, r=5):
    for dx in (-gap, gap):
        pygame.draw.circle(s, (30, 26, 30), (cx + dx, cy), r)
        pygame.draw.circle(s, (255, 255, 255), (cx + dx - 1, cy - 2), max(1, r // 2))


def _cheeks(s, cx, cy, gap=22):
    for dx in (-gap, gap):
        pygame.draw.circle(s, (255, 150, 160), (cx + dx, cy), 5)


def _draw(s, kind, col):
    cx, head_y, body_y = W // 2, 46, 88
    dk, lt = _dark(col), _light(col)
    # tails / back parts behind the body
    if kind == "fox":
        pygame.draw.ellipse(s, col, (70, 70, 40, 26))
        pygame.draw.ellipse(s, (255, 250, 240), (94, 76, 16, 14))
    if kind == "raccoon":
        for i in range(4):
            pygame.draw.ellipse(s, col if i % 2 else (60, 60, 70), (72 + i * 8, 76 - i * 4, 14, 22))
    if kind == "hedgehog":
        for i in range(11):
            a = math.pi * (0.95 + i * 0.11)
            pygame.draw.polygon(s, dk, [(cx + math.cos(a) * 30, head_y + 30 + math.sin(a) * 30),
                                        (cx + math.cos(a) * 52, head_y + 30 + math.sin(a) * 52),
                                        (cx + math.cos(a + 0.12) * 30, head_y + 30 + math.sin(a + 0.12) * 30)])
    # body
    body = pygame.Rect(cx - 30, body_y - 32, 60, 58)
    pygame.draw.ellipse(s, col, body)
    pygame.draw.ellipse(s, lt, body.inflate(-26, -24).move(0, 8))
    if kind == "tortoise":   # shell
        shell = pygame.Rect(cx - 36, body_y - 34, 72, 50)
        pygame.draw.ellipse(s, (130, 90, 50), shell)
        for i in range(3):
            pygame.draw.ellipse(s, (170, 120, 70), (shell.x + 8 + i * 20, shell.y + 12, 18, 16), 3)
    # feet
    for dx in (-16, 16):
        pygame.draw.ellipse(s, dk, (cx + dx - 10, body_y + 18, 20, 12))
    # ears behind head
    if kind == "bunny":
        for dx in (-12, 8):
            pygame.draw.ellipse(s, col, (cx + dx - 2, 0, 16, 40))
            pygame.draw.ellipse(s, (255, 190, 210), (cx + dx + 2, 6, 8, 28))
    if kind in ("cat", "fox"):
        for dx in (-1, 1):
            pygame.draw.polygon(s, col, [(cx + dx * 26, head_y - 34), (cx + dx * 8, head_y - 20), (cx + dx * 30, head_y - 6)])
            pygame.draw.polygon(s, (255, 190, 200), [(cx + dx * 24, head_y - 27), (cx + dx * 14, head_y - 19), (cx + dx * 26, head_y - 11)])
    if kind == "raccoon":
        for dx in (-20, 20):
            pygame.draw.circle(s, col, (cx + dx, head_y - 22), 10)
            pygame.draw.circle(s, (60, 60, 70), (cx + dx, head_y - 22), 5)
    if kind == "owl":
        for dx in (-1, 1):
            pygame.draw.polygon(s, dk, [(cx + dx * 26, head_y - 30), (cx + dx * 12, head_y - 20), (cx + dx * 28, head_y - 12)])
    if kind == "hedgehog":
        for dx in (-16, 16):
            pygame.draw.circle(s, dk, (cx + dx, head_y - 22), 7)
    # head
    hr = 28
    head_col = (150, 190, 110) if kind == "tortoise" else col
    pygame.draw.circle(s, head_col, (cx, head_y), hr)
    if kind == "raccoon":
        pygame.draw.ellipse(s, (60, 60, 70), (cx - 26, head_y - 10, 52, 18))
    if kind == "owl":
        for dx in (-12, 12):
            pygame.draw.circle(s, (250, 240, 210), (cx + dx, head_y - 2), 11)
    if kind == "fox":
        pygame.draw.ellipse(s, (255, 250, 240), (cx - 16, head_y + 2, 32, 22))
    if kind == "hedgehog":
        pygame.draw.ellipse(s, (240, 210, 170), (cx - 18, head_y - 8, 36, 32))
    _eyes(s, cx, head_y - 2, 12, 5)
    _cheeks(s, cx, head_y + 10)
    # mouths / beaks
    if kind in ("duck", "owl"):
        pts = [(cx - 8, head_y + 6), (cx + 8, head_y + 6), (cx, head_y + 16)] if kind == "owl" else \
              [(cx - 12, head_y + 6), (cx + 12, head_y + 6), (cx + 10, head_y + 14), (cx - 10, head_y + 14)]
        pygame.draw.polygon(s, (250, 160, 40), pts)
    else:
        pygame.draw.circle(s, (60, 40, 40), (cx, head_y + 8), 3)
        pygame.draw.arc(s, (60, 40, 40), (cx - 8, head_y + 6, 16, 10), math.pi * 1.1, math.pi * 1.9, 2)
    if kind == "cat":
        for dy in (8, 13):
            pygame.draw.line(s, (90, 70, 60), (cx - 14, head_y + dy), (cx - 28, head_y + dy - 2), 1)
            pygame.draw.line(s, (90, 70, 60), (cx + 14, head_y + dy), (cx + 28, head_y + dy - 2), 1)
    # accessories
    if kind == "tortoise":   # mayor's top hat + sash
        pygame.draw.rect(s, (50, 40, 60), (cx - 14, head_y - 52, 28, 26), border_radius=3)
        pygame.draw.rect(s, (50, 40, 60), (cx - 22, head_y - 28, 44, 6), border_radius=3)
        pygame.draw.rect(s, (220, 60, 70), (cx - 14, head_y - 34, 28, 5))
        pygame.draw.line(s, (240, 200, 70), (cx - 24, body_y - 20), (cx + 22, body_y + 14), 6)
    if kind == "duck":       # captain's hat
        pygame.draw.rect(s, (40, 60, 120), (cx - 22, head_y - 34, 44, 14), border_radius=6)
        pygame.draw.rect(s, (20, 30, 70), (cx - 26, head_y - 22, 52, 5), border_radius=2)
        pygame.draw.circle(s, (250, 210, 70), (cx, head_y - 28), 4)
    if kind == "owl":        # reading glasses
        for dx in (-12, 12):
            pygame.draw.circle(s, (80, 60, 40), (cx + dx, head_y - 2), 11, 2)
        pygame.draw.line(s, (80, 60, 40), (cx - 1, head_y - 2), (cx + 1, head_y - 2), 2)
    if kind == "hedgehog":   # straw hat
        pygame.draw.ellipse(s, (230, 200, 110), (cx - 32, head_y - 26, 64, 14))
        pygame.draw.ellipse(s, (230, 200, 110), (cx - 16, head_y - 38, 32, 20))
        pygame.draw.rect(s, (90, 160, 80), (cx - 16, head_y - 26, 32, 4))
    if kind == "raccoon":    # backwards cap
        pygame.draw.ellipse(s, (220, 60, 60), (cx - 24, head_y - 30, 48, 22))
        pygame.draw.rect(s, (220, 60, 60), (cx + 14, head_y - 22, 18, 6), border_radius=3)
    if kind == "bunny":      # bow
        pygame.draw.polygon(s, (240, 80, 140), [(cx - 4, body_y - 30), (cx - 16, body_y - 38), (cx - 16, body_y - 22)])
        pygame.draw.polygon(s, (240, 80, 140), [(cx + 4, body_y - 30), (cx + 16, body_y - 38), (cx + 16, body_y - 22)])
    if kind == "cat":        # towel turban
        pygame.draw.ellipse(s, (255, 250, 255), (cx - 22, head_y - 40, 44, 22))
    if kind == "fox":        # explorer scarf
        pygame.draw.rect(s, (60, 140, 90), (cx - 22, body_y - 34, 44, 8), border_radius=4)
