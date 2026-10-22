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


_DRAW = {
    "hunger": _food, "feed": _food, "happiness": _heart, "energy": _bolt, "rest": _moon,
    "cleanliness": _drop, "clean": _drop, "play": _ball, "coin": _coin, "map": _map,
    "plant_flower": _sprout, "plant_sunflower": _sunflower, "harvest": _basket,
    "decorate": _vase, "flowers": _flower, "lollipop": _lolly, "candy_apple": _apple,
    "flower_seeds": _seeds, "sunflower_seeds": _sunseeds, "games": _joystick,
    "snake": _snake, "pet_dash": _dash, "frogger": _frog,
}
