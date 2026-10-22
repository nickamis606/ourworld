"""Cached fonts, text renders and images.

Uses pygame's bundled default font (no fontconfig scan, identical on every
device) and caches everything so nothing is created per frame.
"""
from __future__ import annotations
import os
from collections import OrderedDict

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_fonts: dict = {}
_text: "OrderedDict" = OrderedDict()
_images: dict = {}
_TEXT_CACHE_MAX = 300


def font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    f = _fonts.get(key)
    if f is None:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[key] = f
    return f


def text(s: str, size: int, color=(30, 30, 40), bold: bool = False) -> pygame.Surface:
    """Rendered text surface, LRU-cached (safe to call every frame)."""
    key = (s, size, tuple(color), bold)
    surf = _text.get(key)
    if surf is not None:
        _text.move_to_end(key)
        return surf
    surf = font(size, bold).render(s, True, color)
    _text[key] = surf
    if len(_text) > _TEXT_CACHE_MAX:
        _text.popitem(last=False)
    return surf


def text_outlined(s: str, size: int, color, outline=(30, 30, 40), bold=True) -> pygame.Surface:
    key = ("__o", s, size, tuple(color), tuple(outline), bold)
    surf = _text.get(key)
    if surf is not None:
        return surf
    base = font(size, bold).render(s, True, color)
    edge = font(size, bold).render(s, True, outline)
    surf = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        surf.blit(edge, (dx, dy))
    surf.blit(base, (1, 1))
    _text[key] = surf
    return surf


def image(rel_path: str, alpha: bool = True):
    """Load an image from the repo once. Returns None if missing/broken."""
    if rel_path in _images:
        return _images[rel_path]
    path = os.path.join(ROOT, rel_path)
    surf = None
    if os.path.exists(path):
        try:
            surf = pygame.image.load(path)
            surf = surf.convert_alpha() if alpha else surf.convert()
        except pygame.error as e:
            print(f"[assets] failed to load {rel_path}: {e}")
    _images[rel_path] = surf
    return surf


def clear():
    _fonts.clear(); _text.clear(); _images.clear()
