#!/usr/bin/env python3
"""
StatsBar - Reusable top stats bar UI component.

Displays Hunger, Happiness, Energy, Cleanliness + Coins/Seeds.
Can be used by any scene.
"""

import pygame


class StatsBar:
    def __init__(self, width: int, small_font, tiny_font):
        self.width = width
        self.small_font = small_font
        self.tiny_font = tiny_font
        self.section_width = width // 5
        self.bar_height = 52

    def draw(self, surface, needs, coins: int, total_seeds: int):
        """Draw the full stats bar."""
        stats = [
            ("Hunger", needs.hunger, (220, 60, 60)),
            ("Happiness", needs.happiness, (46, 139, 87)),
            ("Energy", needs.energy, (255, 200, 50)),
            ("Cleanliness", needs.cleanliness, (70, 130, 180)),
        ]

        for i, (label, value, color) in enumerate(stats):
            x = i * self.section_width
            pygame.draw.rect(surface, (245, 245, 245), (x, 0, self.section_width, self.bar_height))
            pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, self.bar_height), 1)

            label_surf = self.small_font.render(label, True, (20, 20, 20))
            surface.blit(label_surf, (x + 8, 4))

            bar_y = 24
            bar_width = self.section_width - 16
            pygame.draw.rect(surface, (180, 180, 180), (x + 8, bar_y, bar_width, 12), border_radius=3)
            fill_width = int(bar_width * max(0, min(1, value / 100)))
            pygame.draw.rect(surface, color, (x + 8, bar_y, fill_width, 12), border_radius=3)

            value_surf = self.tiny_font.render(f"{value:.0f}", True, (20, 20, 20))
            surface.blit(value_surf, (x + self.section_width - 30, bar_y + 1))

        # Coins + Seeds section (5th column)
        x = 4 * self.section_width
        pygame.draw.rect(surface, (250, 248, 240), (x, 0, self.section_width, self.bar_height))
        pygame.draw.line(surface, (180, 160, 140), (x, 0), (x, self.bar_height), 2)

        coins_text = self.small_font.render(f"Coins: {coins}", True, (180, 120, 40))
        surface.blit(coins_text, (x + 10, 8))

        seeds_text = self.small_font.render(f"Seeds: {total_seeds}", True, (60, 130, 60))
        surface.blit(seeds_text, (x + 10, 28))
