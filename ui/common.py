#!/usr/bin/env python3
"""
common.py - Shared UI helper functions for OurWorld.

Contains small, reusable drawing utilities to keep scene and UI code clean.
"""

import pygame
from typing import Tuple


def draw_rounded_rect(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int],
                      radius: int = 8, width: int = 0):
    """
    Draw a rounded rectangle.

    Args:
        surface: Target surface
        rect: Rectangle to draw
        color: Fill or border color
        radius: Corner radius
        width: If > 0, draws only the border with this thickness
    """
    if width > 0:
        pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_text_centered(surface: pygame.Surface, text: str, font: pygame.font.Font,
                      color: Tuple[int, int, int], center_pos: Tuple[int, int]):
    """
    Draw text centered at a given position.
    """
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
             color: Tuple[int, int, int], pos: Tuple[int, int]):
    """
    Simple text drawing at top-left position.
    """
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, pos)


def draw_progress_bar(surface: pygame.Surface, rect: pygame.Rect, value: float,
                     max_value: float = 100.0, bg_color=(180, 180, 180),
                     fill_color=(100, 200, 100), border_radius: int = 4):
    """
    Draw a simple progress bar.
    """
    # Background
    pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)

    # Fill
    if max_value > 0:
        fill_ratio = max(0.0, min(1.0, value / max_value))
        fill_width = int(rect.width * fill_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=border_radius)


def get_centered_rect(center: Tuple[int, int], width: int, height: int) -> pygame.Rect:
    """
    Return a rect centered at the given point.
    """
    x = center[0] - width // 2
    y = center[1] - height // 2
    return pygame.Rect(x, y, width, height)
