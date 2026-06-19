#!/usr/bin/env python3
"""
OurWorld Arcade - Frogger (improved throwback style)
Much better visuals + playable speeds.
"""

import pygame
import random
from dataclasses import dataclass

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Better retro colors
BG_COLOR = (15, 25, 15)
GRASS_TOP = (45, 120, 45)
GRASS_BOTTOM = (55, 140, 55)
ROAD_COLOR = (45, 45, 50)
ROAD_LINE = (220, 220, 220)
WATER_COLOR = (25, 70, 130)
WATER_HIGHLIGHT = (40, 100, 160)
CAR_BODY = [(200, 40, 40), (40, 140, 200), (220, 170, 40), (160, 50, 180)]
CAR_CABIN = (60, 60, 70)
LOG_COLOR = (120, 75, 35)
LOG_HIGHLIGHT = (160, 110, 60)
FROG_COLOR = (70, 190, 70)
FROG_DARK = (40, 110, 40)
TEXT_COLOR = (245, 250, 245)
ACCENT = (255, 215, 80)
SAFE_ZONE = (35, 100, 35)


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
        self.big_font = pygame.font.SysFont("arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("arial", 15)

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

        # Tuned slower speeds for playability
        self.lanes = [
            {'y': 18, 'speed': 1.4, 'dir': 1,  'is_water': False},
            {'y': 16, 'speed': 1.1, 'dir': -1, 'is_water': False},
            {'y': 14, 'speed': 1.7, 'dir': 1,  'is_water': False},
            {'y': 10, 'speed': 0.9, 'dir': -1, 'is_water': True},
            {'y': 8,  'speed': 1.2, 'dir': 1,  'is_water': True},
            {'y': 6,  'speed': 0.75,'dir': -1, 'is_water': True},
        ]

        self.cars = []
        self.logs = []
        self._spawn_vehicles()

        self.last_move_time = 0
        self.move_cooldown = 220

    def _spawn_vehicles(self):
        self.cars.clear()
        self.logs.clear()

        for lane in self.lanes:
            y = lane['y']
            speed = lane['speed']
            direction = lane['dir']
            is_water = lane['is_water']

            num = 3 if is_water else 4
            spacing = GRID_COLS // num

            for i in range(num):
                x = (i * spacing + random.randint(0, spacing - 2)) % GRID_COLS
                if is_water:
                    self.logs.append({'x': float(x), 'y': y, 'width': 5, 'speed': speed, 'dir': direction})
                else:
                    self.cars.append({'x': float(x), 'y': y, 'width': 3, 'speed': speed, 'dir': direction, 'color': random.choice(CAR_BODY)})

    def handle_key(self, key):
        if self.game_over or self.won:
            if key == pygame.K_r:
                self.reset_game()
            elif key in (pygame.K_q, pygame.K_ESCAPE):
                self.running = False
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
            if self.frog_y < 17:
                self.score += 8

    def update(self, dt):
        if self.game_over or self.won or not self.running:
            return

        self.instruction_timer += dt * 1000
        if self.show_instructions and self.instruction_timer > 3200:
            self.show_instructions = False

        for car in self.cars:
            car['x'] += car['speed'] * car['dir'] * 0.6
            if car['x'] < -car['width']:
                car['x'] = GRID_COLS + 1
            if car['x'] > GRID_COLS + 1:
                car['x'] = -car['width']

        for log in self.logs:
            log['x'] += log['speed'] * log['dir'] * 0.6
            if log['x'] < -log['width']:
                log['x'] = GRID_COLS + 1
            if log['x'] > GRID_COLS + 1:
                log['x'] = -log['width']

        self._check_collisions()

        if self.frog_y <= 2:
            self.won = True
            self.score += 120
            self.running = False

    def _check_collisions(self):
        for car in self.cars:
            if car['y'] == self.frog_y and car['x'] <= self.frog_x < car['x'] + car['width']:
                self._lose_life()
                return

        on_log = False
        current_lane = next((l for l in self.lanes if l['y'] == self.frog_y), None)

        if current_lane and current_lane.get('is_water', False):
            for log in self.logs:
                if log['y'] == self.frog_y and log['x'] <= self.frog_x < log['x'] + log['width']:
                    on_log = True
                    self.frog_x = self.frog_x + log['speed'] * log['dir'] * 0.6
                    self.frog_x = max(0, min(GRID_COLS - 1, int(self.frog_x)))
                    break

            if not on_log:
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
            cy = y * CELL_SIZE

            if y >= 17:
                pygame.draw.rect(target, GRASS_BOTTOM, (0, cy, SCREEN_WIDTH, CELL_SIZE))
                for i in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.line(target, GRASS_TOP, (i, cy + 5), (i + 15, cy + CELL_SIZE - 3), 2)

            elif y in [18, 16, 14]:
                pygame.draw.rect(target, ROAD_COLOR, (0, cy, SCREEN_WIDTH, CELL_SIZE))
                for i in range(0, SCREEN_WIDTH, 50):
                    pygame.draw.rect(target, ROAD_LINE, (i, cy + CELL_SIZE//2 - 1, 25, 2))

            elif y in [10, 8, 6]:
                pygame.draw.rect(target, WATER_COLOR, (0, cy, SCREEN_WIDTH, CELL_SIZE))
                offset = int((pygame.time.get_ticks() // 80) % 40)
                for i in range(-40, SCREEN_WIDTH, 40):
                    pygame.draw.line(target, WATER_HIGHLIGHT, (i + offset, cy + 6), (i + 25 + offset, cy + 6), 2)

            elif y <= 2:
                pygame.draw.rect(target, SAFE_ZONE, (0, cy, SCREEN_WIDTH, CELL_SIZE))

        for car in self.cars:
            x = int(car['x'] * CELL_SIZE)
            y = car['y'] * CELL_SIZE + 3
            w = car['width'] * CELL_SIZE - 4
            pygame.draw.rect(target, car['color'], (x, y, w, CELL_SIZE - 8), border_radius=4)
            pygame.draw.rect(target, CAR_CABIN, (x + 6, y + 3, w - 12, CELL_SIZE - 14), border_radius=2)

        for log in self.logs:
            x = int(log['x'] * CELL_SIZE)
            y = log['y'] * CELL_SIZE + 4
            w = log['width'] * CELL_SIZE - 6
            pygame.draw.rect(target, LOG_COLOR, (x, y, w, CELL_SIZE - 10), border_radius=5)
            for sx in range(8, w - 8, 18):
                pygame.draw.line(target, LOG_HIGHLIGHT, (x + sx, y + 2), (x + sx, y + CELL_SIZE - 12), 2)

        fx = self.frog_x * CELL_SIZE + 2
        fy = self.frog_y * CELL_SIZE + 2
        pygame.draw.ellipse(target, FROG_COLOR, (fx, fy + 4, CELL_SIZE - 4, CELL_SIZE - 10))
        pygame.draw.ellipse(target, FROG_COLOR, (fx + 4, fy, CELL_SIZE - 10, CELL_SIZE - 8))
        pygame.draw.ellipse(target, FROG_DARK, (fx + 4, fy, CELL_SIZE - 10, CELL_SIZE - 8), 2)
        pygame.draw.circle(target, (255, 255, 200), (fx + 8, fy + 6), 4)
        pygame.draw.circle(target, (255, 255, 200), (fx + 14, fy + 6), 4)
        pygame.draw.circle(target, (30, 30, 30), (fx + 9, fy + 6), 2)
        pygame.draw.circle(target, (30, 30, 30), (fx + 15, fy + 6), 2)

        target.blit(self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR), (12, 8))
        target.blit(self.small_font.render(f"LIVES: {self.lives}", True, TEXT_COLOR), (12, 36))
        target.blit(self.small_font.render("OURWORLD ARCADE • FROGGER", True, ACCENT), (SCREEN_WIDTH - 250, 10))

        if self.show_instructions:
            inst = self.small_font.render("Arrows/WASD: Move   |   Reach the top safe zone!", True, (210, 230, 210))
            target.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, 70))

        if self.game_over:
            msg = self.big_font.render("GAME OVER  •  R = Restart   ESC = Quit", True, (255, 170, 170))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 170))

        if self.won:
            msg = self.big_font.render("NICE! YOU MADE IT ACROSS!", True, (120, 255, 160))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 170))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    g = FroggerGame(screen, clock)
    g.run()
    pygame.quit()