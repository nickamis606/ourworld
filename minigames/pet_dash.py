#!/usr/bin/env python3
"""
OurWorld Arcade - Pet Dash (Improved Endless Runner)
Better visuals + noticeably progressive difficulty.
"""

import pygame
import random
from dataclasses import dataclass

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
GRAVITY = 0.7
JUMP_STRENGTH = -14
DOUBLE_JUMP_STRENGTH = -11
GROUND_Y = 350

# Colors
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (100, 180, 255)
FAR_HILLS = (70, 140, 90)
NEAR_HILLS = (50, 120, 70)
GROUND = (139, 119, 101)
OBSTACLE = (101, 67, 33)
TREAT = (255, 200, 50)


@dataclass
class MinigameResult:
    score: int
    completed: bool
    message: str = ""


class MinigameBase:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.score = 0
        self.font = pygame.font.SysFont("arial", 26)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)

    def handle_key(self, key): pass
    def update(self, dt): pass
    def draw(self, screen=None): pass

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return MinigameResult(self.score, False, "quit")
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_key(pygame.K_SPACE)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        return MinigameResult(self.score, True)


class PetDash(MinigameBase):
    def __init__(self, screen, clock, pet_color=None):
        super().__init__(screen, clock)
        self.pet_color = pet_color or (80, 200, 120)
        self.reset_game()

    def reset_game(self):
        self.pet_x = 130
        self.pet_y = GROUND_Y
        self.pet_vel_y = 0
        self.pet_width = 36
        self.pet_height = 42
        self.jumps = 0
        self.max_jumps = 2

        self.obstacles = []
        self.treats = []
        self.last_obstacle = SCREEN_WIDTH
        self.last_treat = SCREEN_WIDTH

        self.score = 0
        self.distance = 0
        self.game_over = False
        self.running = True
        self.show_instructions = True
        self.instruction_timer = 0

        self.base_speed = 5.0
        self.speed = self.base_speed
        self.next_difficulty = 12          # start ramping earlier

        self.anim_frame = 0
        self.bg_offset = 0

    def spawn_obstacle(self):
        w = random.randint(24, 40)
        h = random.randint(30, 55)
        is_high = random.random() < 0.3
        y = GROUND_Y - h if not is_high else GROUND_Y - h - 65
        x = self.last_obstacle + random.randint(160, 240)
        self.obstacles.append({"x": x, "y": y, "w": w, "h": h})
        self.last_obstacle = x

    def spawn_treat(self):
        x = self.last_treat + random.randint(110, 190)
        y = random.randint(GROUND_Y - 160, GROUND_Y - 70)
        self.treats.append({"x": x, "y": y})
        self.last_treat = x

    def handle_key(self, key):
        if self.game_over:
            if key == pygame.K_r: self.reset_game()
            elif key in (pygame.K_q, pygame.K_ESCAPE): self.running = False
            return

        if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if self.jumps < self.max_jumps:
                self.pet_vel_y = DOUBLE_JUMP_STRENGTH if self.jumps == 1 else JUMP_STRENGTH
                self.jumps += 1
                self.show_instructions = False

        if key == pygame.K_ESCAPE:
            self.running = False

    def update(self, dt):
        if self.game_over or not self.running:
            return

        self.instruction_timer += dt
        if self.instruction_timer > 2.5:
            self.show_instructions = False

        # Physics
        self.pet_vel_y += GRAVITY
        self.pet_y += self.pet_vel_y
        self.anim_frame += 0.25

        if self.pet_y >= GROUND_Y:
            self.pet_y = GROUND_Y
            self.pet_vel_y = 0
            self.jumps = 0

        # Spawn (more frequent as speed increases)
        spawn_gap = max(140, 220 - int(self.speed * 8))
        if not self.obstacles or self.obstacles[-1]["x"] < SCREEN_WIDTH - spawn_gap:
            self.spawn_obstacle()
        if not self.treats or self.treats[-1]["x"] < SCREEN_WIDTH - 100:
            self.spawn_treat()

        # Move world
        move_speed = self.speed
        for o in self.obstacles:
            o["x"] -= move_speed
        for t in self.treats:
            t["x"] -= move_speed * 0.95

        self.obstacles = [o for o in self.obstacles if o["x"] + o["w"] > -10]
        self.treats = [t for t in self.treats if t["x"] > -20]

        # Background scroll (parallax feel)
        self.bg_offset = (self.bg_offset + move_speed * 0.6) % SCREEN_WIDTH

        # Collisions
        pet_rect = pygame.Rect(self.pet_x, self.pet_y - self.pet_height, self.pet_width, self.pet_height)

        for o in self.obstacles:
            if pet_rect.colliderect(pygame.Rect(o["x"], o["y"], o["w"], o["h"])):
                self.game_over = True
                self.running = False
                return

        # Collect treats
        for t in self.treats[:]:
            if pet_rect.colliderect(pygame.Rect(t["x"]-10, t["y"]-10, 24, 24)):
                self.treats.remove(t)
                self.score += 20

        # Scoring & difficulty
        self.distance += move_speed * 0.8
        self.score = int(self.distance / 7) + len([t for t in self.treats if t["x"] < 0]) * 8

        # More aggressive difficulty ramp
        if self.score >= self.next_difficulty:
            self.speed = min(9.0, self.speed + 0.45)   # bigger speed jumps
            self.next_difficulty += 12                   # more frequent increases

    def draw(self, screen=None):
        target = screen or self.screen

        # Sky gradient
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(SKY_TOP[0] * (1-ratio) + SKY_BOTTOM[0] * ratio)
            g = int(SKY_TOP[1] * (1-ratio) + SKY_BOTTOM[1] * ratio)
            b = int(SKY_TOP[2] * (1-ratio) + SKY_BOTTOM[2] * ratio)
            pygame.draw.line(target, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        # Parallax hills
        offset = int(self.bg_offset)
        pygame.draw.ellipse(target, FAR_HILLS, (-offset*0.4, GROUND_Y-120, SCREEN_WIDTH*1.5, 200))
        pygame.draw.ellipse(target, NEAR_HILLS, (-offset*0.7 + 80, GROUND_Y-80, SCREEN_WIDTH*1.5, 160))

        # Ground
        pygame.draw.rect(target, GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # Pet with animation
        px = self.pet_x
        py = int(self.pet_y)
        bob = 0 if self.pet_y >= GROUND_Y else int(3 * abs((self.anim_frame) % 2 - 1))

        # Body
        pygame.draw.ellipse(target, self.pet_color, (px + 2, py - self.pet_height + bob + 4, self.pet_width - 6, self.pet_height - 10))
        # Head
        pygame.draw.ellipse(target, self.pet_color, (px + 22, py - self.pet_height - 6 + bob, 24, 20))
        # Ear
        pygame.draw.polygon(target, self.pet_color, [(px + 32, py - self.pet_height - 8 + bob), (px + 36, py - self.pet_height - 18 + bob), (px + 44, py - self.pet_height - 6 + bob)])

        # Legs
        phase = int(self.anim_frame * 4) % 4
        ly = 8 if phase in (0, 2) else 2
        pygame.draw.rect(target, (40, 40, 40), (px + 8, py - 10 + ly, 6, 14))
        pygame.draw.rect(target, (40, 40, 40), (px + 22, py - 10 - ly, 6, 14))

        # Tail
        tail = int(4 * ((self.anim_frame * 3) % 2 - 1))
        pygame.draw.line(target, self.pet_color, (px + 6, py - 16), (px - 8, py - 20 + tail), 7)

        # Obstacles
        for o in self.obstacles:
            pygame.draw.rect(target, OBSTACLE, (o["x"], o["y"], o["w"], o["h"]), border_radius=5)

        # Treats
        for t in self.treats:
            pygame.draw.circle(target, TREAT, (int(t["x"]), int(t["y"])), 11)
            pygame.draw.circle(target, (255, 240, 120), (int(t["x"]), int(t["y"])), 11, 3)

        # UI
        target.blit(self.font.render(f"SCORE: {self.score}", True, (30, 30, 30)), (18, 12))

        if self.show_instructions:
            inst = self.small_font.render("SPACE / UP = Jump (Double Jump Available!)", True, (40, 40, 40))
            target.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 65))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            target.blit(overlay, (0, 0))
            go = self.big_font.render("GAME OVER", True, (255, 90, 90))
            target.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, 130))
            fs = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            target.blit(fs, (SCREEN_WIDTH // 2 - fs.get_width() // 2, 195))
            again = self.font.render("R = Try Again    ESC = Back to Arcade", True, (200, 255, 200))
            target.blit(again, (SCREEN_WIDTH // 2 - again.get_width() // 2, 260))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = PetDash(screen, clock)
    game.run()
    pygame.quit()}