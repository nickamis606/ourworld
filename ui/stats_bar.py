#!/usr/bin/env python3
"""
StatsBar - Reusable top stats bar UI component.

Updated to use draw_progress_bar from ui/common.py
"""

import pygame
from typing import Tuple

from ui.common import draw_progress_bar


class StatsBar:
    def __init__(self, width: int, small_font, tiny_font):
        self.width = width
        self.small_font = small_font
        self.tiny_font = tiny_font
        self.section_width = width // 5
        self.bar_height = 52

    def draw(self, surface, needs, coins: int, total_seeds: int):
        stats = [
            ("Hunger", needs.hunger, (220, 60, 60)),
            ("Happiness", needs.happiness, (46, 139, 87)),
            ("Energy", needs.energy, (255, 200, 50)),
            ("Cleanliness", needs.cleanliness, (70, 130, 180)),
        ]

        for i, (label, value, color) in enumerate(stats):
            x = i * self.section_width

            # Background section
            pygame.draw.rect(surface, (245, 245, 245), (x, 0, self.section_width, self.bar_height))
            pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, self.bar_height), 1)

            # Label
            label_surf = self.small_font.render(label, True, (20, 20, 20))
            surface.blit(label_surf, (x + 8, 4))

            # Use shared progress bar helper
            bar_rect = pygame.Rect(x + 8, 24, self.section_width - 16, 12)
            draw_progress_bar(surface, bar_rect, value, max_value=100, fill_color=color, border_radius=3)

            # Value text
            value_surf = self.tiny_font.render(f"{value:.0f}", True, (20, 20, 20))
            surface.blit(value_surf, (x + self.section_width - 30, 25))

        # Coins + Seeds section
        x = 4 * self.section_width
        pygame.draw.rect(surface, (250, 248, 240), (x, 0, self.section_width, self.bar_height))
        pygame.draw.line(surface, (180, 160, 140), (x, 0), (x, self.bar_height), 2)

        coins_text = self.small_font.render(f"Coins: {coins}", True, (180, 120, 40))
        surface.blit(coins_text, (x + 10, 8))

        seeds_text = self.small_font.render(f"Seeds: {total_seeds}", True, (60, 130, 60))
        surface.blit(seeds_text, (x + 10, 28))
