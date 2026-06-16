#!/usr/bin/env python3
"""
ArcadeScene - Dedicated scene for the Arcade location.

Handles:
- Arcade menu / game selection
- Launching and running minigames (Snake, Pet Dash)
- Returning scores/rewards to the main game state

This replaces the string-based minigame signaling from MainScene.
"""

import pygame
import time
from typing import Optional, Any

from scenes.base_scene import BaseScene
from minigames import get_minigame


class ArcadeScene(BaseScene):
    def __init__(self, game_state: Any, screen: pygame.Surface):
        super().__init__(game_state, screen)
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.small_font = pygame.font.SysFont("Arial", 14)
        self.font = pygame.font.SysFont("Arial", 22)

        self.selected_game = 0  # 0 = Snake, 1 = Pet Dash
        self.minigame = None
        self.minigame_type = None
        self.status = "Choose a game!"

        self.next_scene = None  # Can request return to MainScene

    def handle_event(self, event: pygame.event.Event):
        if self.minigame:
            if event.type == pygame.KEYDOWN and hasattr(self.minigame, 'handle_key'):
                self.minigame.handle_key(event.key)
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_game = (self.selected_game - 1) % 2
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_game = (self.selected_game + 1) % 2
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._launch_selected_game()
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self._return_to_main()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Simple click detection on game buttons
            if pygame.Rect(150, 200, 150, 80).collidepoint(event.pos):
                self.selected_game = 0
                self._launch_selected_game()
            elif pygame.Rect(340, 200, 150, 80).collidepoint(event.pos):
                self.selected_game = 1
                self._launch_selected_game()

    def _launch_selected_game(self):
        if self.minigame:
            return

        if self.selected_game == 0:
            self.minigame_type = "snake"
            MinigameClass = get_minigame("snake")
            self.minigame = MinigameClass(self.screen, pygame.time.Clock())
            self.status = "Snake time! Arrows/WASD • ESC to quit"
        else:
            self.minigame_type = "pet_dash"
            MinigameClass = get_minigame("pet_dash")
            color = getattr(self.game_state.pet, 'color', (200, 150, 100))
            self.minigame = MinigameClass(self.screen, pygame.time.Clock(), color)
            self.status = "Pet Dash! SPACE/UP to jump • ESC to quit"

    def _return_to_main(self):
        self.next_scene = "main"
        if self.minigame:
            self._handle_minigame_end()

    def update(self, dt: float):
        if self.minigame:
            self.minigame.update(dt)

            if getattr(self.minigame, 'game_over', False):
                self._handle_minigame_end()

    def _handle_minigame_end(self):
        if not self.minigame:
            return

        score = getattr(self.minigame, 'score', 0)

        if self.minigame_type == "snake":
            bonus = min(40, score // 3)
            if bonus > 0:
                self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
            self.game_state.earn_coins(max(20, score // 2))
            self.status = f"Snake complete! +{bonus} Happiness, +{max(20, score // 2)} coins"
        else:
            bonus = min(30, score // 4)
            if bonus > 0:
                self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
            self.game_state.earn_coins(max(15, score // 3))
            self.status = f"Pet Dash complete! +{bonus} Happiness"

        self.minigame = None
        self.minigame_type = None

    def draw(self, surface: pygame.Surface):
        surface.fill((50, 45, 70))

        # Title
        title = self.font.render("ARCADE", True, (255, 220, 100))
        surface.blit(title, (self.width//2 - title.get_width()//2, 40))

        if self.minigame and hasattr(self.minigame, 'draw'):
            self.minigame.draw(surface)
            # Overlay status
            status_surf = self.small_font.render(self.status, True, (200, 200, 200))
            surface.blit(status_surf, (20, self.height - 40))
            return

        # Game selection buttons
        snake_rect = pygame.Rect(150, 200, 150, 80)
        dash_rect = pygame.Rect(340, 200, 150, 80)

        # Snake button
        color = (80, 200, 120) if self.selected_game == 0 else (60, 150, 90)
        pygame.draw.rect(surface, color, snake_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), snake_rect, width=3, border_radius=10)
        surface.blit(self.small_font.render("SNAKE", True, (255, 255, 255)), (snake_rect.x + 45, snake_rect.y + 30))

        # Pet Dash button
        color = (255, 160, 80) if self.selected_game == 1 else (200, 120, 60)
        pygame.draw.rect(surface, color, dash_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), dash_rect, width=3, border_radius=10)
        surface.blit(self.small_font.render("PET DASH", True, (255, 255, 255)), (dash_rect.x + 35, dash_rect.y + 30))

        # Instructions
        inst = self.small_font.render("Left/Right to select  •  Enter/Space to play  •  ESC to leave arcade", True, (180, 180, 180))
        surface.blit(inst, (self.width//2 - inst.get_width()//2, 320))

        # Status
        status_surf = self.small_font.render(self.status, True, (200, 200, 200))
        surface.blit(status_surf, (20, self.height - 40))
