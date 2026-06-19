#!/usr/bin/env python3
"""
ActionAnimator - Reusable Pygame animation system for care actions.

Improved with better visuals, new effects, longer duration, and more satisfying effects.
"""

import pygame
import time
import math
from typing import Optional


class ActionAnimator:
    """
    Reusable animation controller for pet care actions.
    
    Usage:
        animator = ActionAnimator()
        animator.start("feed")
        
        in update(dt):
            animator.update(dt)
            
        in draw(surface):
            if animator.is_active:
                animator.draw(surface, pet_x, pet_y)
    """

    def __init__(self):
        self.is_active = False
        self.action_type: Optional[str] = None
        self.start_time = 0.0
        self.duration = 1.3
        self.progress = 0.0

    def start(self, action_type: str):
        """Start a new action animation."""
        self.is_active = True
        self.action_type = action_type.lower()
        self.start_time = time.time()
        self.progress = 0.0

    def update(self, dt: float):
        """Update animation state. Call every frame with delta time."""
        if not self.is_active:
            return

        elapsed = time.time() - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)

        if self.progress >= 1.0:
            self.is_active = False
            self.action_type = None

    def draw(self, surface: pygame.Surface, cx: int, cy: int):
        """Draw the current animation effect centered at (cx, cy)."""
        if not self.is_active or not self.action_type:
            return

        if self.action_type == "feed":
            self._draw_feed(surface, cx, cy)
        elif self.action_type == "play":
            self._draw_play(surface, cx, cy)
        elif self.action_type == "clean":
            self._draw_clean(surface, cx, cy)
        elif self.action_type == "rest":
            self._draw_rest(surface, cx, cy)
        elif self.action_type == "plant":
            self._draw_plant(surface, cx, cy)

    # ===================== FEED =====================
    def _draw_feed(self, surface, cx, cy):
        p = self.progress
        pygame.draw.ellipse(surface, (139, 69, 19), (cx + 45, cy + 8, 50, 26))
        pygame.draw.ellipse(surface, (210, 180, 140), (cx + 50, cy + 3, 40, 20))

        for i in range(5):
            x = cx + 55 + (i - 2) * 7
            y = cy - 5 - (p * 55) - (i * 4)
            size = 3 + (1 if i % 2 == 0 else 0)
            pygame.draw.circle(surface, (180, 140, 80), (x, y), size)

        if p > 0.6:
            heart_p = (p - 0.6) / 0.4
            hx = cx + 70
            hy = cy - 15 - (heart_p * 20)
            pygame.draw.circle(surface, (255, 100, 150), (hx - 4, hy), 5)
            pygame.draw.circle(surface, (255, 100, 150), (hx + 4, hy), 5)
            pygame.draw.polygon(surface, (255, 100, 150), [(hx - 8, hy + 2), (hx, hy + 12), (hx + 8, hy + 2)])

    # ===================== PLAY (Much improved) =====================
    def _draw_play(self, surface, cx, cy):
        p = self.progress

        # Multiple energetic bounces
        bounce = abs(math.sin(p * math.pi * 2.5)) * 32
        ball_y = cy + 15 - bounce

        # Ball with slight squash on impact
        squash = 1.0
        if bounce < 5:
            squash = 0.7 + (bounce / 5) * 0.3

        # Main ball
        pygame.draw.ellipse(surface, (255, 99, 71), (cx + 58, ball_y - 9 * squash, 18, 18 * squash))
        # Highlight
        pygame.draw.ellipse(surface, (255, 160, 120), (cx + 62, ball_y - 6 * squash, 6, 5))

        # Strong motion lines / speed lines
        for i in range(4):
            line_y = ball_y + (i - 1.5) * 6
            length = 20 + i * 5
            pygame.draw.line(surface, (255, 150, 80), 
                            (cx + 45, line_y), (cx + 45 - length, line_y - 8), 2)

        # Impact dust / particles when hitting ground
        if bounce < 8:
            for i in range(5):
                px = cx + 60 + (i - 2) * 6
                py = cy + 22 + (i % 2) * 3
                size = 2 + (1 if i % 2 == 0 else 0)
                pygame.draw.circle(surface, (200, 180, 140), (px, py), size)

    # ===================== CLEAN =====================
    def _draw_clean(self, surface, cx, cy):
        p = self.progress
        for i in range(6):
            x = cx + 50 + math.sin((p * 4) + i) * 12 + (i - 2.5) * 8
            y = cy - (p * 60) - (i * 6)
            size = 4 + (i % 3)
            pygame.draw.circle(surface, (135, 206, 250), (x, y), size, 2)
            pygame.draw.circle(surface, (200, 240, 255), (x - 2, y - 2), max(1, size - 3))

    # ===================== REST =====================
    def _draw_rest(self, surface, cx, cy):
        p = self.progress
        for i in range(4):
            offset_x = i * 10
            offset_y = (p * 35) + (i * 6)
            size = 20 - i * 3
            font = pygame.font.SysFont("Arial", size)
            z_surf = font.render("Z", True, (147, 112, 219))
            surface.blit(z_surf, (cx + 55 + offset_x, cy - 20 - offset_y))

    # ===================== PLANT =====================
    def _draw_plant(self, surface, cx, cy):
        p = self.progress
        base_x = cx + 55
        base_y = cy + 10

        stem_height = int(p * 35)
        pygame.draw.line(surface, (34, 120, 34), (base_x, base_y), (base_x, base_y - stem_height), 3)

        if p > 0.3:
            leaf_p = (p - 0.3) / 0.7
            pygame.draw.ellipse(surface, (60, 160, 60), (base_x - 18, base_y - stem_height + 5, 16, 10))
            pygame.draw.ellipse(surface, (60, 160, 60), (base_x + 2, base_y - stem_height + 8, 16, 10))

        if p > 0.7:
            flower_y = base_y - stem_height
            pygame.draw.circle(surface, (255, 100, 150), (base_x, flower_y - 5), 6)
            pygame.draw.circle(surface, (255, 200, 80), (base_x, flower_y - 5), 3)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    animator = ActionAnimator()

    running = True
    last_time = time.time()
    while running:
        dt = time.time() - last_time
        last_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f: animator.start("feed")
                if event.key == pygame.K_p: animator.start("play")
                if event.key == pygame.K_c: animator.start("clean")
                if event.key == pygame.K_r: animator.start("rest")
                if event.key == pygame.K_t: animator.start("plant")

        animator.update(dt)
        screen.fill((245, 235, 220))
        animator.draw(screen, 300, 200)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()