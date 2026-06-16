#!/usr/bin/env python3
"""
MapOverlay - Reusable component for the neighborhood map overlay.

Handles drawing the map background, location badges, and connecting lines.
"""

import pygame
from typing import Dict, Tuple

from ui.common import draw_rounded_rect


class MapOverlay:
    def __init__(self, small_font, font):
        self.small_font = small_font
        self.font = font

        # Predefine location positions and data
        self.locations = {
            "home":                {"pos": (60, 110),  "name": "Home",      "color": (139, 90, 43),  "icon": "home"},
            "backyard":            {"pos": (200, 110), "name": "Backyard",   "color": (101, 67, 33),  "icon": "backyard"},
            "park":                {"pos": (340, 110), "name": "Park",       "color": (34, 139, 34),  "icon": "park"},
            "sweeties_candy_shop": {"pos": (60, 230),  "name": "Sweeties",   "color": (200, 50, 70),  "icon": "candy_shop"},
            "gens_garden":         {"pos": (200, 230), "name": "Garden",     "color": (90, 150, 210), "icon": "gens_garden"},
            "arcade":              {"pos": (340, 230), "name": "Arcade",     "color": (100, 149, 237), "icon": "arcade"},
        }

    def draw(self, surface, current_location: str):
        """Draw the full map overlay."""
        # Semi-transparent background
        overlay = pygame.Surface((640, 300), pygame.SRCALPHA)
        overlay.fill((250, 248, 240, 235))
        surface.blit(overlay, (0, 60))

        # Title
        title = self.font.render("Neighborhood Map — Click a location", True, (20, 20, 20))
        surface.blit(title, (25, 70))

        # Connecting path lines
        pygame.draw.line(surface, (180, 160, 140), (120, 180), (520, 180), 3)
        pygame.draw.line(surface, (180, 160, 140), (200, 180), (200, 260), 2)
        pygame.draw.line(surface, (180, 160, 140), (420, 180), (420, 260), 2)

        # Draw each location badge
        for key, data in self.locations.items():
            x, y = data["pos"]
            is_current = (key == current_location)
            self._draw_location_badge(surface, x, y, data, is_current)

    def _draw_location_badge(self, surface, x: int, y: int, data: dict, is_current: bool):
        rect = pygame.Rect(x, y, 130, 95)

        # Shadow
        pygame.draw.rect(surface, (0, 0, 0, 40), (x+3, y+3, 130, 95), border_radius=12)

        # Main badge
        draw_rounded_rect(surface, rect, (255, 255, 255), radius=12)
        border_w = 5 if is_current else 3
        draw_rounded_rect(surface, rect, data["color"], radius=12, width=border_w)

        # Icon (simple colored circle for now)
        cx, cy = x + 65, y + 45
        pygame.draw.circle(surface, data["color"], (cx, cy - 15), 18)

        # Name
        name_surf = self.small_font.render(data["name"], True, data["color"])
        surface.blit(name_surf, (x + 10, y + 70))

    def get_clicked_location(self, pos: Tuple[int, int]) -> str:
        """Return the location key that was clicked, or empty string."""
        for key, data in self.locations.items():
            rect = pygame.Rect(*data["pos"], 130, 95)
            if rect.collidepoint(pos):
                return key
        return ""
