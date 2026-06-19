#!/usr/bin/env python3
"""
OurWorld Arcade - Frogger (throwback style)
Classic Frogger mechanics in retro pixel style.
"""

import pygame
import random
from dataclasses import dataclass

# Screen / Grid
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Colors (retro feel)
BG_COLOR = (20, 30, 20)
GRASS_COLOR = (60, 140, 60)
ROAD_COLOR = (50, 50, 50)
WATER_COLOR = (30, 80, 140)
CAR_COLORS = [(200, 50, 50), (50, 150, 200), (220, 180, 50), (180, 50, 180)]
LOG_COLOR = (139, 90, 43)
FROG_COLOR = (80, 200, 80)
FROG_OUTLINE = (30, 100, 30)
SAFE_COLOR = (40, 120, 40)
TEXT_COLOR = (240, 245, 250)
ACCENT = (255, 220, 100)


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
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 42, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)

    def handle_key(self, key): pass
    def update(self, dt): pass
    def draw(self, screen=None): pass

    def run(self):
        while self.running:
            dt = self.clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return MinigameResult(self.score, False, "quit")
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        return MinigameResult(self.score, True)


class FroggerGame(MinigameBase):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        self.reset_game()

    def reset_game(self):
        self.frog_x = GRID_COLS // 2
        self.frog_y = GRID_ROWS - 2
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.won = False
        self.show_instructions = True
        self.instruction_timer = 0

        # Lane definitions
        self.lanes = [
            {'y': 18, 'speed': 2.5, 'dir': 1, 'is_water': False, 'color': CAR_COLORS[0]},
            {'y': 16, 'speed': 1.8, 'dir': -1, 'is_water': False, 'color': CAR_COLORS[1]},
            {'y': 14, 'speed': 3.2, 'dir': 1, 'is_water': False, 'color': CAR_COLORS[2]},
            {'y': 10, 'speed': 1.5, 'dir': -1, 'is_water': True, 'color': LOG_COLOR},
            {'y': 8, 'speed': 2.0, 'dir': 1, 'is_water': True, 'color': LOG_COLOR},
            {'y': 6, 'speed': 1.2, 'dir': -1, 'is_water': True, 'color': LOG_COLOR},
        ]

        self.cars = []
        self.logs = []
        self._spawn_vehicles()

        self.last_move_time = 0
        self.move_cooldown = 180

    def _spawn_vehicles(self):
        self.cars.clear()
        self.logs.clear()

        for lane in self.lanes:
            y = lane['y']
            speed = lane['speed']
            direction = lane['dir']
            is_water = lane['is_water']
            color = lane['color']

            num = 4 if not is_water else 3
            spacing = GRID_COLS // num

            for i in range(num):
                x = (i * spacing + random.randint(0, spacing//2)) % GRID_COLS
                width = 3 if not is_water else 5
                if is_water:
                    self.logs.append({'x': x, 'y': y, 'width': width, 'speed': speed, 'dir': direction, 'color': color})
                else:
                    self.cars.append({'x': x, 'y': y, 'width': width, 'speed': speed, 'dir': direction, 'color': color})

    def handle_key(self, key):
        if self.game_over or self.won:
            if key == pygame.K_r: self.reset_game()
            elif key in (pygame.K_q, pygame.K_ESCAPE): self.running = False
            return

        if self.show_instructions:
            self.show_instructions = False

        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_cooldown:
            return

        moved = False
        if key in (pygame.K_UP, pygame.K_w):
            self.frog_y = max(0, self.frog_y - 1)
            moved = True
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.frog_y = min(GRID_ROWS - 1, self.frog_y + 1)
            moved = True
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.frog_x = max(0, self.frog_x - 1)
            moved = True
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.frog_x = min(GRID_COLS - 1, self.frog_x + 1)
            moved = True

        if moved:
            self.last_move_time = now
            self.score += 5

    def update(self, dt):
        if self.game_over or self.won or not self.running:
            return

        self.instruction_timer += dt * 1000
        if self.show_instructions and self.instruction_timer > 3500:
            self.show_instructions = False

        for car in self.cars:
            car['x'] += car['speed'] * car['dir'] * 0.8
            if car['x'] < -car['width']: car['x'] = GRID_COLS
            if car['x'] > GRID_COLS: car['x'] = -car['width']

        for log in self.logs:
            log['x'] += log['speed'] * log['dir'] * 0.8
            if log['x'] < -log['width']: log['x'] = GRID_COLS
            if log['x'] > GRID_COLS: log['x'] = -log['width']

        self._check_collisions()

        if self.frog_y <= 2:
            self.won = True
            self.score += 100
            self.running = False

    def _check_collisions(self):
        for car in self.cars:
            if car['y'] == self.frog_y and car['x'] <= self.frog_x < car['x'] + car['width']:
                self._lose_life()
                return

        on_log = False
        for log in self.logs:
            if log['y'] == self.frog_y and log['x'] <= self.frog_x < log['x'] + log['width']:
                on_log = True
                self.frog_x = int(self.frog_x + log['speed'] * log['dir'] * 0.8)
                self.frog_x = max(0, min(GRID_COLS-1, self.frog_x))
                break

        if self.frog_y in [l['y'] for l in self.lanes if l['is_water']] and not on_log:
            self._lose_life()

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            self.running = False
        else:
            self.frog_x = GRID_COLS // 2
            self.frog_y = GRID_ROWS - 2

    def draw(self, screen=None):
        target = screen or self.screen
        target.fill(BG_COLOR)

        for y in range(GRID_ROWS):
            if y >= 17:
                color = GRASS_COLOR
            elif y in [18, 16, 14]:
                color = ROAD_COLOR
            elif y in [10, 8, 6]:
                color = WATER_COLOR
            elif y <= 2:
                color = SAFE_COLOR
            else:
                color = (35, 50, 35)
            pygame.draw.rect(target, color, (0, y * CELL_SIZE, SCREEN_WIDTH, CELL_SIZE))

        for car in self.cars:
            x = int(car['x'] * CELL_SIZE)
            y = car['y'] * CELL_SIZE
            w = car['width'] * CELL_SIZE
            pygame.draw.rect(target, car['color'], (x, y + 2, w - 4, CELL_SIZE - 4), border_radius=3)

        for log in self.logs:
            x = int(log['x'] * CELL_SIZE)
            y = log['y'] * CELL_SIZE
            w = log['width'] * CELL_SIZE
            pygame.draw.rect(target, log['color'], (x, y + 4, w - 4, CELL_SIZE - 8), border_radius=4)

        fx = self.frog_x * CELL_SIZE
        fy = self.frog_y * CELL_SIZE
        pygame.draw.rect(target, FROG_COLOR, (fx + 2, fy + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=6)
        pygame.draw.rect(target, FROG_OUTLINE, (fx + 2, fy + 2, CELL_SIZE - 4, CELL_SIZE - 4), width=2, border_radius=6)
        pygame.draw.circle(target, (20, 40, 20), (fx + 7, fy + 7), 3)
        pygame.draw.circle(target, (20, 40, 20), (fx + 13, fy + 7), 3)

        target.blit(self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR), (12, 8))
        target.blit(self.small_font.render(f"LIVES: {self.lives}", True, TEXT_COLOR), (12, 38))
        target.blit(self.small_font.render("OURWORLD ARCADE • FROGGER", True, ACCENT), (SCREEN_WIDTH - 260, 10))

        if self.show_instructions:
            inst = self.small_font.render("Arrows/WASD to move  •  Reach the top!  •  Avoid cars & water", True, (200, 220, 200))
            target.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, 80))

        if self.game_over:
            msg = self.big_font.render("GAME OVER - R to restart, ESC to quit", True, (255, 180, 180))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 180))

        if self.won:
            msg = self.big_font.render("YOU MADE IT! +100 pts", True, (100, 255, 150))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 180))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    g = FroggerGame(screen, clock)
    g.run()
    pygame.quit()