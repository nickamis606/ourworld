"""Code-drawn furniture for the Home grid (no art files). Cached per (key, size)."""
import pygame

from core.furniture import FURNITURE, GRID_COLS

_cache: dict = {}

COL_X0, COL_W = 40, 80
ROW_Y = {0: 196, 1: 330, 2: 390}     # bottom (feet) of each row
CELL_H = {0: 70, 1: 60, 2: 58}


def cell_rect(col, row):
    h = CELL_H[row]
    return pygame.Rect(COL_X0 + col * COL_W - COL_W // 2 + 4, ROW_Y[row] - h, COL_W - 8, h)


def _dark(c, k=60):
    return tuple(max(0, v - k) for v in c)


def surface(key, size=64):
    ck = (key, size)
    s = _cache.get(ck)
    if s is not None:
        return s
    n = size
    s = pygame.Surface((n, n), pygame.SRCALPHA)
    col = FURNITURE.get(key, ("", False, (200, 200, 200)))[2]
    d = _dark(col)
    if key == "picture":
        pygame.draw.rect(s, (150, 100, 50), (n * .1, n * .15, n * .8, n * .65), border_radius=4)
        pygame.draw.rect(s, (200, 230, 250), (n * .18, n * .23, n * .64, n * .49))
        pygame.draw.circle(s, (250, 210, 80), (int(n * .66), int(n * .36)), int(n * .07))
        pygame.draw.polygon(s, (110, 180, 100), [(n * .18, n * .72), (n * .4, n * .42), (n * .62, n * .72)])
    elif key == "clock":
        pygame.draw.polygon(s, col, [(n * .5, n * .05), (n * .85, n * .3), (n * .15, n * .3)])
        pygame.draw.rect(s, col, (n * .22, n * .28, n * .56, n * .6), border_radius=4)
        pygame.draw.circle(s, (250, 245, 230), (int(n * .5), int(n * .5)), int(n * .17))
        pygame.draw.line(s, (40, 30, 30), (n * .5, n * .5), (n * .5, n * .38), 2)
        pygame.draw.line(s, (40, 30, 30), (n * .5, n * .5), (n * .6, n * .52), 2)
        pygame.draw.line(s, d, (n * .5, n * .7), (n * .5, n * .86), 2)
    elif key == "star_lights":
        pygame.draw.arc(s, (90, 80, 70), (0, -n * .2, n, n * .7), 3.4, 6.0, 2)
        for i in range(5):
            x = n * (.1 + i * .2)
            y = n * (.32 + (.1 if i in (1, 3) else .16 if i == 2 else 0))
            pygame.draw.circle(s, (250, 230, 120), (int(x), int(y)), int(n * .07))
            pygame.draw.circle(s, (255, 250, 210), (int(x), int(y)), int(n * .03))
    elif key == "garland":
        pygame.draw.arc(s, (110, 80, 50), (0, -n * .25, n, n * .7), 3.4, 6.0, 2)
        for i, c in enumerate([(220, 110, 40), (240, 180, 50), (190, 70, 40), (220, 110, 40), (240, 180, 50)]):
            x = n * (.08 + i * .2)
            y = n * (.3 + (.1 if i in (1, 3) else .14 if i == 2 else 0))
            pygame.draw.ellipse(s, c, (x, y, n * .16, n * .1))
    elif key == "plant":
        pygame.draw.polygon(s, (190, 110, 70), [(n * .3, n * .62), (n * .7, n * .62), (n * .64, n * .95), (n * .36, n * .95)])
        for dx, dy in ((-.18, -.2), (0, -.3), (.18, -.2), (-.1, -.08), (.1, -.08)):
            pygame.draw.ellipse(s, col, (n * (.4 + dx), n * (.5 + dy), n * .2, n * .32))
    elif key == "lamp":
        pygame.draw.rect(s, (120, 90, 60), (n * .47, n * .4, n * .06, n * .5))
        pygame.draw.ellipse(s, (120, 90, 60), (n * .32, n * .88, n * .36, n * .1))
        pygame.draw.polygon(s, col, [(n * .3, n * .45), (n * .7, n * .45), (n * .6, n * .12), (n * .4, n * .12)])
        glow = pygame.Surface((n, n), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 230, 150, 60), (n // 2, int(n * .4)), int(n * .45))
        s.blit(glow, (0, 0))
    elif key == "toy_box":
        pygame.draw.rect(s, col, (n * .12, n * .45, n * .76, n * .5), border_radius=5)
        pygame.draw.rect(s, d, (n * .1, n * .4, n * .8, n * .12), border_radius=4)
        pygame.draw.circle(s, (90, 160, 230), (int(n * .35), int(n * .4)), int(n * .1))
        pygame.draw.polygon(s, (250, 210, 70), [(n * .55, n * .42), (n * .65, n * .22), (n * .75, n * .42)])
        pygame.draw.circle(s, (255, 255, 255), (int(n * .5), int(n * .7)), int(n * .07))
    elif key == "cushion":
        pygame.draw.ellipse(s, d, (n * .05, n * .6, n * .9, n * .36))
        pygame.draw.ellipse(s, col, (n * .08, n * .56, n * .84, n * .32))
        pygame.draw.ellipse(s, _dark(col, -30), (n * .25, n * .62, n * .5, n * .16))
    elif key == "beanbag":
        pygame.draw.ellipse(s, col, (n * .1, n * .35, n * .8, n * .62))
        pygame.draw.ellipse(s, _dark(col, -40), (n * .25, n * .42, n * .3, n * .18))
    elif key == "bookshelf":
        pygame.draw.rect(s, col, (n * .14, n * .15, n * .72, n * .82), border_radius=3)
        for row in range(3):
            y = n * (.2 + row * .26)
            for i, c in enumerate([(200, 70, 70), (70, 120, 200), (230, 190, 60), (100, 170, 100)]):
                pygame.draw.rect(s, c, (n * (.2 + i * .15), y, n * .11, n * .2))
            pygame.draw.rect(s, d, (n * .14, y + n * .2, n * .72, n * .04))
    elif key == "fishbowl":
        pygame.draw.rect(s, (150, 110, 70), (n * .2, n * .82, n * .6, n * .14), border_radius=3)
        pygame.draw.circle(s, (180, 225, 250), (int(n * .5), int(n * .56)), int(n * .3))
        pygame.draw.circle(s, (120, 190, 240), (int(n * .5), int(n * .56)), int(n * .3), 2)
        pygame.draw.ellipse(s, (250, 140, 40), (n * .38, n * .52, n * .2, n * .12))
        pygame.draw.polygon(s, (250, 140, 40), [(n * .56, n * .58), (n * .64, n * .52), (n * .64, n * .64)])
    elif key == "trophy":
        pygame.draw.polygon(s, col, [(n * .26, n * .15), (n * .74, n * .15), (n * .64, n * .5), (n * .36, n * .5)])
        pygame.draw.circle(s, col, (int(n * .26), int(n * .26)), int(n * .09), 3)
        pygame.draw.circle(s, col, (int(n * .74), int(n * .26)), int(n * .09), 3)
        pygame.draw.rect(s, col, (n * .45, n * .48, n * .1, n * .2))
        pygame.draw.rect(s, (130, 90, 50), (n * .28, n * .68, n * .44, n * .28), border_radius=3)
    elif key == "pumpkin":
        pygame.draw.ellipse(s, d, (n * .1, n * .38, n * .8, n * .58))
        pygame.draw.ellipse(s, col, (n * .12, n * .4, n * .76, n * .54))
        pygame.draw.line(s, d, (n * .5, n * .44), (n * .5, n * .92), 2)
        pygame.draw.rect(s, (80, 130, 50), (n * .46, n * .26, n * .08, n * .16))
    elif key == "snowglobe":
        pygame.draw.rect(s, (150, 100, 60), (n * .22, n * .78, n * .56, n * .18), border_radius=4)
        pygame.draw.circle(s, col, (int(n * .5), int(n * .5)), int(n * .3))
        pygame.draw.circle(s, (255, 255, 255), (int(n * .5), int(n * .62)), int(n * .09))
        pygame.draw.circle(s, (255, 255, 255), (int(n * .5), int(n * .48)), int(n * .06))
        for x, y in ((.36, .36), (.6, .3), (.66, .52), (.4, .52)):
            pygame.draw.circle(s, (255, 255, 255), (int(n * x), int(n * y)), 2)
    elif key == "egg_basket":
        pygame.draw.ellipse(s, (250, 150, 190), (n * .25, n * .38, n * .2, n * .28))
        pygame.draw.ellipse(s, (140, 200, 250), (n * .42, n * .32, n * .2, n * .28))
        pygame.draw.ellipse(s, (250, 220, 90), (n * .58, n * .4, n * .2, n * .26))
        pygame.draw.polygon(s, (190, 140, 80), [(n * .14, n * .58), (n * .86, n * .58), (n * .74, n * .95), (n * .26, n * .95)])
        pygame.draw.arc(s, (160, 110, 60), (n * .16, n * .14, n * .68, n * .9), 0.2, 2.9, 3)
    elif key == "beach_ball":
        r = int(n * .3)
        c = (n // 2, int(n * .66))
        pygame.draw.circle(s, (255, 255, 255), c, r)
        pygame.draw.polygon(s, col, [c, (c[0] - r, c[1]), (c[0] - r * .7, c[1] - r * .7), (c[0], c[1] - r)])
        pygame.draw.polygon(s, (90, 160, 250), [c, (c[0] + r, c[1]), (c[0] + r * .7, c[1] + r * .7), (c[0], c[1] + r)])
        pygame.draw.circle(s, d, c, r, 2)
    else:
        pygame.draw.rect(s, col, (n * .2, n * .3, n * .6, n * .6), border_radius=6)
    _cache[ck] = s
    return s


def draw_layout(surf, layout, size=64):
    for col, row, key in sorted(layout, key=lambda it: it[1]):
        r = cell_rect(col, row)
        img = surface(key, size if row == 0 else 58)
        surf.blit(img, img.get_rect(midbottom=(r.centerx, r.bottom)))


__all__ = ["surface", "draw_layout", "cell_rect", "GRID_COLS"]
