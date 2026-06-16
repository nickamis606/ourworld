#!/usr/bin/env python3
"""
MainScene - Primary gameplay scene (now using shared UI components for StatsBar and ActionButtons).
"""

import pygame
import time
import math
from typing import Optional, Any

from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite
from ui.stats_bar import StatsBar
from ui.action_buttons import ActionButtons   # NEW


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

        # Use ActionButtons for click detection
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
            if pygame.Rect(450, 280, 80, 45).collidepoint(pos) or pygame.Rect(540, 280, 80, 45).collidepoint(pos):
                self.next_scene = "arcade"
                return

        # Location-specific interactions (unchanged for now)
        if loc == "sweeties_candy_shop":
            if pygame.Rect(450, 280, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("sweeties_candy_shop", "lollipop")
                self.status = result.get("msg", "")
                if result.get("success"):
                    self.anim_state = {"type": "feed", "start": time.time()}
            elif pygame.Rect(450, 335, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("sweeties_candy_shop", "candy_apple")
                self.status = result.get("msg", "")
                if result.get("success"):
                    self.anim_state = {"type": "feed", "start": time.time()}

        elif loc == "gens_garden":
            if pygame.Rect(450, 280, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("gens_garden", "flower_seeds")
                self.status = result.get("msg", "")
            elif pygame.Rect(450, 335, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("gens_garden", "sunflower_seeds")
                self.status = result.get("msg", "")

        elif loc == "backyard":
            if pygame.Rect(30, 70, 180, 40).collidepoint(pos):
                if self.game_state.pet.inventory.get("flower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("flower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.anim_state = {"type": "plant", "start": time.time()}
            elif pygame.Rect(30, 120, 180, 40).collidepoint(pos):
                if self.game_state.pet.inventory.get("sunflower_seeds", 0) > 0:
                    result = self.game_state.plant_seed("sunflower_seeds")
                    self.status = result.get("msg", "")
                    if result.get("success"):
                        self.anim_state = {"type": "plant", "start": time.time()}
            elif pygame.Rect(450, 70, 160, 40).collidepoint(pos):
                result = self.game_state.harvest_plant()
                self.status = result.get("msg", "")

        elif loc == "home":
            if pygame.Rect(30, 70, 200, 40).collidepoint(pos):
                result = self.game_state.decorate_home()
                self.status = result.get("msg", "")

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

        # Shared UI components
        needs = self.game_state.pet.needs
        total_seeds = (self.game_state.pet.inventory.get("flower_seeds", 0) +
                       self.game_state.pet.inventory.get("sunflower_seeds", 0))
        self.stats_bar.draw(surface, needs, self.game_state.pet.coins, total_seeds)

        self._draw_environment(surface, loc)
        self.pet_sprite.draw(surface)
        self._draw_mood(surface)
        self._draw_status(surface)

        # Use shared ActionButtons
        self.action_buttons.draw(surface, anim_state_active=bool(self.anim_state))

        self._draw_shop_ui(surface)
        self._draw_backyard_plant_ui(surface)
        self._draw_harvest_button(surface)
        self._draw_decorate_button(surface)
        self._draw_arcade_games(surface)

        if self.map_mode:
            self._draw_map_overlay(surface)

        if self.anim_state:
            self._draw_anim_effect(surface)

        hint = self.tiny_font.render("F/P/C/R • M=Map • Q=Quit", True, (100, 100, 100))
        surface.blit(hint, (15, 455))

    # The remaining private drawing methods stay for now (can be further extracted later)
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

    def _draw_shop_ui(self, surface):
        if self.map_mode:
            return
        loc = self.game_state.pet.location
        if loc == "sweeties_candy_shop":
            btn1 = pygame.Rect(450, 280, 160, 45)
            pygame.draw.rect(surface, (255, 200, 210), btn1, border_radius=8)
            pygame.draw.rect(surface, (200, 50, 70), btn1, width=2, border_radius=8)
            surface.blit(self.small_font.render("Buy Lollipop (10)", True, (200, 50, 70)), (460, 292))

            btn2 = pygame.Rect(450, 335, 160, 45)
            pygame.draw.rect(surface, (255, 200, 210), btn2, border_radius=8)
            pygame.draw.rect(surface, (200, 50, 70), btn2, width=2, border_radius=8)
            surface.blit(self.small_font.render("Buy Candy Apple (25)", True, (200, 50, 70)), (460, 347))

        elif loc == "gens_garden":
            btn1 = pygame.Rect(450, 280, 160, 45)
            pygame.draw.rect(surface, (200, 230, 255), btn1, border_radius=8)
            pygame.draw.rect(surface, (90, 150, 210), btn1, width=2, border_radius=8)
            surface.blit(self.small_font.render("Buy Flower Seeds (12)", True, (90, 150, 210)), (460, 292))

    def _draw_backyard_plant_ui(self, surface):
        if self.game_state.pet.location != "backyard" or self.map_mode:
            return
        inv = self.game_state.pet.inventory
        if inv.get("flower_seeds", 0) > 0:
            btn = pygame.Rect(30, 70, 180, 40)
            pygame.draw.rect(surface, (180, 230, 180), btn, border_radius=8)
            pygame.draw.rect(surface, (40, 140, 60), btn, width=2, border_radius=8)
            surface.blit(self.small_font.render("Plant Flower Seeds", True, (30, 100, 50)), (40, 80))
        if inv.get("sunflower_seeds", 0) > 0:
            btn = pygame.Rect(30, 120, 180, 40)
            pygame.draw.rect(surface, (180, 230, 180), btn, border_radius=8)
            pygame.draw.rect(surface, (40, 140, 60), btn, width=2, border_radius=8)
            surface.blit(self.small_font.render("Plant Sunflower Seeds", True, (30, 100, 50)), (40, 130))

    def _draw_harvest_button(self, surface):
        if self.game_state.pet.location != "backyard" or self.map_mode:
            return
        mature_count = sum(1 for p in self.game_state.pet.garden if p.get("stage", 0) >= 3)
        if mature_count == 0:
            return
        btn = pygame.Rect(450, 70, 160, 40)
        pygame.draw.rect(surface, (255, 200, 150), btn, border_radius=8)
        pygame.draw.rect(surface, (200, 120, 50), btn, width=2, border_radius=8)
        surface.blit(self.small_font.render("Harvest Flower", True, (150, 80, 30)), (465, 80))

    def _draw_decorate_button(self, surface):
        if self.game_state.pet.location != "home" or self.map_mode:
            return
        if self.game_state.pet.inventory.get("flowers", 0) < 5:
            return
        btn = pygame.Rect(30, 70, 200, 40)
        pygame.draw.rect(surface, (255, 220, 240), btn, border_radius=8)
        pygame.draw.rect(surface, (200, 80, 150), btn, width=2, border_radius=8)
        surface.blit(self.small_font.render("Decorate Home (5)", True, (180, 60, 130)), (40, 80))

    def _draw_arcade_games(self, surface):
        if self.game_state.pet.location != "arcade" or self.map_mode:
            return
        panel = pygame.Rect(450, 260, 170, 85)
        pygame.draw.rect(surface, (40, 45, 70), panel, border_radius=10)
        pygame.draw.rect(surface, (100, 149, 237), panel, width=2, border_radius=10)
        surface.blit(self.small_font.render("ARCADE GAMES", True, (255, 220, 100)), (460, 268))

        snake_btn = pygame.Rect(460, 295, 70, 40)
        pygame.draw.rect(surface, (80, 200, 120), snake_btn, border_radius=6)
        surface.blit(self.tiny_font.render("Snake", True, (255, 255, 255)), (475, 305))

        dash_btn = pygame.Rect(540, 295, 70, 40)
        pygame.draw.rect(surface, (255, 160, 80), dash_btn, border_radius=6)
        surface.blit(self.tiny_font.render("Pet Dash", True, (255, 255, 255)), (548, 305))

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
