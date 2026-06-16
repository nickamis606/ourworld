#!/usr/bin/env python3
"""
OurWorld - Main entry point (thin controller version)

Architecture:
- PetSelectionScreen (uses PetSprite)
- OurWorldPygame acts as thin controller
- MainScene handles the primary gameplay view
- Minigames are launched from MainScene signals

This is a major step toward clean scene-based architecture.
"""

import pygame
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.game_state import GameState
from minigames import get_minigame
from sprites.pet_sprite import PetSprite
from scenes.main_scene import MainScene

WIDTH, HEIGHT = 640, 480
FPS = 30


PET_ROSTER = [
    {"id": 0, "name": "Bubbles", "color": (255, 182, 193), "style": "round"},
    {"id": 1, "name": "Milo", "color": (255, 200, 150), "style": "cat"},
    {"id": 2, "name": "Luna", "color": (180, 220, 255), "style": "round"},
    {"id": 3, "name": "Sprout", "color": (200, 255, 180), "style": "plant"},
    {"id": 4, "name": "Pip", "color": (255, 220, 150), "style": "round"},
    {"id": 5, "name": "Nova", "color": (220, 180, 255), "style": "star"},
]


class PetSelectionScreen:
    """Pet selection screen (kept mostly as-is from previous refactor)."""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.selected_index = 0
        self.bob = 0.0
        self.done = False

        self.pet_sprites = []
        for i, pet_data in enumerate(PET_ROSTER):
            col = i % 3
            row = i // 3
            x = 120 + col * 180
            y = 160 + row * 140
            sprite = PetSprite(pet_data, size=1.0, pos=(x, y))
            self.pet_sprites.append(sprite)

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
                    for i, sprite in enumerate(self.pet_sprites):
                        if sprite.rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.done = True
                            break

            self.bob = (self.bob + 0.1) % (2 * 3.14159)

            for i, sprite in enumerate(self.pet_sprites):
                sprite.set_selected(i == self.selected_index)
                if i == self.selected_index:
                    sprite.set_bob(self.bob)
                sprite.update(0)

            self.draw()
            clock.tick(30)

        chosen = PET_ROSTER[self.selected_index]
        return {"id": chosen["id"], "name": chosen["name"], "color": chosen["color"], "style": chosen["style"]}

    def draw(self):
        self.screen.fill((245, 250, 255))
        title = self.font.render("Choose Your Companion", True, (20, 20, 20))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        for sprite in self.pet_sprites:
            sprite.draw(self.screen)

        chosen = PET_ROSTER[self.selected_index]
        info = self.small_font.render(f"Selected: {chosen['name']} • Press ENTER", True, (20, 20, 20))
        self.screen.blit(info, (WIDTH//2 - info.get_width()//2, 420))
        pygame.display.flip()


class OurWorldPygame:
    """
    Thin controller / game manager.

    Responsibilities:
    - Create and manage MainScene
    - Handle minigame launching
    - Top-level game loop and quitting
    - Save on exit

    Most gameplay logic now lives in MainScene.
    """

    def __init__(self, pet_config):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("OurWorld")
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.game_state.pet.name = pet_config["name"]
        self.pet_config = pet_config

        # Create the main gameplay scene
        self.main_scene = MainScene(self.game_state, self.screen, pet_config)
        self.current_scene = self.main_scene

        # Minigame state
        self.minigame = None
        self.minigame_type = None

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # Let current scene handle the event
                    if self.minigame:
                        if hasattr(self.minigame, 'handle_key') and event.type == pygame.KEYDOWN:
                            self.minigame.handle_key(event.key)
                        elif hasattr(self.minigame, 'handle_event'):
                            self.minigame.handle_event(event)
                    else:
                        self.current_scene.handle_event(event)

            # Update
            if self.minigame:
                self.minigame.update(dt)

                # Check if minigame ended
                if getattr(self.minigame, 'game_over', False):
                    self._handle_minigame_end()
            else:
                self.current_scene.update(dt)

                # Check if MainScene requested a minigame
                if self.current_scene.next_scene == "snake":
                    self._start_minigame("snake")
                elif self.current_scene.next_scene == "pet_dash":
                    self._start_minigame("pet_dash")

            # Draw
            if self.minigame and hasattr(self.minigame, 'draw'):
                self.minigame.draw(self.screen)
            else:
                self.current_scene.draw(self.screen)

            pygame.display.flip()

        self.game_state.save()
        pygame.quit()
        sys.exit()

    def _start_minigame(self, game_type: str):
        self.minigame_type = game_type
        MinigameClass = get_minigame(game_type)

        if game_type == "snake":
            self.minigame = MinigameClass(self.screen, self.clock)
        elif game_type == "pet_dash":
            self.minigame = MinigameClass(self.screen, self.clock, self.pet_config.get("color"))

        # Reset the request flag
        self.current_scene.next_scene = None

    def _handle_minigame_end(self):
        if not self.minigame:
            return

        score = getattr(self.minigame, 'score', 0)

        if self.minigame_type == "snake":
            bonus = min(40, score // 3)
            if bonus > 0:
                self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
            self.game_state.earn_coins(max(20, score // 2))
        elif self.minigame_type == "pet_dash":
            bonus = min(30, score // 4)
            if bonus > 0:
                self.game_state.pet.needs.happiness = min(100, self.game_state.pet.needs.happiness + bonus)
            self.game_state.earn_coins(max(15, score // 3))

        self.minigame = None
        self.minigame_type = None
        # Return to main scene
        self.current_scene.status = "Great job in the arcade!"


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    selection = PetSelectionScreen(screen)
    pet_config = selection.run()
    game = OurWorldPygame(pet_config)
    game.run()
