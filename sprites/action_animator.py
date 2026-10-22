#!/usr/bin/env python3
"""
ActionAnimator - Reusable Pygame animation system for care actions.

Robust dt-based timing (no wall-clock time.time() dependency) so animations
run smoothly at any FPS and don't "freeze" or jump.
"""

import pygame
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

    # Duration (seconds) and post-easing linger for each action type
    _DURATIONS = {
        "feed": 1.3,   # bowl appears, food rises, heart pops — moderate pace
        "play": 1.1,   # quick, energetic bounces
        "clean": 1.4,  # bubbles rise slowly, linger
        "rest": 1.6,   # slow, dreamy Z drift
        "plant": 1.5,
    }
    # Extra frames to linger at peak before fade-out
    _LINGER = {
        "feed": 0.18,
        "play": 0.12,
        "clean": 0.18,
        "rest": 0.20,
        "plant": 0.15,
    }

    # Button pulse: lasts 300 ms, fades from full→transparent
    _PULSE_DURATION = 0.3

    def __init__(self):
        self.is_active = False
        self.action_type: Optional[str] = None
        self.elapsed = 0.0
        self.duration = 1.3
        self.linger = 0.0
        self.progress = 0.0
        self.pulse_action: Optional[str] = None
        self.pulse_elapsed = 0.0
        # Font cache for Rest Z characters (avoids creating fonts every frame)
        self._z_fonts: dict = {}

    def start(self, action_type: str):
        """Start a new action animation."""
        self.is_active = True
        self.action_type = action_type.lower()
        self.elapsed = 0.0
        self.duration = self._DURATIONS.get(self.action_type, 1.3)
        self.linger = self._LINGER.get(self.action_type, 0.0)
        self.progress = 0.0
        # Trigger button pulse for this action
        self.pulse_action = self.action_type
        self.pulse_elapsed = 0.0

    def update(self, dt: float):
        """Update animation state using delta time (robust for game loops)."""
        if self.pulse_action is not None:
            self.pulse_elapsed += dt
            if self.pulse_elapsed >= self._PULSE_DURATION:
                self.pulse_action = None
                self.pulse_elapsed = 0.0

        if not self.is_active:
            return

        self.elapsed += dt

        # During linger phase: hold at peak, just let time pass
        # During active phase: apply eased progress
        self.progress = self._ease(self.elapsed / self.duration)
        if self.elapsed >= self.duration + self.linger:
            # Fade-out phase
            fade_start = self.duration + self.linger
            fade_end = fade_start + 0.2
            fade = 1.0 - max(0.0, min(1.0, (self.elapsed - fade_start) / (fade_end - fade_start)))
            if fade <= 0:
                self.is_active = False
                self.action_type = None
                self.elapsed = 0.0
                return
            self._fade_alpha = fade
            self.progress = 1.0

    @staticmethod
    def _ease(p: float) -> float:
        """Smooth easing: fast start, gentle landing."""
        # Cubic ease-out: starts fast, slows at end
        return 1.0 - (1.0 - p) ** 3

    def get_pulse(self) -> tuple:
        """Return (action_name, pulse_alpha) for button highlight.

        pulse_alpha: 0.0→1.0→0.0 over _PULSE_DURATION (triangular envelope).
        """
        if self.pulse_action is None:
            return (None, 0.0)
        mid = self._PULSE_DURATION / 2
        t = self.pulse_elapsed
        alpha = 1.0 - abs(t - mid) / mid  # triangle: 0→1→0
        return (self.pulse_action, alpha)

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
        # Bowl appears with a slight pop-in
        bowl_scale = 0.85 + 0.15 * min(1.0, p * 4.0)  # 0.85→1.0 in first 25% of anim
        bowl_w = int(50 * bowl_scale)
        bowl_h = int(26 * bowl_scale)
        bowl_x = cx + 55 - bowl_w // 2 + 20
        bowl_y = cy + 8 - int(2 * bowl_scale)
        pygame.draw.ellipse(surface, (139, 69, 19), (bowl_x, bowl_y, bowl_w, bowl_h))
        pygame.draw.ellipse(surface, (210, 180, 140),
                            (bowl_x + 5, bowl_y - 3, bowl_w - 10, bowl_h - 6))
        pygame.draw.ellipse(surface, (160, 100, 50),
                            (bowl_x, bowl_y, bowl_w, 3), width=2)

        # Food particles rise and spread
        for i in range(5):
            # Each particle has its own rise timing
            particle_p = min(1.0, max(0.0, (p * 1.2 - i * 0.1) / 0.8))
            rise = particle_p * 55
            spread = (i - 2) * (3 + particle_p * 5)
            x = cx + 55 + spread
            y = cy - rise - (i * 3)
            # Particles shrink as they rise
            size = int((3 + (1 if i % 2 == 0 else 0)) * (1.0 - particle_p * 0.3))
            alpha = int(255 * (1.0 - particle_p * 0.6))
            col = tuple(int(c * (0.7 + particle_p * 0.3)) for c in (180, 140, 80))
            pygame.draw.circle(surface, col, (x, y), max(1, size))

        # Heart pops up after bowl is fully formed (p > 0.25), bounces, then lingers
        if p > 0.2:
            heart_p = min(1.0, (p - 0.2) / 0.5)  # appears in first 50% after p=0.2
            # Heartbeat: slight scale pulse once heart is fully formed
            heartbeat = 1.0
            if p > 0.65:
                beat = math.sin((p - 0.65) * math.pi * 8)  # rapid beats
                heartbeat = 1.0 + beat * 0.08 * (1.0 - (p - 0.65) / 0.35)

            hx = cx + 70
            # Heart rises from bowl to above pet head
            hy = cy - 5 - heart_p * 35
            # Heart scales with heartbeat
            h_size = int(5 * heartbeat)
            # Draw heart with slight glow (offset circles for glow effect)
            glow_color = (255, 150, 180)
            pygame.draw.circle(surface, glow_color, (hx - 4, hy), h_size + 1)
            pygame.draw.circle(surface, glow_color, (hx + 4, hy), h_size + 1)
            pygame.draw.circle(surface, glow_color, (hx, hy + 3), h_size + 1)
            pygame.draw.circle(surface, (255, 100, 150), (hx - 4, hy), h_size)
            pygame.draw.circle(surface, (255, 100, 150), (hx + 4, hy), h_size)
            pygame.draw.circle(surface, (255, 100, 150), (hx, hy + 3), h_size)
            pygame.draw.polygon(surface, (255, 100, 150),
                                [(hx - 8 * heartbeat, hy + 2),
                                 (hx, hy + 12 * heartbeat),
                                 (hx + 8 * heartbeat, hy + 2)])

    # ===================== PLAY =====================
    def _draw_play(self, surface, cx, cy):
        p = self.progress

        # Multiple energetic bounces — speed up as animation progresses
        bounce_speed = 2.5 + p * 0.5  # accelerates slightly
        bounce = abs(math.sin(p * math.pi * bounce_speed)) * 32
        ball_y = cy + 15 - bounce

        # Squash/stretch: stretch when moving fast, squash on impact
        speed = abs(math.cos(p * math.pi * bounce_speed))  # velocity proxy
        squash_x = 1.0 + speed * 0.15
        squash_y = 1.0 - speed * 0.1
        ball_w = int(18 * squash_x)
        ball_h = int(18 * squash_y)

        # Main ball
        ball_x = cx + 58 - ball_w // 2 + 9
        pygame.draw.ellipse(surface, (255, 99, 71), (ball_x, ball_y - ball_h // 2, ball_w, ball_h))
        # Highlight (stays elliptical even during squash)
        pygame.draw.ellipse(surface, (255, 160, 120),
                            (ball_x + 4, ball_y - ball_h // 2 + 2, 6, max(3, ball_h // 3)))
        # Inner highlight
        pygame.draw.ellipse(surface, (255, 220, 180),
                            (ball_x + 6, ball_y - ball_h // 2 + 4, 3, max(1, ball_h // 5)))

        # Motion lines that shrink as ball rises (visible when ball is low)
        ball_height_ratio = 1.0 - bounce / 32  # 0=high, 1=low
        if ball_height_ratio > 0.2:
            for i in range(4):
                line_y = ball_y + (i - 1.5) * 6
                line_length = int((20 + i * 5) * ball_height_ratio)
                alpha_color = (int(255 * ball_height_ratio),
                               int(150 * ball_height_ratio),
                               int(80 * ball_height_ratio))
                pygame.draw.line(surface, alpha_color,
                                 (cx + 45, line_y),
                                 (cx + 45 - line_length, line_y - 8), 2)

        # Impact ring on ground when ball hits
        if bounce < 6:
            ring_progress = 1.0 - bounce / 6
            ring_radius = int(8 + ring_progress * 14)
            ring_alpha = int(180 * (1.0 - ring_progress))
            ring_col = (int(200 * (1.0 - ring_progress * 0.5)),
                        int(180 * (1.0 - ring_progress * 0.5)),
                        int(140 * (1.0 - ring_progress * 0.5)))
            pygame.draw.circle(surface, ring_col,
                               (cx + 67, cy + 22), ring_radius, max(1, int(3 * (1.0 - ring_progress))))

    # ===================== CLEAN =====================
    def _draw_clean(self, surface, cx, cy):
        p = self.progress
        for i in range(8):  # more bubbles for a richer feel
            # Each bubble has its own phase offset
            phase = i * math.pi * 0.5
            bubble_p = min(1.0, max(0.0, (p * 1.3 - i * 0.08) / 0.7))

            # Sine-wave drift with increasing amplitude
            drift = math.sin((p * 3) + phase + i * 0.3) * (10 + bubble_p * 8)
            x = cx + 50 + drift + (i - 3.5) * 9

            # Rise with slight parallax
            y = cy - (bubble_p * 65) - (i * 5)

            # Bubbles grow then pop at peak
            if bubble_p < 0.5:
                grow = bubble_p * 2  # 0→1
            else:
                grow = 2.0 - bubble_p  # 1→0 (pop)

            size = int((3 + (i % 3)) * grow)
            if size <= 0:
                continue

            # Bubble: semi-transparent fill + bright rim
            brightness = int(120 + bubble_p * 80)
            col = (min(255, brightness), min(255, brightness + 40), min(255, brightness + 80))
            pygame.draw.circle(surface, col, (x, y), size)
            # Bright rim
            rim_col = (min(255, brightness + 60), min(255, brightness + 100), min(255, brightness + 120))
            pygame.draw.circle(surface, rim_col, (x - 1, y - 1), max(1, size - 2))

            # Sparkle on top-left of each bubble
            if size >= 3 and bubble_p > 0.2 and bubble_p < 0.8:
                sparkle = math.sin(p * math.pi * 6 + i) * 0.5 + 0.5
                sparkle_size = int(2 * sparkle)
                sparkle_col = (255, 255, 255)
                if sparkle_size > 0:
                    pygame.draw.circle(surface, sparkle_col, (x - size // 3, y - size // 3), sparkle_size)

    # ===================== REST =====================
    def _draw_rest(self, surface, cx, cy):
        p = self.progress
        for i in range(4):
            # Each Z drifts at its own speed
            z_phase = i * 0.25
            z_p = min(1.0, max(0.0, (p * 1.1 - z_phase) / (1.0 - z_phase)))

            # Gentle sine wobble
            wobble = math.sin(p * math.pi * 1.5 + i * 0.8) * 3
            offset_x = wobble + i * 12
            offset_y = z_p * 45 + i * 7

            # Z characters start small, grow to full size, then fade out
            if z_p < 0.3:
                z_scale = z_p / 0.3  # 0→1
            elif z_p < 0.7:
                z_scale = 1.0
            else:
                z_scale = 1.0 - (z_p - 0.7) / 0.3  # 1→0

            font_size = int(22 * z_scale)
            if font_size < 4:
                continue

            # Cache font surfaces to avoid re-creating every frame
            if font_size not in self._z_fonts:
                self._z_fonts[font_size] = pygame.font.SysFont("Arial", font_size)
            font = self._z_fonts[font_size]

            # Z color: deeper purple at peak, fades to lighter
            purple_r = int(147 * (0.5 + z_scale * 0.5))
            purple_g = int(112 * (0.5 + z_scale * 0.5))
            purple_b = int(219 * (0.5 + z_scale * 0.5))
            z_surf = font.render("Z", True, (purple_r, purple_g, purple_b))
            surface.blit(z_surf, (cx + 55 + offset_x, cy - 25 - offset_y))

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
    while running:
        dt = clock.tick(60) / 1000.0

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

    pygame.quit()
