#!/usr/bin/env python3
"""
OurWorld Arcade - Snake (final clean version)
- Responsive arrow keys + WASD
- draw(self, screen=None) compatible
"""

import pygame
import random
from dataclasses import dataclass

GRID_COLS = 32
GRID_ROWS = 24
CELL_SIZE = 20
SCREEN_WIDTH = GRID_COLS * CELL_SIZE
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE
FPS = 30
MOVE_INTERVAL_MS = 130

BG_COLOR = (18, 22, 30)
GRID_COLOR = (35, 42, 55)
SNAKE_HEAD_COLOR = (80, 200, 120)
SNAKE_BODY_COLOR = (55, 160, 90)
SNAKE_OUTLINE = (30, 90, 50)
TREAT_COLOR = (255, 120, 80)
TEXT_COLOR = (240, 245, 250)
ACCENT = (255, 200, 80)


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
            self.update(dt)
            self.draw()
            pygame.display.flip()
        return MinigameResult(self.score, True)


class SnakeGame(MinigameBase):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        self.reset_game()
        self.last_move_time = 0
        self.move_interval = MOVE_INTERVAL_MS
        self.game_over = False
        self.show_instructions = True
        self.instruction_timer = 0

    def reset_game(self):
        mid_x = GRID_COLS // 2
        mid_y = GRID_ROWS // 2
        self.snake = [(mid_x, mid_y), (mid_x-1, mid_y), (mid_x-2, mid_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.treat_pos = self._spawn_treat()
        self.score = 0
        self.move_interval = MOVE_INTERVAL_MS
        self.game_over = False
        self.running = True
        self.show_instructions = True
        self.instruction_timer = 0

    def _spawn_treat(self):
        while True:
            p = (random.randint(0, GRID_COLS-1), random.randint(0, GRID_ROWS-1))
            if p not in self.snake:
                return p

    def handle_key(self, key):
        if self.game_over:
            if key == pygame.K_r: self.reset_game()
            elif key in (pygame.K_q, pygame.K_ESCAPE): self.running = False
            return

        if key in (pygame.K_UP, pygame.K_w):   new_dir = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s): new_dir = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a): new_dir = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d): new_dir = (1, 0)
        else:
            if key == pygame.K_ESCAPE: self.running = False
            return

        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_direction = new_dir
            self.direction = new_dir   # immediate response

        if self.show_instructions:
            self.show_instructions = False

    def update(self, dt):
        if self.game_over or not self.running: return
        self.instruction_timer += dt * 1000
        if self.show_instructions and self.instruction_timer > 2800:
            self.show_instructions = False

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_interval: return

        self.direction = self.next_direction
        hx, hy = self.snake[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])

        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS) or new_head in self.snake:
            self.game_over = True
            self.running = False
            return

        self.snake.insert(0, new_head)
        if new_head == self.treat_pos:
            self.score += 10
            self.treat_pos = self._spawn_treat()
            if self.score % 5 == 0: self.move_interval = max(70, self.move_interval - 8)
        else:
            self.snake.pop()
        self.last_move_time = now

    def draw(self, screen=None):
        target = screen or self.screen
        target.fill(BG_COLOR)

        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(target, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(target, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)

        for i, (gx, gy) in enumerate(self.snake):
            rect = pygame.Rect(gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            col = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(target, col, rect, border_radius=4)
            pygame.draw.rect(target, SNAKE_OUTLINE, rect, width=2, border_radius=4)
            if i == 0:
                ex = rect.centerx + (self.direction[0] * 5)
                ey = rect.centery + (self.direction[1] * 5)
                pygame.draw.circle(target, (20, 30, 20), (ex, ey), 3)

        tx, ty = self.treat_pos
        pygame.draw.ellipse(target, TREAT_COLOR, (tx*CELL_SIZE+2, ty*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4))

        target.blit(self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR), (12, 8))
        target.blit(self.small_font.render("OURWORLD ARCADE • SNAKE", True, ACCENT), (SCREEN_WIDTH - 220, 10))

        if self.game_over:
            over = self.big_font.render("GAME OVER - R to restart, ESC to quit", True, (255, 180, 180))
            target.blit(over, (SCREEN_WIDTH//2 - over.get_width()//2, 200))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    g = SnakeGame(screen, clock)
    g.run()
    pygame.quit()