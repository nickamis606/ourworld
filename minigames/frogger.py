#!/usr/bin/env python3
"""
OurWorld Arcade - Frogger (with proper levels)
Multiple homes, level progression, increasing difficulty.

Polished for visual feedback: death splash, home-fill glow,
centered level banner, level-transition pause, and clear restart path.
"""

import math
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
HOME_EMPTY = (40, 100, 40)
HOME_FILLED = (255, 215, 80)
HOME_GLOW = (255, 240, 160)
TEXT = (250, 255, 250)
ACCENT = (255, 215, 80)
SAFE = (35, 95, 35)

# Death feedback types
DEATH_NONE = 0
DEATH_CAR = 1
DEATH_WATER = 2

# Timing constants (ms)
DEATH_FLASH_MS = 700
HOME_GLOW_MS = 600
HOME_PULSE_INTERVAL = 100
LEVEL_TRANSITION_MS = 1800
FROG_RESET_MS = 300


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
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
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

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------

    def reset_game(self):
        """Reset all game state to start of level 1."""
        self.frog_x = GRID_COLS // 2
        self.frog_y = GRID_ROWS - 2
        self.lives = 3
        self.score = 0
        self.level = 1
        self.homes = [False] * 5
        self.home_positions = [4, 10, 16, 22, 28]
        self.game_over = False
        self.won = False
        self.show_instructions = True
        self.instruction_timer = 0

        self.base_speeds = [0.85, 0.65, 0.95, 0.55, 0.75, 0.45]
        self._update_level_speeds()

        self.cars = []
        self.logs = []
        self._spawn_vehicles()

        self.last_move_time = 0
        self.move_cooldown = 190

        # Feedback timing (ms remaining)
        self.death_timer = 0
        self.death_type = DEATH_NONE
        self.flash_timer = 0        # brief white screen flash on death
        self.golden_flash = 0       # golden screen flash on last home fill
        self.home_glow_timers = [0] * 5
        self.heart_flash = 0        # lives flash white when a life is lost
        self.level_transition_timer = 0

    # ------------------------------------------------------------------
    #  Level / difficulty
    # ------------------------------------------------------------------

    def _update_level_speeds(self):
        multiplier = 1.0 + (self.level - 1) * 0.12
        self.lane_speeds = [s * multiplier for s in self.base_speeds]

    def _spawn_vehicles(self):
        self.cars.clear()
        self.logs.clear()
        for i, lane in enumerate(self.lanes):
            y = lane['y']
            speed = self.lane_speeds[i]
            direction = lane['dir']
            is_water = lane['is_water']
            count = 3 if is_water else 4
            spacing = GRID_COLS // count
            for j in range(count):
                x = (j * spacing + random.randint(0, spacing - 2)) % GRID_COLS
                if is_water:
                    self.logs.append({'x': float(x), 'y': y, 'width': 5,
                                      'speed': speed, 'dir': direction})
                else:
                    self.cars.append({
                        'x': float(x), 'y': y, 'width': 3,
                        'speed': speed, 'dir': direction,
                        'color': random.choice(CAR_COLORS),
                    })

    @property
    def lanes(self):
        return [
            {'y': 18, 'dir': 1,  'is_water': False},
            {'y': 16, 'dir': -1, 'is_water': False},
            {'y': 14, 'dir': 1,  'is_water': False},
            {'y': 10, 'dir': -1, 'is_water': True},
            {'y': 8,  'dir': 1,  'is_water': True},
            {'y': 6,  'dir': -1, 'is_water': True},
        ]

    # ------------------------------------------------------------------
    #  Input
    # ------------------------------------------------------------------

    def handle_key(self, key):
        # Game-over screen — allow restart
        if self.game_over:
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

        # Block movement during death-flash / home-glow / level-transition
        if self.death_timer > 0 or self.level_transition_timer > 0:
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

    # ------------------------------------------------------------------
    #  Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.game_over:
            # Keep drawing the game-over screen; no gameplay updates.
            self._tick_feedback(dt)
            return

        self.instruction_timer += dt * 1000
        if self.show_instructions and self.instruction_timer > 2800:
            self.show_instructions = False

        # Vehicles
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
        self._tick_feedback(dt)

    def _tick_feedback(self, dt):
        """Decrement ms-based timers every frame."""
        ms = dt * 1000
        if self.death_timer > 0:
            self.death_timer = max(0, self.death_timer - ms)
        if self.flash_timer > 0:
            self.flash_timer = max(0, self.flash_timer - ms)
        if self.golden_flash > 0:
            self.golden_flash = max(0, self.golden_flash - ms)
        if self.heart_flash > 0:
            self.heart_flash = max(0, self.heart_flash - ms)
        if self.level_transition_timer > 0:
            self.level_transition_timer -= ms
            if self.level_transition_timer <= 0:
                # Start next level
                self.level_transition_timer = 0
                self.level += 1
                self.homes = [False] * 5
                self.home_glow_timers = [0] * 5
                self._update_level_speeds()
                self._spawn_vehicles()
                self.frog_x = GRID_COLS // 2
                self.frog_y = GRID_ROWS - 2
                # Clear won flag — it belongs to the completed game, not the new one
                self.won = False
        for i in range(5):
            if self.home_glow_timers[i] > 0:
                self.home_glow_timers[i] = max(0, self.home_glow_timers[i] - ms)

    # ------------------------------------------------------------------
    #  Collision / scoring
    # ------------------------------------------------------------------

    def _check_collisions(self):
        # Cars
        if self.death_timer <= 0:
            for car in self.cars:
                if car['y'] == self.frog_y and car['x'] <= self.frog_x < car['x'] + car['width']:
                    self._lose_life(DEATH_CAR)
                    return

        # Water — log carrying
        lane = next((l for l in self.lanes if l['y'] == self.frog_y), None)
        if lane and lane.get('is_water', False):
            on_log = False
            for log in self.logs:
                if log['y'] == self.frog_y:
                    log_left = log['x']
                    log_right = log['x'] + log['width']
                    if log_left - 0.2 <= self.frog_x < log_right + 0.2:
                        on_log = True
                        self.frog_x += log['speed'] * log['dir'] * 0.65
                        self.frog_x = max(0, min(GRID_COLS - 1, int(round(self.frog_x))))
                        break
            if not on_log and self.death_timer <= 0:
                self._lose_life(DEATH_WATER)
                return

        # Top row — home checking
        if self.frog_y <= 2 and self.death_timer <= 0 and self.level_transition_timer <= 0:
            self._try_fill_home()

    def _try_fill_home(self):
        for i, home_x in enumerate(self.home_positions):
            if not self.homes[i] and abs(self.frog_x - home_x) <= 2:
                self.homes[i] = True
                self.home_glow_timers[i] = HOME_GLOW_MS
                self.score += 100 + (self.level * 20)

                if all(self.homes):
                    self.golden_flash = 600  # golden screen flash for last home
                    self.level_transition_timer = LEVEL_TRANSITION_MS
                else:
                    self.death_timer = FROG_RESET_MS

                self.frog_x = GRID_COLS // 2
                self.frog_y = GRID_ROWS - 2
                return

        # Landed on top but not in a home
        self._lose_life(DEATH_CAR)

    def _lose_life(self, death_type=DEATH_CAR):
        self.lives -= 1
        self.death_type = death_type
        self.death_timer = DEATH_FLASH_MS
        self.flash_timer = 120       # 120 ms white screen flash
        self.heart_flash = 500       # 500 ms heart flash
        if self.lives <= 0:
            self.game_over = True
            # Keep running so the game-over screen is drawn

    # ------------------------------------------------------------------
    #  Drawing
    # ------------------------------------------------------------------

    def draw(self, screen=None):
        target = screen or self.screen
        target.fill(BG)
        now = pygame.time.get_ticks()

        # --- Background lanes ---
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
                offset = (now // 65) % 32
                for gx in range(-32, SCREEN_WIDTH, 32):
                    pygame.draw.line(target, WATER_LINE,
                                     (gx + offset, cy + 5),
                                     (gx + 18 + offset, cy + 5), 2)
            elif y <= 2:
                pygame.draw.rect(target, SAFE, (0, cy, SCREEN_WIDTH, CELL_SIZE))

        # --- Homes ---
        for i, home_x in enumerate(self.home_positions):
            hx = home_x * CELL_SIZE
            if self.homes[i]:
                # Pulsing glow during HOME_GLOW_MS
                color = HOME_FILLED
                if self.home_glow_timers[i] > 0:
                    pulse = 0.5 + 0.5 * ((now // HOME_PULSE_INTERVAL) % 2)
                    r = int(color[0] + (255 - color[0]) * pulse)
                    g = int(color[1] + (255 - color[1]) * pulse)
                    b = int(color[2] + (255 - color[2]) * pulse)
                    color = (r, g, b)
                pygame.draw.ellipse(target, color,
                                    (hx, 2 * CELL_SIZE + 4,
                                     CELL_SIZE * 2, CELL_SIZE - 6))
                # Outer glow ring
                pygame.draw.ellipse(target, HOME_GLOW,
                                    (hx - 2, 2 * CELL_SIZE + 2,
                                     CELL_SIZE * 2 + 4, CELL_SIZE - 2), 2)
            else:
                # Dashed-looking border so empty homes stand out from the SAFE background
                pygame.draw.ellipse(target, (100, 160, 100),
                                    (hx - 1, 2 * CELL_SIZE + 3,
                                     CELL_SIZE * 2 + 2, CELL_SIZE - 4), 2)
                pygame.draw.ellipse(target, HOME_EMPTY,
                                    (hx, 2 * CELL_SIZE + 4,
                                     CELL_SIZE * 2, CELL_SIZE - 6))

        # --- Cars ---
        for car in self.cars:
            x = int(car['x'] * CELL_SIZE)
            y = car['y'] * CELL_SIZE + 2
            w = car['width'] * CELL_SIZE - 4
            pygame.draw.rect(target, car['color'], (x, y, w, CELL_SIZE - 6),
                             border_radius=4)
            pygame.draw.rect(target, CAR_CABIN,
                             (x + 5, y + 4, w - 10, CELL_SIZE - 14),
                             border_radius=2)
            pygame.draw.ellipse(target, (20, 20, 20),
                                (x + 2, y + CELL_SIZE - 6, 6, 5))
            pygame.draw.ellipse(target, (20, 20, 20),
                                (x + w - 8, y + CELL_SIZE - 6, 6, 5))

        # --- Logs ---
        for log in self.logs:
            x = int(log['x'] * CELL_SIZE)
            y = log['y'] * CELL_SIZE + 3
            w = log['width'] * CELL_SIZE - 6
            pygame.draw.rect(target, LOG, (x, y, w, CELL_SIZE - 8),
                             border_radius=5)
            for sx in range(5, w - 5, 12):
                pygame.draw.line(target, LOG_DETAIL,
                                 (x + sx, y + 2),
                                 (x + sx, y + CELL_SIZE - 10), 2)

        # --- Frog ---
        fx = self.frog_x * CELL_SIZE + 1
        fy = self.frog_y * CELL_SIZE + 1
        if self.death_timer > 0 and (now // 60) % 2 == 0:
            # Flash white during death flash
            pygame.draw.ellipse(target, (255, 255, 255),
                                (fx, fy, CELL_SIZE, CELL_SIZE))
        elif self.death_timer > 0 and self.death_timer < FROG_RESET_MS:
            # Fade-in on respawn: frog grows from transparent to solid
            fade_progress = self.death_timer / FROG_RESET_MS
            alpha = int(200 * fade_progress)
            frog_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(frog_surf, FROG + (alpha,),
                                (2, 5, CELL_SIZE - 4, CELL_SIZE - 9))
            pygame.draw.ellipse(frog_surf, FROG + (alpha,),
                                (5, 0, CELL_SIZE - 10, CELL_SIZE - 5))
            pygame.draw.ellipse(frog_surf, FROG_DARK + (alpha,),
                                (5, 0, CELL_SIZE - 10, CELL_SIZE - 5), 2)
            pygame.draw.circle(frog_surf, FROG_EYE + (alpha,), (9, 4), 3)
            pygame.draw.circle(frog_surf, FROG_EYE + (alpha,), (14, 4), 3)
            target.blit(frog_surf, (fx, fy))
        else:
            pygame.draw.ellipse(target, FROG,
                                (fx + 2, fy + 5, CELL_SIZE - 4, CELL_SIZE - 9))
            pygame.draw.ellipse(target, FROG,
                                (fx + 5, fy, CELL_SIZE - 10, CELL_SIZE - 5))
            pygame.draw.ellipse(target, FROG_DARK,
                                (fx + 5, fy, CELL_SIZE - 10, CELL_SIZE - 5), 2)
            pygame.draw.circle(target, FROG_EYE, (fx + 9, fy + 4), 3)
            pygame.draw.circle(target, FROG_EYE, (fx + 14, fy + 4), 3)
            pygame.draw.circle(target, (20, 20, 20), (fx + 10, fy + 4), 1)
            pygame.draw.circle(target, (20, 20, 20), (fx + 15, fy + 4), 1)

        # --- White screen flash ---
        if self.flash_timer > 0:
            flash_alpha = min(255, int(200 * (self.flash_timer / 120)))
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, flash_alpha))
            target.blit(flash_surf, (0, 0))

        # --- Golden screen flash (last home fill) ---
        if self.golden_flash > 0:
            glow = 0.5 + 0.5 * ((now // 200) % 2)
            flash_alpha = min(255, int(180 * glow * (self.golden_flash / 600)))
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 240, 140, flash_alpha))
            target.blit(flash_surf, (0, 0))

        # --- Death splash overlay ---
        if self.death_timer > 0:
            splash = ((255, 100, 100) if self.death_type == DEATH_CAR
                      else (80, 140, 255))
            cx = fx + CELL_SIZE // 2
            cy = fy + CELL_SIZE // 2
            for ring in range(1, 6):
                alpha = max(0, int(160 * (1 - ring / 5)))
                r = int(splash[0] * alpha / 255)
                g = int(splash[1] * alpha / 255)
                b = int(splash[2] * alpha / 255)
                pygame.draw.circle(target, (r, g, b), (cx, cy),
                                   ring * 10 + 4, 3)

        # --- UI ---
        # Large centered level indicator
        level_text = self.big_font.render(f"LEVEL {self.level}", True, ACCENT)
        target.blit(level_text,
                     (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 8))
        target.blit(self.font.render(f"SCORE: {self.score}", True, TEXT),
                     (12, 8 + level_text.get_height() + 4))
        if self.heart_flash > 0:
            pulse = 0.5 + 0.5 * ((now // 100) % 2)
            heart_color = (int(255 * pulse + 250 * (1 - pulse)),
                           int(80 * pulse + 250 * (1 - pulse)),
                           int(80 * pulse + 250 * (1 - pulse)))
            heart_text = f"LIVES: {'♥' * self.lives}"
            target.blit(self.small_font.render(heart_text, True, heart_color),
                        (12, 36))
        else:
            target.blit(self.small_font.render(f"LIVES: {'♥' * self.lives}", True, TEXT),
                         (12, 36))
        target.blit(self.small_font.render("OURWORLD ARCADE • FROGGER", True, ACCENT),
                     (SCREEN_WIDTH - 250, 10))

        # Home progress
        filled = sum(self.homes)
        target.blit(self.small_font.render(f"HOMES: {filled}/5", True, TEXT),
                     (SCREEN_WIDTH - 120, 36))

        if self.show_instructions:
            inst = self.small_font.render(
                "Arrows/WASD: Move   |   Fill all homes to advance level!",
                True, (200, 230, 200))
            target.blit(inst,
                        (SCREEN_WIDTH // 2 - inst.get_width() // 2, 65))

        # Level-transition banner
        if self.level_transition_timer > 0:
            # Breathing pulse: peaks in middle of transition, fades at edges
            t = self.level_transition_timer / LEVEL_TRANSITION_MS
            pulse = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(t * math.pi))
            alpha = min(255, int(255 * pulse * min(1, self.level_transition_timer / 400)))
            banner = pygame.Surface((420, 90), pygame.SRCALPHA)
            banner.fill((8, 18, 8, alpha // 3))
            target.blit(banner,
                        (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 - 45))
            msg = self.big_font.render(
                f"LEVEL {self.level - 1} COMPLETE!", True, (255, 240, 180))
            # Subtle scale pulse on text
            scale = int(1 + 0.04 * pulse)
            scaled_msg = pygame.transform.scale_by(msg, scale)
            target.blit(scaled_msg,
                        (SCREEN_WIDTH // 2 - scaled_msg.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 20))

        # Game-over screen
        if self.game_over:
            msg = self.big_font.render("GAME OVER", True, (255, 120, 120))
            target.blit(msg,
                        (SCREEN_WIDTH // 2 - msg.get_width() // 2, 160))
            sub = self.font.render("R = Try Again    ESC = Quit",
                                   True, (220, 200, 200))
            target.blit(sub,
                        (SCREEN_WIDTH // 2 - sub.get_width() // 2,
                         160 + msg.get_height() + 8))

        if self.won:
            msg = self.big_font.render("YOU CROSSED! GREAT JOB!", True, (110, 255, 150))
            target.blit(msg,
                        (SCREEN_WIDTH // 2 - msg.get_width() // 2, 165))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    g = FroggerGame(screen, clock)
    g.run()
    pygame.quit()
