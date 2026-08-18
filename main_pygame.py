#!/usr/bin/env python3
"""
OurWorld - Thin controller with proper scene management

Now supports clean switching between MainScene and ArcadeScene.
Uses on_enter/on_exit lifecycle to prevent state leakage (map staying visible, etc).
"""

import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.game_state import GameState
from scenes.main_scene import MainScene
from scenes.arcade_scene import ArcadeScene

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
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.selected_index = 0
        self.bob = 0.0
        self.done = False

        from sprites.pet_sprite import PetSprite
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
    Thin scene manager / controller.

    Responsibilities:
    - Owns the scene instances (reuses MainScene for performance)
    - Handles switching via next_scene flag
    - Calls on_enter/on_exit lifecycle so scenes can reset transient state
      (prevents bugs like map staying visible when returning from Arcade)
    """

    def __init__(self, pet_config):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("OurWorld")
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.game_state.pet.name = pet_config["name"]
        self.pet_config = pet_config

        self.main_scene = MainScene(self.game_state, self.screen, pet_config)
        self.arcade_scene = None
        self.current_scene = self.main_scene
        # Initial enter
        self.current_scene.on_enter()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.current_scene.handle_event(event)

            self.current_scene.update(dt)

            # === Scene switching logic with lifecycle ===
            next_name = getattr(self.current_scene, 'next_scene', None)

            if next_name == "arcade":
                old_scene = self.current_scene
                if self.arcade_scene is None:
                    self.arcade_scene = ArcadeScene(self.game_state, self.screen)
                self.current_scene = self.arcade_scene

                old_scene.next_scene = None
                old_scene.on_exit()
                self.current_scene.on_enter()
                self.current_scene.next_scene = None

            elif next_name == "main":
                old_scene = self.current_scene
                self.current_scene = self.main_scene

                old_scene.next_scene = None
                old_scene.on_exit()
                self.current_scene.on_enter()
                self.current_scene.next_scene = None
                self.arcade_scene = None  # clean up arcade instance

            self.current_scene.draw(self.screen)

            # Draw save indicator flash.
            indicator = self.game_state.save_manager.get_save_indicator(self.screen)
            if indicator:
                alpha, x, y = indicator
                text = self.main_scene.small_font.render("💾 Saved", True, (255, 255, 255))
                surf = pygame.Surface((text.get_width() + 8, text.get_height() + 4), pygame.SRCALPHA)
                pygame.draw.rect(surf, (40, 40, 40, alpha), surf.get_rect(), border_radius=4)
                surf.blit(text, (4, 2))
                self.screen.blit(surf, (x - surf.get_width(), y - surf.get_height()))

            pygame.display.flip()

        self.game_state.save()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    selection = PetSelectionScreen(screen)
    pet_config = selection.run()
    game = OurWorldPygame(pet_config)
    game.run()
