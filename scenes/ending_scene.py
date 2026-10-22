"""EndingScene: the Wish Lantern is lit. Fireworks + a short thank-you roll.

Cheap: one cached backdrop blit, <= ~80 particle circles, cached text lines.
"""
import math
import random

import pygame

from core import story_data as SD
from engine import assets
from scenes.base_scene import BaseScene
from sprites import backdrops
from ui.common import hint_bar, panel

COLORS = [(255, 120, 170), (255, 220, 90), (130, 210, 255), (160, 240, 150), (255, 170, 90)]


class EndingScene(BaseScene):
    low_power_ok = False

    def on_enter(self, **kw):
        self.t = 0.0
        self.rng = random.Random(7)
        self.parts = []      # [x, y, vx, vy, life, color]
        self.next_burst = 0.3
        st, pet = self.state.story, self.state.pet
        self.lines = [
            ("Festival of Lights!", 32, (255, 230, 150)),
            (f"{pet.name} and you woke up {SD.TOWN}!", 22, (255, 255, 255)),
            ("", 10, (0, 0, 0)),
            ("Starring", 18, (220, 210, 240)),
        ] + [(f"{n['name']}, {n['title']}", 18, (255, 255, 255)) for n in SD.NPCS.values()] + [
            ("", 10, (0, 0, 0)),
            (f"Stickers found: {len(st.stickers)}/{len(SD.STICKERS)}", 18, (220, 210, 240)),
            (f"Best friends level: {self.state.bond_level}", 18, (220, 210, 240)),
            ("", 10, (0, 0, 0)),
            ("Thanks for playing!", 26, (255, 230, 150)),
            ("Keep visiting: new Daily Wishes every day.", 18, (255, 255, 255)),
        ]

    def is_animating(self):
        return True

    def handle_action(self, a):
        if a in ("A", "START", "B") and self.t > 2.0:
            self.game.switch("main", message="Willowby is glowing! Check your Journal for Daily Wishes.")

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.handle_action("A")

    def update(self, dt):
        self.t += dt
        self.next_burst -= dt
        if self.next_burst <= 0 and len(self.parts) < 60:
            self.next_burst = self.rng.uniform(0.5, 1.1)
            x, y = self.rng.randint(80, 560), self.rng.randint(70, 200)
            col = self.rng.choice(COLORS)
            for k in range(16):
                a = k / 16 * math.tau
                sp = self.rng.uniform(60, 110)
                self.parts.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 1.2, col])
        alive = []
        for p in self.parts:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 60 * dt
            p[4] -= dt
            if p[4] > 0:
                alive.append(p)
        self.parts = alive

    def draw(self, surf):
        surf.blit(backdrops.get("lantern_hill", "day", "v1"), (0, 0))
        for x, y, _, _, life, col in self.parts:
            pygame.draw.circle(surf, col, (int(x), int(y)), 3 if life > 0.4 else 2)
        # credits roll inside a dark panel
        surf.blit(panel((380, 300), (20, 16, 40, 170), 18, None), (20, 110))
        y = 360 - self.t * 34
        clip = surf.get_clip()
        surf.set_clip(pygame.Rect(20, 118, 380, 284))
        for text, size, col in self.lines:
            if text and -40 < y < 420:
                t = assets.text_outlined(text, size, col, (30, 20, 50)) if size >= 26 else assets.text(text, size, col, bold=True)
                surf.blit(t, t.get_rect(center=(210, int(y))))
            y += size + 12
        surf.set_clip(clip)
        if y < 140:   # roll finished: loop it
            self.t = 0.0 if self.t > 3 else self.t
        if self.t > 2.0 or y < 140:
            hint_bar(surf, [("A", "Continue")])
