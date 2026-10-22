"""Procedural icons, rendered once per (name, size) and cached."""
import math

import pygame

_cache: dict = {}


def icon(name: str, size: int = 24) -> pygame.Surface:
    key = (name, size)
    s = _cache.get(key)
    if s is None:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        _DRAW.get(name, _dot)(s, size)
        _cache[key] = s
    return s


def _dot(s, n):
    pygame.draw.circle(s, (200, 200, 200), (n // 2, n // 2), n // 3)


def _food(s, n):  # bowl with food
    pygame.draw.ellipse(s, (240, 170, 80), (n * .15, n * .25, n * .7, n * .35))
    pygame.draw.polygon(s, (200, 90, 50), [(n * .05, n * .45), (n * .95, n * .45), (n * .75, n * .85), (n * .25, n * .85)])
    pygame.draw.line(s, (250, 220, 200), (n * .2, n * .55), (n * .8, n * .55), 2)


def _heart(s, n):
    c = (240, 80, 130)
    r = n * .24
    pygame.draw.circle(s, c, (int(n * .32), int(n * .38)), int(r))
    pygame.draw.circle(s, c, (int(n * .68), int(n * .38)), int(r))
    pygame.draw.polygon(s, c, [(n * .1, n * .45), (n * .9, n * .45), (n * .5, n * .9)])


def _bolt(s, n):
    pygame.draw.polygon(s, (250, 200, 40), [(n * .6, n * .05), (n * .2, n * .55), (n * .48, n * .55),
                                             (n * .38, n * .95), (n * .82, n * .4), (n * .52, n * .4)])
    pygame.draw.polygon(s, (190, 140, 20), [(n * .6, n * .05), (n * .2, n * .55), (n * .48, n * .55),
                                             (n * .38, n * .95), (n * .82, n * .4), (n * .52, n * .4)], 1)


def _drop(s, n):
    c = (70, 160, 235)
    pygame.draw.circle(s, c, (n // 2, int(n * .62)), int(n * .3))
    pygame.draw.polygon(s, c, [(n * .5, n * .05), (n * .22, n * .55), (n * .78, n * .55)])
    pygame.draw.circle(s, (210, 240, 255), (int(n * .4), int(n * .62)), max(2, n // 10))


def _coin(s, n):
    pygame.draw.circle(s, (200, 140, 20), (n // 2, n // 2), n // 2 - 1)
    pygame.draw.circle(s, (250, 205, 60), (n // 2, n // 2), n // 2 - 3)
    pygame.draw.rect(s, (200, 140, 20), (n * .44, n * .28, n * .12, n * .44))


def _ball(s, n):
    pygame.draw.circle(s, (240, 90, 70), (n // 2, n // 2), n // 2 - 2)
    pygame.draw.arc(s, (255, 255, 255), (n * .1, n * .1, n * .8, n * .8), 0.3, 2.6, 2)


def _moon(s, n):
    pygame.draw.circle(s, (180, 160, 250), (n // 2, n // 2), n // 2 - 2)
    pygame.draw.circle(s, (0, 0, 0, 0), (int(n * .66), int(n * .38)), n // 2 - 3)
    pygame.draw.circle(s, (255, 255, 255), (int(n * .75), int(n * .75)), 2)


def _map(s, n):
    pts = [(n * .08, n * .2), (n * .36, n * .1), (n * .64, n * .2), (n * .92, n * .1),
           (n * .92, n * .8), (n * .64, n * .9), (n * .36, n * .8), (n * .08, n * .9)]
    pygame.draw.polygon(s, (240, 230, 200), pts)
    pygame.draw.polygon(s, (150, 120, 80), pts, 2)
    pygame.draw.line(s, (150, 120, 80), (n * .36, n * .1), (n * .36, n * .8), 1)
    pygame.draw.line(s, (150, 120, 80), (n * .64, n * .2), (n * .64, n * .9), 1)
    pygame.draw.circle(s, (220, 60, 60), (int(n * .5), int(n * .5)), max(2, n // 8))


def _sprout(s, n):
    pygame.draw.line(s, (60, 150, 60), (n // 2, n * .9), (n // 2, n * .35), 3)
    pygame.draw.ellipse(s, (90, 190, 80), (n * .12, n * .25, n * .38, n * .22))
    pygame.draw.ellipse(s, (90, 190, 80), (n * .5, n * .15, n * .38, n * .22))
    pygame.draw.rect(s, (140, 90, 50), (n * .25, n * .8, n * .5, n * .15), border_radius=2)


def _sunflower(s, n):
    pygame.draw.line(s, (60, 150, 60), (n // 2, n * .95), (n // 2, n * .5), 3)
    for a in range(8):
        ang = a * math.tau / 8
        pygame.draw.circle(s, (250, 200, 40), (int(n / 2 + math.cos(ang) * n * .22), int(n * .38 + math.sin(ang) * n * .22)), max(2, n // 8))
    pygame.draw.circle(s, (130, 80, 30), (n // 2, int(n * .38)), max(3, n // 6))


def _flower(s, n):
    for a in range(5):
        ang = a * math.tau / 5
        pygame.draw.circle(s, (250, 120, 170), (int(n / 2 + math.cos(ang) * n * .2), int(n / 2 + math.sin(ang) * n * .2)), max(3, n // 6))
    pygame.draw.circle(s, (255, 220, 90), (n // 2, n // 2), max(2, n // 8))


def _basket(s, n):
    pygame.draw.arc(s, (150, 100, 50), (n * .2, n * .05, n * .6, n * .7), 0, math.pi, 3)
    pygame.draw.rect(s, (180, 120, 60), (n * .1, n * .45, n * .8, n * .45), border_radius=4)
    for k in range(3):
        pygame.draw.circle(s, (250, 120, 170), (int(n * (.3 + k * .2)), int(n * .45)), max(2, n // 9))


def _vase(s, n):
    pygame.draw.polygon(s, (90, 150, 210), [(n * .3, n * .45), (n * .7, n * .45), (n * .78, n * .95), (n * .22, n * .95)])
    for k, c in enumerate(((250, 120, 170), (250, 210, 60), (180, 140, 255))):
        x = n * (.3 + k * .2)
        pygame.draw.line(s, (60, 150, 60), (n / 2, n * .5), (x, n * .2), 2)
        pygame.draw.circle(s, c, (int(x), int(n * .18)), max(2, n // 8))


def _lolly(s, n):
    pygame.draw.line(s, (240, 240, 240), (n // 2, n * .95), (n // 2, n * .5), 3)
    pygame.draw.circle(s, (250, 90, 150), (n // 2, int(n * .38)), int(n * .32))
    pygame.draw.arc(s, (255, 255, 255), (n * .3, n * .18, n * .4, n * .4), 0, 4.5, 2)


def _apple(s, n):
    pygame.draw.circle(s, (210, 40, 50), (n // 2, int(n * .58)), int(n * .36))
    pygame.draw.line(s, (120, 80, 40), (n // 2, n * .25), (n * .55, n * .05), 3)
    pygame.draw.ellipse(s, (255, 150, 150), (n * .3, n * .4, n * .15, n * .2))


def _seeds(s, n):
    pygame.draw.rect(s, (240, 220, 170), (n * .18, n * .08, n * .64, n * .84), border_radius=3)
    pygame.draw.circle(s, (250, 120, 170), (n // 2, int(n * .4)), max(3, n // 6))
    for k in range(3):
        pygame.draw.circle(s, (120, 80, 40), (int(n * (.32 + k * .18)), int(n * .76)), 2)


def _sunseeds(s, n):
    _seeds(s, n)
    pygame.draw.circle(s, (250, 200, 40), (n // 2, int(n * .4)), max(3, n // 5))
    pygame.draw.circle(s, (130, 80, 30), (n // 2, int(n * .4)), max(2, n // 10))


def _joystick(s, n):
    pygame.draw.rect(s, (60, 60, 80), (n * .1, n * .6, n * .8, n * .32), border_radius=4)
    pygame.draw.line(s, (40, 40, 40), (n // 2, n * .62), (n * .5, n * .25), 4)
    pygame.draw.circle(s, (230, 50, 60), (n // 2, int(n * .22)), max(3, n // 6))


def _snake(s, n):
    pts = [(n * .1, n * .7), (n * .3, n * .5), (n * .5, n * .7), (n * .7, n * .5), (n * .88, n * .3)]
    pygame.draw.lines(s, (80, 200, 110), False, pts, max(3, n // 6))
    pygame.draw.circle(s, (80, 200, 110), (int(n * .88), int(n * .3)), max(3, n // 7))


def _dash(s, n):
    pygame.draw.ellipse(s, (240, 160, 80), (n * .15, n * .35, n * .6, n * .4))
    pygame.draw.circle(s, (240, 160, 80), (int(n * .75), int(n * .35)), max(3, n // 6))
    for k in range(3):
        pygame.draw.line(s, (255, 255, 255), (0, n * (.4 + k * .12)), (n * .12, n * (.4 + k * .12)), 2)


def _frog(s, n):
    pygame.draw.ellipse(s, (70, 190, 70), (n * .12, n * .3, n * .76, n * .55))
    for x in (.3, .7):
        pygame.draw.circle(s, (70, 190, 70), (int(n * x), int(n * .3)), max(3, n // 7))
        pygame.draw.circle(s, (20, 20, 20), (int(n * x), int(n * .3)), max(1, n // 14))


def _swim(s, n):  # waves + splash
    for k in range(2):
        y = n * (.55 + k * .2)
        pts = [(n * x / 8, y + (n * .07 if x % 2 else -n * .07)) for x in range(9)]
        pygame.draw.lines(s, (60, 160, 230) if k else (120, 200, 250), False, pts, max(2, n // 10))
    pygame.draw.circle(s, (200, 235, 255), (int(n * .3), int(n * .25)), max(2, n // 10))
    pygame.draw.circle(s, (200, 235, 255), (int(n * .55), int(n * .15)), max(2, n // 12))
    pygame.draw.circle(s, (200, 235, 255), (int(n * .72), int(n * .3)), max(2, n // 9))


def _book(s, n):  # open book
    pygame.draw.polygon(s, (240, 235, 220), [(n * .5, n * .3), (n * .08, n * .2), (n * .08, n * .78), (n * .5, n * .88)])
    pygame.draw.polygon(s, (250, 245, 232), [(n * .5, n * .3), (n * .92, n * .2), (n * .92, n * .78), (n * .5, n * .88)])
    pygame.draw.line(s, (150, 90, 160), (n * .5, n * .3), (n * .5, n * .88), 2)
    for k in range(3):
        y = n * (.38 + k * .14)
        pygame.draw.line(s, (170, 160, 150), (n * .16, y), (n * .42, y + n * .03), 1)
        pygame.draw.line(s, (170, 160, 150), (n * .58, y + n * .03), (n * .84, y), 1)
    pygame.draw.polygon(s, (150, 90, 160), [(n * .08, n * .78), (n * .5, n * .88), (n * .92, n * .78),
                                           (n * .92, n * .86), (n * .5, n * .96), (n * .08, n * .86)])


def _spa(s, n):  # rolled towel + bubbles
    pygame.draw.rect(s, (250, 170, 210), (n * .1, n * .5, n * .62, n * .34), border_radius=max(2, n // 8))
    pygame.draw.circle(s, (255, 220, 235), (int(n * .72), int(n * .67)), int(n * .17))
    pygame.draw.circle(s, (230, 140, 190), (int(n * .72), int(n * .67)), int(n * .08))
    for (x, y, r) in ((.25, .3, .12), (.48, .18, .09), (.68, .32, .1)):
        pygame.draw.circle(s, (200, 235, 255), (int(n * x), int(n * y)), max(2, int(n * r)), max(1, n // 16))


def _bricks(s, n):
    cols = [(240, 90, 90), (250, 180, 60), (90, 200, 120)]
    for r in range(3):
        for c in range(3):
            pygame.draw.rect(s, cols[r], (n * (.06 + c * .31), n * (.08 + r * .17), n * .27, n * .13))
    pygame.draw.circle(s, (255, 255, 255), (int(n * .55), int(n * .7)), max(2, n // 10))
    pygame.draw.rect(s, (120, 200, 255), (n * .25, n * .86, n * .5, n * .1), border_radius=2)


def _cards(s, n):
    pygame.draw.rect(s, (90, 110, 200), (n * .08, n * .2, n * .45, n * .62), border_radius=max(2, n // 10))
    pygame.draw.rect(s, (255, 250, 240), (n * .42, n * .12, n * .45, n * .62), border_radius=max(2, n // 10))
    pygame.draw.rect(s, (90, 110, 200), (n * .42, n * .12, n * .45, n * .62), max(1, n // 16), border_radius=max(2, n // 10))
    _heart_at(s, n * .645, n * .43, n * .28)


def _heart_at(s, cx, cy, w):
    r = max(2, int(w * .3))
    pygame.draw.circle(s, (230, 70, 110), (int(cx - w * .25), int(cy - w * .1)), r)
    pygame.draw.circle(s, (230, 70, 110), (int(cx + w * .25), int(cy - w * .1)), r)
    pygame.draw.polygon(s, (230, 70, 110), [(cx - w * .55, cy), (cx + w * .55, cy), (cx, cy + w * .55)])


def _mole(s, n):
    pygame.draw.ellipse(s, (60, 40, 30), (n * .05, n * .68, n * .9, n * .26))
    pygame.draw.ellipse(s, (150, 100, 70), (n * .22, n * .25, n * .56, n * .6))
    pygame.draw.rect(s, (60, 40, 30), (n * .05, n * .8, n * .9, n * .2))
    for x in (.4, .6):
        pygame.draw.circle(s, (20, 20, 20), (int(n * x), int(n * .45)), max(1, n // 16))
    pygame.draw.circle(s, (240, 140, 150), (int(n * .5), int(n * .56)), max(2, n // 12))


def _talk(s, n):
    pygame.draw.ellipse(s, (255, 255, 255), (n * .06, n * .12, n * .88, n * .62))
    pygame.draw.polygon(s, (255, 255, 255), [(n * .25, n * .6), (n * .2, n * .92), (n * .48, n * .68)])
    for k in range(3):
        pygame.draw.circle(s, (120, 100, 160), (int(n * (.3 + k * .2)), int(n * .43)), max(1, n // 14))


def _explore(s, n):
    pygame.draw.circle(s, (220, 240, 255), (int(n * .42), int(n * .42)), int(n * .28))
    pygame.draw.circle(s, (90, 70, 50), (int(n * .42), int(n * .42)), int(n * .28), max(2, n // 10))
    pygame.draw.line(s, (90, 70, 50), (n * .62, n * .62), (n * .92, n * .92), max(3, n // 7))


def _lantern(s, n):
    pygame.draw.circle(s, (255, 230, 150), (n // 2, int(n * .55)), int(n * .4))
    pygame.draw.rect(s, (255, 200, 90), (n * .3, n * .3, n * .4, n * .52), border_radius=max(2, n // 6))
    pygame.draw.rect(s, (130, 80, 40), (n * .3, n * .3, n * .4, n * .52), max(1, n // 14), border_radius=max(2, n // 6))
    pygame.draw.rect(s, (130, 80, 40), (n * .36, n * .2, n * .28, n * .1))
    pygame.draw.line(s, (130, 80, 40), (n * .5, n * .02), (n * .5, n * .2), 2)


def _journal(s, n):
    pygame.draw.rect(s, (200, 90, 80), (n * .14, n * .08, n * .72, n * .84), border_radius=max(2, n // 10))
    pygame.draw.rect(s, (250, 240, 220), (n * .26, n * .16, n * .52, n * .68), border_radius=2)
    for k in range(3):
        pygame.draw.line(s, (180, 160, 140), (n * .32, n * (.32 + k * .16)), (n * .72, n * (.32 + k * .16)), 1)
    pygame.draw.rect(s, (250, 200, 70), (n * .6, n * .02, n * .1, n * .3))


def _square(s, n):
    pygame.draw.ellipse(s, (160, 160, 170), (n * .1, n * .55, n * .8, n * .3))
    pygame.draw.ellipse(s, (120, 190, 240), (n * .2, n * .6, n * .6, n * .18))
    pygame.draw.rect(s, (160, 160, 170), (n * .44, n * .2, n * .12, n * .45))
    pygame.draw.circle(s, (120, 190, 240), (n // 2, int(n * .18)), max(2, n // 9))


def _woods(s, n):
    pygame.draw.rect(s, (110, 72, 44), (n * .44, n * .5, n * .12, n * .44))
    pygame.draw.circle(s, (60, 140, 70), (n // 2, int(n * .38)), int(n * .32))
    for k in range(5):
        x = n * (.25 + k * .12)
        pygame.draw.line(s, (90, 170, 90), (x, n * .45), (x, n * .8), 2)


def _star_shape(s, cx, cy, r, col):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(s, col, pts)


def _spark(s, n):
    _star_shape(s, n / 2, n / 2, n * .46, (255, 220, 90))


_DRAW = {
    "hunger": _food, "feed": _food, "happiness": _heart, "energy": _bolt, "rest": _moon,
    "cleanliness": _drop, "clean": _drop, "play": _ball, "coin": _coin, "map": _map,
    "plant_flower": _sprout, "plant_sunflower": _sunflower, "harvest": _basket,
    "decorate": _vase, "flowers": _flower, "lollipop": _lolly, "candy_apple": _apple,
    "flower_seeds": _seeds, "sunflower_seeds": _sunseeds, "games": _joystick,
    "snake": _snake, "pet_dash": _dash, "frogger": _frog,
    "swim": _swim, "read": _book, "spa": _spa, "pamper": _spa,
    "brick_bop": _bricks, "pet_pairs": _cards, "mole_pop": _mole,
    "talk": _talk, "explore": _explore, "lantern": _lantern, "light": _lantern,
    "journal": _journal, "square": _square, "woods": _woods, "spark": _spark,
}


# ---------------------------------------------------------------- stickers
_scache: dict = {}


def sticker(shape: str, col: tuple, size: int = 48, owned: bool = True) -> pygame.Surface:
    """Round die-cut sticker with a simple shape. Unowned = gray silhouette."""
    key = (shape, col, size, owned)
    s = _scache.get(key)
    if s is not None:
        return s
    n = size
    s = pygame.Surface((n, n), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 255, 255) if owned else (90, 86, 100), (n // 2, n // 2), n // 2)
    pygame.draw.circle(s, (230, 225, 235) if owned else (70, 66, 80), (n // 2, n // 2), n // 2, 2)
    c = col if owned else (120, 116, 130)
    d = _dark(c)
    m = n / 2
    if shape == "star":
        _star_shape(s, m, m, n * .32, c)
    elif shape == "key":
        pygame.draw.circle(s, c, (int(n * .35), int(m)), int(n * .14), max(2, n // 12))
        pygame.draw.line(s, c, (n * .47, m), (n * .78, m), max(3, n // 10))
        pygame.draw.line(s, c, (n * .7, m), (n * .7, n * .64), max(2, n // 12))
    elif shape == "check":
        r = pygame.Rect(n * .22, n * .22, n * .56, n * .56)
        pygame.draw.rect(s, c, r)
        for k in range(3):
            pygame.draw.line(s, (255, 255, 255), (r.x + k * r.w / 3 + 6, r.y), (r.x + k * r.w / 3 + 6, r.bottom), 2)
            pygame.draw.line(s, (255, 255, 255), (r.x, r.y + k * r.h / 3 + 6), (r.right, r.y + k * r.h / 3 + 6), 2)
    elif shape == "swirl":
        pygame.draw.line(s, (200, 170, 130), (m, m), (m, n * .9), max(2, n // 14))
        pygame.draw.circle(s, c, (int(m), int(n * .42)), int(n * .24))
        pygame.draw.arc(s, (255, 255, 255), (m - n * .14, n * .28, n * .28, n * .28), 0, 4.5, 2)
    elif shape == "leaf":
        pygame.draw.ellipse(s, c, (n * .2, n * .3, n * .6, n * .4))
        pygame.draw.line(s, d, (n * .22, n * .62), (n * .78, n * .4), 2)
    elif shape == "shell":
        pygame.draw.polygon(s, c, [(n * .2, n * .62), (m, n * .2), (n * .8, n * .62)])
        pygame.draw.ellipse(s, c, (n * .2, n * .5, n * .6, n * .24))
        for k in (-1, 0, 1):
            pygame.draw.line(s, d, (m, n * .24), (m + k * n * .22, n * .68), 2)
    elif shape == "book":
        pygame.draw.rect(s, c, (n * .24, n * .22, n * .52, n * .56), border_radius=3)
        pygame.draw.rect(s, (255, 250, 230), (n * .3, n * .26, n * .4, n * .1))
    elif shape == "bubbles":
        for (x, y, r) in ((.4, .55, .18), (.62, .38, .13), (.64, .64, .09)):
            pygame.draw.circle(s, c, (int(n * x), int(n * y)), int(n * r), max(2, n // 16))
    elif shape == "fox":
        pygame.draw.polygon(s, c, [(n * .2, n * .25), (n * .8, n * .25), (m, n * .8)])
        pygame.draw.polygon(s, (255, 250, 240), [(n * .35, n * .5), (n * .65, n * .5), (m, n * .8)])
        pygame.draw.circle(s, (30, 30, 30), (int(m), int(n * .76)), max(2, n // 16))
    elif shape == "lantern":
        _lantern(s, n) if owned else pygame.draw.rect(s, c, (n * .3, n * .3, n * .4, n * .5), border_radius=6)
    elif shape == "flag":
        pygame.draw.line(s, (90, 70, 60), (n * .1, n * .35), (n * .9, n * .35), 2)
        for k, cc in enumerate((c, (250, 120, 170), (250, 210, 70))):
            x = n * (.16 + k * .24)
            pygame.draw.polygon(s, cc if owned else c, [(x, n * .35), (x + n * .2, n * .35), (x + n * .1, n * .7)])
    elif shape == "acorn":
        pygame.draw.ellipse(s, c, (n * .3, n * .38, n * .4, n * .42))
        pygame.draw.ellipse(s, d, (n * .26, n * .28, n * .48, n * .2))
    elif shape == "mushroom":
        pygame.draw.rect(s, (245, 235, 215), (n * .42, n * .45, n * .16, n * .3))
        pygame.draw.ellipse(s, c, (n * .2, n * .24, n * .6, n * .32))
        pygame.draw.circle(s, (255, 255, 255), (int(n * .4), int(n * .36)), max(2, n // 14))
    elif shape == "feather":
        pygame.draw.ellipse(s, c, (n * .38, n * .14, n * .24, n * .66))
        pygame.draw.line(s, d, (m, n * .18), (m, n * .86), 2)
    elif shape == "pinecone":
        pygame.draw.ellipse(s, c, (n * .32, n * .2, n * .36, n * .6))
        for k in range(4):
            pygame.draw.line(s, d, (n * .34, n * (.3 + k * .12)), (n * .66, n * (.3 + k * .12)), 2)
    elif shape == "ladybug":
        pygame.draw.circle(s, c, (int(m), int(m + 2)), int(n * .26))
        pygame.draw.line(s, (30, 30, 30), (m, n * .28), (m, n * .76), 2)
        pygame.draw.circle(s, (30, 30, 30), (int(m), int(n * .28)), int(n * .1))
        for (x, y) in ((.4, .48), (.6, .48), (.42, .64), (.58, .64)):
            pygame.draw.circle(s, (30, 30, 30), (int(n * x), int(n * y)), max(2, n // 18))
    else:
        pygame.draw.circle(s, c, (int(m), int(m)), int(n * .25))
    _scache[key] = s
    return s


def _dark(c, k=50):
    return tuple(max(0, v - k) for v in c)
