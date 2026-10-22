"""Per-location backdrops.

Each backdrop is rendered ONCE into an opaque 640x480 surface and cached, so
drawing a location costs a single blit per frame. A tiny ambient layer
(clouds, neon flicker, sparkles...) is drawn on top for life.
Home uses the painted asset pack; the other eight places are procedural so
they work with zero art files and cost ~0 bytes on disk.
"""
import math
import random

import pygame

from engine import assets

W, H = 640, 480
FLOOR_Y = 330          # where the pet stands; HUD sits above 44 and below 392
_cache: dict = {}


def get(location: str) -> pygame.Surface:
    surf = _cache.get(location)
    if surf is None:
        surf = pygame.Surface((W, H)).convert() if pygame.display.get_surface() else pygame.Surface((W, H))
        BUILDERS.get(location, _park)(surf)
        _cache[location] = surf
    return surf


def clear_cache():
    _cache.clear()


# ---------------------------------------------------------------- helpers
def _vgrad(surf, rect, top, bottom):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        pygame.draw.line(surf, c, (x, y + i), (x + w - 1, y + i))


def _cloud(surf, x, y, s=1.0, col=(255, 255, 255)):
    for dx, dy, r in ((0, 0, 18), (20, -8, 22), (42, 0, 18), (22, 6, 18)):
        pygame.draw.circle(surf, col, (int(x + dx * s), int(y + dy * s)), int(r * s))


def _tree(surf, x, y, s=1.0, leaf=(52, 150, 70)):
    dark = tuple(max(0, c - 30) for c in leaf)
    pygame.draw.rect(surf, (110, 74, 44), (x - 7 * s, y - 10 * s, 14 * s, 50 * s), border_radius=3)
    for dx, dy, r, c in ((0, -40, 34, dark), (-22, -22, 26, dark), (22, -22, 26, dark),
                         (0, -46, 28, leaf), (-16, -28, 20, leaf), (16, -30, 20, leaf)):
        pygame.draw.circle(surf, c, (int(x + dx * s), int(y + dy * s)), int(r * s))


def _flower(surf, x, y, petal, r=4):
    for a in range(5):
        ang = a * math.tau / 5
        pygame.draw.circle(surf, petal, (int(x + math.cos(ang) * r), int(y + math.sin(ang) * r)), r)
    pygame.draw.circle(surf, (255, 220, 90), (x, y), max(2, r - 1))


def _sign(surf, text, cx, y, bg, fg=(255, 255, 255)):
    t = assets.text(text, 26, fg, bold=True)
    rect = pygame.Rect(0, 0, t.get_width() + 28, t.get_height() + 12)
    rect.midtop = (cx, y)
    pygame.draw.rect(surf, (60, 40, 30), rect.inflate(6, 6), border_radius=10)
    pygame.draw.rect(surf, bg, rect, border_radius=8)
    surf.blit(t, t.get_rect(center=rect.center))


# ---------------------------------------------------------------- places
def _home(surf):
    base = assets.image("assets/backgrounds/home/base.png", alpha=False)
    if base is None:
        _vgrad(surf, (0, 0, W, FLOOR_Y), (236, 214, 186), (214, 186, 150))
        _vgrad(surf, (0, FLOOR_Y, W, H - FLOOR_Y), (178, 128, 84), (140, 96, 60))
        return
    surf.blit(base, (0, 0))
    for name, pos in (("window", (440, 70)), ("shelf", (24, 120)),
                      ("rug", (232, 300)), ("table", (452, 300))):
        img = assets.image(f"assets/backgrounds/home/layers/{name}.png")
        if img is not None:
            surf.blit(img, pos)


def _backyard(surf):
    _vgrad(surf, (0, 0, W, 250), (150, 205, 245), (215, 238, 250))
    _cloud(surf, 90, 80, 1.0); _cloud(surf, 430, 60, 0.8)
    # house wall corner + back door
    pygame.draw.rect(surf, (214, 170, 128), (0, 120, 150, 150))
    pygame.draw.polygon(surf, (150, 80, 60), [(0, 120), (150, 120), (150, 104), (0, 90)])
    pygame.draw.rect(surf, (120, 80, 50), (50, 170, 50, 100), border_radius=4)
    pygame.draw.circle(surf, (240, 200, 90), (90, 222), 4)
    # picket fence
    for x in range(160, W, 26):
        pygame.draw.rect(surf, (250, 248, 240), (x, 190, 18, 70))
        pygame.draw.polygon(surf, (250, 248, 240), [(x, 190), (x + 9, 178), (x + 18, 190)])
    pygame.draw.rect(surf, (230, 226, 216), (150, 210, W - 150, 8))
    pygame.draw.rect(surf, (230, 226, 216), (150, 240, W - 150, 8))
    _tree(surf, 560, 215, 1.0, (70, 160, 80))
    _vgrad(surf, (0, 255, W, H - 255), (118, 186, 96), (88, 150, 70))
    for i in range(140):
        x, y = random.Random(i).randint(0, W), random.Random(i * 7).randint(262, H)
        pygame.draw.line(surf, (70, 140, 60), (x, y), (x + 2, y - 5), 1)
    # garden bed (plants are drawn by the scene on top)
    pygame.draw.rect(surf, (96, 62, 36), (70, 352, 500, 34), border_radius=8)
    pygame.draw.rect(surf, (128, 86, 52), (70, 352, 500, 34), 4, border_radius=8)
    # watering can
    pygame.draw.rect(surf, (90, 150, 200), (590, 330, 30, 24), border_radius=4)
    pygame.draw.line(surf, (90, 150, 200), (590, 336), (574, 324), 4)


def _park(surf):
    _vgrad(surf, (0, 0, W, 260), (120, 190, 245), (200, 232, 250))
    pygame.draw.circle(surf, (255, 236, 150), (560, 80), 34)
    pygame.draw.circle(surf, (255, 246, 200), (560, 80), 24)
    _cloud(surf, 70, 90, 0.9)
    # distant hills
    pygame.draw.ellipse(surf, (130, 190, 120), (-120, 190, 520, 160))
    pygame.draw.ellipse(surf, (110, 176, 106), (300, 200, 520, 150))
    _vgrad(surf, (0, 262, W, H - 262), (128, 200, 108), (96, 166, 82))
    for x, y, s in ((60, 260, 1.1), (180, 245, 0.7), (600, 262, 1.0), (470, 240, 0.6)):
        _tree(surf, x, y, s)
    # pond
    pygame.draw.ellipse(surf, (80, 140, 190), (420, 300, 190, 56))
    pygame.draw.ellipse(surf, (130, 190, 230), (440, 310, 140, 30))
    pygame.draw.ellipse(surf, (90, 170, 90), (560, 312, 26, 12))  # lily pad
    # path
    pygame.draw.polygon(surf, (222, 200, 160), [(250, H), (390, H), (350, 270), (300, 270)])
    # bench
    pygame.draw.rect(surf, (140, 92, 52), (40, 318, 120, 10), border_radius=3)
    pygame.draw.rect(surf, (140, 92, 52), (40, 296, 120, 8), border_radius=3)
    for bx in (50, 140):
        pygame.draw.rect(surf, (80, 70, 70), (bx, 328, 6, 22))
    for i, (x, y) in enumerate(((210, 300), (240, 360), (420, 380), (590, 372), (120, 380))):
        _flower(surf, x, y, [(255, 120, 160), (255, 255, 255), (250, 200, 80)][i % 3], 4)
    _sign(surf, "PARK", 320, 200, (70, 140, 80))


def _candy(surf):
    # striped wallpaper interior
    for x in range(0, W, 32):
        pygame.draw.rect(surf, (255, 222, 232) if (x // 32) % 2 else (255, 240, 246), (x, 0, 32, 300))
    pygame.draw.rect(surf, (240, 120, 160), (0, 290, W, 10))
    # checkered floor
    for y in range(300, H, 30):
        for x in range(0, W, 30):
            c = (250, 250, 250) if ((x + y) // 30) % 2 else (240, 160, 190)
            pygame.draw.rect(surf, c, (x, y, 30, 30))
    # shelves with candy jars
    for sy in (90, 170):
        pygame.draw.rect(surf, (170, 110, 70), (30, sy + 46, 580, 10), border_radius=3)
        for i, jx in enumerate(range(50, 600, 70)):
            col = [(255, 90, 140), (120, 200, 255), (255, 200, 80), (140, 220, 140), (200, 140, 255)][(i + sy) % 5]
            pygame.draw.rect(surf, (230, 245, 255), (jx, sy, 40, 46), border_radius=8)
            for k in range(6):
                pygame.draw.circle(surf, col, (jx + 10 + (k % 3) * 10, sy + 24 + (k // 3) * 10), 5)
            pygame.draw.rect(surf, (200, 80, 110), (jx + 4, sy - 6, 32, 8), border_radius=3)
    # counter
    pygame.draw.rect(surf, (200, 60, 90), (40, 260, 560, 60), border_radius=10)
    for x in range(52, 590, 28):
        pygame.draw.rect(surf, (255, 255, 255), (x, 262, 12, 56))
    pygame.draw.rect(surf, (150, 40, 70), (34, 252, 572, 14), border_radius=6)
    # giant lollipop decor
    pygame.draw.line(surf, (240, 240, 240), (600, 250), (600, 160), 6)
    pygame.draw.circle(surf, (255, 110, 170), (600, 140), 30)
    pygame.draw.circle(surf, (255, 255, 255), (600, 140), 30, 4)
    _sign(surf, "Sweetie's", 320, 20, (220, 60, 110))


def _gens(surf):
    # greenhouse: glass panes + plant tables
    _vgrad(surf, (0, 0, W, 300), (200, 236, 222), (226, 246, 236))
    for x in range(0, W, 80):
        pygame.draw.line(surf, (150, 190, 170), (x, 0), (x, 300), 4)
    pygame.draw.line(surf, (150, 190, 170), (0, 120), (W, 120), 4)
    for x in range(0, W, 80):
        pygame.draw.line(surf, (246, 252, 250), (x + 12, 10), (x + 40, 60), 2)
    _vgrad(surf, (0, 300, W, H - 300), (170, 140, 110), (140, 112, 86))
    for y in range(310, H, 24):
        pygame.draw.line(surf, (155, 125, 98), (0, y), (W, y), 1)
    # hanging baskets
    for x in (120, 320, 520):
        pygame.draw.line(surf, (120, 100, 80), (x, 0), (x, 60), 2)
        pygame.draw.ellipse(surf, (150, 100, 60), (x - 26, 56, 52, 26))
        for k in range(5):
            pygame.draw.circle(surf, (70, 160, 80), (x - 20 + k * 10, 60), 9)
            _flower(surf, x - 18 + k * 9, 56, (255, 140, 180), 3)
    # potting tables with seedlings
    for tx in (30, 400):
        pygame.draw.rect(surf, (130, 90, 56), (tx, 250, 210, 14), border_radius=3)
        pygame.draw.rect(surf, (110, 74, 44), (tx + 10, 264, 8, 50))
        pygame.draw.rect(surf, (110, 74, 44), (tx + 192, 264, 8, 50))
        for k in range(5):
            px = tx + 14 + k * 40
            pygame.draw.polygon(surf, (190, 100, 60), [(px, 226), (px + 28, 226), (px + 24, 250), (px + 4, 250)])
            pygame.draw.line(surf, (60, 140, 60), (px + 14, 226), (px + 14, 206), 3)
            _flower(surf, px + 14, 202, [(255, 120, 160), (255, 220, 80), (160, 180, 255)][k % 3], 5)
    # seed packet rack
    pygame.draw.rect(surf, (100, 150, 200), (262, 150, 116, 150), border_radius=6)
    for r in range(3):
        for c in range(3):
            col = [(255, 200, 80), (255, 130, 170), (150, 220, 140)][(r + c) % 3]
            pygame.draw.rect(surf, col, (272 + c * 36, 162 + r * 44, 28, 36), border_radius=3)
    _sign(surf, "Gen's Garden", 320, 92, (60, 130, 90))


def _arcade(surf):
    _vgrad(surf, (0, 0, W, 300), (28, 20, 52), (52, 30, 80))
    # neon stripes
    pygame.draw.line(surf, (255, 60, 200), (0, 40), (W, 40), 3)
    pygame.draw.line(surf, (60, 220, 255), (0, 48), (W, 48), 2)
    # checker carpet
    for y in range(300, H, 24):
        for x in range(0, W, 24):
            c = (40, 30, 70) if ((x + y) // 24) % 2 else (64, 40, 100)
            pygame.draw.rect(surf, c, (x, y, 24, 24))
    # cabinets
    cols = [(220, 60, 90), (60, 160, 230), (250, 190, 50), (110, 210, 120)]
    for i, x in enumerate((30, 150, 470, 560)):
        c = cols[i]
        pygame.draw.rect(surf, tuple(v // 2 for v in c), (x, 150, 70, 170), border_radius=6)
        pygame.draw.rect(surf, c, (x + 4, 154, 62, 22), border_radius=4)
        pygame.draw.rect(surf, (10, 20, 30), (x + 8, 184, 54, 46), border_radius=3)
        pygame.draw.rect(surf, (40, 200, 120), (x + 12, 188, 46, 38))
        pygame.draw.rect(surf, (30, 30, 40), (x + 6, 240, 58, 20), border_radius=3)
        pygame.draw.circle(surf, (255, 80, 80), (x + 22, 250), 5)
        pygame.draw.circle(surf, (255, 220, 60), (x + 44, 250), 5)
    _sign(surf, "ARCADE", 320, 70, (120, 40, 160), (255, 230, 120))
    # prize counter
    pygame.draw.rect(surf, (90, 60, 140), (250, 240, 140, 70), border_radius=8)
    for k in range(4):
        pygame.draw.circle(surf, [(255, 120, 160), (120, 220, 255), (255, 220, 90), (160, 255, 160)][k],
                           (270 + k * 32, 232), 10)


def _pond(surf):
    _vgrad(surf, (0, 0, W, 200), (110, 190, 245), (205, 236, 252))
    pygame.draw.circle(surf, (255, 236, 150), (90, 80), 30)
    _cloud(surf, 380, 70, 0.9); _cloud(surf, 540, 110, 0.6)
    # far shore with reeds and trees
    pygame.draw.ellipse(surf, (110, 176, 106), (-80, 160, 800, 90))
    for x, y, sc in ((40, 200, 0.7), (150, 190, 0.5), (520, 195, 0.6), (610, 205, 0.8)):
        _tree(surf, x, y, sc, (60, 150, 80))
    # water
    _vgrad(surf, (0, 205, W, 120), (70, 150, 200), (40, 110, 170))
    rng = random.Random(42)
    for _ in range(26):
        x, y = rng.randint(0, W), rng.randint(215, 318)
        pygame.draw.line(surf, (150, 205, 240), (x, y), (x + rng.randint(10, 26), y), 1)
    # lily pads
    for x, y in ((90, 300), (140, 285), (470, 270)):
        pygame.draw.ellipse(surf, (80, 170, 90), (x, y, 34, 12))
        pygame.draw.line(surf, (40, 110, 170), (x + 17, y + 6), (x + 30, y + 2), 2)
    _flower(surf, 110, 296, (255, 170, 210), 3)
    # sandy beach
    pygame.draw.ellipse(surf, (240, 216, 160), (-100, 300, 860, 120))
    _vgrad(surf, (0, 340, W, H - 340), (240, 216, 160), (222, 192, 136))
    for i in range(60):
        r = random.Random(i * 13)
        pygame.draw.circle(surf, (210, 180, 128), (r.randint(0, W), r.randint(345, H)), 1)
    # dock
    pygame.draw.polygon(surf, (150, 104, 64), [(470, 330), (640, 330), (640, 352), (460, 352)])
    for x in range(476, 640, 22):
        pygame.draw.line(surf, (120, 80, 48), (x, 330), (x - 2, 352), 2)
    for x in (480, 560, 630):
        pygame.draw.rect(surf, (110, 72, 42), (x - 4, 352, 8, 30))
    # beach umbrella + towel
    pygame.draw.line(surf, (240, 240, 240), (400, 380), (390, 286), 4)
    pygame.draw.polygon(surf, (240, 80, 90), [(330, 300), (452, 272), (390, 262)])
    pygame.draw.polygon(surf, (255, 255, 255), [(360, 293), (420, 279), (390, 262)])
    pygame.draw.rect(surf, (70, 150, 220), (340, 372, 90, 18), border_radius=4)
    pygame.draw.line(surf, (250, 250, 250), (340, 381), (430, 381), 3)
    # bucket
    pygame.draw.polygon(surf, (250, 200, 60), [(560, 372), (588, 372), (584, 396), (564, 396)])
    pygame.draw.arc(surf, (60, 60, 60), (560, 360, 28, 24), 0, math.pi, 2)
    _sign(surf, "SUNNY POND", 520, 150, (40, 130, 190))


def _library(surf):
    _vgrad(surf, (0, 0, W, 320), (120, 82, 60), (96, 62, 44))
    # wainscot
    pygame.draw.rect(surf, (80, 50, 34), (0, 250, W, 80))
    for x in range(0, W, 64):
        pygame.draw.rect(surf, (96, 62, 42), (x + 6, 258, 52, 64), 2, border_radius=3)
    # arched window
    win = pygame.Rect(270, 70, 100, 150)
    pygame.draw.rect(surf, (200, 230, 250), (win.x, win.y + 40, win.w, win.h - 40))
    pygame.draw.ellipse(surf, (200, 230, 250), (win.x, win.y, win.w, 84))
    pygame.draw.line(surf, (90, 60, 40), (win.centerx, win.y), (win.centerx, win.bottom), 4)
    pygame.draw.line(surf, (90, 60, 40), (win.x, win.y + 100), (win.right, win.y + 100), 4)
    pygame.draw.rect(surf, (90, 60, 40), (win.x - 6, win.bottom, win.w + 12, 10))
    # bookshelves both sides
    rng = random.Random(7)
    spines = [(190, 60, 60), (60, 110, 180), (70, 150, 90), (220, 170, 60), (140, 80, 160), (230, 120, 80)]
    for sx in (20, 400):
        pygame.draw.rect(surf, (70, 42, 26), (sx, 60, 220, 270), border_radius=4)
        for row in range(4):
            y = 74 + row * 62
            pygame.draw.rect(surf, (52, 30, 18), (sx + 10, y, 200, 52))
            x = sx + 12
            while x < sx + 200:
                w = rng.randint(8, 16)
                h = rng.randint(34, 50)
                if x + w > sx + 208:
                    break
                pygame.draw.rect(surf, rng.choice(spines), (x, y + 52 - h, w, h))
                pygame.draw.line(surf, (255, 240, 200), (x + 2, y + 52 - h + 6), (x + w - 3, y + 52 - h + 6), 1)
                x += w + 1
            pygame.draw.rect(surf, (90, 56, 34), (sx + 6, y + 52, 208, 6))
    # floor + rug
    _vgrad(surf, (0, 330, W, H - 330), (150, 104, 66), (122, 82, 50))
    for y in range(340, H, 22):
        pygame.draw.line(surf, (128, 88, 54), (0, y), (W, y), 1)
    pygame.draw.ellipse(surf, (150, 60, 80), (200, 340, 260, 60))
    pygame.draw.ellipse(surf, (190, 100, 110), (220, 348, 220, 44), 3)
    # reading armchair + lamp
    pygame.draw.rect(surf, (60, 110, 120), (500, 290, 110, 70), border_radius=14)
    pygame.draw.rect(surf, (80, 140, 150), (510, 270, 90, 50), border_radius=12)
    pygame.draw.line(surf, (60, 50, 40), (80, 380), (80, 250), 4)
    pygame.draw.polygon(surf, (250, 220, 140), [(56, 260), (104, 260), (92, 228), (68, 228)])
    pygame.draw.ellipse(surf, (60, 50, 40), (60, 374, 40, 10))
    _sign(surf, "LIBRARY", 555, 226, (130, 80, 150))


def _spa(surf):
    _vgrad(surf, (0, 0, W, 320), (200, 236, 232), (176, 220, 214))
    # wall tiles
    for y in range(60, 320, 32):
        pygame.draw.line(surf, (160, 206, 200), (0, y), (W, y), 1)
    for x in range(0, W, 32):
        pygame.draw.line(surf, (160, 206, 200), (x, 60), (x, 320), 1)
    # mirror
    pygame.draw.ellipse(surf, (230, 200, 120), (70, 80, 110, 140))
    pygame.draw.ellipse(surf, (220, 240, 250), (78, 88, 94, 124))
    pygame.draw.line(surf, (255, 255, 255), (100, 110), (120, 96), 3)
    # towel shelf
    pygame.draw.rect(surf, (200, 160, 120), (470, 110, 140, 8))
    for i, c in enumerate(((250, 170, 210), (255, 255, 255), (170, 210, 250))):
        pygame.draw.rect(surf, c, (480 + i * 42, 82, 38, 28), border_radius=6)
    # plant
    pygame.draw.polygon(surf, (220, 150, 110), [(560, 300), (600, 300), (594, 336), (566, 336)])
    for a in (-0.9, -0.4, 0.0, 0.4, 0.9):
        pygame.draw.line(surf, (70, 160, 90), (580, 300), (580 + math.sin(a) * 40, 300 - math.cos(a) * 60), 5)
    # floor
    for y in range(320, H, 40):
        for x in range(0, W, 40):
            c = (236, 236, 244) if ((x + y) // 40) % 2 else (214, 220, 232)
            pygame.draw.rect(surf, c, (x, y, 40, 40))
    # bathtub with bubbles
    pygame.draw.ellipse(surf, (250, 250, 255), (300, 270, 260, 70))
    pygame.draw.rect(surf, (250, 250, 255), (300, 300, 260, 60), border_bottom_left_radius=30,
                     border_bottom_right_radius=30)
    pygame.draw.ellipse(surf, (120, 200, 230), (314, 278, 232, 44))
    rng = random.Random(3)
    for _ in range(18):
        pygame.draw.circle(surf, (255, 255, 255), (rng.randint(320, 540), rng.randint(276, 302)), rng.randint(6, 13))
    for x in (330, 530):
        pygame.draw.rect(surf, (230, 200, 120), (x - 6, 356, 12, 14), border_radius=3)
    pygame.draw.line(surf, (190, 190, 200), (540, 268), (540, 236), 5)
    pygame.draw.line(surf, (190, 190, 200), (540, 236), (520, 236), 5)
    # bath mat
    pygame.draw.rect(surf, (250, 170, 210), (160, 376, 150, 24), border_radius=10)
    _sign(surf, "PAWS & CLAWS SPA", 420, 180, (200, 100, 160))


BUILDERS = {"home": _home, "backyard": _backyard, "park": _park,
            "sweeties_candy_shop": _candy, "gens_garden": _gens, "arcade": _arcade,
            "pond": _pond, "library": _library, "spa": _spa}


# ---------------------------------------------------------------- ambient
def draw_ambient(surf, location: str, t: float) -> None:
    """Cheap per-frame life on top of the cached backdrop."""
    if location in ("park", "backyard"):
        x = (t * 12) % (W + 160) - 120
        _cloud(surf, x, 40 if location == "park" else 120, 0.7, (250, 252, 255))
        if location == "park":   # butterfly
            bx = 200 + math.sin(t * 0.7) * 120
            by = 230 + math.sin(t * 2.1) * 20
            flap = abs(math.sin(t * 12)) * 6 + 2
            pygame.draw.ellipse(surf, (255, 170, 60), (bx - flap - 2, by - 4, flap + 2, 8))
            pygame.draw.ellipse(surf, (255, 170, 60), (bx, by - 4, flap + 2, 8))
    elif location == "arcade":
        if int(t * 3) % 4:
            pygame.draw.line(surf, (255, 60, 200), (0, 40), (W, 40), 3)
        for i, x in enumerate((30, 150, 470, 560)):
            c = (40, 200 - (int(t * 8 + i * 3) % 5) * 25, 120)
            pygame.draw.rect(surf, c, (x + 12, 188, 46, 38))
    elif location == "sweeties_candy_shop":
        for i in range(3):
            k = (t * 0.8 + i * 0.33) % 1.0
            x, y = 80 + i * 220, 150 + int(math.sin(k * math.pi) * -20)
            r = int(3 * math.sin(k * math.pi)) + 1
            pygame.draw.circle(surf, (255, 255, 255), (x, y), r)
    elif location == "gens_garden":
        for i in range(2):
            bx = 120 + i * 300 + math.sin(t * (0.9 + i * 0.3)) * 60
            by = 150 + math.sin(t * 1.7 + i) * 18
            pygame.draw.circle(surf, (250, 210, 40), (int(bx), int(by)), 4)
            pygame.draw.circle(surf, (40, 40, 40), (int(bx) + 2, int(by)), 2)
    elif location == "pond":
        # duck paddling along + glinting ripples
        dx = 40 + (t * 18) % 600
        dy = 250 + math.sin(t * 2) * 2
        pygame.draw.ellipse(surf, (255, 255, 255), (dx - 14, dy - 6, 28, 14))
        pygame.draw.circle(surf, (255, 255, 255), (int(dx + 10), int(dy - 8)), 6)
        pygame.draw.polygon(surf, (250, 170, 40), [(dx + 15, dy - 9), (dx + 22, dy - 7), (dx + 15, dy - 5)])
        pygame.draw.circle(surf, (20, 20, 20), (int(dx + 11), int(dy - 10)), 1)
        for i in range(4):
            k = (t * 0.5 + i * 0.25) % 1.0
            x = 60 + i * 150
            pygame.draw.ellipse(surf, (190, 225, 250), (x - 20 * k, 300 - 4 * k, 40 * k + 2, 8 * k + 2), 1)
    elif location == "library":
        # lamp glow flicker + a slowly drifting page
        g = 2 + int(2 * math.sin(t * 5))
        pygame.draw.circle(surf, (255, 230, 150), (80, 262), 10 + g, 2)
        k = (t * 0.12) % 1.0
        px, py = 140 + k * 360, 100 + math.sin(t * 1.5) * 18 + k * 200
        pygame.draw.polygon(surf, (250, 245, 230), [(px, py), (px + 14, py - 4), (px + 16, py + 8), (px + 2, py + 12)])
    elif location == "spa":
        # steam rising from the tub
        for i in range(5):
            k = (t * 0.35 + i * 0.2) % 1.0
            x = 340 + i * 44 + math.sin(t * 2 + i) * 6
            r = 4 + int(k * 10)
            if k < 0.85:
                pygame.draw.circle(surf, (245, 250, 252), (int(x), int(270 - k * 120)), r, 2)
    elif location == "home":
        # sunbeam dust motes in the window
        for i in range(4):
            k = (t * 0.15 + i * 0.25) % 1.0
            pygame.draw.circle(surf, (255, 240, 200), (480 + i * 22, int(100 + k * 90)), 1)
