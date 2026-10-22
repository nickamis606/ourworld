"""TravelScene: a short (~1.5 s, skippable) walk down the street between places."""
import math

import pygame

from core import world
from core.roster import roster_entry
from engine import assets
from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite
from ui.common import panel

DURATION = 1.6
STRIP_W = 1280
_strip = None


def _build_strip():
    """Street scenery, rendered once (wider than the screen so it can scroll)."""
    s = pygame.Surface((STRIP_W, 480))
    for i in range(300):
        t = i / 299
        pygame.draw.line(s, (int(150 + 80 * t), int(200 + 40 * t), int(245 + 5 * t)), (0, i), (STRIP_W, i))
    colors = [(230, 160, 140), (160, 200, 230), (240, 210, 140), (180, 220, 170), (220, 170, 210)]
    x = 0
    k = 0
    while x < STRIP_W:
        w = 120 + (k * 37) % 60
        h = 120 + (k * 53) % 70
        c = colors[k % len(colors)]
        pygame.draw.rect(s, c, (x, 300 - h, w - 10, h))
        pygame.draw.polygon(s, tuple(max(0, v - 50) for v in c), [(x - 6, 300 - h), (x + w - 4, 300 - h), (x + (w - 10) // 2, 300 - h - 40)])
        for wy in range(300 - h + 20, 280, 40):
            for wx in range(x + 14, x + w - 30, 34):
                pygame.draw.rect(s, (255, 250, 210), (wx, wy, 18, 18))
        x += w
        k += 1
    pygame.draw.rect(s, (120, 190, 100), (0, 300, STRIP_W, 30))
    pygame.draw.rect(s, (200, 195, 185), (0, 330, STRIP_W, 40))
    pygame.draw.rect(s, (80, 80, 90), (0, 370, STRIP_W, 110))
    for x in range(0, STRIP_W, 80):
        pygame.draw.rect(s, (250, 230, 120), (x, 420, 44, 6))
        pygame.draw.line(s, (170, 165, 155), (x, 330), (x, 370), 2)
    return s.convert() if pygame.display.get_surface() else s


class TravelScene(BaseScene):
    low_power_ok = False

    def __init__(self, game):
        super().__init__(game)
        self.dest = "home"
        self.t = 0.0
        self.pet = None

    def on_enter(self, dest="home", **kw):
        global _strip
        if _strip is None:
            _strip = _build_strip()
        self.dest = dest
        self.origin = self.state.pet.location
        self.t = 0.0
        self.pet = PetSprite(roster_entry(self.state.pet.species_id), height=96)

    def is_animating(self):
        return True

    def handle_action(self, a):
        if a in ("A", "B", "START"):
            self._arrive()

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self._arrive()

    def _arrive(self):
        if self.game.transitioning:
            return
        self.state.change_location(self.dest)
        self.game.switch("main", arrived=True)

    def update(self, dt):
        self.t += dt
        self.pet.update(dt)
        if self.t >= DURATION:
            self._arrive()

    def draw(self, surf):
        p = min(1.0, self.t / DURATION)
        scroll = int((p * (STRIP_W - 640)))
        surf.blit(_strip, (0, 0), pygame.Rect(scroll, 0, 640, 480))
        x = 140 + p * 360
        hop = abs(math.sin(self.t * 11))
        self.pet.set_feet(x, 368)
        self.pet.draw(surf, {"dy": -16 * hop, "sx": 1 + 0.06 * (1 - hop), "sy": 1 - 0.06 * (1 - hop)})
        frm = world.LOCATIONS[self.origin].get("short", world.LOCATIONS[self.origin]["name"])
        to = world.LOCATIONS[self.dest]["name"]
        card = panel((420, 74), (255, 250, 240, 235), 14)
        surf.blit(card, (110, 40))
        surf.blit(assets.text(f"Leaving {frm}", 20, (130, 110, 100)), (130, 50))
        t = assets.text(f"Off to {to}!", 34, world.LOCATIONS[self.dest]["color"], bold=True)
        surf.blit(t, (130, 74))
        # progress dots
        for i in range(5):
            on = p * 5 > i
            pygame.draw.circle(surf, (255, 200, 60) if on else (200, 190, 180), (430 + i * 18, 92), 6)
