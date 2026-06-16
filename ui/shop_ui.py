#!/usr/bin/env python3
"""
ShopUI - Reusable component for shop interfaces in OurWorld.

Currently supports:
- Sweeties Candy Shop (Lollipop, Candy Apple)
- Gens Garden (Flower Seeds, Sunflower Seeds)

Can be extended for future shops.
"""

import pygame
from typing import Dict, Tuple


class ShopUI:
    def __init__(self, small_font):
        self.small_font = small_font

        # Shop button definitions
        self.buttons: Dict[str, dict] = {
            # Sweeties Candy Shop
            "lollipop": {
                "rect": pygame.Rect(450, 280, 160, 45),
                "color": (255, 200, 210),
                "border": (200, 50, 70),
                "label": "Buy Lollipop (10)"
            },
            "candy_apple": {
                "rect": pygame.Rect(450, 335, 160, 45),
                "color": (255, 200, 210),
                "border": (200, 50, 70),
                "label": "Buy Candy Apple (25)"
            },
            # Gens Garden
            "flower_seeds": {
                "rect": pygame.Rect(450, 280, 160, 45),
                "color": (200, 230, 255),
                "border": (90, 150, 210),
                "label": "Buy Flower Seeds (12)"
            },
            "sunflower_seeds": {
                "rect": pygame.Rect(450, 335, 160, 45),
                "color": (200, 230, 255),
                "border": (90, 150, 210),
                "label": "Buy Sunflower Seeds (20)"
            },
        }

    def draw(self, surface, location: str):
        """Draw shop buttons for the current location."""
        if location == "sweeties_candy_shop":
            self._draw_button(surface, "lollipop")
            self._draw_button(surface, "candy_apple")
        elif location == "gens_garden":
            self._draw_button(surface, "flower_seeds")
            self._draw_button(surface, "sunflower_seeds")

    def _draw_button(self, surface, key: str):
        btn = self.buttons[key]
        rect = btn["rect"]

        pygame.draw.rect(surface, btn["color"], rect, border_radius=8)
        pygame.draw.rect(surface, btn["border"], rect, width=2, border_radius=8)
        text_surf = self.small_font.render(btn["label"], True, btn["border"])
        surface.blit(text_surf, (rect.x + 10, rect.y + 12))

    def get_clicked_item(self, pos: Tuple[int, int], location: str) -> str:
        """Return which item was clicked, or empty string."""
        if location == "sweeties_candy_shop":
            if self.buttons["lollipop"]["rect"].collidepoint(pos):
                return "lollipop"
            if self.buttons["candy_apple"]["rect"].collidepoint(pos):
                return "candy_apple"
        elif location == "gens_garden":
            if self.buttons["flower_seeds"]["rect"].collidepoint(pos):
                return "flower_seeds"
            if self.buttons["sunflower_seeds"]["rect"].collidepoint(pos):
                return "sunflower_seeds"
        return ""
