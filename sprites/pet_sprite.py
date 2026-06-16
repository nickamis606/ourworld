#!/usr/bin/env python3
"""
PetSprite - Reusable Pygame sprite for OurWorld pets.

Handles drawing of the 6 pet styles with bobbing animation.
Designed to be used in both the selection screen and main game scenes.

Future: Add support for action animations, mood expressions, and sprite sheets.
"""

import pygame
import math
from typing import Optional, Dict, Any


class PetSprite(pygame.sprite.Sprite):
    """
    A reusable sprite representing one of the OurWorld pets.

    Args:
        pet_config: Dict with keys: id, name, color, style
        size: Base size scale (default 1.0). Use >1.0 for in-game, <1.0 for previews.
        pos: Initial (x, y) center position
        pet_state: Optional reference to core.pet_state.PetState for mood/animation hooks
    """

    PET_STYLES = {
        0: "round",      # Bubbles
        1: "cat",        # Milo
        2: "round",      # Luna (with star)
        3: "plant",      # Sprout
        4: "round",      # Pip
        5: "star",       # Nova
    }

    def __init__(self, pet_config: Dict[str, Any], size: float = 1.0, pos: tuple = (0, 0),
                 pet_state: Optional[Any] = None):
        super().__init__()
        self.pet_config = pet_config
        self.pet_id = pet_config.get("id", 0)
        self.name = pet_config.get("name", "Pet")
        self.base_color = pet_config.get("color", (200, 200, 200))
        self.style = pet_config.get("style", "round")
        self.size_scale = size
        self.pet_state = pet_state  # for future mood/expression driving

        self.bob_offset = 0.0
        self.bob_speed = 0.08
        self.is_selected = False

        # Create initial surface (will be redrawn in update/draw)
        base_size = int(80 * self.size_scale)
        self.image = pygame.Surface((base_size, base_size + 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        # For action animation hooks (future)
        self.action_animator = None
        self.current_action = None

    def set_position(self, x: int, y: int):
        self.rect.center = (x, y)

    def set_bob(self, bob_value: float):
        """Set external bob value (used by selection screen)."""
        self.bob_offset = bob_value

    def set_selected(self, selected: bool):
        self.is_selected = selected

    def update(self, dt: float = 0.0):
        """Update bob animation. Call every frame with dt in seconds."""
        if dt > 0:
            self.bob_offset = (self.bob_offset + self.bob_speed * dt * 60) % (2 * math.pi)
        else:
            # Fallback for fixed-tick updates
            self.bob_offset = (self.bob_offset + self.bob_speed) % (2 * math.pi)

    def draw(self, surface: pygame.Surface):
        """Draw the pet centered on self.rect."""
        cx, cy = self.rect.center
        bob_y = int(5 * abs(math.pi - self.bob_offset) / math.pi) if self.is_selected else 0
        draw_y = cy + bob_y

        scale = self.size_scale
        self._draw_pet_body(surface, cx, draw_y, scale)

        # Draw name below pet
        if self.name:
            font = pygame.font.SysFont("Arial", int(13 * scale))
            name_surf = font.render(self.name, True, (20, 20, 20))
            surface.blit(name_surf, (cx - name_surf.get_width() // 2, draw_y + int(42 * scale)))

        # Selection highlight
        if self.is_selected:
            highlight_rect = pygame.Rect(cx - int(45 * scale), draw_y - int(55 * scale),
                                         int(90 * scale), int(105 * scale))
            pygame.draw.rect(surface, (255, 215, 0), highlight_rect, width=4, border_radius=12)

    def _draw_pet_body(self, surface: pygame.Surface, cx: int, cy: int, scale: float):
        """Internal method containing the pet drawing logic for all 6 styles."""
        pid = self.pet_id
        color = self.base_color

        if pid == 0:  # Bubbles - round pink
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(220, 120, 150), cheek_color=(255, 130, 170))
        elif pid == 1:  # Milo - cat green
            self._draw_cat_pet(surface, cx, cy, scale)
        elif pid == 2:  # Luna - round with star
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(120, 170, 220), accent_color=(255, 215, 0))
        elif pid == 3:  # Sprout - plant
            self._draw_plant_pet(surface, cx, cy, color, scale)
        elif pid == 4:  # Pip - round with bow
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(220, 180, 130), cheek_color=(255, 180, 200))
        elif pid == 5:  # Nova - star
            self._draw_star_pet(surface, cx, cy, color, scale)
        else:
            # Fallback simple circle
            r = int(30 * scale)
            pygame.draw.circle(surface, color, (cx, cy), r)

    def _draw_round_pet(self, surface, cx, cy, color, scale, ear_color=None, cheek_color=None, accent_color=None):
        s = scale
        # Body
        pygame.draw.ellipse(surface, color, (cx - int(34*s), cy - int(10*s), int(68*s), int(62*s)))
        pygame.draw.ellipse(surface, ear_color or (220, 120, 150),
                            (cx - int(34*s), cy - int(10*s), int(68*s), int(62*s)), int(4*s))
        # Head
        pygame.draw.ellipse(surface, color, (cx - int(28*s), cy - int(40*s), int(56*s), int(42*s)))
        # Ears
        pygame.draw.ellipse(surface, ear_color or (255, 130, 170), (cx - int(30*s), cy - int(48*s), int(22*s), int(18*s)))
        pygame.draw.ellipse(surface, cheek_color or (255, 80, 140), (cx - int(26*s), cy - int(45*s), int(12*s), int(10*s)))
        pygame.draw.ellipse(surface, ear_color or (255, 130, 170), (cx + int(8*s), cy - int(48*s), int(22*s), int(18*s)))
        pygame.draw.ellipse(surface, cheek_color or (255, 80, 140), (cx + int(14*s), cy - int(45*s), int(12*s), int(10*s)))
        # Eyes
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(16*s), cy - int(26*s), int(14*s), int(13*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + int(2*s), cy - int(26*s), int(14*s), int(13*s)))
        pygame.draw.ellipse(surface, (60, 90, 200), (cx - int(12*s), cy - int(23*s), int(7*s), int(7*s)))
        pygame.draw.ellipse(surface, (60, 90, 200), (cx + int(6*s), cy - int(23*s), int(7*s), int(7*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(9*s), cy - int(21*s), int(4*s), int(4*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(9*s), cy - int(21*s), int(4*s), int(4*s)))
        # Mouth
        pygame.draw.arc(surface, (80, 80, 80), (cx - int(8*s), cy - int(10*s), int(16*s), int(9*s)), 0, math.pi, int(2*s))

        if accent_color:  # For Luna star
            pygame.draw.polygon(surface, accent_color, [
                (cx, cy - int(48*s)), (cx - int(14*s), cy - int(36*s)), (cx - int(7*s), cy - int(36*s)),
                (cx - int(3*s), cy - int(44*s)), (cx + int(3*s), cy - int(44*s)), (cx + int(7*s), cy - int(36*s)),
                (cx + int(14*s), cy - int(36*s))
            ])

    def _draw_cat_pet(self, surface, cx, cy, scale):
        s = scale
        pygame.draw.ellipse(surface, (70, 170, 85), (cx - int(30*s), cy - int(8*s), int(60*s), int(55*s)))
        pygame.draw.ellipse(surface, (45, 130, 60), (cx - int(30*s), cy - int(8*s), int(60*s), int(55*s)), int(4*s))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(22*s), cy - int(30*s), int(44*s), int(32*s)))
        pygame.draw.ellipse(surface, (70, 170, 85), (cx - int(20*s), cy - int(36*s), int(16*s), int(14*s)))
        pygame.draw.ellipse(surface, (70, 170, 85), (cx + int(4*s), cy - int(36*s), int(16*s), int(14*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(13*s), cy - int(22*s), int(11*s), int(10*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + int(2*s), cy - int(22*s), int(11*s), int(10*s)))
        pygame.draw.ellipse(surface, (40, 70, 160), (cx - int(9*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (40, 70, 160), (cx + int(6*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(6*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(9*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.arc(surface, (50, 50, 50), (cx - int(5*s), cy - int(8*s), int(10*s), int(6*s)), 0, math.pi, int(2*s))

    def _draw_plant_pet(self, surface, cx, cy, color, scale):
        s = scale
        pygame.draw.ellipse(surface, color, (cx - int(26*s), cy - int(5*s), int(52*s), int(50*s)))
        pygame.draw.ellipse(surface, (120, 200, 130), (cx - int(26*s), cy - int(5*s), int(52*s), int(50*s)), int(4*s))
        pygame.draw.ellipse(surface, color, (cx - int(22*s), cy - int(32*s), int(44*s), int(36*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(20*s), cy - int(42*s), int(40*s), int(18*s)))
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy - int(48*s)), int(8*s))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(11*s), cy - int(20*s), int(10*s), int(9*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + int(1*s), cy - int(20*s), int(10*s), int(9*s)))
        pygame.draw.ellipse(surface, (60, 100, 200), (cx - int(8*s), cy - int(17*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (60, 100, 200), (cx + int(6*s), cy - int(17*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(5*s), cy - int(15*s), int(3*s), int(3*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(7*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.arc(surface, (60, 60, 60), (cx - int(5*s), cy - int(8*s), int(10*s), int(6*s)), 0, math.pi, int(2*s))

    def _draw_star_pet(self, surface, cx, cy, color, scale):
        s = scale
        pygame.draw.ellipse(surface, color, (cx - int(26*s), cy - int(5*s), int(52*s), int(48*s)))
        pygame.draw.ellipse(surface, (160, 120, 200), (cx - int(26*s), cy - int(5*s), int(52*s), int(48*s)), int(4*s))
        pygame.draw.ellipse(surface, color, (cx - int(24*s), cy - int(32*s), int(48*s), int(36*s)))
        pygame.draw.ellipse(surface, (180, 200, 255), (cx - int(20*s), cy - int(40*s), int(40*s), int(12*s)))
        # Star points
        pygame.draw.polygon(surface, (255, 215, 80), [
            (cx - int(8*s), cy - int(38*s)), (cx - int(5*s), cy - int(45*s)), (cx - int(2*s), cy - int(38*s))
        ])
        pygame.draw.polygon(surface, (255, 215, 80), [
            (cx + int(8*s), cy - int(38*s)), (cx + int(5*s), cy - int(45*s)), (cx + int(2*s), cy - int(38*s))
        ])
        pygame.draw.ellipse(surface, color, (cx - int(22*s), cy - int(40*s), int(12*s), int(12*s)))
        pygame.draw.ellipse(surface, color, (cx + int(10*s), cy - int(40*s), int(12*s), int(12*s)))
        # Eyes
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(13*s), cy - int(20*s), int(11*s), int(10*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + int(2*s), cy - int(20*s), int(11*s), int(10*s)))
        pygame.draw.ellipse(surface, (90, 130, 255), (cx - int(9*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (90, 130, 255), (cx + int(6*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(7*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(9*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.arc(surface, (60, 60, 60), (cx - int(6*s), cy - int(8*s), int(12*s), int(7*s)), 0, math.pi, int(2*s))

    def get_current_mood(self) -> str:
        """Placeholder for future mood system integration."""
        if self.pet_state and hasattr(self.pet_state, 'needs'):
            avg = (self.pet_state.needs.hunger + self.pet_state.needs.happiness +
                   self.pet_state.needs.energy + self.pet_state.needs.cleanliness) / 4
            if avg > 70:
                return "happy"
            elif avg > 40:
                return "okay"
            else:
                return "sad"
        return "neutral"


# Quick test function (can be run standalone)
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    test_pets = [
        {"id": 0, "name": "Bubbles", "color": (255, 182, 193), "style": "round"},
        {"id": 1, "name": "Milo", "color": (255, 200, 150), "style": "cat"},
        {"id": 2, "name": "Luna", "color": (180, 220, 255), "style": "round"},
        {"id": 3, "name": "Sprout", "color": (200, 255, 180), "style": "plant"},
        {"id": 4, "name": "Pip", "color": (255, 220, 150), "style": "round"},
        {"id": 5, "name": "Nova", "color": (220, 180, 255), "style": "star"},
    ]

    sprites = []
    for i, cfg in enumerate(test_pets):
        x = 100 + (i % 3) * 220
        y = 150 + (i // 3) * 220
        ps = PetSprite(cfg, size=1.2, pos=(x, y))
        ps.set_selected(i == 0)
        sprites.append(ps)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((245, 250, 255))
        dt = clock.tick(60) / 1000.0

        for ps in sprites:
            ps.update(dt)
            ps.draw(screen)

        pygame.display.flip()

    pygame.quit()
