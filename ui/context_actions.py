#!/usr/bin/env python3
"""
ContextActions - Reusable component for location-specific action buttons.

Handles:
- Backyard: Plant Flower Seeds, Plant Sunflower Seeds, Harvest
- Home: Decorate Home

This keeps MainScene cleaner by moving context-sensitive UI out.
"""

import pygame
from typing import Optional, Tuple

from ui.common import draw_rounded_rect


class ContextActions:
    def __init__(self, small_font):
        self.small_font = small_font

        # Backyard buttons
        self.plant_flower_btn = pygame.Rect(30, 70, 180, 40)
        self.plant_sunflower_btn = pygame.Rect(30, 120, 180, 40)
        self.harvest_btn = pygame.Rect(450, 70, 160, 40)

        # Home button
        self.decorate_btn = pygame.Rect(30, 70, 200, 40)

    def draw(self, surface, location: str, inventory: dict, has_mature_plants: bool = False):
        """Draw context buttons based on current location and state."""
        if location == "backyard":
            self._draw_backyard_buttons(surface, inventory, has_mature_plants)
        elif location == "home":
            self._draw_home_buttons(surface, inventory)

    def _draw_backyard_buttons(self, surface, inventory: dict, has_mature_plants: bool):
        # Plant Flower Seeds
        if inventory.get("flower_seeds", 0) > 0:
            draw_rounded_rect(surface, self.plant_flower_btn, (180, 230, 180), radius=8)
            draw_rounded_rect(surface, self.plant_flower_btn, (40, 140, 60), radius=8, width=2)
            text = self.small_font.render("Plant Flower Seeds", True, (30, 100, 50))
            surface.blit(text, (self.plant_flower_btn.x + 10, self.plant_flower_btn.y + 10))

        # Plant Sunflower Seeds
        if inventory.get("sunflower_seeds", 0) > 0:
            draw_rounded_rect(surface, self.plant_sunflower_btn, (180, 230, 180), radius=8)
            draw_rounded_rect(surface, self.plant_sunflower_btn, (40, 140, 60), radius=8, width=2)
            text = self.small_font.render("Plant Sunflower Seeds", True, (30, 100, 50))
            surface.blit(text, (self.plant_sunflower_btn.x + 10, self.plant_sunflower_btn.y + 10))

        # Harvest button (only if mature plants exist)
        if has_mature_plants:
            draw_rounded_rect(surface, self.harvest_btn, (255, 200, 150), radius=8)
            draw_rounded_rect(surface, self.harvest_btn, (200, 120, 50), radius=8, width=2)
            text = self.small_font.render("Harvest Flower", True, (150, 80, 30))
            surface.blit(text, (self.harvest_btn.x + 15, self.harvest_btn.y + 10))

    def _draw_home_buttons(self, surface, inventory: dict):
        if inventory.get("flowers", 0) >= 5:
            draw_rounded_rect(surface, self.decorate_btn, (255, 220, 240), radius=8)
            draw_rounded_rect(surface, self.decorate_btn, (200, 80, 150), radius=8, width=2)
            text = self.small_font.render("Decorate Home (5)", True, (180, 60, 130))
            surface.blit(text, (self.decorate_btn.x + 10, self.decorate_btn.y + 10))

    def get_clicked_action(self, pos: Tuple[int, int], location: str) -> Optional[str]:
        """Return the action that was clicked, or None."""
        if location == "backyard":
            if self.plant_flower_btn.collidepoint(pos):
                return "plant_flower"
            if self.plant_sunflower_btn.collidepoint(pos):
                return "plant_sunflower"
            if self.harvest_btn.collidepoint(pos):
                return "harvest"
        elif location == "home":
            if self.decorate_btn.collidepoint(pos):
                return "decorate"
        return None
