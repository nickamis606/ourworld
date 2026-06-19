#!/usr/bin/env python3
"""
ActionAnimator - Reusable Pygame animation system for care actions.

This replaces the old Tkinter version and the hardcoded _draw_anim_effect.
"""

import pygame
import time
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
        self.duration = 0.9  # seconds
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

    # --- Individual animation drawers ---

    def _draw_feed(self, surface, cx, cy):
        # Simple food bowl + crumbs effect
        progress = self.progress
        # Bowl
        pygame.draw.ellipse(surface, (139, 69, 19), (cx + 50, cy + 10, 45, 22))
        # Food inside
        alpha = max(0, 255 - int(progress * 200))
        food_color = (210, 180, 140)
        pygame.draw.ellipse(surface, food_color, (cx + 55, cy + 5, 35, 18))
        # Rising crumbs/particles
        for i in range(3):
            offset = (progress * 40) + (i * 8)
            pygame.draw.circle(surface, (180, 140, 90), 
                               (cx + 65 + i*8, cy - 5 - offset), 3)

    def _draw_play(self, surface, cx, cy):
        progress = self.progress
        # Bouncing ball
        bounce = abs((progress * 2 - 1)) * 25
        ball_y = cy + 15 - bounce
        pygame.draw.circle(surface, (255, 99, 71), (cx + 70, ball_y), 10)
        # Simple motion lines
        if progress < 0.7:
            pygame.draw.line(surface, (200, 80, 60), (cx + 55, ball_y), (cx + 40, ball_y - 15), 2)

    def _draw_clean(self, surface, cx, cy):
        progress = self.progress
        # Rising bubbles
        for i in range(4):
            x_offset = (i - 1.5) * 12
            y_offset = (progress * 50) + (i * 7)
            size = 5 + (i % 2) * 2
            pygame.draw.circle(surface, (135, 206, 250), 
                               (cx + 55 + x_offset, cy - y_offset), size, 2)

    def _draw_rest(self, surface, cx, cy):
        progress = self.progress
        # Floating Z's
        for i, offset in enumerate([0, 12, 24]):
            size = 18 - i * 3
            font = pygame.font.SysFont("Arial", size)
            z_surf = font.render("Z", True, (147, 112, 219))
            surface.blit(z_surf, (cx + 50 + offset, cy - 25 - (progress * 30) - i*8))

    def _draw_plant(self, surface, cx, cy):
        progress = self.progress
        # Small plant growth particles
        for i in range(3):
            x = cx + 55 + (i - 1) * 15
            y = cy + 5 - (progress * 25)
            size = 4 + int(progress * 3)
            pygame.draw.circle(surface, (60, 160, 60), (x, y), size)
            if progress > 0.4:
                pygame.draw.circle(surface, (80, 180, 80), (x, y - 8), 3)


if __name__ == "__main__":
    # Simple test
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
                if event.key == pygame.K_f:
                    animator.start("feed")
                elif event.key == pygame.K_p:
                    animator.start("play")
                elif event.key == pygame.K_c:
                    animator.start("clean")
                elif event.key == pygame.K_r:
                    animator.start("rest")

        animator.update(dt)

        screen.fill((245, 235, 220))
        animator.draw(screen, 300, 200)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()