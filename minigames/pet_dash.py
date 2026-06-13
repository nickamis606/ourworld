#!/usr/bin/env python3
"""
OurWorld Arcade - Pet Dash v2 (Much more fun version)
"""

import pygame
import random
from dataclasses import dataclass

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
GRAVITY = 0.65
JUMP_STRENGTH = -13.5
DOUBLE_JUMP_STRENGTH = -11.5
GROUND_Y = 340

BG_COLOR = (100, 180, 255)
GROUND_COLOR = (139, 119, 101)
OBSTACLE_COLOR = (101, 67, 33)
TREAT_COLOR = (255, 215, 0)


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
        self.font = pygame.font.SysFont("arial", 28)
        self.big_font = pygame.font.SysFont("arial", 52, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)

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
        self.pet_x = 120
        self.pet_y = GROUND_Y
        self.pet_vel_y = 0
        self.pet_width = 38
        self.pet_height = 44
        self.jumps = 0
        self.max_jumps = 2

        self.obstacles = []
        self.treats = []
        self.last_obstacle_x = SCREEN_WIDTH + 100
        self.last_treat_x = SCREEN_WIDTH + 80

        self.score = 0
        self.distance = 0
        self.game_over = False
        self.running = True
        self.show_instructions = True
        self.instruction_timer = 0
        self.speed = 4.8
        self.next_speed_increase = 12

        self.anim_frame = 0

    def spawn_obstacle(self):
        height = random.randint(32, 58)
        is_high = random.random() < 0.35
        y = GROUND_Y - height if not is_high else GROUND_Y - height - 70
        x = self.last_obstacle_x + random.randint(160, 240)
        self.obstacles.append({"x": x, "y": y, "w": random.randint(26, 42), "h": height})
        self.last_obstacle_x = x

    def spawn_treat(self):
        x = self.last_treat_x + random.randint(90, 190)
        y = random.randint(GROUND_Y - 140, GROUND_Y - 60)
        self.treats.append({"x": x, "y": y})
        self.last_treat_x = x

    def handle_key(self, key):
        if self.game_over:
            if key == pygame.K_r:
                self.reset_game()
            elif key in (pygame.K_q, pygame.K_ESCAPE):
                self.running = False
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
        if self.instruction_timer > 3.0:
            self.show_instructions = False

        # Pet physics
        self.pet_vel_y += GRAVITY
        self.pet_y += self.pet_vel_y
        self.anim_frame += 0.2

        if self.pet_y >= GROUND_Y:
            self.pet_y = GROUND_Y
            self.pet_vel_y = 0
            self.jumps = 0

        # Spawn obstacles & treats
        if not self.obstacles or self.obstacles[-1]["x"] < SCREEN_WIDTH - 220:
            self.spawn_obstacle()
        if not self.treats or self.treats[-1]["x"] < SCREEN_WIDTH - 140:
            self.spawn_treat()

        # Move everything
        for o in self.obstacles:
            o["x"] -= self.speed
        for t in self.treats:
            t["x"] -= self.speed

        self.obstacles = [o for o in self.obstacles if o["x"] + o["w"] > 0]
        self.treats = [t for t in self.treats if t["x"] > -30]

        # Collision with obstacles
        pet_rect = pygame.Rect(self.pet_x, self.pet_y - self.pet_height, self.pet_width, self.pet_height)
        for o in self.obstacles:
            if pet_rect.colliderect(pygame.Rect(o["x"], o["y"], o["w"], o["h"])):
                self.game_over = True
                self.running = False
                return

        # Collect treats
        for t in self.treats[:]:
            treat_rect = pygame.Rect(t["x"] - 8, t["y"] - 8, 24, 24)
            if pet_rect.colliderect(treat_rect):
                self.treats.remove(t)
                self.score += 25

        # Scoring
        self.distance += self.speed * 0.7
        self.score = int(self.distance / 8) + len([t for t in self.treats if t["x"] < 0]) * 5  # bonus for passed treats

        # Difficulty ramp
        if self.score >= self.next_speed_increase:
            self.speed = min(8.2, self.speed + 0.4)
            self.next_speed_increase += 15

    def draw(self, screen=None):
        target = screen or self.screen
        target.fill(BG_COLOR)

        # Parallax hills
        pygame.draw.rect(target, (80, 160, 100), (0, GROUND_Y - 60, SCREEN_WIDTH, 80))
        pygame.draw.rect(target, (60, 140, 80), (0, GROUND_Y - 30, SCREEN_WIDTH, 50))

        # Ground
        pygame.draw.rect(target, GROUND_COLOR, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # Pet (with running animation)
        px = self.pet_x
        py = int(self.pet_y)
        bob = 3 if self.pet_y < GROUND_Y else int(2 * abs((self.anim_frame * 2) % 2 - 1))

        # Body
        pygame.draw.ellipse(target, self.pet_color, (px + 4, py - self.pet_height + bob + 6, self.pet_width - 8, self.pet_height - 12))
        # Head
        pygame.draw.ellipse(target, self.pet_color, (px + 24, py - self.pet_height - 8 + bob, 26, 22))
        # Ear
        pygame.draw.polygon(target, self.pet_color, [(px+34, py-self.pet_height-12+bob), (px+38, py-self.pet_height-22+bob), (px+46, py-self.pet_height-10+bob)])

        # Legs (running)
        leg_phase = int(self.anim_frame * 3) % 4
        leg_y = 6 if leg_phase in (0, 2) else -2
        pygame.draw.rect(target, (50, 50, 50), (px + 10, py - 12 + leg_y, 7, 16))
        pygame.draw.rect(target, (50, 50, 50), (px + 24, py - 12 - leg_y, 7, 16))

        # Tail wag
        tail_angle = int(self.anim_frame * 6) % 6 - 3
        pygame.draw.line(target, self.pet_color, (px + 8, py - 18), (px - 6, py - 22 + tail_angle), 8)

        # Obstacles
        for o in self.obstacles:
            pygame.draw.rect(target, OBSTACLE_COLOR, (o["x"], o["y"], o["w"], o["h"]), border_radius=6)

        # Treats
        for t in self.treats:
            tx, ty = t["x"], t["y"]
            pygame.draw.circle(target, TREAT_COLOR, (int(tx), int(ty)), 12)
            pygame.draw.circle(target, (255, 240, 100), (int(tx), int(ty)), 12, 3)

        # UI
        target.blit(self.font.render(f"SCORE: {self.score}", True, (30, 30, 30)), (20, 15))

        if self.show_instructions:
            inst = self.small_font.render("SPACE / UP = Jump (Double Jump!)", True, (40, 40, 40))
            target.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 70))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            target.blit(overlay, (0, 0))
            go = self.big_font.render("GAME OVER", True, (255, 100, 100))
            target.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, 140))
            final = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            target.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, 210))
            bonus = self.small_font.render(f"+{min(50, self.score // 2)} Happiness!", True, (255, 215, 0))
            target.blit(bonus, (SCREEN_WIDTH // 2 - bonus.get_width() // 2, 250))
            again = self.font.render("R = Try Again   ESC = Return", True, (200, 255, 200))
            target.blit(again, (SCREEN_WIDTH // 2 - again.get_width() // 2, 300))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = PetDash(screen, clock)
    game.run()
    pygame.quit()