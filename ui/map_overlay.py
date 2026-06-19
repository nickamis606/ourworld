#!/usr/bin/env python3
"""
MapOverlay - Reusable component for the neighborhood map overlay.

Improved with cached panel, distinctive geometric icons, stronger
current-location highlighting, and cozier visual treatment.
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

        # Cache the semi-transparent panel once (performance + consistency)
        self._panel = pygame.Surface((640, 300), pygame.SRCALPHA)
        self._panel.fill((250, 248, 240, 235))

    def draw(self, surface, current_location: str):
        """Draw the full map overlay (uses cached panel)."""
        surface.blit(self._panel, (0, 60))

        # Title
        title = self.font.render("Neighborhood Map — Click a location", True, (20, 20, 20))
        surface.blit(title, (25, 70))

        # Connecting path lines (slightly softer)
        pygame.draw.line(surface, (180, 160, 140), (120, 180), (520, 180), 4)
        pygame.draw.line(surface, (180, 160, 140), (200, 180), (200, 260), 3)
        pygame.draw.line(surface, (180, 160, 140), (420, 180), (420, 260), 3)

        # Draw each location badge
        for key, data in self.locations.items():
            x, y = data["pos"]
            is_current = (key == current_location)
            self._draw_location_badge(surface, x, y, data, is_current)

    def _draw_location_badge(self, surface, x: int, y: int, data: dict, is_current: bool):
        rect = pygame.Rect(x, y, 130, 95)

        # Soft shadow
        pygame.draw.rect(surface, (0, 0, 0, 35), (x+3, y+3, 130, 95), border_radius=12)

        # Main badge
        draw_rounded_rect(surface, rect, (255, 255, 255), radius=12)
        border_w = 6 if is_current else 3
        border_color = (255, 215, 0) if is_current else data["color"]
        draw_rounded_rect(surface, rect, border_color, radius=12, width=border_w)

        # Icon (distinctive per location)
        cx, cy = x + 65, y + 42
        self._draw_icon(surface, cx, cy, data["icon"], data["color"], is_current)

        # Name
        name_surf = self.small_font.render(data["name"], True, data["color"])
        surface.blit(name_surf, (x + 10, y + 70))

    def _draw_icon(self, surface, cx: int, cy: int, icon_type: str, color, is_current: bool):
        """Draw simple, distinctive geometric icons for each location."""
        if icon_type == "home":
            # House: body + roof
            pygame.draw.rect(surface, color, (cx-14, cy-5, 28, 20), border_radius=2)
            pygame.draw.polygon(surface, (max(0, color[0]-30), max(0, color[1]-20), max(0, color[2]-10)),
                                [(cx-18, cy-5), (cx, cy-22), (cx+18, cy-5)])
            # Door
            pygame.draw.rect(surface, (80, 50, 30), (cx-5, cy+2, 10, 13))
        elif icon_type == "backyard" or icon_type == "park":
            # Tree
            pygame.draw.rect(surface, (101, 67, 33), (cx-4, cy-2, 8, 18))
            pygame.draw.circle(surface, color, (cx, cy-12), 14)
            pygame.draw.circle(surface, (max(0, color[0]-20), min(255, color[1]+10), max(0, color[2]-10)),
                               (cx-7, cy-8), 9)
            pygame.draw.circle(surface, (max(0, color[0]-20), min(255, color[1]+10), max(0, color[2]-10)),
                               (cx+7, cy-8), 9)
        elif icon_type == "candy_shop":
            # Lollipop
            pygame.draw.rect(surface, (180, 140, 100), (cx-2, cy-5, 4, 22))
            pygame.draw.circle(surface, color, (cx, cy-12), 11)
            # Simple swirl hint
            pygame.draw.arc(surface, (255, 255, 255), (cx-7, cy-19, 14, 14), 0.5, 2.5, 2)
        elif icon_type == "gens_garden":
            # Flower / plant
            pygame.draw.line(surface, (34, 120, 34), (cx, cy+8), (cx, cy-10), 3)
            import math
            for angle, r in [(-30, 8), (30, 8), (0, 10)]:
                rad = math.radians(270 + angle)
                px = cx + int(r * math.cos(rad))
                py = cy - 10 + int(r * math.sin(rad) * 0.6)
                pygame.draw.circle(surface, color, (px, py), 6)
            pygame.draw.circle(surface, (255, 220, 80), (cx, cy-10), 4)  # center
        elif icon_type == "arcade":
            # Simple arcade cabinet / joystick
            pygame.draw.rect(surface, color, (cx-12, cy-8, 24, 22), border_radius=3)
            pygame.draw.rect(surface, (40, 40, 40), (cx-8, cy-3, 16, 10), border_radius=2)
            # Joystick nub
            pygame.draw.circle(surface, (255, 200, 50), (cx, cy-12), 5)
            pygame.draw.circle(surface, (200, 150, 30), (cx, cy-12), 2)

    def get_clicked_location(self, pos: Tuple[int, int]) -> str:
        """Return the location key that was clicked, or empty string."""
        for key, data in self.locations.items():
            rect = pygame.Rect(*data["pos"], 130, 95)
            if rect.collidepoint(pos):
                return key
        return ""