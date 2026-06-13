#!/usr/bin/env python3
"""
OurWorld Pygame - Complete Version with Custom Pets
"""

import pygame
import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.game_state import GameState

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

PET_ROSTER = [
    {"id": 0, "name": "Bubbles", "color": (255, 182, 193), "style": "round"},
    {"id": 1, "name": "Milo",    "color": (255, 200, 150), "style": "cat"},
    {"id": 2, "name": "Luna",    "color": (180, 220, 255), "style": "round"},
    {"id": 3, "name": "Sprout",  "color": (200, 255, 180), "style": "plant"},
    {"id": 4, "name": "Pip",     "color": (255, 220, 150), "style": "round"},
    {"id": 5, "name": "Nova",    "color": (220, 180, 255), "style": "star"},
]

# ==================== DRAW FUNCTIONS ====================

def draw_pet_preview(screen, x, y, pet_data, is_selected=False, bob=0):
    color = pet_data["color"]
    name = pet_data["name"]
    offset_y = int(5 * abs(3.14159 - bob) / 3.14159) if is_selected else 0
    cy = y + offset_y

    if pet_data["id"] == 0:  # Bubbles
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

    elif pet_data["id"] == 1:  # Milo
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

    elif pet_data["id"] == 2:  # Luna
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

    elif pet_data["id"] == 3:  # Sprout
        pygame.draw.ellipse(screen, color, (x-26, cy-5, 52, 50))
        pygame.draw.ellipse(screen, (120, 200, 130), (x-26, cy-5, 52, 50), 4)
        pygame.draw.ellipse(screen, color, (x-22, cy-32, 44, 36))
        pygame.draw.ellipse(screen, (255, 255, 255), (x-20, cy-42, 40, 18))
        pygame.draw.circle(screen, (255, 255, 255), (x, cy-48), 8)
        pygame.draw.ellipse(screen, WHITE, (x-11, cy-20, 10, 9))
        pygame.draw.ellipse(screen, WHITE, (x+1, cy-20, 10, 9))
        pygame.draw.ellipse(screen, (60, 100, 200), (x-8, cy-17, 5, 5))
        pygame.draw.ellipse(screen, (60, 100, 200), (x+4, cy-17, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-5, cy-15, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+7, cy-15, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-5, cy-7, 10, 6), 0, 3.14, 2)

    elif pet_data["id"] == 4:  # Pip
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
        pygame.draw.ellipse(screen, BLACK, (x-6, cy-15, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-15, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-5, cy-7, 10, 6), 0, 3.14, 2)

    elif pet_data["id"] == 5:  # Nova
        pygame.draw.ellipse(screen, color, (x-26, cy-5, 52, 48))
        pygame.draw.ellipse(screen, (160, 120, 200), (x-26, cy-5, 52, 48), 4)
        pygame.draw.ellipse(screen, color, (x-24, cy-32, 48, 36))
        pygame.draw.ellipse(screen, (180, 200, 255), (x-20, cy-40, 40, 12))
        pygame.draw.polygon(screen, (255, 215, 80), [(x-8, cy-38), (x-5, cy-45), (x-2, cy-38)])
        pygame.draw.polygon(screen, (255, 215, 80), [(x+8, cy-38), (x+5, cy-45), (x+2, cy-38)])
        pygame.draw.ellipse(screen, color, (x-22, cy-38, 12, 12))
        pygame.draw.ellipse(screen, color, (x+10, cy-38, 12, 12))
        pygame.draw.ellipse(screen, WHITE, (x-13, cy-20, 11, 10))
        pygame.draw.ellipse(screen, WHITE, (x+2, cy-20, 11, 10))
        pygame.draw.ellipse(screen, (90, 130, 255), (x-9, cy-17, 5, 5))
        pygame.draw.ellipse(screen, (90, 130, 255), (x+6, cy-17, 5, 5))
        pygame.draw.ellipse(screen, BLACK, (x-6, cy-15, 3, 3))
        pygame.draw.ellipse(screen, BLACK, (x+9, cy-15, 3, 3))
        pygame.draw.arc(screen, (60, 60, 60), (x-5, cy-7, 10, 6), 0, 3.14, 2)

    name_surf = pygame.font.SysFont("Arial", 13).render(name, True, BLACK)
    screen.blit(name_surf, (x - name_surf.get_width()//2, cy + 42))

    if is_selected:
        pygame.draw.rect(screen, (255, 215, 0), (x-45, cy-55, 90, 105), width=4, border_radius=12)


# ==================== MAIN CLASSES ====================

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
        self.pet_style = pet_config.get("style", "round")

        self.pet_bob = 0
        self.status = f"Take good care of {self.game_state.pet.name}!"
        self.map_mode = False
        self.selected_loc = None
        self.anim_state = None
        self.last_tick = pygame.time.get_ticks()
        self.state = "main"
        self.snake = None

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
            elif self.state == "snake" and self.snake:
                self.snake.update(dt)
                if self.snake.game_over:
                    bonus = self.snake.score // 5
                    if bonus > 0:
                        self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
                        self.status = f"Snake bonus! +{bonus} Happiness"
                    self.state = "main"
                    self.snake = None

            self.draw()
            pygame.display.flip()

        self.game_state.save()
        pygame.quit()
        sys.exit()

    def handle_key(self, key):
        if self.state == "snake" and self.snake:
            self.snake.handle_key(key)
            return

        if key in (pygame.K_q, pygame.K_ESCAPE):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_f: self.start_action("feed")
        elif key == pygame.K_p: self.start_action("play")
        elif key == pygame.K_c: self.start_action("clean")
        elif key == pygame.K_r: self.start_action("rest")
        elif key == pygame.K_m: self.map_mode = not self.map_mode
        elif key == pygame.K_s and self.game_state.pet.location == "arcade":
            self.start_snake()
        elif key == pygame.K_1: self.change_location("home")
        elif key == pygame.K_2: self.change_location("park")
        elif key == pygame.K_3: self.change_location("arcade")

    def handle_click(self, pos):
        if self.map_mode:
            if pygame.Rect(50, 110, 160, 120).collidepoint(pos):
                self.change_location("home"); self.map_mode = False
            elif pygame.Rect(230, 110, 160, 120).collidepoint(pos):
                self.change_location("park"); self.map_mode = False
            elif pygame.Rect(410, 110, 160, 120).collidepoint(pos):
                self.change_location("arcade"); self.map_mode = False
            return

        if self.btn_feed.collidepoint(pos):   self.start_action("feed")
        elif self.btn_play.collidepoint(pos): self.start_action("play")
        elif self.btn_clean.collidepoint(pos): self.start_action("clean")
        elif self.btn_rest.collidepoint(pos): self.start_action("rest")
        elif self.btn_map.collidepoint(pos):  self.map_mode = not self.map_mode

    def start_action(self, action):
        if self.anim_state or self.map_mode: return
        self.anim_state = {"type": action, "start": time.time()}
        self.status = f"{action.capitalize()}ing..."

    def update_animation(self):
        if not self.anim_state: return
        if time.time() - self.anim_state["start"] > 0.85:
            action = self.anim_state["type"]
            result = self.game_state.perform_care_action(action)
            if result.get("success"):
                self.status = result.get("bonus", f"{self.game_state.pet.name} loved that!")
            self.anim_state = None

    def change_location(self, loc):
        if loc != self.game_state.pet.location:
            self.game_state.change_location(loc)
            info = self.game_state.get_current_location_info()
            self.status = f"Moved to {info['name']}. {info['desc']}"
        self.map_mode = False

    def start_snake(self):
        self.state = "snake"
        self.snake = SimpleSnake()
        self.status = "Snake time! Arrows move • ESC to return"

    def draw_top_stats_bar(self):
        bar_height = 52
        section_width = WIDTH // 4
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

    def draw_environment(self, loc):
        if loc == "home":
            pygame.draw.rect(self.screen, (200, 170, 130), (0, 260, 640, 220))
            pygame.draw.rect(self.screen, (135, 206, 250), (480, 80, 100, 80), width=5)
            pygame.draw.line(self.screen, (139, 69, 19), (530, 80), (530, 160), 4)
            pygame.draw.rect(self.screen, (180, 100, 80), (60, 250, 180, 55))
        elif loc == "park":
            pygame.draw.rect(self.screen, (120, 180, 120), (0, 260, 640, 220))
            for tx in (80, 520):
                pygame.draw.rect(self.screen, (139, 69, 19), (tx-8, 200, 16, 55))
                pygame.draw.circle(self.screen, (34, 160, 50), (tx, 175), 38)
        else:
            pygame.draw.rect(self.screen, (60, 55, 80), (0, 260, 640, 220))
            for x in (70, 480):
                pygame.draw.rect(self.screen, (50, 50, 60), (x, 150, 85, 120), border_radius=6)
                pygame.draw.rect(self.screen, (0, 220, 80), (x+12, 165, 60, 35))
                pygame.draw.circle(self.screen, (255, 50, 50), (x+25, 215), 7)
                pygame.draw.circle(self.screen, (255, 220, 50), (x+55, 215), 7)

    def draw_pet(self):
        cx, cy = 340, 210 + int(5 * abs(3.14159 - self.pet_bob) / 3.14159)
        color = self.pet_color
        pid = self.pet_id

        if pid == 0:      # Bubbles
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

        elif pid == 1:    # Milo
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

        elif pid == 2:    # Luna
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

        elif pid == 3:    # Sprout
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

        elif pid == 4:    # Pip
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

        elif pid == 5:    # Nova
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

    def draw_map(self):
        overlay = pygame.Surface((640, 260), pygame.SRCALPHA)
        overlay.fill((245, 245, 245, 240))
        self.screen.blit(overlay, (0, 75))
        self.screen.blit(self.font.render("Map - Click location", True, BLACK), (25, 85))

        self.draw_location_card(50, 115, "home", "Home", (139, 69, 19))
        self.draw_location_card(230, 115, "park", "Park", GREEN)
        self.draw_location_card(410, 115, "arcade", "Arcade", (65, 105, 225))

    def draw_location_card(self, x, y, key, name, color):
        rect = pygame.Rect(x, y, 160, 115)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, width=3, border_radius=10)
        self.screen.blit(self.font.render(name, True, color), (x+30, y+75))

    def draw_anim_effect(self):
        if not self.anim_state: return
        etype = self.anim_state["type"]
        elapsed = time.time() - self.anim_state["start"]
        cx, cy = 340, 210

        if etype == "feed":
            pygame.draw.ellipse(self.screen, (139, 69, 19), (cx+70, cy+15, 50, 25))
            if elapsed < 0.5:
                pygame.draw.circle(self.screen, (200, 50, 50), (cx+95, cy), 8)
        elif etype == "play":
            bx = cx + 80 + int(30 * ((elapsed % 0.6) - 0.3))
            pygame.draw.circle(self.screen, (255, 99, 71), (bx, cy+30), 12)
        elif etype == "clean":
            for i in range(3):
                by = cy - 20 - int((elapsed * 50 + i*15) % 50)
                pygame.draw.circle(self.screen, (135, 206, 250), (cx+60 + i*20, by), 7, 2)
        elif etype == "rest":
            for ox, oy in [(40, -30), (55, -42)]:
                self.screen.blit(self.font.render("Z", True, PURPLE), (cx+ox, cy+oy))

    def draw(self):
        if self.state == "snake" and self.snake:
            self.screen.fill(DARK)
            self.snake.draw(self.screen)
            return

        loc = self.game_state.pet.location
        if loc == "home":
            bg = (245, 235, 220)
        elif loc == "park":
            bg = (200, 230, 200)
        else:
            bg = (210, 200, 230)
        self.screen.fill(bg)

        self.draw_top_stats_bar()
        self.draw_environment(loc)
        self.draw_pet()
        self.draw_mood()
        self.draw_status()
        self.draw_buttons()

        if self.map_mode:
            self.draw_map()

        if self.anim_state:
            self.draw_anim_effect()

        hint = self.tiny_font.render("F/P/C/R • M=Map • S=Snake • Q=Quit", True, (100,100,100))
        self.screen.blit(hint, (15, 455))


class SimpleSnake:
    def __init__(self):
        self.w = 400
        self.h = 400
        self.cell = 20
        self.cols = self.w // self.cell
        self.rows = self.h // self.cell
        self.reset()

    def reset(self):
        self.snake = [(self.cols//2, self.rows//2)]
        self.dir = (1, 0)
        self.apple = self.place_apple()
        self.score = 0
        self.game_over = False
        self.last_move = pygame.time.get_ticks()

    def place_apple(self):
        while True:
            p = (random.randint(0, self.cols-1), random.randint(0, self.rows-1))
            if p not in self.snake: return p

    def update(self, dt):
        if self.game_over: return
        if pygame.time.get_ticks() - self.last_move > 130:
            self.last_move = pygame.time.get_ticks()
            self.move()

    def move(self):
        head = self.snake[0]
        new = (head[0] + self.dir[0], head[1] + self.dir[1])
        if not (0 <= new[0] < self.cols and 0 <= new[1] < self.rows) or new in self.snake:
            self.game_over = True
            return
        self.snake.insert(0, new)
        if new == self.apple:
            self.score += 10
            self.apple = self.place_apple()
        else:
            self.snake.pop()

    def handle_key(self, key):
        if self.game_over:
            if key == pygame.K_r: self.reset()
            elif key in (pygame.K_ESCAPE, pygame.K_q): self.game_over = True
            return
        if key in (pygame.K_UP, pygame.K_w) and self.dir != (0, 1): self.dir = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s) and self.dir != (0, -1): self.dir = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a) and self.dir != (1, 0): self.dir = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.dir != (-1, 0): self.dir = (1, 0)
        elif key in (pygame.K_ESCAPE, pygame.K_q): self.game_over = True

    def draw(self, screen):
        ox, oy = 120, 40
        pygame.draw.rect(screen, (25, 25, 35), (ox-8, oy-8, self.w+16, self.h+16), border_radius=8)
        pygame.draw.rect(screen, BLACK, (ox, oy, self.w, self.h))

        ax, ay = self.apple
        pygame.draw.ellipse(screen, RED, (ox + ax*self.cell + 2, oy + ay*self.cell + 2, self.cell-4, self.cell-4))

        for i, (x, y) in enumerate(self.snake):
            color = (80, 255, 80) if i == 0 else (40, 180, 40)
            pygame.draw.rect(screen, color, (ox + x*self.cell, oy + y*self.cell, self.cell-2, self.cell-2), border_radius=3)

        txt = pygame.font.SysFont("Arial", 18).render(f"Score: {self.score}", True, YELLOW)
        screen.blit(txt, (ox, oy + self.h + 8))
        if self.game_over:
            over = pygame.font.SysFont("Arial", 16).render("GAME OVER — R to restart or ESC to return", True, RED)
            screen.blit(over, (ox - 5, oy + self.h + 32))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    selection = PetSelectionScreen(screen)
    pet_config = selection.run()

    game = OurWorldPygame(pet_config)
    game.run()