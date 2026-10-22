#!/usr/bin/env python3
"""Fishing at Sunny Pond. A to cast (timing sets distance), wait for the
bite, A to hook, then hold Left/Right to keep the fish inside your green
zone until the meter fills. 5 casts per trip. Nothing is ever lost:
a fish that slips away just swims off.
"""
from __future__ import annotations

import math
import random

import pygame

from core import fish_data
from minigames.base import MinigameBase, SCREEN_WIDTH as W, SCREEN_HEIGHT as H

CASTS = 5
BITE_WINDOW = 1.1
BAR_X, BAR_Y, BAR_W = 120, 420, 400
ZONE_W = 120
ZONE_SPEED = 300.0
FILL, DRAIN = 0.38, 0.20
DOCK = (96, 292)


class Fishing(MinigameBase):
    def __init__(self, screen, clock=None, roll=None, seed=None, pet_color=(240, 170, 190), pet_img=None):
        super().__init__(screen, clock)
        self.pet_img = pet_img
        self.rng = random.Random(seed)
        self.roll = roll or (lambda bonus: fish_data.roll(self.rng, "day", "summer", bonus))
        self.pet_color = pet_color
        self.phase = "aim"          # aim | wait | bite | reel | show
        self.t = 0.0
        self.power = 0.0
        self.casts_left = CASTS
        self.catches = []           # [(key, size_cm)]
        self.wait = 0.0
        self.timer = 0.0
        self.fish = None
        self.fish_x = 0.5
        self.fish_v = 0.0
        self.zone_x = 0.5
        self.meter = 0.3
        self.msg = "Press A to cast!"
        self.bobber = None
        self._bg = None

    # ------------------------------------------------------------- input
    def handle_action(self, a):
        if self.game_over or a != "A":
            return
        if self.phase == "aim":
            self.power = 0.5 - 0.5 * math.cos(self.t * 3.2)
            self.casts_left -= 1
            self.phase = "wait"
            self.wait = 1.0 + self.rng.random() * 2.2
            d = 0.25 + 0.75 * self.power
            self.bobber = (DOCK[0] + 60 + int(420 * d), 250 + int(140 * (1 - d) * 0.4))
            self.msg = "Shhh... wait for a bite"
        elif self.phase == "wait":
            self.msg = "Too soon! The fish swam off. Cast again."
            self._next()
        elif self.phase == "bite":
            self.fish = self.roll(self.power * 0.6)
            self.phase = "reel"
            self.meter = 0.3
            self.fish_x = 0.2 if self.rng.random() < 0.5 else 0.8   # start away from you
            self.fish_v, self.zone_x = 0.0, 0.5
            self.msg = "Hold Left/Right: keep the fish in the green!"

    def _next(self):
        self.bobber = None
        if self.casts_left <= 0:
            self.phase = "done"
            self.timer = 1.2
        else:
            self.phase = "aim"

    # ------------------------------------------------------------ update
    def update(self, dt):
        if self.game_over:
            return
        self.t += dt
        if self.phase == "wait":
            self.wait -= dt
            if self.wait <= 0:
                self.phase = "bite"
                self.timer = BITE_WINDOW
                self.msg = "A BITE! Press A!"
        elif self.phase == "bite":
            self.timer -= dt
            if self.timer <= 0:
                self.msg = "It got away... try again!"
                self._next()
        elif self.phase == "reel":
            pull = fish_data.FISH[self.fish][5]
            # fish wanders: smooth push plus the odd dart
            self.fish_v += (math.sin(self.t * (1.3 + pull)) * 1.2 + (self.rng.random() - 0.5) * 3.4) * pull * dt
            self.fish_v *= 0.96
            self.fish_x += self.fish_v * dt
            if self.fish_x < 0.03 or self.fish_x > 0.97:
                self.fish_v = -self.fish_v * 0.6
                self.fish_x = max(0.03, min(0.97, self.fish_x))
            d = (("RIGHT" in self.held) - ("LEFT" in self.held)) * ZONE_SPEED / BAR_W
            half = ZONE_W / BAR_W / 2
            self.zone_x = max(half, min(1 - half, self.zone_x + d * dt))
            inside = abs(self.fish_x - self.zone_x) <= half
            self.meter += (FILL if inside else -DRAIN / max(0.6, 1.0 / pull)) * dt
            if self.meter >= 1.0:
                info = fish_data.FISH[self.fish]
                size = int(round(18 * info[4] * (0.8 + 0.5 * self.rng.random())))
                self.catches.append((self.fish, size))
                self.score += info[2]
                self.phase = "show"
                self.timer = 1.6
                self.msg = f"You caught a {info[0]}! ({size} cm)"
            elif self.meter <= 0:
                self.msg = "It wiggled free! Splash!"
                self._next()
        elif self.phase == "show":
            self.timer -= dt
            if self.timer <= 0:
                self._next()
        elif self.phase == "done":
            self.timer -= dt
            if self.timer <= 0:
                self.end()

    # -------------------------------------------------------------- draw
    def _background(self):
        s = pygame.Surface((W, H)).convert() if pygame.display.get_surface() else pygame.Surface((W, H))
        for y in range(0, 200, 4):
            k = y / 200
            pygame.draw.rect(s, (int(150 + 60 * k), int(205 + 30 * k), 250), (0, y, W, 4))
        pygame.draw.ellipse(s, (110, 175, 100), (-80, 150, 420, 110))
        pygame.draw.ellipse(s, (96, 160, 92), (260, 160, 480, 100))
        for y in range(200, H, 4):
            k = (y - 200) / (H - 200)
            pygame.draw.rect(s, (int(80 - 30 * k), int(160 - 40 * k), int(210 - 40 * k)), (0, y, W, 4))
        rng = random.Random(3)
        for _ in range(30):
            x, y = rng.randint(0, W), rng.randint(214, H - 80)
            pygame.draw.line(s, (150, 200, 240), (x, y), (x + rng.randint(10, 30), y), 1)
        # dock
        pygame.draw.rect(s, (120, 80, 50), (0, 300, 150, 26))
        for x in (10, 60, 110):
            pygame.draw.rect(s, (95, 62, 40), (x, 326, 12, 60))
        for x in range(0, 150, 25):
            pygame.draw.line(s, (95, 62, 40), (x, 300), (x, 326), 2)
        # lily pads
        for x, y in ((520, 330), (580, 370), (460, 390)):
            pygame.draw.ellipse(s, (70, 150, 80), (x, y, 46, 20))
            pygame.draw.circle(s, (250, 190, 210), (x + 30, y + 8), 5)
        return s

    def draw(self, surface=None):
        surface = surface or self.screen
        if self._bg is None:
            self._bg = self._background()
        surface.blit(self._bg, (0, 0))
        # fish shadows drifting
        for i in range(3):
            x = 170 + (self.t * (18 + i * 7) + i * 150) % (W - 170)
            y = 320 + i * 22 + int(6 * math.sin(self.t + i))
            pygame.draw.ellipse(surface, (50, 100, 150), (int(x), y, 34, 12))
        # pet on the dock + rod
        px, py = DOCK
        if self.pet_img is not None:
            surface.blit(self.pet_img, self.pet_img.get_rect(midbottom=(px - 6, py + 6)))
        else:
            pygame.draw.ellipse(surface, self.pet_color, (px - 24, py - 40, 48, 44))
            pygame.draw.circle(surface, self.pet_color, (px, py - 52), 18)
            pygame.draw.circle(surface, (40, 30, 30), (px + 6, py - 54), 3)
        tip = (px + 70, py - 90)
        pygame.draw.line(surface, (120, 80, 40), (px + 10, py - 30), tip, 4)
        if self.bobber:
            bx, by = self.bobber
            bob = int(3 * math.sin(self.t * 4))
            if self.phase == "bite":
                bob = 6 + int(5 * math.sin(self.t * 30))
            pygame.draw.line(surface, (240, 240, 240), tip, (bx, by + bob), 1)
            pygame.draw.circle(surface, (240, 60, 60), (bx, by + bob), 8)
            pygame.draw.rect(surface, (255, 255, 255), (bx - 8, by + bob, 17, 5))
            if self.phase == "bite":
                t = self.big_font.render("!", True, (255, 230, 80))
                surface.blit(t, t.get_rect(center=(bx, by - 40)))
        elif self.phase in ("aim",):
            pygame.draw.line(surface, (240, 240, 240), tip, (tip[0] + 6, tip[1] + 60), 1)
        if self.phase == "aim":
            p = 0.5 - 0.5 * math.cos(self.t * 3.2)
            r = pygame.Rect(BAR_X, BAR_Y, BAR_W, 22)
            pygame.draw.rect(surface, (30, 40, 60), r.inflate(6, 6), border_radius=8)
            pygame.draw.rect(surface, (90, 200, 120), (r.x, r.y, int(r.w * p), r.h), border_radius=6)
            surface.blit(self.small_font.render("Cast power", True, (255, 255, 255)), (r.x, r.y - 28))
        if self.phase == "reel":
            r = pygame.Rect(BAR_X, BAR_Y, BAR_W, 30)
            pygame.draw.rect(surface, (30, 40, 60), r.inflate(6, 6), border_radius=8)
            pygame.draw.rect(surface, (60, 90, 140), r, border_radius=6)
            zx = r.x + int(self.zone_x * r.w) - ZONE_W // 2
            pygame.draw.rect(surface, (110, 220, 130), (zx, r.y, ZONE_W, r.h), border_radius=6)
            col = fish_data.FISH[self.fish][3]
            fx = r.x + int(self.fish_x * r.w)
            pygame.draw.ellipse(surface, col, (fx - 14, r.y + 7, 24, 16))
            pygame.draw.polygon(surface, col, [(fx + 8, r.centery), (fx + 16, r.y + 6), (fx + 16, r.bottom - 6)])
            m = pygame.Rect(BAR_X, BAR_Y - 22, BAR_W, 10)
            pygame.draw.rect(surface, (30, 40, 60), m.inflate(4, 4), border_radius=5)
            pygame.draw.rect(surface, (250, 200, 60), (m.x, m.y, int(m.w * max(0, self.meter)), m.h), border_radius=5)
        if self.phase == "show" and self.catches:
            key, size = self.catches[-1]
            col = fish_data.FISH[key][3]
            cx, cy = 320, 200
            pygame.draw.circle(surface, (255, 250, 230), (cx, cy), 56)
            s = fish_data.FISH[key][4]
            pygame.draw.ellipse(surface, col, (cx - 36 * s, cy - 16 * s, 60 * s, 32 * s))
            pygame.draw.polygon(surface, col, [(cx + 20 * s, cy), (cx + 40 * s, cy - 18 * s), (cx + 40 * s, cy + 18 * s)])
            pygame.draw.circle(surface, (30, 30, 30), (int(cx - 22 * s), int(cy - 4 * s)), 3)
        self.hud(surface, f"Fish: {len(self.catches)}", f"Casts left: {self.casts_left}")
        t = self.small_font.render(self.msg, True, (255, 255, 255))
        bg = pygame.Surface((t.get_width() + 24, t.get_height() + 10), pygame.SRCALPHA)
        bg.fill((20, 30, 50, 170))
        surface.blit(bg, bg.get_rect(center=(320, 462)))
        surface.blit(t, t.get_rect(center=(320, 462)))
