"""Code-drawn growth accessories and idle emote bubbles (no extra art files)."""
import math

import pygame

from engine import assets


def draw_accessory(surf, rect, stage, t=0.0):
    cx = rect.centerx
    if stage == "baby":
        # a tiny sprout curl on the head
        top = rect.top + 4
        pygame.draw.line(surf, (60, 140, 60), (cx, top + 6), (cx, top - 8), 3)
        pygame.draw.ellipse(surf, (110, 200, 90), (cx - 12, top - 16, 12, 8))
        pygame.draw.ellipse(surf, (110, 200, 90), (cx, top - 14, 12, 8))
    elif stage == "kid":
        # a cozy scarf around the neck
        y = rect.top + int(rect.h * 0.70)
        w = int(rect.w * 0.52)
        r = pygame.Rect(0, 0, w, 12)
        r.center = (cx, y)
        pygame.draw.rect(surf, (150, 40, 50), r.inflate(2, 2), border_radius=6)
        pygame.draw.rect(surf, (230, 70, 80), r, border_radius=6)
        tail = [(r.right - 18, r.bottom - 2), (r.right - 6, r.bottom - 2), (r.right - 2 + int(2 * math.sin(t * 3)), r.bottom + 16),
                (r.right - 14, r.bottom + 14)]
        pygame.draw.polygon(surf, (230, 70, 80), tail)
        for i in range(3):
            pygame.draw.line(surf, (255, 220, 220), (r.x + 10 + i * 14, r.y + 2), (r.x + 10 + i * 14, r.bottom - 3), 2)
    elif stage == "adult":
        # a little gold crown
        top = rect.top + 2
        pts = [(cx - 16, top + 4), (cx - 16, top - 10), (cx - 8, top - 3), (cx, top - 14), (cx + 8, top - 3),
               (cx + 16, top - 10), (cx + 16, top + 4)]
        pygame.draw.polygon(surf, (150, 100, 20), [(x, y + 1) for x, y in pts])
        pygame.draw.polygon(surf, (250, 205, 60), pts)
        pygame.draw.circle(surf, (230, 80, 120), (cx, top - 2), 3)


_EMOTE_TEXT = {"zzz": "z Z", "question": "?", "hmph": "hmph", "babble": "goo!", "sigh": "...",
               "bounce": "!"}


def draw_emote(surf, x, y, kind, k):
    """k: 0..1 life of the bubble (pops in, floats, fades)."""
    rise = int(10 * k)
    y = y - rise
    scale = min(1.0, k * 5)
    if scale <= 0:
        return
    r = int(18 * scale)
    pygame.draw.circle(surf, (90, 70, 70), (x, y + 1), r + 2)
    pygame.draw.circle(surf, (255, 252, 246), (x, y), r)
    pygame.draw.circle(surf, (255, 252, 246), (x - 10, y + r), 4)
    if r < 12:
        return
    if kind == "heart":
        pygame.draw.circle(surf, (235, 80, 110), (x - 5, y - 2), 6)
        pygame.draw.circle(surf, (235, 80, 110), (x + 5, y - 2), 6)
        pygame.draw.polygon(surf, (235, 80, 110), [(x - 11, y), (x + 11, y), (x, y + 11)])
    elif kind == "note":
        pygame.draw.circle(surf, (90, 110, 200), (x - 4, y + 6), 5)
        pygame.draw.line(surf, (90, 110, 200), (x, y + 6), (x, y - 10), 3)
        pygame.draw.line(surf, (90, 110, 200), (x, y - 10), (x + 8, y - 6), 3)
    elif kind in ("sparkle", "star"):
        c = (250, 200, 60)
        pygame.draw.polygon(surf, c, [(x, y - 11), (x + 3, y - 3), (x + 11, y), (x + 3, y + 3), (x, y + 11),
                                      (x - 3, y + 3), (x - 11, y), (x - 3, y - 3)])
    elif kind == "rain":
        pygame.draw.circle(surf, (150, 160, 180), (x - 5, y - 3), 7)
        pygame.draw.circle(surf, (150, 160, 180), (x + 5, y - 4), 8)
        for i in range(3):
            pygame.draw.line(surf, (90, 140, 230), (x - 6 + i * 6, y + 5), (x - 8 + i * 6, y + 11), 2)
    else:
        txt = assets.text(_EMOTE_TEXT.get(kind, "!"), 18 if len(_EMOTE_TEXT.get(kind, "!")) < 4 else 14,
                          (90, 60, 60), bold=True)
        surf.blit(txt, txt.get_rect(center=(x, y)))
