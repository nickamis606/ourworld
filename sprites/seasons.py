"""Seasonal tints, baked props and cheap falling particles.

Props are painted once into the cached tinted backdrop (zero per-frame cost);
particles are ~14 tiny shapes per frame, outdoors only.
"""
import math
import random

import pygame

W, H = 640, 480
OUTDOOR_SEASONAL = {"park", "backyard", "pond", "willow_woods", "town_square", "lantern_hill"}

SEASON_TINT = {"fall": (255, 236, 212), "winter": (222, 232, 255),
               "spring": (244, 255, 244), "summer": (255, 250, 228)}
DIM_TINT = (182, 182, 200)       # gentle stakes: the town looks a bit gray


def mul(a, b):
    return tuple(a[i] * b[i] // 255 for i in range(3))


def _pumpkin(s, x, y, r=12):
    pygame.draw.ellipse(s, (120, 60, 20), (x - r - 1, y - r * 0.8 - 1, 2 * r + 2, 1.6 * r + 2))
    pygame.draw.ellipse(s, (240, 130, 40), (x - r, y - r * 0.8, 2 * r, 1.6 * r))
    pygame.draw.line(s, (200, 100, 30), (x, y - r * 0.7), (x, y + r * 0.7), 2)
    pygame.draw.rect(s, (80, 130, 50), (x - 2, y - r - 4, 4, 6))


def _egg(s, x, y, col):
    pygame.draw.ellipse(s, (90, 70, 60), (x - 7, y - 10, 14, 19))
    pygame.draw.ellipse(s, col, (x - 6, y - 9, 12, 17))
    pygame.draw.line(s, (255, 255, 255), (x - 5, y - 2), (x + 5, y - 2), 2)


def _snowman(s, x, y):
    for r, dy in ((22, 0), (16, -32), (11, -56)):
        pygame.draw.circle(s, (120, 130, 160), (x, y + dy - r + 1), r + 1)
        pygame.draw.circle(s, (250, 252, 255), (x, y + dy - r), r)
    hy = y - 56 - 11
    pygame.draw.circle(s, (30, 30, 40), (x - 4, hy - 2), 2)
    pygame.draw.circle(s, (30, 30, 40), (x + 4, hy - 2), 2)
    pygame.draw.polygon(s, (250, 140, 40), [(x, hy + 2), (x + 12, hy + 4), (x, hy + 5)])
    pygame.draw.rect(s, (200, 50, 60), (x - 14, y - 52, 28, 5))


def _bunting(s, y, cols):
    pygame.draw.line(s, (90, 70, 60), (0, y), (W, y + 8), 2)
    for i in range(16):
        x = i * 42 + 10
        yy = y + int(8 * x / W)
        pygame.draw.polygon(s, cols[i % len(cols)], [(x, yy), (x + 24, yy), (x + 12, yy + 18)])


def paint_props(s, location, season, event, extras=()):
    """Bake season/event decorations into the backdrop copy."""
    rng = random.Random(f"{location}-{season}")
    outdoor = location in OUTDOOR_SEASONAL
    # the visible ground is roughly y 300..392 (the action bar covers the rest)
    if outdoor and season == "winter":
        frost = pygame.Surface((W, H - 300), pygame.SRCALPHA)
        for _ in range(26):     # soft snow patches over the ground
            x = rng.randint(-60, W)
            w = rng.randint(70, 170)
            pygame.draw.ellipse(frost, (250, 252, 255, 150), (x, rng.randint(10, 80), w, rng.randint(14, 26)))
        for _ in range(12):     # drifts along the front edge
            x = rng.randint(-40, W)
            pygame.draw.ellipse(frost, (248, 251, 255, 235), (x, rng.randint(70, 84), rng.randint(90, 170), 34))
        s.blit(frost, (0, 300))
        for _ in range(90):
            s.set_at((rng.randint(0, W - 1), rng.randint(44, 390)), (255, 255, 255))
    elif outdoor and season == "fall":
        for _ in range(40):
            x, y = rng.randint(0, W), rng.randint(320, 392)
            pygame.draw.ellipse(s, rng.choice([(220, 110, 40), (230, 170, 50), (190, 70, 40)]), (x, y, 10, 5))
    elif outdoor and season == "spring":
        for _ in range(30):
            x, y = rng.randint(0, W), rng.randint(320, 392)
            c = rng.choice([(255, 190, 220), (255, 250, 255), (250, 220, 120)])
            pygame.draw.circle(s, c, (x, y), 3)
    if event == "harvest_fair" and location == "town_square":
        _bunting(s, 70, [(240, 130, 40), (230, 200, 60), (190, 70, 40)])
        for x, y, r in ((40, 372, 14), (76, 382, 11), (566, 374, 13), (604, 384, 12), (110, 386, 9)):
            _pumpkin(s, x, y, r)
    if event == "harvest_fair" and location in ("park", "backyard"):
        _pumpkin(s, 604, 380, 13)
    if event == "egg_hunt" and location == "park":
        for i, (x, y) in enumerate(((70, 378), (190, 386), (470, 382), (606, 374))):
            _egg(s, x, y, [(250, 150, 190), (140, 200, 250), (250, 220, 90), (170, 230, 150)][i])
    if event == "summer_splash" and location == "pond":
        _bunting(s, 60, [(250, 90, 90), (250, 220, 70), (90, 170, 250)])
    if "snowman" in extras and location == "park":
        _snowman(s, 196, 394)


def draw_particles(surf, location, season, t):
    if location not in OUTDOOR_SEASONAL:
        return
    if season == "winter":
        for i in range(16):
            x = (i * 53 + math.sin(t * 0.9 + i) * 20) % W
            y = (t * (26 + i % 5 * 6) + i * 61) % (H - 44) + 44
            pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), 2 + i % 2)
    elif season == "fall":
        for i in range(8):
            x = (i * 87 + t * 18 + math.sin(t * 1.4 + i) * 30) % W
            y = (t * (22 + i % 3 * 7) + i * 97) % (H - 44) + 44
            c = ((230, 130, 40), (220, 90, 40), (240, 190, 60))[i % 3]
            w = 4 + int(3 * abs(math.sin(t * 3 + i)))
            pygame.draw.ellipse(surf, c, (int(x), int(y), w + 2, 5))
    elif season == "spring":
        for i in range(7):
            x = (i * 97 + t * 14 + math.sin(t + i) * 24) % W
            y = (t * (16 + i % 3 * 5) + i * 71) % (H - 44) + 44
            pygame.draw.circle(surf, (255, 200, 225), (int(x), int(y)), 3)
