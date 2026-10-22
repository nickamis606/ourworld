#!/usr/bin/env python3
"""Mole Pop - whack-a-mole on a 3x3 field. D-pad aims, A bops. 40 s rounds.

Moles +10, golden moles +30, bopping an empty hole costs a 0.4 s stun
(no points lost, so zero is the floor). Pops get quicker as time runs out.
"""
from __future__ import annotations

import random

import pygame

from minigames.base import MinigameBase, SCREEN_WIDTH as W, SCREEN_HEIGHT as H

ROUND = 40.0
HOLE_W, HOLE_H = 130, 46
GX = [140, 320, 500]
GY = [170, 286, 402]


class MolePop(MinigameBase):
    def __init__(self, screen, clock=None, seed=None):
        super().__init__(screen, clock)
        self.rng = random.Random(seed)
        self.time_left = ROUND
        self.cursor = 4
        self.moles = {}        # hole -> [time_left_up, golden, bonked_t]
        self.spawn_t = 0.6
        self.stun = 0.0
        self.hits = 0
        self.swing = 0.0
        self._bg = None

    def handle_action(self, a):
        if self.game_over:
            return
        c, r = self.cursor % 3, self.cursor // 3
        if a == "LEFT":
            c = max(0, c - 1)
        elif a == "RIGHT":
            c = min(2, c + 1)
        elif a == "UP":
            r = max(0, r - 1)
        elif a == "DOWN":
            r = min(2, r + 1)
        elif a == "A":
            self.bop(self.cursor)
        self.cursor = r * 3 + c

    def bop(self, hole):
        if self.stun > 0:
            return False
        self.swing = 0.15
        m = self.moles.get(hole)
        if m and m[2] <= 0:
            self.score += 30 if m[1] else 10
            self.hits += 1
            m[2] = 0.3          # show the bonked face briefly
            return True
        self.stun = 0.4
        return False

    def update(self, dt):
        if self.game_over:
            return
        self.time_left -= dt
        self.stun = max(0.0, self.stun - dt)
        self.swing = max(0.0, self.swing - dt)
        pace = 0.55 + 0.45 * (self.time_left / ROUND)   # 1.0 -> 0.55
        for hole in list(self.moles):
            m = self.moles[hole]
            if m[2] > 0:
                m[2] -= dt
                if m[2] <= 0:
                    del self.moles[hole]
                continue
            m[0] -= dt
            if m[0] <= 0:
                del self.moles[hole]
        self.spawn_t -= dt
        if self.spawn_t <= 0:
            free = [h for h in range(9) if h not in self.moles]
            if free:
                h = self.rng.choice(free)
                self.moles[h] = [self.rng.uniform(0.7, 1.2) * pace, self.rng.random() < 0.12, 0.0]
            self.spawn_t = self.rng.uniform(0.35, 0.7) * pace
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True

    def _background(self):
        if self._bg is None:
            bg = pygame.Surface((W, H))
            bg.fill((120, 190, 100))
            for i in range(160):
                x, y = (i * 97) % W, 50 + (i * 53) % (H - 50)
                pygame.draw.line(bg, (90, 160, 80), (x, y), (x + 2, y - 6), 2)
            for h in range(9):
                cx, cy = GX[h % 3], GY[h // 3]
                pygame.draw.ellipse(bg, (100, 70, 40), (cx - HOLE_W // 2 - 6, cy - HOLE_H // 2 - 4, HOLE_W + 12, HOLE_H + 10))
                pygame.draw.ellipse(bg, (40, 26, 16), (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
            self._bg = bg
        return self._bg

    def draw(self, screen=None):
        t = screen or self.screen
        t.blit(self._background(), (0, 0))
        for hole, (up, golden, bonk) in self.moles.items():
            cx, cy = GX[hole % 3], GY[hole // 3]
            body = (250, 210, 60) if golden else (150, 105, 75)
            top = cy - 62
            clip = t.get_clip()
            t.set_clip(pygame.Rect(cx - 70, top - 10, 140, cy - top + 10))
            pygame.draw.ellipse(t, body, (cx - 34, top, 68, 80))
            pygame.draw.ellipse(t, (240, 200, 180), (cx - 18, top + 30, 36, 24))
            if bonk > 0:
                pygame.draw.line(t, (30, 20, 20), (cx - 18, top + 18), (cx - 8, top + 26), 3)
                pygame.draw.line(t, (30, 20, 20), (cx - 18, top + 26), (cx - 8, top + 18), 3)
                pygame.draw.line(t, (30, 20, 20), (cx + 8, top + 18), (cx + 18, top + 26), 3)
                pygame.draw.line(t, (30, 20, 20), (cx + 8, top + 26), (cx + 18, top + 18), 3)
            else:
                pygame.draw.circle(t, (20, 20, 20), (cx - 12, top + 22), 5)
                pygame.draw.circle(t, (20, 20, 20), (cx + 12, top + 22), 5)
            pygame.draw.circle(t, (230, 110, 120), (cx, top + 36), 5)
            t.set_clip(clip)
            # front lip of the hole hides the mole's bottom
            pygame.draw.ellipse(t, (100, 70, 40), (cx - HOLE_W // 2 - 6, cy + 4, HOLE_W + 12, 16))
        # mallet cursor
        cx, cy = GX[self.cursor % 3], GY[self.cursor // 3]
        lift = 0 if self.swing > 0 else 26
        col = (200, 200, 210) if self.stun > 0 else (255, 190, 40)
        pygame.draw.ellipse(t, col, (cx - HOLE_W // 2 - 8, cy - HOLE_H // 2 - 6, HOLE_W + 16, HOLE_H + 12), 4)
        pygame.draw.rect(t, (150, 100, 60), (cx + 30, cy - 90 - lift, 10, 60), border_radius=3)
        pygame.draw.rect(t, (220, 70, 70), (cx + 8, cy - 104 - lift, 54, 28), border_radius=8)
        self.hud(t, f"SCORE {self.score}", f"MOLE POP  {int(self.time_left)}s", color=(255, 255, 255))


if __name__ == "__main__":
    pygame.init()
    print(MolePop(pygame.display.set_mode((W, H))).run())
