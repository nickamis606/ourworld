#!/usr/bin/env python3
"""
MainScene - The primary gameplay scene for OurWorld.

Handles:
- Environment / location background
- Pet display (via PetSprite)
- Top stats bar
- Action buttons (Feed, Play, Clean, Rest, Map)
- Location-specific UIs (shops, planting, arcade, harvest, decorate)
- Action animations
- Status + mood text
- Map overlay

This scene replaces most of the old monolithic OurWorldPygame drawing/logic.
"""

import pygame
import time
import math
from typing import Optional, Any

from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite


class MainScene(BaseScene):
    def __init__(self, game_state: Any, screen: pygame.Surface, pet_config: dict):
        super().__init__(game_state, screen)

        self.pet_config = pet_config
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Fonts
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.tiny_font = pygame.font.SysFont("Arial", 12)

        # Pet sprite (created here or passed in)
        self.pet_sprite = PetSprite(pet_config, size=1.3, pos=(340, 210))
        self.pet_bob = 0.0

        # UI state
        self.map_mode = False
        self.anim_state: Optional[dict] = None
        self.status = f"Take good care of {game_state.pet.name}!"

        # Action buttons (bottom bar)
        self.btn_feed = pygame.Rect(25, 415, 90, 36)
        self.btn_play = pygame.Rect(125, 415, 90, 36)
        self.btn_clean = pygame.Rect(225, 415, 90, 36)
        self.btn_rest = pygame.Rect(325, 415, 90, 36)
        self.btn_map = pygame.Rect(430, 415, 85, 36)

        # For scene switching requests
        self.next_scene = None

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
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

        # Bottom buttons
        if self.btn_feed.collidepoint(pos):
            self.start_action("feed")
        elif self.btn_play.collidepoint(pos):
            self.start_action("play")
        elif self.btn_clean.collidepoint(pos):
            self.start_action("clean")
        elif self.btn_rest.collidepoint(pos):
            self.start_action("rest")
        elif self.btn_map.collidepoint(pos):
            self.map_mode = not self.map_mode

        # Location-specific buttons
        loc = self.game_state.pet.location

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
            elif pygame.Rect(450, 70, 160, 40).collidepoint(pos):  # Harvest
                result = self.game_state.harvest_plant()
                self.status = result.get("msg", "")

        elif loc == "home":
            if pygame.Rect(30, 70, 200, 40).collidepoint(pos):  # Decorate
                result = self.game_state.decorate_home()
                self.status = result.get("msg", "")

        elif loc == "arcade":
            if pygame.Rect(450, 280, 80, 45).collidepoint(pos):
                self._request_snake()
            elif pygame.Rect(540, 280, 80, 45).collidepoint(pos):
                self._request_pet_dash()

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
                self.change_location(loc)
                self.map_mode = False
                return

    # ------------------------------------------------------------------
    # Game logic
    # ------------------------------------------------------------------
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

    def _request_snake(self):
        # Signal to controller that we want to start Snake
        self.next_scene = "snake"

    def _request_pet_dash(self):
        self.next_scene = "pet_dash"

    # ------------------------------------------------------------------
    # Update & Draw
    # ------------------------------------------------------------------
    def update(self, dt: float):
        super().update(dt)

        self.pet_bob = (self.pet_bob + 0.08) % (2 * math.pi)
        self.pet_sprite.set_bob(self.pet_bob)
        self.pet_sprite.update(dt)

        if self.anim_state:
            self.update_animation()

    def draw(self, surface: pygame.Surface):
        # Background by location
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

        self._draw_top_stats_bar(surface)
        self._draw_environment(surface, loc)
        self.pet_sprite.draw(surface)
        self._draw_mood(surface)
        self._draw_status(surface)
        self._draw_buttons(surface)

        self._draw_shop_ui(surface)
        self._draw_backyard_plant_ui(surface)
        self._draw_harvest_button(surface)
        self._draw_decorate_button(surface)
        self._draw_arcade_games(surface)

        if self.map_mode:
            self._draw_map_overlay(surface)

        if self.anim_state:
            self._draw_anim_effect(surface)

        # Hint text
        hint = self.tiny_font.render("F/P/C/R • M=Map • Q=Quit", True, (100, 100, 100))
        surface.blit(hint, (15, 455))

    # ------------------------------------------------------------------
    # Drawing helpers (kept private for now)
    # ------------------------------------------------------------------
    def _draw_top_stats_bar(self, surface):
        # (Same implementation as before, kept for brevity in this step)
        section_width = self.width // 5
        bar_height = 52
        needs = self.game_state.pet.needs

        stats = [
            ("Hunger", needs.hunger, (220, 60, 60)),
            ("Happiness", needs.happiness, (46, 139, 87)),
            ("Energy", needs.energy, (255, 200, 50)),
            ("Cleanliness", needs.cleanliness, (70, 130, 180)),
        ]

        for i, (label, value, color) in enumerate(stats):
            x = i * section_width
            pygame.draw.rect(surface, (245, 245, 245), (x, 0, section_width, bar_height))
            pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, bar_height), 1)
            label_surf = self.small_font.render(label, True, (20, 20, 20))
            surface.blit(label_surf, (x + 8, 4))
            bar_y = 24
            bar_width = section_width - 16
            pygame.draw.rect(surface, (180, 180, 180), (x + 8, bar_y, bar_width, 12), border_radius=3)
            fill_width = int(bar_width * max(0, min(1, value / 100)))
            pygame.draw.rect(surface, color, (x + 8, bar_y, fill_width, 12), border_radius=3)
            value_surf = self.tiny_font.render(f"{value:.0f}", True, (20, 20, 20))
            surface.blit(value_surf, (x + section_width - 30, bar_y + 1))

        # Coins + Seeds section
        x = 4 * section_width
        pygame.draw.rect(surface, (250, 248, 240), (x, 0, section_width, bar_height))
        pygame.draw.line(surface, (180, 160, 140), (x, 0), (x, bar_height), 2)
        coins_text = self.small_font.render(f"Coins: {self.game_state.pet.coins}", True, (180, 120, 40))
        surface.blit(coins_text, (x + 10, 8))
        inv = self.game_state.pet.inventory
        total_seeds = inv.get("flower_seeds", 0) + inv.get("sunflower_seeds", 0)
        seeds_text = self.small_font.render(f"Seeds: {total_seeds}", True, (60, 130, 60))
        surface.blit(seeds_text, (x + 10, 28))

    def _draw_environment(self, surface, loc):
        # Simplified version of previous draw_environment
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
        else:  # arcade
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

    def _draw_buttons(self, surface):
        buttons = [
            (self.btn_feed, "Feed (F)", (255, 140, 0)),
            (self.btn_play, "Play (P)", (46, 139, 87)),
            (self.btn_clean, "Clean (C)", (70, 130, 180)),
            (self.btn_rest, "Rest (R)", (147, 112, 219)),
        ]
        for rect, text, color in buttons:
            pygame.draw.rect(surface, color, rect, border_radius=8)
            if self.anim_state:
                pygame.draw.rect(surface, (90, 90, 90), rect, width=3, border_radius=8)
            surface.blit(self.small_font.render(text, True, (255, 255, 255)), (rect.x + 8, rect.y + 8))

        pygame.draw.rect(surface, (100, 149, 237), self.btn_map, border_radius=8)
        surface.blit(self.small_font.render("MAP (M)", True, (255, 255, 255)), (self.btn_map.x + 10, self.btn_map.y + 8))

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
