#!/usr/bin/env python3
"""
ArcadePanel - Reusable component for the arcade games selection UI.

Handles drawing the "ARCADE GAMES" panel with Snake and Pet Dash buttons.
"""

import pygame
from typing import Optional, Tuple

from ui.common import draw_rounded_rect


class ArcadePanel:
    def __init__(self, small_font, tiny_font):
        self.small_font = small_font
        self.tiny_font = tiny_font

        self.panel_rect = pygame.Rect(450, 260, 170, 85)
        self.snake_btn = pygame.Rect(460, 295, 70, 40)
        self.dash_btn = pygame.Rect(540, 295, 70, 40)

    def draw(self, surface):
        """Draw the arcade games panel."""
        draw_rounded_rect(surface, self.panel_rect, (40, 45, 70), radius=10)
        draw_rounded_rect(surface, self.panel_rect, (100, 149, 237), radius=10, width=2)

        title = self.small_font.render("ARCADE GAMES", True, (255, 220, 100))
        surface.blit(title, (self.panel_rect.x + 10, self.panel_rect.y + 8))

        # Snake button
        draw_rounded_rect(surface, self.snake_btn, (80, 200, 120), radius=6)
        self.tiny_font.render("Snake", True, (255, 255, 255))
        surface.blit(self.tiny_font.render("Snake", True, (255, 255, 255)), (self.snake_btn.x + 15, self.snake_btn.y + 10))

        # Pet Dash button
        draw_rounded_rect(surface, self.dash_btn, (255, 160, 80), radius=6)
        surface.blit(self.tiny_font.render("Pet Dash", True, (255, 255, 255)), (self.dash_btn.x + 8, self.dash_btn.y + 10))

    def get_clicked_game(self, pos: Tuple[int, int]) -> Optional[str]:
        """Return 'snake', 'pet_dash', or None."""
        if self.snake_btn.collidepoint(pos):
            return "snake"
        if self.dash_btn.collidepoint(pos):
            return "pet_dash"
        return None
