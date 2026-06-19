#!/usr/bin/env python3
"""
MainScene - Primary gameplay scene.

Now uses both ActionAnimator and LocationBackground foundation.
"""

import pygame
import time
import math
from typing import Optional, Any

from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite
from sprites.location_background import LocationBackground
from ui.stats_bar import StatsBar
from ui.action_buttons import ActionButtons
from ui.shop_ui import ShopUI
from ui.context_actions import ContextActions
from ui.arcade_panel import ArcadePanel
from ui.map_overlay import MapOverlay
from core.action_animator import ActionAnimator


class MainScene(BaseScene):
    def __init__(self, game_state: Any, screen: pygame.Surface, pet_config: dict):
        super().__init__(game_state, screen)

        self.pet_config = pet_config
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.tiny_font = pygame.font.SysFont("Arial", 12)

        self.stats_bar = StatsBar(self.width, self.small_font, self.tiny_font)
        self.action_buttons = ActionButtons(y=415, small_font=self.small_font)
        self.shop_ui = ShopUI(self.small_font)
        self.context_actions = ContextActions(self.small_font)
        self.arcade_panel = ArcadePanel(self.small_font, self.tiny_font)
        self.map_overlay = MapOverlay(self.small_font, self.font)

        self.pet_sprite = PetSprite(pet_config, size=0.95, pos=(340, 210))
        self.pet_bob = 0.0

        # New asset-based background system (with procedural fallback)
        self.location_bg = LocationBackground(self.width, self.height)

        # Cached procedural backgrounds (fallback)
        self.bg_surfaces: dict[str, pygame.Surface] = {}
        self._prepare_location_background(self.game_state.pet.location)

        # Load background asset if available (otherwise uses procedural)
        self._load_location_background(self.game_state.pet.location)

        # Animation system
        self.animator = ActionAnimator()

        self.map_mode = False
        self.status = f"Take good care of {game_state.pet.name}!"

        self.next_scene = None

    def _load_location_background(self, location: str):
        """Try to load asset-based background, fall back to procedural."""
        self.location_bg.load(location, procedural_fallback=self._prepare_location_background)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

    def _handle_key(self, key: int):
        if key in (pygame.K_q, pygame.K_ESCAPE):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_f:
            self.start_action("feed")
        elif key == pygame.K_p:
            self.start_action("play")
        elif key == pygame.K_c:
            self.start_action("clean")
        elif key == pygame.K_r:
            self.start_action("rest")
        elif key == pygame.K_m:
            self.map_mode = not self.map_mode

    def _handle_click(self, pos: tuple):
        if self.map_mode:
            clicked = self.map_overlay.get_clicked_location(pos)
            if clicked:
                if clicked == "arcade":
                    self.next_scene = "arcade"
                else:
                    self.change_location(clicked)
                self.map_mode = False
            return

        btn_rects = self.action_buttons.get_all_rects()
        if btn_rects["feed"].collidepoint(pos):
            self.start_action("feed")
        elif btn_rects["play"].collidepoint(pos):
            self.start_action("play")
        elif btn_rects["clean"].collidepoint(pos):
            self.start_action("clean")
        elif btn_rects["rest"].collidepoint(pos):
            self.start_action("rest")
        elif btn_rects["map"].collidepoint(pos):
            self.map_mode = not self.map_mode

        loc = self.game_state.pet.location

        if loc == "arcade":
            game = self.arcade_panel.get_clicked_game(pos)
            if game:
                self.next_scene = "arcade"
                return

        if loc in ("sweeties_candy_shop", "gens_garden"):
            item = self.shop_ui.get_clicked_item(pos, loc)
            if item:
                result = self.game_state.buy_item(loc, item)
                self.status = result.get("msg", "")
                if result.get("success") and item in ("lollipop", "candy_apple"):
                    self.start_action("feed")
                return

        action = self.context_actions.get_clicked_action(pos, loc)
        if action:
            if action == "plant_flower":
                if self.game_state.pet.inventory.get("flower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("flower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.start_action("plant")
            elif action == "plant_sunflower":
                if self.game_state.pet.inventory.get("sunflower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("sunflower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.start_action("plant")
            elif action == "harvest":
                result = self.game_state.harvest_plant()
                self.status = result.get("msg", "")
            elif action == "decorate":
                result = self.game_state.decorate_home()
                self.status = result.get("msg", "")
            return

    def start_action(self, action: str):
        if self.map_mode:
            return
        self.animator.start(action)
        self.status = f"{action.capitalize()}ing..."

    def change_location(self, loc: str):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
            self._prepare_location_background(loc)
            self._load_location_background(loc)  # Try asset or fallback
        self.map_mode = False

    def update(self, dt: float):
        super().update(dt)
        self.pet_bob = (self.pet_bob + 0.08) % (2 * math.pi)
        self.pet_sprite.set_bob(self.pet_bob)
        self.pet_sprite.update(dt)
        self.animator.update(dt)

    def draw(self, surface: pygame.Surface):
        loc = self.game_state.pet.location

        if self.map_mode:
            if loc in self.bg_surfaces:
                surface.blit(self.bg_surfaces[loc], (0, 0))
            else:
                surface.fill((210, 200, 230))
            self.map_overlay.draw(surface, loc)
            needs = self.game_state.pet.needs
            total_seeds = (self.game_state.pet.inventory.get("flower_seeds", 0) +
                           self.game_state.pet.inventory.get("sunflower_seeds", 0))
            self.stats_bar.draw(surface, needs, self.game_state.pet.coins, total_seeds)
            return

        # Draw background (asset if available, otherwise procedural)
        if self.location_bg.has_asset():
            self.location_bg.draw(surface)
        else:
            if loc in self.bg_surfaces:
                surface.blit(self.bg_surfaces[loc], (0, 0))
            else:
                surface.fill((210, 200, 230))

        needs = self.game_state.pet.needs
        total_seeds = (self.game_state.pet.inventory.get("flower_seeds", 0) +
                       self.game_state.pet.inventory.get("sunflower_seeds", 0))
        self.stats_bar.draw(surface, needs, self.game_state.pet.coins, total_seeds)

        if loc == "backyard":
            self._draw_garden_plants(surface)
        if loc == "home":
            self._draw_home_decoration(surface)

        self.pet_sprite.draw(surface)
        self._draw_mood(surface)
        self._draw_status(surface)
        self.action_buttons.draw(surface, anim_state_active=self.animator.is_active)

        self.shop_ui.draw(surface, loc)

        has_mature = any(p.get("stage", 0) >= 3 for p in self.game_state.pet.garden)
        self.context_actions.draw(surface, loc, self.game_state.pet.inventory, has_mature)

        if loc == "arcade":
            self.arcade_panel.draw(surface)

        if self.animator.is_active:
            self.animator.draw(surface, 340, 210)

        hint = self.tiny_font.render("F/P/C/R • M=Map • Q=Quit", True, (100, 100, 100))
        surface.blit(hint, (15, 455))

    # Keep existing procedural background method as fallback
    def _prepare_location_background(self, loc: str):
        """Procedural fallback background (used when no asset exists)."""
        bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if loc == "home":
            pygame.draw.rect(bg, (200, 170, 130), (0, 260, self.width, 220))
            pygame.draw.rect(bg, (180, 140, 110), (0, 0, self.width, 260))
            pygame.draw.rect(bg, (135, 206, 250), (480, 70, 110, 95), width=6)
            pygame.draw.rect(bg, (255, 245, 200, 70), (485, 75, 100, 85), border_radius=3)
            for i in range(3):
                pygame.draw.line(bg, (100, 80, 60), (485, 75 + i*28), (585, 75 + i*28), 2)
            pygame.draw.line(bg, (100, 80, 60), (535, 75), (535, 160), 2)
            pygame.draw.ellipse(bg, (140, 80, 60), (80, 300, 200, 90))
            pygame.draw.ellipse(bg, (120, 60, 40), (90, 310, 180, 70))
            pygame.draw.rect(bg, (120, 80, 50), (300, 340, 80, 12))
            pygame.draw.rect(bg, (100, 60, 30), (305, 352, 8, 35))
            pygame.draw.rect(bg, (100, 60, 30), (367, 352, 8, 35))
            pygame.draw.rect(bg, (90, 60, 40), (40, 120, 120, 18))
            for i, c in enumerate([(200,80,80), (80,160,80), (80,120,200), (220,180,60)]):
                pygame.draw.rect(bg, c, (50 + i*28, 123, 20, 12))

        elif loc == "park":
            pygame.draw.rect(bg, (120, 180, 120), (0, 260, self.width, 220))
            for x in range(0, 640, 40):
                pygame.draw.ellipse(bg, (100, 160, 100), (x, 280 + (x % 80)//2, 50, 25))
            for tx, ty, s in [(80, 200, 1.0), (520, 210, 0.9), (300, 195, 1.1), (150, 220, 0.75)]:
                pygame.draw.rect(bg, (101, 67, 33), (tx-6*s, ty+10*s, 12*s, 35*s))
                pygame.draw.circle(bg, (34, 160, 50), (tx, ty-5*s), 32*s)
                pygame.draw.circle(bg, (30, 140, 45), (tx-12*s, ty+5*s), 20*s)
                pygame.draw.circle(bg, (30, 140, 45), (tx+12*s, ty+5*s), 20*s)
            pygame.draw.ellipse(bg, (180, 160, 130), (200, 340, 240, 50))
            for fx, fy in [(220, 310), (400, 305), (280, 325)]:
                pygame.draw.circle(bg, (255, 100, 150), (fx, fy), 6)
                pygame.draw.circle(bg, (255, 200, 80), (fx, fy), 3)

        elif loc == "backyard":
            pygame.draw.rect(bg, (140, 190, 120), (0, 260, self.width, 220))
            pygame.draw.rect(bg, (120, 90, 60), (0, 355, self.width, 10))
            for x in range(30, 610, 55):
                pygame.draw.rect(bg, (100, 70, 40), (x, 340, 8, 30))
            pygame.draw.rect(bg, (101, 67, 33), (60, 300, 520, 55), border_radius=6)
            pygame.draw.rect(bg, (80, 50, 30), (60, 300, 520, 55), width=3, border_radius=6)
            pygame.draw.rect(bg, (110, 80, 50), (500, 280, 70, 10))
            pygame.draw.rect(bg, (90, 60, 30), (505, 290, 8, 22))
            pygame.draw.rect(bg, (90, 60, 30), (557, 290, 8, 22))

        elif loc == "sweeties_candy_shop":
            pygame.draw.rect(bg, (255, 235, 240), (0, 260, self.width, 220))
            pygame.draw.rect(bg, (200, 50, 70), (130, 220, 380, 100), border_radius=10)
            pygame.draw.polygon(bg, (210, 180, 140), [(120, 220), (320, 185), (520, 220)])
            for i in range(8):
                stripe_x = 135 + i * 45
                pygame.draw.line(bg, (255, 200, 220), (stripe_x, 198), (stripe_x + 30, 198), 3)
            pygame.draw.rect(bg, (110, 65, 35), (280, 250, 70, 70))
            pygame.draw.circle(bg, (255, 215, 90), (335, 285), 6)
            pygame.draw.circle(bg, (255, 130, 190), (155, 240), 18)
            pygame.draw.circle(bg, (130, 200, 255), (485, 240), 18)
            pygame.draw.circle(bg, (255, 190, 90), (165, 270), 12)
            pygame.draw.circle(bg, (90, 180, 255), (475, 270), 12)
            pygame.draw.rect(bg, (255, 250, 220), (160, 235, 25, 25), border_radius=3)
            pygame.draw.rect(bg, (255, 250, 220), (455, 235, 25, 25), border_radius=3)

        elif loc == "gens_garden":
            pygame.draw.rect(bg, (140, 190, 120), (0, 260, self.width, 220))
            pygame.draw.rect(bg, (120, 85, 55), (80, 290, 480, 80), border_radius=8)
            pygame.draw.rect(bg, (90, 60, 35), (80, 290, 480, 80), width=4, border_radius=8)
            for row in range(3):
                y = 305 + row * 22
                pygame.draw.line(bg, (60, 130, 50), (100, y), (540, y), 2)
            for x in [140, 240, 340, 440]:
                pygame.draw.line(bg, (130, 95, 60), (x, 285), (x, 365), 3)
            pygame.draw.circle(bg, (255, 100, 150), (160, 310), 7)
            pygame.draw.circle(bg, (255, 200, 80), (260, 320), 7)
            pygame.draw.circle(bg, (150, 180, 255), (360, 308), 7)
            pygame.draw.circle(bg, (255, 150, 200), (460, 318), 7)

        else:
            pygame.draw.rect(bg, (50, 45, 70), (0, 260, self.width, 220))
            for x_pos in (120, 400):
                pygame.draw.rect(bg, (40, 40, 55), (x_pos, 260, 120, 100), border_radius=8)

        self.bg_surfaces[loc] = bg

    def _draw_home_decoration(self, surface):
        if not self.game_state.pet.home_decorated:
            return
        base_x, base_y = 480, 320
        pygame.draw.rect(surface, (180, 120, 80), (base_x, base_y, 50, 45), border_radius=4)
        pygame.draw.line(surface, (34, 120, 34), (base_x + 15, base_y), (base_x + 15, base_y - 35), 3)
        pygame.draw.line(surface, (34, 120, 34), (base_x + 25, base_y), (base_x + 25, base_y - 40), 3)
        pygame.draw.circle(surface, (255, 100, 150), (base_x + 15, base_y - 42), 8)
        pygame.draw.circle(surface, (255, 200, 80), (base_x + 25, base_y - 48), 8)

    def _draw_garden_plants(self, surface):
        bed_x, bed_y = 100, 305
        for i, plant in enumerate(self.game_state.pet.garden[:8]):
            col = i % 4
            row = i // 4
            px = bed_x + col * 110
            py = bed_y + row * 55
            stage = plant.get("stage", 0)
            ptype = plant.get("type", "flower")

            if stage == 0:
                pygame.draw.circle(surface, (101, 67, 33), (px + 20, py + 15), 6)
            elif stage == 1:
                pygame.draw.line(surface, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
            elif stage == 2:
                pygame.draw.line(surface, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
                pygame.draw.circle(surface, (80, 180, 80), (px + 20, py + 3), 6)
            else:
                pygame.draw.line(surface, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
                if ptype == "flower":
                    pygame.draw.circle(surface, (255, 100, 150), (px + 20, py + 2), 9)
                else:
                    pygame.draw.circle(surface, (255, 200, 50), (px + 20, py + 2), 9)

    def _draw_mood(self, surface):
        needs = self.game_state.pet.needs
        avg = (needs.hunger + needs.happiness + needs.energy + needs.cleanliness) / 4
        if avg > 70:
            mood, col = "Happy :)", (60, 200, 80)
        elif avg > 40:
            mood, col = "Okay", (220, 180, 40)
        else:
            mood, col = "Sad :(", (230, 100, 100)
        txt = self.font.render(mood, True, col)
        surface.blit(txt, (300, 60))

    def _draw_status(self, surface):
        txt = self.small_font.render(self.status, True, (20, 20, 20))
        surface.blit(txt, (15, 375))

    def change_location(self, loc: str):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
            self._prepare_location_background(loc)
            self._load_location_background(loc)
        self.map_mode = False

    def update(self, dt: float):
        super().update(dt)
        self.pet_bob = (self.pet_bob + 0.08) % (2 * math.pi)
        self.pet_sprite.set_bob(self.pet_bob)
        self.pet_sprite.update(dt)
        self.animator.update(dt)