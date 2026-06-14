#!/usr/bin/env python3
"""
OurWorld - Complete Version
All locations, shops, arcade, planting, coins, clean top bar
"""

import pygame
import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.game_state import GameState
from minigames import get_minigame

WIDTH, HEIGHT = 640, 480
FPS = 30

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK = (35, 35, 45)
GRAY = (180, 180, 180)
GREEN = (46, 139, 87)
BLUE = (70, 130, 180)
RED = (220, 60, 60)
YELLOW = (255, 200, 50)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
CANDY_RED = (200, 50, 70)
GARDEN_BLUE = (90, 150, 210)
GARDEN_GREEN = (60, 160, 80)
WAFFLE = (210, 180, 140)

PET_ROSTER = [
    {"id": 0, "name": "Bubbles", "color": (255, 182, 193), "style": "round"},
    {"id": 1, "name": "Milo", "color": (255, 200, 150), "style": "cat"},
    {"id": 2, "name": "Luna", "color": (180, 220, 255), "style": "round"},
    {"id": 3, "name": "Sprout", "color": (200, 255, 180), "style": "plant"},
    {"id": 4, "name": "Pip", "color": (255, 220, 150), "style": "round"},
    {"id": 5, "name": "Nova", "color": (220, 180, 255), "style": "star"},
]


def draw_pet_preview(screen, x, y, pet_data, is_selected=False, bob=0):
    color = pet_data["color"]
    name = pet_data["name"]
    offset_y = int(5 * abs(3.14159 - bob) / 3.14159) if is_selected else 0
    cy = y + offset_y

    if pet_data["id"] == 0:
        pygame.draw.ellipse(screen, color, (x-34, cy-10, 68, 62))
        pygame.draw.ellipse(screen, (220, 120, 150), (x-34, cy-10, 68, 62), 4)
        pygame.draw.ellipse(screen, color, (x-28, cy-40, 56, 42))
        pygame.draw.ellipse(screen, (255, 130, 170), (x-30, cy-48, 22, 18))
        pygame.draw.ellipse(screen, (255, 80, 140), (x-26, cy-45, 12, 10))
        pygame.draw.ellipse(screen, (255, 130, 170), (x+8, cy-48, 22, 18))
        pygame.draw.ellipse(screen, (255, 80, 140), (x+14, cy-45, 12, 10))
        pygame.draw.ellipse(screen, WHITE, (x-16, cy-26, 14, 13))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-26, 14, 13))
        pygame.draw.ellipse(screen, (60, 90, 200), (x-12, cy-23, 7, 7))
        pygame.draw.ellipse(screen, (60, 90, 200), (x+6, cy-23, 7, 7))
        pygame.draw.ellipse(screen, BLACK, (x-9, cy-21, 4, 4))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-21, 4, 4))
        pygame.draw.arc(screen, (80, 80, 80), (x-8, cy-10, 16, 9), 0, 3.14, 2)
    elif pet_data["id"] == 1:
        pygame.draw.ellipse(screen, (70, 170, 85), (x-30, cy-8, 60, 55))
        pygame.draw.ellipse(screen, (45, 130, 60), (x-30, cy-8, 60, 55), 4)
        pygame.draw.ellipse(screen, (255, 255, 255), (x-22, cy-30, 44, 32))
        pygame.draw.ellipse(screen, (70, 170, 85), (x-20, cy-36, 16, 14))
        pygame.draw.ellipse(screen, (70, 170, 85), (x+4, cy-36, 16, 14))
        pygame.draw.ellipse(screen, WHITE, (x-13, cy-22, 11, 10))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-22, 11, 10))
        pygame.draw.ellipse(screen, (40, 70, 160), (x-9, cy-19, 5, 5))
        pygame.draw.ellipse(screen, (40, 70, 160), (x+6, cy-19, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-6, cy-17, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-17, 3, 3))
        pygame.draw.arc(screen, (50, 50, 50), (x-5, cy-8, 10, 6), 0, 3.14, 2)
    elif pet_data["id"] == 2:
        pygame.draw.ellipse(screen, color, (x-30, cy-8, 60, 52))
        pygame.draw.ellipse(screen, (120, 170, 220), (x-30, cy-8, 60, 52), 4)
        pygame.draw.ellipse(screen, color, (x-26, cy-35, 52, 40))
        pygame.draw.polygon(screen, (255, 215, 0), [(x, cy-48), (x-14, cy-36), (x-7, cy-36), (x-3, cy-44), (x+3, cy-44), (x+7, cy-36), (x+14, cy-36)])
        pygame.draw.ellipse(screen, color, (x-24, cy-38, 14, 14))
        pygame.draw.ellipse(screen, color, (x+10, cy-38, 14, 14))
        pygame.draw.ellipse(screen, WHITE, (x-14, cy-24, 12, 11))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-24, 12, 11))
        pygame.draw.ellipse(screen, (70, 110, 220), (x-10, cy-21, 7, 7))
        pygame.draw.ellipse(screen, (70, 110, 220), (x+6, cy-21, 7, 7))
        pygame.draw.ellipse(screen, BLACK, (x-7, cy-19, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-19, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-6, cy-9, 12, 7), 0, 3.14, 2)
    elif pet_data["id"] == 3:
        pygame.draw.ellipse(screen, color, (x-26, cy-5, 52, 50))
        pygame.draw.ellipse(screen, (120, 200, 130), (x-26, cy-5, 52, 50), 4)
        pygame.draw.ellipse(screen, color, (x-22, cy-32, 44, 36))
        pygame.draw.ellipse(screen, (255, 255, 255), (x-20, cy-42, 40, 18))
        pygame.draw.circle(screen, (255, 255, 255), (x, cy-48), 8)
        pygame.draw.ellipse(screen, WHITE, (x-11, cy-20, 10, 9))
        pygame.draw.ellipse(screen, WHITE, (x+1, cy-20, 10, 9))
        pygame.draw.ellipse(screen, (60, 100, 200), (x-8, cy-17, 5, 5))
        pygame.draw.ellipse(screen, (60, 100, 200), (x+6, cy-17, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-5, cy-15, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+7, cy-17, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-5, cy-8, 10, 6), 0, 3.14, 2)
    elif pet_data["id"] == 4:
        pygame.draw.ellipse(screen, color, (x-26, cy-5, 52, 48))
        pygame.draw.ellipse(screen, (220, 180, 130), (x-26, cy-5, 52, 48), 4)
        pygame.draw.ellipse(screen, color, (x-24, cy-32, 48, 36))
        pygame.draw.ellipse(screen, (255, 180, 200), (x-22, cy-38, 44, 12))
        pygame.draw.circle(screen, (255, 130, 170), (x-10, cy-35), 5)
        pygame.draw.circle(screen, (255, 130, 170), (x+10, cy-35), 5)
        pygame.draw.ellipse(screen, WHITE, (x-13, cy-20, 11, 10))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-20, 11, 10))
        pygame.draw.ellipse(screen, (80, 110, 200), (x-9, cy-17, 5, 5))
        pygame.draw.ellipse(screen, (80, 110, 200), (x+6, cy-17, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-7, cy-17, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-17, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-6, cy-8, 12, 7), 0, 3.14, 2)
    elif pet_data["id"] == 5:
        pygame.draw.ellipse(screen, color, (x-26, cy-5, 52, 48))
        pygame.draw.ellipse(screen, (160, 120, 200), (x-26, cy-5, 52, 48), 4)
        pygame.draw.ellipse(screen, color, (x-24, cy-32, 48, 36))
        pygame.draw.ellipse(screen, (180, 200, 255), (x-20, cy-40, 40, 12))
        pygame.draw.polygon(screen, (255, 215, 80), [(x-8, cy-38), (x-5, cy-45), (x-2, cy-38)])
        pygame.draw.polygon(screen, (255, 215, 80), [(x+8, cy-38), (x+5, cy-45), (x+2, cy-38)])
        pygame.draw.ellipse(screen, color, (x-22, cy-40, 12, 12))
        pygame.draw.ellipse(screen, color, (x+10, cy-40, 12, 12))
        pygame.draw.ellipse(screen, WHITE, (x-13, cy-20, 11, 10))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-20, 11, 10))
        pygame.draw.ellipse(screen, (90, 130, 255), (x-9, cy-17, 5, 5))
        pygame.draw.ellipse(screen, (90, 130, 255), (x+6, cy-17, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-7, cy-17, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-17, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-6, cy-8, 12, 7), 0, 3.14, 2)

    name_surf = pygame.font.SysFont("Arial", 13).render(name, True, BLACK)
    screen.blit(name_surf, (x - name_surf.get_width()//2, cy + 42))
    if is_selected:
        pygame.draw.rect(screen, (255, 215, 0), (x-45, cy-55, 90, 105), width=4, border_radius=12)


class PetSelectionScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.selected_index = 0
        self.bob = 0
        self.done = False

    def run(self):
        clock = pygame.time.Clock()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.done = True
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = (self.selected_index - 1) % len(PET_ROSTER)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = (self.selected_index + 1) % len(PET_ROSTER)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(PET_ROSTER)):
                        col = i % 3
                        row = i // 3
                        px = 120 + col * 180
                        py = 160 + row * 140
                        if pygame.Rect(px-40, py-50, 80, 100).collidepoint(event.pos):
                            self.selected_index = i
                            self.done = True
            self.bob = (self.bob + 0.1) % (2 * 3.14159)
            self.draw()
            clock.tick(30)
        chosen = PET_ROSTER[self.selected_index]
        return {"id": chosen["id"], "name": chosen["name"], "color": chosen["color"], "style": chosen["style"]}

    def draw(self):
        self.screen.fill((245, 250, 255))
        title = self.font.render("Choose Your Companion", True, BLACK)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        for i, pet in enumerate(PET_ROSTER):
            col = i % 3
            row = i // 3
            x = 120 + col * 180
            y = 160 + row * 140
            is_selected = (i == self.selected_index)
            draw_pet_preview(self.screen, x, y, pet, is_selected, self.bob if is_selected else 0)
        chosen = PET_ROSTER[self.selected_index]
        info = self.small_font.render(f"Selected: {chosen['name']} • Press ENTER", True, BLACK)
        self.screen.blit(info, (WIDTH//2 - info.get_width()//2, 420))
        pygame.display.flip()


class OurWorldPygame:
    def __init__(self, pet_config):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("OurWorld")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.tiny_font = pygame.font.SysFont("Arial", 12)
        self.game_state = GameState()
        self.game_state.pet.name = pet_config["name"]
        self.pet_config = pet_config
        self.pet_color = pet_config["color"]
        self.pet_id = pet_config["id"]
        self.pet_bob = 0
        self.anim_state = None
        self.last_tick = pygame.time.get_ticks()
        self.status = f"Take good care of {self.game_state.pet.name}!"
        self.map_mode = False
        self.state = "main"
        self.snake_game = None

        self.btn_feed = pygame.Rect(25, 415, 90, 36)
        self.btn_play = pygame.Rect(125, 415, 90, 36)
        self.btn_clean = pygame.Rect(225, 415, 90, 36)
        self.btn_rest = pygame.Rect(325, 415, 90, 36)
        self.btn_map = pygame.Rect(430, 415, 85, 36)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            now = pygame.time.get_ticks()
            if now - self.last_tick > 1500:
                self.game_state.tick()
                self.last_tick = now

            self.pet_bob = (self.pet_bob + 0.08) % (2 * 3.14159)

            if self.state == "main":
                self.update_animation()
            elif self.state == "snake" and self.snake_game:
                self.snake_game.update(dt)
                if getattr(self.snake_game, 'game_over', False):
                    bonus = min(40, getattr(self.snake_game, 'score', 0) // 3)
                    if bonus > 0:
                        self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
                        self.status = f"Arcade bonus! +{bonus} Happiness"
                    self.game_state.earn_coins(max(20, getattr(self.snake_game, 'score', 0) // 2))
                    self.state = "main"
                    self.snake_game = None

            self.draw()
            pygame.display.flip()

        self.game_state.save()
        pygame.quit()
        sys.exit()

    def handle_key(self, key):
        if self.state == "snake" and self.snake_game:
            if hasattr(self.snake_game, 'handle_key'):
                self.snake_game.handle_key(key)
            return

        if key in (pygame.K_q, pygame.K_ESCAPE):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_f: self.start_action("feed")
        elif key == pygame.K_p: self.start_action("play")
        elif key == pygame.K_c: self.start_action("clean")
        elif key == pygame.K_r: self.start_action("rest")
        elif key == pygame.K_m: self.map_mode = not self.map_mode

    def handle_click(self, pos):
        if self.map_mode:
            if pygame.Rect(60, 110, 130, 95).collidepoint(pos):
                self.change_location("home"); self.map_mode = False
            elif pygame.Rect(200, 110, 130, 95).collidepoint(pos):
                self.change_location("backyard"); self.map_mode = False
            elif pygame.Rect(340, 110, 130, 95).collidepoint(pos):
                self.change_location("park"); self.map_mode = False
            elif pygame.Rect(60, 230, 130, 95).collidepoint(pos):
                self.change_location("sweeties_candy_shop"); self.map_mode = False
            elif pygame.Rect(200, 230, 130, 95).collidepoint(pos):
                self.change_location("gens_garden"); self.map_mode = False
            elif pygame.Rect(340, 230, 130, 95).collidepoint(pos):
                self.change_location("arcade"); self.map_mode = False
            return

        # Bottom action buttons
        if self.btn_feed.collidepoint(pos): self.start_action("feed")
        elif self.btn_play.collidepoint(pos): self.start_action("play")
        elif self.btn_clean.collidepoint(pos): self.start_action("clean")
        elif self.btn_rest.collidepoint(pos): self.start_action("rest")
        elif self.btn_map.collidepoint(pos): self.map_mode = not self.map_mode

        # Shop buying (right side)
        if self.game_state.pet.location == "sweeties_candy_shop":
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

        elif self.game_state.pet.location == "gens_garden":
            if pygame.Rect(450, 280, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("gens_garden", "flower_seeds")
                self.status = result.get("msg", "")
            elif pygame.Rect(450, 335, 160, 45).collidepoint(pos):
                result = self.game_state.buy_item("gens_garden", "sunflower_seeds")
                self.status = result.get("msg", "")

        # Backyard planting buttons (now high up)
        if self.game_state.pet.location == "backyard":
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

        # Arcade buttons
        if self.game_state.pet.location == "arcade":
            if pygame.Rect(450, 280, 80, 45).collidepoint(pos):
                self.start_snake()
            elif pygame.Rect(540, 280, 80, 45).collidepoint(pos):
                self.start_pet_dash()

        # Harvest button (Backyard) - right side
        if self.game_state.pet.location == "backyard":
            if pygame.Rect(450, 70, 160, 40).collidepoint(pos):
                result = self.game_state.harvest_plant()
                self.status = result.get("msg", "")

        # Decorate button (Home)
        if self.game_state.pet.location == "home":
            if pygame.Rect(30, 70, 200, 40).collidepoint(pos):
                result = self.game_state.decorate_home()
                self.status = result.get("msg", "")

    def start_action(self, action):
        if self.anim_state or self.map_mode: return
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

    def change_location(self, loc):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
        self.map_mode = False

    def start_snake(self):
        self.state = "snake"
        SnakeClass = get_minigame("snake")
        self.snake_game = SnakeClass(self.screen, self.clock)
        self.status = "Snake time! Arrows/WASD • ESC to return"

    def start_pet_dash(self):
        self.state = "snake"
        PetDashClass = get_minigame("pet_dash")
        self.snake_game = PetDashClass(self.screen, self.clock, self.pet_color)
        self.status = "Pet Dash! SPACE/UP to jump • ESC to return"

    def draw_top_stats_bar(self):
        section_width = WIDTH // 5
        bar_height = 52
        needs = self.game_state.pet.needs

        stats = [
            ("Hunger", needs.hunger, RED),
            ("Happiness", needs.happiness, GREEN),
            ("Energy", needs.energy, YELLOW),
            ("Cleanliness", needs.cleanliness, BLUE),
        ]

        for i, (label, value, color) in enumerate(stats):
            x = i * section_width
            pygame.draw.rect(self.screen, (245, 245, 245), (x, 0, section_width, bar_height))
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, bar_height), 1)
            label_surf = self.small_font.render(label, True, BLACK)
            self.screen.blit(label_surf, (x + 8, 4))
            bar_y = 24
            bar_width = section_width - 16
            pygame.draw.rect(self.screen, GRAY, (x + 8, bar_y, bar_width, 12), border_radius=3)
            fill_width = int(bar_width * max(0, min(1, value / 100)))
            pygame.draw.rect(self.screen, color, (x + 8, bar_y, fill_width, 12), border_radius=3)
            value_surf = self.tiny_font.render(f"{value:.0f}", True, BLACK)
            self.screen.blit(value_surf, (x + section_width - 30, bar_y + 1))

        # 5th section - Coins + Seeds
        x = 4 * section_width
        pygame.draw.rect(self.screen, (250, 248, 240), (x, 0, section_width, bar_height))
        pygame.draw.line(self.screen, (180, 160, 140), (x, 0), (x, bar_height), 2)
        coins_text = self.small_font.render(f"Coins: {self.game_state.pet.coins}", True, (180, 120, 40))
        self.screen.blit(coins_text, (x + 10, 8))
        inv = self.game_state.pet.inventory
        total_seeds = inv.get("flower_seeds", 0) + inv.get("sunflower_seeds", 0)
        seeds_text = self.small_font.render(f"Seeds: {total_seeds}", True, (60, 130, 60))
        self.screen.blit(seeds_text, (x + 10, 28))

    def draw_garden_plants(self):
        if self.game_state.pet.location != "backyard":
            return

        bed_x, bed_y = 100, 305
        cols = 4
        rows = 2
        spacing_x = 110
        spacing_y = 55

        for i, plant in enumerate(self.game_state.pet.garden[:8]):
            col = i % cols
            row = i // cols
            px = bed_x + col * spacing_x
            py = bed_y + row * spacing_y

            stage = plant["stage"]
            ptype = plant["type"]

            if stage == 0:  # just planted
                pygame.draw.circle(self.screen, (101, 67, 33), (px + 20, py + 15), 6)
            elif stage == 1:  # sprout
                pygame.draw.line(self.screen, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
            elif stage == 2:  # budding
                pygame.draw.line(self.screen, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
                pygame.draw.circle(self.screen, (80, 180, 80), (px + 20, py + 3), 6)
            else:  # mature (stage 3)
                pygame.draw.line(self.screen, (34, 120, 34), (px + 20, py + 25), (px + 20, py + 5), 3)
                if ptype == "flower":
                    pygame.draw.circle(self.screen, (255, 100, 150), (px + 20, py + 2), 9)
                    pygame.draw.circle(self.screen, (255, 180, 200), (px + 20, py + 2), 5)
                else:  # sunflower
                    pygame.draw.circle(self.screen, (255, 200, 50), (px + 20, py + 2), 9)
                    pygame.draw.circle(self.screen, (139, 90, 40), (px + 20, py + 2), 4)

    def draw_harvest_button(self):
        if self.game_state.pet.location != "backyard" or self.map_mode:
            return

        # Only show if there is at least one mature plant
        mature_count = sum(1 for p in self.game_state.pet.garden if p.get("stage", 0) >= 3)
        if mature_count == 0:
            return

        # Positioned on the right side (same area as arcade/shop buttons)
        btn = pygame.Rect(450, 70, 160, 40)
        pygame.draw.rect(self.screen, (255, 200, 150), btn, border_radius=8)
        pygame.draw.rect(self.screen, (200, 120, 50), btn, width=2, border_radius=8)
        self.screen.blit(self.small_font.render("Harvest Flower", True, (150, 80, 30)), (465, 80))

    def draw_decorate_button(self):
        if self.game_state.pet.location != "home" or self.map_mode:
            return

        if self.game_state.pet.inventory.get("flowers", 0) < 5:
            return

        btn = pygame.Rect(30, 70, 200, 40)
        pygame.draw.rect(self.screen, (255, 220, 240), btn, border_radius=8)
        pygame.draw.rect(self.screen, (200, 80, 150), btn, width=2, border_radius=8)
        self.screen.blit(self.small_font.render("Decorate Home (5)", True, (180, 60, 130)), (40, 80))

    def draw_environment(self, loc):
        if loc == "home":
            pygame.draw.rect(self.screen, (200, 170, 130), (0, 260, 640, 220))
            pygame.draw.rect(self.screen, (135, 206, 250), (480, 80, 100, 80), width=5)
            pygame.draw.line(self.screen, (139, 69, 19), (530, 80), (530, 160), 4)
            pygame.draw.rect(self.screen, (180, 100, 80), (60, 250, 180, 55))
            self.draw_home_decoration()
        elif loc == "park":
            pygame.draw.rect(self.screen, (120, 180, 120), (0, 260, 640, 220))
            for tx in (80, 520):
                pygame.draw.rect(self.screen, (139, 69, 19), (tx-8, 200, 16, 55))
                pygame.draw.circle(self.screen, (34, 160, 50), (tx, 175), 38)
        elif loc == "backyard":
            pygame.draw.rect(self.screen, (140, 190, 120), (0, 260, 640, 220))
            # Brown garden bed
            pygame.draw.rect(self.screen, (101, 67, 33), (80, 290, 480, 110), border_radius=8)
            pygame.draw.rect(self.screen, (80, 50, 30), (80, 290, 480, 110), width=3, border_radius=8)

            # Draw planted flowers in a grid (max 8)
            self.draw_garden_plants()
        elif loc == "sweeties_candy_shop":
            pygame.draw.rect(self.screen, (255, 235, 240), (0, 260, 640, 220))
            pygame.draw.rect(self.screen, (200, 50, 70), (150, 245, 340, 120), border_radius=6)
            pygame.draw.polygon(self.screen, (210, 180, 140), [(140, 245), (320, 200), (500, 245)])
            pygame.draw.circle(self.screen, (255, 80, 150), (200, 275), 16)
            pygame.draw.line(self.screen, (200, 200, 200), (200, 291), (200, 315), 3)
            pygame.draw.circle(self.screen, (80, 200, 255), (440, 280), 14)
            pygame.draw.line(self.screen, (200, 200, 200), (440, 294), (440, 315), 3)
        elif loc == "gens_garden":
            pygame.draw.rect(self.screen, (230, 245, 255), (0, 260, 640, 220))
            pygame.draw.rect(self.screen, (90, 150, 210), (150, 250, 340, 110), border_radius=6)
            pygame.draw.rect(self.screen, (139, 90, 60), (160, 335, 320, 25))
            for fx, col in [(200, (255, 150, 180)), (280, (255, 220, 80)), (360, (150, 220, 255)), (440, (180, 255, 150))]:
                pygame.draw.circle(self.screen, col, (fx, 323), 10)
                pygame.draw.circle(self.screen, (50, 140, 50), (fx, 323), 6)
        else:  # arcade
            pygame.draw.rect(self.screen, (50, 45, 70), (0, 260, 640, 220))
            for x in (120, 400):
                pygame.draw.rect(self.screen, (40, 40, 55), (x, 260, 120, 100), border_radius=8)
                pygame.draw.rect(self.screen, (0, 220, 80), (x+15, 275, 90, 36))
                pygame.draw.circle(self.screen, (255, 50, 50), (x+40, 318), 8)
                pygame.draw.circle(self.screen, (255, 220, 50), (x+80, 318), 8)

    def draw_home_decoration(self):
        if self.game_state.pet.location != "home" or not self.game_state.pet.home_decorated:
            return

        # Position of the vase (on the right side of the home area)
        base_x = 480
        base_y = 320

        # Vase (simple pot shape)
        pygame.draw.rect(self.screen, (180, 120, 80), (base_x, base_y, 50, 45), border_radius=4)
        pygame.draw.rect(self.screen, (140, 90, 60), (base_x, base_y, 50, 45), width=2, border_radius=4)

        # Stems
        pygame.draw.line(self.screen, (34, 120, 34), (base_x + 15, base_y), (base_x + 15, base_y - 35), 3)
        pygame.draw.line(self.screen, (34, 120, 34), (base_x + 25, base_y), (base_x + 25, base_y - 40), 3)
        pygame.draw.line(self.screen, (34, 120, 34), (base_x + 35, base_y), (base_x + 35, base_y - 32), 3)

        # Flowers on top
        pygame.draw.circle(self.screen, (255, 100, 150), (base_x + 15, base_y - 42), 8)
        pygame.draw.circle(self.screen, (255, 180, 200), (base_x + 15, base_y - 42), 4)

        pygame.draw.circle(self.screen, (255, 200, 80), (base_x + 25, base_y - 48), 8)
        pygame.draw.circle(self.screen, (255, 230, 150), (base_x + 25, base_y - 48), 4)

        pygame.draw.circle(self.screen, (150, 200, 255), (base_x + 35, base_y - 40), 7)
        pygame.draw.circle(self.screen, (200, 230, 255), (base_x + 35, base_y - 40), 3)

    def draw_pet(self):
        cx, cy = 340, 210 + int(5 * abs(3.14159 - self.pet_bob) / 3.14159)
        color = self.pet_color
        pid = self.pet_id

        if pid == 0:
            pygame.draw.ellipse(self.screen, color, (cx-38, cy-5, 76, 62))
            pygame.draw.ellipse(self.screen, (220, 120, 150), (cx-38, cy-5, 76, 62), 4)
            pygame.draw.ellipse(self.screen, color, (cx-30, cy-42, 60, 45))
            pygame.draw.ellipse(self.screen, (255, 130, 170), (cx-32, cy-48, 20, 15))
            pygame.draw.ellipse(self.screen, (255, 80, 140), (cx-28, cy-45, 12, 10))
            pygame.draw.ellipse(self.screen, (255, 130, 170), (cx+12, cy-48, 20, 15))
            pygame.draw.ellipse(self.screen, (255, 80, 140), (cx+17, cy-45, 12, 10))
            pygame.draw.ellipse(self.screen, WHITE, (cx-18, cy-28, 14, 13))
            pygame.draw.ellipse(self.screen, WHITE, (cx+4, cy-28, 14, 13))
            pygame.draw.ellipse(self.screen, (60, 90, 200), (cx-14, cy-25, 7, 7))
            pygame.draw.ellipse(self.screen, (60, 90, 200), (cx+8, cy-25, 7, 7))
            pygame.draw.ellipse(self.screen, BLACK, (cx-11, cy-23, 4, 4))
            pygame.draw.ellipse(self.screen, BLACK, (cx+11, cy-23, 4, 4))
            pygame.draw.arc(self.screen, (60, 60, 60), (cx-7, cy-10, 14, 9), 0, 3.14, 2)
        elif pid == 1:
            pygame.draw.ellipse(self.screen, (70, 170, 85), (cx-32, cy-5, 64, 55))
            pygame.draw.ellipse(self.screen, (45, 130, 60), (cx-32, cy-5, 64, 55), 4)
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cx-24, cy-35, 48, 38))
            pygame.draw.ellipse(self.screen, (70, 170, 85), (cx-24, cy-42, 16, 16))
            pygame.draw.ellipse(self.screen, (70, 170, 85), (cx+8, cy-42, 16, 16))
            pygame.draw.ellipse(self.screen, WHITE, (cx-15, cy-25, 13, 12))
            pygame.draw.ellipse(self.screen, WHITE, (cx+2, cy-25, 13, 12))
            pygame.draw.ellipse(self.screen, (40, 70, 160), (cx-11, cy-22, 7, 7))
            pygame.draw.ellipse(self.screen, (40, 70, 160), (cx+6, cy-22, 7, 7))
            pygame.draw.ellipse(self.screen, BLACK, (cx-8, cy-20, 3, 3))
            pygame.draw.ellipse(self.screen, BLACK, (cx+9, cy-20, 3, 3))
            pygame.draw.arc(self.screen, (50, 50, 50), (cx-6, cy-9, 12, 7), 0, 3.14, 2)
        elif pid == 2:
            pygame.draw.ellipse(self.screen, color, (cx-32, cy-5, 64, 52))
            pygame.draw.ellipse(self.screen, (120, 170, 220), (cx-32, cy-5, 64, 52), 4)
            pygame.draw.ellipse(self.screen, color, (cx-28, cy-38, 56, 45))
            pygame.draw.polygon(self.screen, (255, 215, 0), [(cx, cy-52), (cx-14, cy-40), (cx-7, cy-40), (cx-3, cy-48), (cx+3, cy-48), (cx+7, cy-40), (cx+14, cy-40)])
            pygame.draw.ellipse(self.screen, color, (cx-26, cy-42, 15, 17))
            pygame.draw.ellipse(self.screen, color, (cx+11, cy-42, 15, 17))
            pygame.draw.ellipse(self.screen, WHITE, (cx-15, cy-24, 13, 12))
            pygame.draw.ellipse(self.screen, WHITE, (cx+2, cy-24, 13, 12))
            pygame.draw.ellipse(self.screen, (70, 110, 220), (cx-11, cy-21, 7, 7))
            pygame.draw.ellipse(self.screen, (70, 110, 220), (cx+6, cy-21, 7, 7))
            pygame.draw.ellipse(self.screen, BLACK, (cx-8, cy-19, 3, 3))
            pygame.draw.ellipse(self.screen, BLACK, (cx+9, cy-19, 3, 3))
            pygame.draw.arc(self.screen, (60, 60, 60), (cx-7, cy-10, 14, 8), 0, 3.14, 2)
        elif pid == 3:
            pygame.draw.ellipse(self.screen, color, (cx-28, cy-3, 56, 50))
            pygame.draw.ellipse(self.screen, (120, 200, 130), (cx-28, cy-3, 56, 50), 4)
            pygame.draw.ellipse(self.screen, color, (cx-24, cy-35, 48, 40))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cx-22, cy-46, 44, 22))
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy-52), 8)
            pygame.draw.ellipse(self.screen, WHITE, (cx-13, cy-22, 11, 10))
            pygame.draw.ellipse(self.screen, WHITE, (cx+2, cy-22, 11, 10))
            pygame.draw.ellipse(self.screen, (60, 100, 200), (cx-10, cy-19, 5, 5))
            pygame.draw.ellipse(self.screen, (60, 100, 200), (cx+5, cy-19, 5, 5))
            pygame.draw.ellipse(self.screen, BLACK, (cx-8, cy-17, 3, 3))
            pygame.draw.ellipse(self.screen, BLACK, (cx+7, cy-17, 3, 3))
            pygame.draw.arc(self.screen, (60, 60, 60), (cx-5, cy-8, 10, 6), 0, 3.14, 2)
        elif pid == 4:
            pygame.draw.ellipse(self.screen, color, (cx-28, cy-3, 56, 48))
            pygame.draw.ellipse(self.screen, (220, 180, 130), (cx-28, cy-3, 56, 48), 4)
            pygame.draw.ellipse(self.screen, color, (cx-26, cy-35, 52, 40))
            pygame.draw.ellipse(self.screen, (255, 180, 200), (cx-24, cy-42, 48, 13))
            pygame.draw.circle(self.screen, (255, 130, 170), (cx-10, cy-38), 5)
            pygame.draw.circle(self.screen, (255, 130, 170), (cx+10, cy-38), 5)
            pygame.draw.ellipse(self.screen, WHITE, (cx-14, cy-22, 12, 11))
            pygame.draw.ellipse(self.screen, WHITE, (cx+2, cy-22, 12, 11))
            pygame.draw.ellipse(self.screen, (80, 110, 200), (cx-10, cy-19, 6, 6))
            pygame.draw.ellipse(self.screen, (80, 110, 200), (cx+6, cy-19, 6, 6))
            pygame.draw.ellipse(self.screen, BLACK, (cx-7, cy-17, 3, 3))
            pygame.draw.ellipse(self.screen, BLACK, (cx+9, cy-17, 3, 3))
            pygame.draw.arc(self.screen, (60, 60, 60), (cx-6, cy-8, 12, 7), 0, 3.14, 2)
        elif pid == 5:
            pygame.draw.ellipse(self.screen, color, (cx-28, cy-3, 56, 48))
            pygame.draw.ellipse(self.screen, (160, 120, 200), (cx-28, cy-3, 56, 48), 4)
            pygame.draw.ellipse(self.screen, color, (cx-26, cy-35, 52, 40))
            pygame.draw.ellipse(self.screen, (180, 200, 255), (cx-22, cy-42, 44, 13))
            pygame.draw.polygon(self.screen, (255, 215, 80), [(cx-9, cy-40), (cx-6, cy-46), (cx-3, cy-40)])
            pygame.draw.polygon(self.screen, (255, 215, 80), [(cx+9, cy-40), (cx+6, cy-46), (cx+3, cy-40)])
            pygame.draw.ellipse(self.screen, color, (cx-24, cy-40, 13, 13))
            pygame.draw.ellipse(self.screen, color, (cx+11, cy-40, 13, 13))
            pygame.draw.ellipse(self.screen, WHITE, (cx-14, cy-22, 12, 11))
            pygame.draw.ellipse(self.screen, WHITE, (cx+2, cy-22, 12, 11))
            pygame.draw.ellipse(self.screen, (90, 130, 255), (cx-10, cy-19, 6, 6))
            pygame.draw.ellipse(self.screen, (90, 130, 255), (cx+6, cy-19, 6, 6))
            pygame.draw.ellipse(self.screen, BLACK, (cx-7, cy-17, 3, 3))
            pygame.draw.ellipse(self.screen, BLACK, (cx+9, cy-17, 3, 3))
            pygame.draw.arc(self.screen, (60, 60, 60), (cx-6, cy-8, 12, 7), 0, 3.14, 2)

    def draw_mood(self):
        needs = self.game_state.pet.needs
        avg = (needs.hunger + needs.happiness + needs.energy + needs.cleanliness) / 4
        if avg > 70: mood, col = "Happy :)", (60, 200, 80)
        elif avg > 40: mood, col = "Okay", (220, 180, 40)
        else: mood, col = "Sad :(", (230, 100, 100)
        txt = self.font.render(mood, True, col)
        self.screen.blit(txt, (300, 60))

    def draw_status(self):
        txt = self.small_font.render(self.status, True, BLACK)
        self.screen.blit(txt, (15, 375))

    def draw_buttons(self):
        data = [
            (self.btn_feed, "Feed (F)", ORANGE),
            (self.btn_play, "Play (P)", GREEN),
            (self.btn_clean, "Clean (C)", BLUE),
            (self.btn_rest, "Rest (R)", PURPLE),
        ]
        for rect, text, color in data:
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            if self.anim_state:
                pygame.draw.rect(self.screen, (90, 90, 90), rect, width=3, border_radius=8)
            self.screen.blit(self.small_font.render(text, True, WHITE), (rect.x + 8, rect.y + 8))
        pygame.draw.rect(self.screen, (100, 149, 237), self.btn_map, border_radius=8)
        self.screen.blit(self.small_font.render("MAP (M)", True, WHITE), (self.btn_map.x + 10, self.btn_map.y + 8))

    def draw_shop_ui(self):
        if self.map_mode or self.state != "main":
            return
        if self.game_state.pet.location == "sweeties_candy_shop":
            btn1 = pygame.Rect(450, 280, 160, 45)
            pygame.draw.rect(self.screen, (255, 200, 210), btn1, border_radius=8)
            pygame.draw.rect(self.screen, CANDY_RED, btn1, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Buy Lollipop (10)", True, CANDY_RED), (460, 292))

            btn2 = pygame.Rect(450, 335, 160, 45)
            pygame.draw.rect(self.screen, (255, 200, 210), btn2, border_radius=8)
            pygame.draw.rect(self.screen, CANDY_RED, btn2, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Buy Candy Apple (25)", True, CANDY_RED), (460, 347))

        elif self.game_state.pet.location == "gens_garden":
            btn1 = pygame.Rect(450, 280, 160, 45)
            pygame.draw.rect(self.screen, (200, 230, 255), btn1, border_radius=8)
            pygame.draw.rect(self.screen, GARDEN_BLUE, btn1, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Buy Flower Seeds (12)", True, GARDEN_BLUE), (460, 292))

            btn2 = pygame.Rect(450, 335, 160, 45)
            pygame.draw.rect(self.screen, (200, 230, 255), btn2, border_radius=8)
            pygame.draw.rect(self.screen, GARDEN_BLUE, btn2, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Buy Sunflower Seeds (20)", True, GARDEN_BLUE), (460, 347))

    def draw_backyard_plant_ui(self):
        if self.game_state.pet.location != "backyard" or self.map_mode:
            return

        inv = self.game_state.pet.inventory

        # Moved high up, directly under the status bar
        if inv.get("flower_seeds", 0) > 0:
            btn = pygame.Rect(30, 70, 180, 40)
            pygame.draw.rect(self.screen, (180, 230, 180), btn, border_radius=8)
            pygame.draw.rect(self.screen, (40, 140, 60), btn, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Plant Flower Seeds", True, (30, 100, 50)), (40, 80))

        if inv.get("sunflower_seeds", 0) > 0:
            btn = pygame.Rect(30, 120, 180, 40)
            pygame.draw.rect(self.screen, (180, 230, 180), btn, border_radius=8)
            pygame.draw.rect(self.screen, (40, 140, 60), btn, width=2, border_radius=8)
            self.screen.blit(self.small_font.render("Plant Sunflower Seeds", True, (30, 100, 50)), (40, 130))

    def draw_arcade_games(self):
        if self.game_state.pet.location != "arcade" or self.map_mode or self.state != "main":
            return
        panel = pygame.Rect(450, 260, 170, 85)
        pygame.draw.rect(self.screen, (40, 45, 70), panel, border_radius=10)
        pygame.draw.rect(self.screen, (100, 149, 237), panel, width=2, border_radius=10)
        self.screen.blit(self.small_font.render("ARCADE GAMES", True, (255, 220, 100)), (460, 268))

        snake_btn = pygame.Rect(460, 295, 70, 40)
        pygame.draw.rect(self.screen, (80, 200, 120), snake_btn, border_radius=6)
        self.screen.blit(self.tiny_font.render("Snake", True, WHITE), (475, 305))

        dash_btn = pygame.Rect(540, 295, 70, 40)
        pygame.draw.rect(self.screen, (255, 160, 80), dash_btn, border_radius=6)
        self.screen.blit(self.tiny_font.render("Pet Dash", True, WHITE), (548, 305))

    def draw_anim_effect(self):
        if not self.anim_state:
            return

        etype = self.anim_state["type"]
        elapsed = time.time() - self.anim_state["start"]
        cx, cy = 340, 210

        if etype == "feed":
            # Check if we're in the candy shop for special candy animation
            if self.game_state.pet.location == "sweeties_candy_shop":
                # Candy-themed eating animation
                candy_x = cx + 90 - int(elapsed * 120)   # Candy moves left toward pet

                # Draw lollipop/candy
                pygame.draw.circle(self.screen, (255, 80, 150), (candy_x, cy + 10), 12)
                pygame.draw.line(self.screen, (200, 200, 200), (candy_x, cy + 22), (candy_x, cy + 45), 3)

                # Sparkles
                if int(elapsed * 10) % 2 == 0:
                    pygame.draw.circle(self.screen, (255, 255, 200), (candy_x - 8, cy - 5), 3)
                    pygame.draw.circle(self.screen, (255, 255, 200), (candy_x + 6, cy + 18), 2)

                # Pet mouth opens slightly while eating
                if elapsed < 0.6:
                    pygame.draw.arc(self.screen, (80, 40, 40), (cx - 8, cy + 5, 16, 10), 0, 3.14, 2)
                else:
                    pygame.draw.arc(self.screen, (80, 40, 40), (cx - 8, cy + 5, 16, 8), 0, 3.14, 2)

            else:
                # Normal feed animation (other locations)
                pygame.draw.ellipse(self.screen, (139, 69, 19), (cx + 70, cy + 15, 50, 25))

        elif etype == "play":
            bx = cx + 80 + int(30 * ((elapsed % 0.6) - 0.3))
            pygame.draw.circle(self.screen, (255, 99, 71), (bx, cy + 30), 12)

        elif etype == "clean":
            for i in range(3):
                by = cy - 20 - int((elapsed * 50 + i * 15) % 50)
                pygame.draw.circle(self.screen, (135, 206, 250), (cx + 60 + i * 20, by), 7, 2)

        elif etype == "rest":
            for ox, oy in [(40, -30), (55, -42)]:
                self.screen.blit(self.font.render("Z", True, PURPLE), (cx + ox, cy + oy))

        elif etype == "plant":
            for i in range(3):
                pygame.draw.circle(self.screen, (60, 160, 60), (cx + 60 + i * 15, cy - 10 - i * 8), 5)

    def draw(self):
        if self.state == "snake" and self.snake_game:
            self.screen.fill(DARK)
            if hasattr(self.snake_game, 'draw'):
                self.snake_game.draw(self.screen)
            return

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
        self.screen.fill(bg)

        self.draw_top_stats_bar()
        self.draw_environment(loc)
        self.draw_pet()
        self.draw_mood()
        self.draw_status()
        self.draw_buttons()

        self.draw_shop_ui()
        self.draw_backyard_plant_ui()
        self.draw_harvest_button()
        self.draw_decorate_button()
        self.draw_arcade_games()

        if self.map_mode:
            self.draw_map()
        if self.anim_state:
            self.draw_anim_effect()

        hint = self.tiny_font.render("F/P/C/R • M=Map • Q=Quit", True, (100, 100, 100))
        self.screen.blit(hint, (15, 455))

    def draw_map(self):
        overlay = pygame.Surface((640, 300), pygame.SRCALPHA)
        overlay.fill((250, 248, 240, 235))
        self.screen.blit(overlay, (0, 60))
        self.screen.blit(self.font.render("Neighborhood Map — Click a location", True, BLACK), (25, 70))
        pygame.draw.line(self.screen, (180, 160, 140), (120, 180), (520, 180), 3)
        pygame.draw.line(self.screen, (180, 160, 140), (200, 180), (200, 260), 2)
        pygame.draw.line(self.screen, (180, 160, 140), (420, 180), (420, 260), 2)

        positions = [
            (60, 110, "home"), (200, 110, "backyard"), (340, 110, "park"),
            (60, 230, "sweeties_candy_shop"), (200, 230, "gens_garden"), (340, 230, "arcade")
        ]
        for px, py, key in positions:
            data = self.game_state.LOCATIONS[key]
            self.draw_location_badge(px, py, key, data["name"], data["color"], data["icon"])

    def draw_location_badge(self, x, y, key, name, color, icon_key):
        rect = pygame.Rect(x, y, 130, 95)
        is_current = (key == self.game_state.pet.location)
        pygame.draw.rect(self.screen, (0, 0, 0, 40), (x+3, y+3, 130, 95), border_radius=12)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=12)
        border_w = 5 if is_current else 3
        pygame.draw.rect(self.screen, color, rect, width=border_w, border_radius=12)
        self.draw_location_icon(x + 8, y + 8, icon_key, size=52)
        name_surf = self.small_font.render(name, True, color)
        self.screen.blit(name_surf, (x + 8, y + 68))

    def draw_location_icon(self, x, y, icon_key, size=48):
        cx, cy = x + size // 2, y + size // 2
        if icon_key == "home":
            pygame.draw.rect(self.screen, (180, 100, 70), (x+6, cy-2, size-12, size-14), border_radius=3)
            pygame.draw.polygon(self.screen, (139, 69, 19), [(x, cy-2), (cx, y+4), (x+size, cy-2)])
            pygame.draw.rect(self.screen, (80, 50, 30), (cx-5, cy+8, 10, 14))
            pygame.draw.rect(self.screen, (255, 220, 100), (x+12, cy-8, 8, 8))
        elif icon_key == "park":
            pygame.draw.rect(self.screen, (101, 67, 33), (cx-4, cy+2, 8, 18))
            pygame.draw.circle(self.screen, (34, 139, 34), (cx, cy-6), 16)
            pygame.draw.circle(self.screen, (46, 160, 50), (cx-8, cy-2), 11)
            pygame.draw.circle(self.screen, (46, 160, 50), (cx+9, cy-1), 10)
        elif icon_key == "arcade":
            pygame.draw.rect(self.screen, (60, 60, 80), (x+8, y+6, size-16, size-12), border_radius=4)
            pygame.draw.rect(self.screen, (255, 200, 50), (x+12, y+10, size-24, 12))
            pygame.draw.circle(self.screen, (255, 80, 80), (cx-6, cy+8), 4)
            pygame.draw.circle(self.screen, (80, 200, 120), (cx+6, cy+8), 4)
        elif icon_key == "backyard":
            pygame.draw.rect(self.screen, (139, 115, 85), (x+4, cy+2, size-8, 18), border_radius=2)
            for i in range(3):
                pygame.draw.rect(self.screen, (60, 120, 50), (x+10 + i*12, cy-4, 8, 10))
            for fx in (x+6, x+size-10):
                pygame.draw.rect(self.screen, (120, 90, 60), (fx, y+8, 4, size-14))
        elif icon_key == "candy_shop":
            pygame.draw.rect(self.screen, CANDY_RED, (x+6, cy-4, size-12, size-16), border_radius=3)
            pygame.draw.polygon(self.screen, WAFFLE, [(x+2, cy-4), (cx, y+2), (x+size-2, cy-4)])
            for i in range(3):
                pygame.draw.line(self.screen, (180, 150, 100), (x+8+i*8, cy-12), (x+10+i*7, cy-4), 2)
            pygame.draw.circle(self.screen, (255, 80, 150), (x+12, cy+12), 6)
            pygame.draw.line(self.screen, (200, 200, 200), (x+12, cy+18), (x+12, cy+26), 2)
            pygame.draw.circle(self.screen, (80, 200, 255), (x+size-12, cy+10), 5)
            pygame.draw.line(self.screen, (200, 200, 200), (x+size-12, cy+15), (x+size-12, cy+22), 2)
        elif icon_key == "gens_garden":
            pygame.draw.rect(self.screen, GARDEN_BLUE, (x+6, cy-2, size-12, size-14), border_radius=3)
            pygame.draw.rect(self.screen, (139, 90, 60), (x+8, cy+10, size-16, 10))
            for fx, col in [(x+14, (255, 180, 200)), (cx, (255, 220, 80)), (x+size-14, (180, 220, 255))]:
                pygame.draw.circle(self.screen, col, (fx, cy+6), 5)
                pygame.draw.circle(self.screen, (60, 160, 60), (fx, cy+6), 3)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    selection = PetSelectionScreen(screen)
    pet_config = selection.run()
    game = OurWorldPygame(pet_config)
    game.run()