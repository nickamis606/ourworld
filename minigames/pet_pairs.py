#!/usr/bin/env python3
"""Pet Pairs - memory match on a 4x4 board. D-pad moves, A flips.

Score: 25 per pair, +2 per second left when the board is cleared.
"""
from __future__ import annotations

import random

import pygame

from minigames.base import MinigameBase, SCREEN_WIDTH as W, SCREEN_HEIGHT as H
from ui.icons import icon

COLS = ROWS = 4
CARD_W, CARD_H, GAP = 104, 86, 10
X0 = (W - (COLS * CARD_W + (COLS - 1) * GAP)) // 2
Y0 = 58
TIME_LIMIT = 75.0
FACES = ["feed", "happiness", "energy", "cleanliness", "coin", "flowers", "frogger", "lollipop"]
MISMATCH_SHOW = 0.75


class PetPairs(MinigameBase):
    def __init__(self, screen, clock=None, seed=None):
        super().__init__(screen, clock)
        rng = random.Random(seed)
        deck = FACES * 2
        rng.shuffle(deck)
        self.cards = deck                    # index -> face
        self.matched = [False] * len(deck)
        self.open: list = []                 # indices currently face-up (unmatched)
        self.cursor = 0
        self.time_left = TIME_LIMIT
        self.hide_t = 0.0
        self.pairs = 0
        self.flash = {}                      # index -> seconds of match glow

    def rect(self, i):
        c, r = i % COLS, i // COLS
        return pygame.Rect(X0 + c * (CARD_W + GAP), Y0 + r * (CARD_H + GAP), CARD_W, CARD_H)

    def handle_action(self, a):
        if self.game_over:
            return
        c, r = self.cursor % COLS, self.cursor // COLS
        if a == "LEFT":
            c = (c - 1) % COLS
        elif a == "RIGHT":
            c = (c + 1) % COLS
        elif a == "UP":
            r = (r - 1) % ROWS
        elif a == "DOWN":
            r = (r + 1) % ROWS
        elif a == "A":
            self.flip(self.cursor)
        self.cursor = r * COLS + c

    def flip(self, i):
        if self.hide_t > 0 or self.matched[i] or i in self.open:
            return False
        self.open.append(i)
        if len(self.open) == 2:
            a, b = self.open
            if self.cards[a] == self.cards[b]:
                self.matched[a] = self.matched[b] = True
                self.flash[a] = self.flash[b] = 0.5
                self.pairs += 1
                self.score += 25
                self.open = []
                if all(self.matched):
                    self.score += int(self.time_left) * 2
                    self.game_over = True
            else:
                self.hide_t = MISMATCH_SHOW
        return True

    def update(self, dt):
        if self.game_over:
            return
        self.time_left -= dt
        for k in list(self.flash):
            self.flash[k] -= dt
            if self.flash[k] <= 0:
                del self.flash[k]
        if self.hide_t > 0:
            self.hide_t -= dt
            if self.hide_t <= 0:
                self.open = []
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True

    def draw(self, screen=None):
        t = screen or self.screen
        t.fill((250, 236, 214))
        for i, face in enumerate(self.cards):
            r = self.rect(i)
            up = self.matched[i] or i in self.open
            pygame.draw.rect(t, (150, 110, 90), r.move(0, 3), border_radius=10)
            if up:
                col = (255, 255, 250) if not self.matched[i] else (220, 245, 220)
                if i in self.flash:
                    col = (255, 250, 180)
                pygame.draw.rect(t, col, r, border_radius=10)
                ic = icon(face, 52)
                t.blit(ic, ic.get_rect(center=r.center))
            else:
                pygame.draw.rect(t, (120, 150, 220), r, border_radius=10)
                pygame.draw.rect(t, (170, 195, 245), r.inflate(-14, -14), 3, border_radius=8)
                q = self.font.render("?", True, (230, 240, 255))
                t.blit(q, q.get_rect(center=r.center))
            if i == self.cursor:
                pygame.draw.rect(t, (255, 190, 40), r.inflate(8, 8), 4, border_radius=12)
        bar = pygame.Rect(140, 448, 360, 8)
        pygame.draw.rect(t, (210, 190, 170), bar, border_radius=4)
        pygame.draw.rect(t, (240, 120, 100) if self.time_left < 15 else (110, 190, 110),
                         (bar.x, bar.y, int(bar.w * self.time_left / TIME_LIMIT), bar.h), border_radius=4)
        self.hud(t, f"SCORE {self.score}", f"PET PAIRS  {self.pairs}/8  {int(self.time_left)}s")


if __name__ == "__main__":
    pygame.init()
    print(PetPairs(pygame.display.set_mode((W, H))).run())
