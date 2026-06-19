#!/usr/bin/env python3
"""
OurWorld Arcade - Frogger
Clean implementation using standard working patterns from popular open source Pygame Frogger clones.
Logs carry the frog correctly.
"""

import pygame
import random
from dataclasses import dataclass

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Colors
BG = (15, 25, 15)
GRASS = (50, 130, 50)
ROAD = (45, 45, 50)
ROAD_LINE = (240, 240, 240)
WATER = (25, 75, 140)
WATER_LINE = (60, 120, 180)
CAR_COLORS = [(200, 40, 40), (40, 140, 200), (220, 180, 40), (170, 50, 180)]
CAR_CABIN = (50, 50, 60)
LOG = (110, 70, 35)
LOG_DETAIL = (150, 105, 60)
FROG = (70, 190, 70)
FROG_DARK = (40, 110, 40)
FROG_EYE = (255, 255, 230)
TEXT = (250, 255, 250)
ACCENT = (255, 215, 80)
SAFE = (35, 95, 35)


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
        self.big_font = pygame.font.SysFont("arial", 38, bold=True)
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

        # Lanes: y, speed, direction, is_water
        self.lanes = [
            {'y': 18, 'speed': 0.85, 'dir': 1,  'is_water': False},
            {'y': 16, 'speed': 0.65, 'dir': -1, 'is_water': False},
            {'y': 14, 'speed': 0.95, 'dir': 1,  'is_water': False},
            {'y': 10, 'speed': 0.55, 'dir': -1, 'is_water': True},
            {'y': 8,  'speed': 0.75, 'dir': 1,  'is_water': True},
            {'y': 6,  'speed': 0.45, 'dir': -1, 'is_water': True},
        ]

        self.cars = []
        self.logs = []
        self._spawn_vehicles()

        self.last_move_time = 0
        self.move_cooldown = 190

    def _spawn_vehicles(self):
        self.cars.clear()
        self.logs.clear()

        for lane in self.lanes:
            y = lane['y']
            speed = lane['speed']
            direction = lane['dir']
            is_water = lane['is_water']

            count = 3 if is_water else 4
            spacing = GRID_COLS // count

            for i in range(count):
                x = (i * spacing + random.randint(0, spacing - 2)) % GRID_COLS
                if is_water:
                    self.logs.append({'x': float(x), 'y': y, 'width': 5, 'speed': speed, 'dir': direction})
                else:
                    self.cars.append({
                        'x': float(x), 'y': y, 'width': 3,
                        'speed': speed, 'dir': direction,
                        'color': random.choice(CAR_COLORS)
                    })

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
            if self.frog_y < 17:
                self.score += 8

    def update(self, dt):
        if self.game_over or self.won or not self.running:
            return

        self.instruction_timer += dt * 1000
        if self.show_instructions and self.instruction_timer > 2800:
            self.show_instructions = False

        for car in self.cars:
            car['x'] += car['speed'] * car['dir'] * 0.5
            if car['x'] < -car['width']:
                car['x'] = GRID_COLS + 2
            if car['x'] > GRID_COLS + 2:
                car['x'] = -car['width']

        for log in self.logs:
            log['x'] += log['speed'] * log['dir'] * 0.5
            if log['x'] < -log['width']:
                log['x'] = GRID_COLS + 2
            if log['x'] > GRID_COLS + 2:
                log['x'] = -log['width']

        self._check_collisions()

        if self.frog_y <= 2:
            self.won = True
            self.score += 150
            self.running = False

    def _check_collisions(self):
        # Cars
        for car in self.cars:
            if car['y'] == self.frog_y and car['x'] <= self.frog_x < car['x'] + car['width']:
                self._lose_life()
                return

        # Water - proper carrying (standard working pattern)
        lane = next((l for l in self.lanes if l['y'] == self.frog_y), None)

        if lane and lane.get('is_water', False):
            on_log = False
            for log in self.logs:
                if log['y'] == self.frog_y:
                    log_left = log['x']
                    log_right = log['x'] + log['width']
                    if log_left - 0.2 <= self.frog_x < log_right + 0.2:
                        on_log = True
                        # Carry frog with the log (correct direction and speed)
                        self.frog_x += log['speed'] * log['dir'] * 0.6
                        self.frog_x = max(0, min(GRID_COLS - 1, int(round(self.frog_x))))
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
        target.fill(BG)

        for y in range(GRID_ROWS):
            cy = y * CELL_SIZE

            if y >= 17:
                pygame.draw.rect(target, GRASS, (0, cy, SCREEN_WIDTH, CELL_SIZE))
            elif y in [18, 16, 14]:
                pygame.draw.rect(target, ROAD, (0, cy, SCREEN_WIDTH, CELL_SIZE))
                for gx in range(0, SCREEN_WIDTH, 45):
                    pygame.draw.rect(target, ROAD_LINE, (gx, cy + 6, 22, 2))
                    pygame.draw.rect(target, ROAD_LINE, (gx, cy + CELL_SIZE - 8, 22, 2))
            elif y in [10, 8, 6]:
                pygame.draw.rect(target, WATER, (0, cy, SCREEN_WIDTH, CELL_SIZE))
                offset = (pygame.time.get_ticks() // 65) % 32
                for gx in range(-32, SCREEN_WIDTH, 32):
                    pygame.draw.line(target, WATER_LINE, (gx + offset, cy + 5), (gx + 18 + offset, cy + 5), 2)
            elif y <= 2:
                pygame.draw.rect(target, SAFE, (0, cy, SCREEN_WIDTH, CELL_SIZE))

        for car in self.cars:
            x = int(car['x'] * CELL_SIZE)
            y = car['y'] * CELL_SIZE + 2
            w = car['width'] * CELL_SIZE - 4
            pygame.draw.rect(target, car['color'], (x, y, w, CELL_SIZE - 6), border_radius=4)
            pygame.draw.rect(target, CAR_CABIN, (x + 5, y + 4, w - 10, CELL_SIZE - 14), border_radius=2)
            pygame.draw.ellipse(target, (20, 20, 20), (x + 2, y + CELL_SIZE - 6, 6, 5))
            pygame.draw.ellipse(target, (20, 20, 20), (x + w - 8, y + CELL_SIZE - 6, 6, 5))

        for log in self.logs:
            x = int(log['x'] * CELL_SIZE)
            y = log['y'] * CELL_SIZE + 3
            w = log['width'] * CELL_SIZE - 6
            pygame.draw.rect(target, LOG, (x, y, w, CELL_SIZE - 8), border_radius=5)
            for sx in range(5, w - 5, 12):
                pygame.draw.line(target, LOG_DETAIL, (x + sx, y + 2), (x + sx, y + CELL_SIZE - 10), 2)

        fx = self.frog_x * CELL_SIZE + 1
        fy = self.frog_y * CELL_SIZE + 1
        pygame.draw.ellipse(target, FROG, (fx + 2, fy + 5, CELL_SIZE - 4, CELL_SIZE - 9))
        pygame.draw.ellipse(target, FROG, (fx + 5, fy, CELL_SIZE - 10, CELL_SIZE - 5))
        pygame.draw.ellipse(target, FROG_DARK, (fx + 5, fy, CELL_SIZE - 10, CELL_SIZE - 5), 2)
        pygame.draw.circle(target, FROG_EYE, (fx + 9, fy + 4), 3)
        pygame.draw.circle(target, FROG_EYE, (fx + 14, fy + 4), 3)
        pygame.draw.circle(target, (20, 20, 20), (fx + 10, fy + 4), 1)
        pygame.draw.circle(target, (20, 20, 20), (fx + 15, fy + 4), 1)

        target.blit(self.font.render(f"SCORE: {self.score}", True, TEXT), (12, 8))
        target.blit(self.small_font.render(f"LIVES: {self.lives}", True, TEXT), (12, 36))
        target.blit(self.small_font.render("OURWORLD ARCADE • FROGGER", True, ACCENT), (SCREEN_WIDTH - 250, 10))

        if self.show_instructions:
            inst = self.small_font.render("Arrows/WASD to move  •  Reach the top safely!", True, (200, 230, 200))
            target.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, 65))

        if self.game_over:
            msg = self.big_font.render("GAME OVER  •  R = Restart   ESC = Quit", True, (255, 160, 160))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 165))

        if self.won:
            msg = self.big_font.render("NICE! YOU MADE IT ACROSS!", True, (110, 255, 150))
            target.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 165))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    g = FroggerGame(screen, clock)
    g.run()
    pygame.quit()