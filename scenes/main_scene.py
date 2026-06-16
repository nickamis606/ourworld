#!/usr/bin/env python3
"""
MainScene - Primary gameplay scene (now using ArcadePanel as well).

UI components:
- StatsBar
- ActionButtons
- ShopUI
- ContextActions
- ArcadePanel (NEW)
"""

import pygame
import time
import math
from typing import Optional, Any

from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite
from ui.stats_bar import StatsBar
from ui.action_buttons import ActionButtons
from ui.shop_ui import ShopUI
from ui.context_actions import ContextActions
from ui.arcade_panel import ArcadePanel   # NEW


class MainScene(BaseScene):
    def __init__(self, game_state: Any, screen: pygame.Surface, pet_config: dict):
        super().__init__(game_state, screen)

        self.pet_config = pet_config
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.tiny_font = pygame.font.SysFont("Arial", 12)

        # Shared UI components
        self.stats_bar = StatsBar(self.width, self.small_font, self.tiny_font)
        self.action_buttons = ActionButtons(y=415, small_font=self.small_font)
        self.shop_ui = ShopUI(self.small_font)
        self.context_actions = ContextActions(self.small_font)
        self.arcade_panel = ArcadePanel(self.small_font, self.tiny_font)

        self.pet_sprite = PetSprite(pet_config, size=1.3, pos=(340, 210))
        self.pet_bob = 0.0

        self.map_mode = False
        self.anim_state: Optional[dict] = None
        self.status = f"Take good care of {game_state.pet.name}!"

        self.next_scene = None

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
            self._handle_map_click(pos)
            return

        # Main action buttons
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

        # Arcade scene switch (now also via ArcadePanel)
        if loc == "arcade":
            game = self.arcade_panel.get_clicked_game(pos)
            if game:
                self.next_scene = "arcade"
                return

            # Fallback for old button positions if needed
            if pygame.Rect(450, 280, 80, 45).collidepoint(pos) or pygame.Rect(540, 280, 80, 45).collidepoint(pos):
                self.next_scene = "arcade"
                return

        # ShopUI
        if loc in ("sweeties_candy_shop", "gens_garden"):
            item = self.shop_ui.get_clicked_item(pos, loc)
            if item:
                result = self.game_state.buy_item(loc, item)
                self.status = result.get("msg", "")
                if result.get("success") and item in ("lollipop", "candy_apple"):
                    self.anim_state = {"type": "feed", "start": time.time()}
                return

        # ContextActions
        action = self.context_actions.get_clicked_action(pos, loc)
        if action:
            if action == "plant_flower":
                if self.game_state.pet.inventory.get("flower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("flower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.anim_state = {"type": "plant", "start": time.time()}
            elif action == "plant_sunflower":
                if self.game_state.pet.inventory.get("sunflower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("sunflower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.anim_state = {"type": "plant", "start": time.time()}
            elif action == "harvest":
                result = self.game_state.harvest_plant()
                self.status = result.get("msg", "")
            elif action == "decorate":
                result = self.game_state.decorate_home()
                self.status = result.get("msg", "")
            return

    def _handle_map_click(self, pos: tuple):
        locations = {
            (60, 110): "home",
            (200, 110): "backyard",
            (340, 110): "park",
            (60, 230): "sweeties_candy_shop",
            (200, 230): "gens_garden",
            (340, 230): "arcade",
        }
        for rect_pos, loc in locations.items():
            if pygame.Rect(*rect_pos, 130, 95).collidepoint(pos):
                if loc == "arcade":
                    self.next_scene = "arcade"
                else:
                    self.change_location(loc)
                self.map_mode = False
                return

    def start_action(self, action: str):
        if self.anim_state or self.map_mode:
            return
        self.anim_state = {"type": action, "start": time.time()}
        self.status = f"{action.capitalize()}ing..."

    def update_animation(self):
        if not self.anim_state:
            return
        if time.time() - self.anim_state["start"] > 0.85:
            action = self.anim_state["type"]
            result = self.game_state.perform_care_action(action)
            if result and result.get("success"):
                self.status = result.get("bonus", f"{self.game_state.pet.name} loved that!")
            else:
                self.status = "Nothing happened..."
            self.anim_state = None

    def change_location(self, loc: str):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
        self.map_mode = False

    def update(self, dt: float):
        super().update(dt)
        self.pet_bob = (self.pet_bob + 0.08) % (2 * math.pi)
        self.pet_sprite.set_bob(self.pet_bob)
        self.pet_sprite.update(dt)

        if self.anim_state:
            self.update_animation()

    def draw(self, surface: pygame.Surface):
        loc = self.game_state.pet.location
        if loc == "home":
            bg = (245, 235, 220)
        elif loc == "park":
            bg = (200, 230, 200)
        elif loc == "backyard":
            bg = (200, 235, 195)
        elif loc == "sweeties_candy_shop":
            bg = (255, 240, 245)
        elif loc == "gens_garden":
            bg = (235, 245, 255)
        else:
            bg = (210, 200, 230)
        surface.fill(bg)

        needs = self.game_state.pet.needs
        total_seeds = (self.game_state.pet.inventory.get("flower_seeds", 0) +
                       self.game_state.pet.inventory.get("sunflower_seeds", 0))
        self.stats_bar.draw(surface, needs, self.game_state.pet.coins, total_seeds)

        self._draw_environment(surface, loc)
        self.pet_sprite.draw(surface)
        self._draw_mood(surface)
        self._draw_status(surface)
        self.action_buttons.draw(surface, anim_state_active=bool(self.anim_state))

        self.shop_ui.draw(surface, loc)

        has_mature = any(p.get("stage", 0) >= 3 for p in self.game_state.pet.garden)
        self.context_actions.draw(surface, loc, self.game_state.pet.inventory, has_mature)

        # Use ArcadePanel when in arcade
        if loc == "arcade" and not self.map_mode:
            self.arcade_panel.draw(surface)

        if self.map_mode:
            self._draw_map_overlay(surface)

        if self.anim_state:
            self._draw_anim_effect(surface)

        hint = self.tiny_font.render("F/P/C/R • M=Map • Q=Quit", True, (100, 100, 100))
        surface.blit(hint, (15, 455))

    # Remaining drawing methods (kept minimal)
    def _draw_environment(self, surface, loc):
        if loc == "home":
            pygame.draw.rect(surface, (200, 170, 130), (0, 260, self.width, 220))
            pygame.draw.rect(surface, (135, 206, 250), (480, 80, 100, 80), width=5)
            pygame.draw.line(surface, (139, 69, 19), (530, 80), (530, 160), 4)
            pygame.draw.rect(surface, (180, 100, 80), (60, 250, 180, 55))
            self._draw_home_decoration(surface)
        elif loc == "park":
            pygame.draw.rect(surface, (120, 180, 120), (0, 260, self.width, 220))
            for tx in (80, 520):
                pygame.draw.rect(surface, (139, 69, 19), (tx-8, 200, 16, 55))
                pygame.draw.circle(surface, (34, 160, 50), (tx, 175), 38)
        elif loc == "backyard":
            pygame.draw.rect(surface, (140, 190, 120), (0, 260, self.width, 220))
            pygame.draw.rect(surface, (101, 67, 33), (80, 290, 480, 110), border_radius=8)
            pygame.draw.rect(surface, (80, 50, 30), (80, 290, 480, 110), width=3, border_radius=8)
            self._draw_garden_plants(surface)
        elif loc == "sweeties_candy_shop":
            pygame.draw.rect(surface, (255, 235, 240), (0, 260, self.width, 220))
            pygame.draw.rect(surface, (200, 50, 70), (150, 245, 340, 120), border_radius=6)
            pygame.draw.polygon(surface, (210, 180, 140), [(140, 245), (320, 200), (500, 245)])
        elif loc == "gens_garden":
            pygame.draw.rect(surface, (230, 245, 255), (0, 260, self.width, 220))
            pygame.draw.rect(surface, (90, 150, 210), (150, 250, 340, 110), border_radius=6)
        else:
            pygame.draw.rect(surface, (50, 45, 70), (0, 260, self.width, 220))
            for x_pos in (120, 400):
                pygame.draw.rect(surface, (40, 40, 55), (x_pos, 260, 120, 100), border_radius=8)

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

    def _draw_anim_effect(self, surface):
        if not self.anim_state:
            return
        etype = self.anim_state["type"]
        elapsed = time.time() - self.anim_state["start"]
        cx, cy = 340, 210

        if etype == "feed":
            pygame.draw.ellipse(surface, (139, 69, 19), (cx + 70, cy + 15, 50, 25))
        elif etype == "play":
            bx = cx + 80 + int(30 * ((elapsed % 0.6) - 0.3))
            pygame.draw.circle(surface, (255, 99, 71), (bx, cy + 30), 12)
        elif etype == "clean":
            for i in range(3):
                by = cy - 20 - int((elapsed * 50 + i * 15) % 50)
                pygame.draw.circle(surface, (135, 206, 250), (cx + 60 + i * 20, by), 7, 2)
        elif etype == "rest":
            for ox, oy in [(40, -30), (55, -42)]:
                surface.blit(self.font.render("Z", True, (147, 112, 219)), (cx + ox, cy + oy))
        elif etype == "plant":
            for i in range(3):
                pygame.draw.circle(surface, (60, 160, 60), (cx + 60 + i * 15, cy - 10 - i * 8), 5)

    def _draw_map_overlay(self, surface):
        overlay = pygame.Surface((self.width, 300), pygame.SRCALPHA)
        overlay.fill((250, 248, 240, 235))
        surface.blit(overlay, (0, 60))
        surface.blit(self.font.render("Neighborhood Map — Click a location", True, (20, 20, 20)), (25, 70))

        positions = [
            (60, 110, "home", "Home"),
            (200, 110, "backyard", "Backyard"),
            (340, 110, "park", "Park"),
            (60, 230, "sweeties_candy_shop", "Sweeties"),
            (200, 230, "gens_garden", "Garden"),
            (340, 230, "arcade", "Arcade"),
        ]
        for px, py, key, name in positions:
            is_current = (key == self.game_state.pet.location)
            rect = pygame.Rect(px, py, 130, 95)
            pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=12)
            border_color = (100, 149, 237) if is_current else (180, 160, 140)
            pygame.draw.rect(surface, border_color, rect, width=4 if is_current else 2, border_radius=12)
            name_surf = self.small_font.render(name, True, border_color)
            surface.blit(name_surf, (px + 10, py + 70))

    def start_action(self, action: str):
        if self.anim_state or self.map_mode:
            return
        self.anim_state = {"type": action, "start": time.time()}
        self.status = f"{action.capitalize()}ing..."

    def update_animation(self):
        if not self.anim_state:
            return
        if time.time() - self.anim_state["start"] > 0.85:
            action = self.anim_state["type"]
            result = self.game_state.perform_care_action(action)
            if result and result.get("success"):
                self.status = result.get("bonus", f"{self.game_state.pet.name} loved that!")
            else:
                self.status = "Nothing happened..."
            self.anim_state = None

    def change_location(self, loc: str):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
        self.map_mode = False

    def update(self, dt: float):
        super().update(dt)
        self.pet_bob = (self.pet_bob + 0.08) % (2 * math.pi)
        self.pet_sprite.set_bob(self.pet_bob)
        self.pet_sprite.update(dt)

        if self.anim_state:
            self.update_animation()
