#!/usr/bin/env python3
"""
ActionButtons - Reusable bottom action button bar for OurWorld.

Updated to use helpers from ui/common.py
"""

import pygame
from typing import Dict

from ui.common import draw_rounded_rect


class ActionButtons:
    def __init__(self, y: int = 415, small_font=None):
        self.y = y
        self.small_font = small_font or pygame.font.SysFont("Arial", 14)

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

    def draw(self, surface, anim_state_active: bool = False,
             pulse_action: str = None, pulse_alpha: float = 0.0):
        for name, btn in self.buttons.items():
            rect = btn["rect"]
            color = btn["color"]
            label = btn["label"]

            # Pulse highlight: brief bright flash on the just-pressed button
            if pulse_action == name and pulse_alpha > 0:
                pulse_color = tuple(min(255, int(c * (1.0 + pulse_alpha * 0.6)))
                                    for c in color)
                draw_rounded_rect(surface, rect, pulse_color, radius=8)

            draw_rounded_rect(surface, rect, color, radius=8)

            if anim_state_active and name != "map":
                draw_rounded_rect(surface, rect, (90, 90, 90), radius=8, width=3)

            text_surf = self.small_font.render(label, True, (255, 255, 255))
            surface.blit(text_surf, (rect.x + 8, rect.y + 8))

    def get_rect(self, name: str) -> pygame.Rect:
        return self.buttons[name]["rect"]

    def get_all_rects(self) -> Dict[str, pygame.Rect]:
        return {name: btn["rect"] for name, btn in self.buttons.items()}
