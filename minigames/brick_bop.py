#!/usr/bin/env python3
"""Brick Bop - a tiny Breakout. Hold Left/Right to move, A to launch.

Cheap on weak ARM: bricks are pre-rendered into one surface that is rebuilt
only when a brick breaks; per frame it's one blit + a paddle + a ball.
"""
from __future__ import annotations

import math
import random

import pygame

from minigames.base import MinigameBase, SCREEN_WIDTH as W, SCREEN_HEIGHT as H

COLS, ROWS = 10, 5
BRICK_W, BRICK_H, GAP = 58, 20, 4
TOP = 64
PADDLE_Y = 436
PADDLE_SPEED = 430.0
BALL_R = 7
ROW_COLORS = [(240, 90, 120), (245, 150, 70), (240, 210, 70), (110, 200, 110), (90, 170, 240)]
ROW_POINTS = [50, 40, 30, 20, 10]


class BrickBop(MinigameBase):
    def __init__(self, screen, clock=None):
        super().__init__(screen, clock)
        self.lives = 3
        self.wave = 1
        self.paddle_w = 96
        self.paddle_x = W / 2
        self._bg = None
        self._new_wave()

    def _new_wave(self):
        self.bricks = {(c, r) for c in range(COLS) for r in range(ROWS)}
        self._bricks_surf = None
        self._reset_ball()

    def _reset_ball(self):
        self.stuck = True
        self.bx, self.by = self.paddle_x, PADDLE_Y - BALL_R - 1
        self.speed = 270.0 + 30 * (self.wave - 1)
        self.vx, self.vy = 0.0, 0.0

    def _launch(self):
        ang = random.uniform(-0.6, 0.6)
        self.vx, self.vy = math.sin(ang) * self.speed, -math.cos(ang) * self.speed
        self.stuck = False

    def brick_rect(self, c, r):
        x0 = (W - (COLS * BRICK_W + (COLS - 1) * GAP)) // 2
        return pygame.Rect(x0 + c * (BRICK_W + GAP), TOP + r * (BRICK_H + GAP), BRICK_W, BRICK_H)

    def handle_action(self, a):
        if self.game_over:
            return
        if a in ("A", "UP") and self.stuck:
            self._launch()

    def update(self, dt):
        if self.game_over:
            return
        dt = min(dt, 0.05)
        d = ("RIGHT" in self.held) - ("LEFT" in self.held)
        half = self.paddle_w / 2
        self.paddle_x = max(half, min(W - half, self.paddle_x + d * PADDLE_SPEED * dt))
        if self.stuck:
            self.bx = self.paddle_x
            return
        # two substeps keep the ball from tunnelling through bricks at 30 FPS
        for _ in range(2):
            self._step(dt / 2)
            if self.stuck or self.game_over:
                break

    def _step(self, dt):
        self.bx += self.vx * dt
        self.by += self.vy * dt
        if self.bx < BALL_R:
            self.bx, self.vx = BALL_R, abs(self.vx)
        elif self.bx > W - BALL_R:
            self.bx, self.vx = W - BALL_R, -abs(self.vx)
        if self.by < 44 + BALL_R:
            self.by, self.vy = 44 + BALL_R, abs(self.vy)
        ball = pygame.Rect(int(self.bx - BALL_R), int(self.by - BALL_R), BALL_R * 2, BALL_R * 2)
        # paddle
        paddle = pygame.Rect(int(self.paddle_x - self.paddle_w / 2), PADDLE_Y, int(self.paddle_w), 12)
        if self.vy > 0 and ball.colliderect(paddle):
            off = (self.bx - self.paddle_x) / (self.paddle_w / 2)
            ang = max(-1.0, min(1.0, off)) * 1.05
            if abs(ang) < 0.18:   # never a dead-straight bounce (avoids endless vertical loops)
                ang = 0.18 if (ang > 0 or (ang == 0 and self.vx >= 0)) else -0.18
            self.vx, self.vy = math.sin(ang) * self.speed, -abs(math.cos(ang) * self.speed)
            self.by = PADDLE_Y - BALL_R - 1
        # bricks
        if self.by < TOP + ROWS * (BRICK_H + GAP) + BALL_R:
            for (c, r) in list(self.bricks):
                br = self.brick_rect(c, r)
                if ball.colliderect(br):
                    self.bricks.discard((c, r))
                    self._bricks_surf = None
                    self.score += ROW_POINTS[r]
                    ox = min(ball.right - br.left, br.right - ball.left)
                    oy = min(ball.bottom - br.top, br.bottom - ball.top)
                    if ox < oy:
                        self.vx = -self.vx
                    else:
                        self.vy = -self.vy
                    self.speed = min(520.0, self.speed + 4)
                    break
        if not self.bricks:
            self.wave += 1
            self.score += 100
            self._new_wave()
            return
        if self.by > H + BALL_R:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

    def _bricks(self):
        if self._bricks_surf is None:
            s = pygame.Surface((W, TOP + ROWS * (BRICK_H + GAP)), pygame.SRCALPHA)
            for (c, r) in self.bricks:
                rect = self.brick_rect(c, r)
                pygame.draw.rect(s, ROW_COLORS[r], rect, border_radius=5)
                pygame.draw.line(s, (255, 255, 255), (rect.x + 4, rect.y + 3), (rect.right - 5, rect.y + 3), 2)
            self._bricks_surf = s
        return self._bricks_surf

    def draw(self, screen=None):
        t = screen or self.screen
        if self._bg is None:
            bg = pygame.Surface((W, H))
            for y in range(0, H, 4):
                k = y / H
                pygame.draw.rect(bg, (int(30 + 20 * k), int(24 + 10 * k), int(60 + 30 * k)), (0, y, W, 4))
            self._bg = bg
        t.blit(self._bg, (0, 0))
        t.blit(self._bricks(), (0, 0))
        px = int(self.paddle_x - self.paddle_w / 2)
        pygame.draw.rect(t, (250, 240, 220), (px, PADDLE_Y, int(self.paddle_w), 12), border_radius=6)
        pygame.draw.rect(t, (240, 120, 160), (px + 6, PADDLE_Y + 3, int(self.paddle_w) - 12, 6), border_radius=3)
        pygame.draw.circle(t, (255, 255, 255), (int(self.bx), int(self.by)), BALL_R)
        pygame.draw.circle(t, (255, 210, 90), (int(self.bx) - 2, int(self.by) - 2), 3)
        self.hud(t, f"SCORE {self.score}", f"BRICK BOP  WAVE {self.wave}  LIVES {self.lives}")
        if self.stuck and not self.game_over:
            m = self.small_font.render("Hold Left/Right to move - A to launch", True, (240, 240, 255))
            t.blit(m, m.get_rect(center=(W // 2, 300)))


if __name__ == "__main__":
    pygame.init()
    g = BrickBop(pygame.display.set_mode((W, H)))
    print(g.run())
