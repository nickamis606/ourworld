#!/usr/bin/env python3
"""
ActionButtons - Reusable bottom action button bar for OurWorld.

Provides the standard 5 buttons:
- Feed, Play, Clean, Rest, Map

Can be reused across scenes.
"""

import pygame
from typing import Dict


class ActionButtons:
    def __init__(self, y: int = 415, small_font=None):
        self.y = y
        self.small_font = small_font or pygame.font.SysFont("Arial", 14)

        # Button definitions: name -> (rect, color, label)
        self.buttons: Dict[str, dict] = {
            "feed": {
                "rect": pygame.Rect(25, y, 90, 36),
                "color": (255, 140, 0),
                "label": "Feed (F)"
            },
            "play": {
                "rect": pygame.Rect(125, y, 90, 36),
                "color": (46, 139, 87),
                "label": "Play (P)"
            },
            "clean": {
                "rect": pygame.Rect(225, y, 90, 36),
                "color": (70, 130, 180),
                "label": "Clean (C)"
            },
            "rest": {
                "rect": pygame.Rect(325, y, 90, 36),
                "color": (147, 112, 219),
                "label": "Rest (R)"
            },
            "map": {
                "rect": pygame.Rect(430, y, 85, 36),
                "color": (100, 149, 237),
                "label": "MAP (M)"
            },
        }

    def draw(self, surface, anim_state_active: bool = False):
        """Draw all action buttons."""
        for name, btn in self.buttons.items():
            rect = btn["rect"]
            color = btn["color"]
            label = btn["label"]

            pygame.draw.rect(surface, color, rect, border_radius=8)

            # Dim effect when an animation is playing
            if anim_state_active and name != "map":
                pygame.draw.rect(surface, (90, 90, 90), rect, width=3, border_radius=8)

            text_color = (255, 255, 255)
            text_surf = self.small_font.render(label, True, text_color)
            surface.blit(text_surf, (rect.x + 8, rect.y + 8))

    def get_rect(self, name: str) -> pygame.Rect:
        """Return the rect for a specific button (for click detection)."""
        return self.buttons[name]["rect"]

    def get_all_rects(self) -> Dict[str, pygame.Rect]:
        """Return all button rects."""
        return {name: btn["rect"] for name, btn in self.buttons.items()}
