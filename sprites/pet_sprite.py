#!/usr/bin/env python3
"""
PetSprite - Reusable Pygame sprite for OurWorld pets.

Now supports both:
- Small sprite assets from assets/pets/ (recommended for visual quality)
- Procedural fallback drawing (if no sprite file exists)

Place optimized sprites in: assets/pets/<lowercase_name>.png

When a sprite is loaded, it is automatically normalized to a consistent
base size (~120px tall) so the `size=` parameter behaves predictably.
"""

import pygame
import math
from pathlib import Path
from typing import Optional, Dict, Any


class PetSprite(pygame.sprite.Sprite):
    """
    A reusable sprite representing one of the OurWorld pets.

    Supports sprite assets + procedural fallback.
    Loaded sprites are normalized to a sensible base size.
    """

    # Mapping from pet name (lowercase) to filename
    PET_SPRITE_NAMES = {
        0: "bubbles",
        1: "milo",
        2: "luna",
        3: "sprout",
        4: "pip",
        5: "nova",
    }

    TARGET_HEIGHT = 120   # Normalized height for loaded sprites

    def __init__(self, pet_config: Dict[str, Any], size: float = 1.0, pos: tuple = (0, 0),
                 pet_state: Optional[Any] = None):
        super().__init__()
        self.pet_config = pet_config
        self.pet_id = pet_config.get("id", 0)
        self.name = pet_config.get("name", "Pet")
        self.base_color = pet_config.get("color", (200, 200, 200))
        self.style = pet_config.get("style", "round")
        self.size_scale = size
        self.pet_state = pet_state

        self.bob_offset = 0.0
        self.bob_speed = 0.08
        self.is_selected = False

        # Try to load sprite asset first
        self.sprite_image = self._load_sprite()

        if self.sprite_image:
            w, h = self.sprite_image.get_size()
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        else:
            base_size = int(80 * self.size_scale)
            self.image = pygame.Surface((base_size, base_size + 20), pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=pos)

        self.action_animator = None
        self.current_action = None

    def _load_sprite(self) -> Optional[pygame.Surface]:
        """Try to load a sprite from assets/pets/ and auto-center the content.

        Assets may have the pet offset from the center (e.g. 832×1248 PNGs).
        We compute the bounding box of non-transparent pixels, center that
        within a new surface, then scale to TARGET_HEIGHT so the drawn pet
        appears correctly centred at rect.center.
        """
        sprite_name = self.PET_SPRITE_NAMES.get(self.pet_id)
        if not sprite_name:
            return None

        possible_paths = [
            Path("assets/pets") / f"{sprite_name}.png",
            Path(__file__).parent.parent / "assets/pets" / f"{sprite_name}.png",
            Path("assets/pets") / f"{sprite_name}.jpg",
            Path(__file__).parent.parent / "assets/pets" / f"{sprite_name}.jpg",
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    img = pygame.image.load(str(path)).convert_alpha()

                    # Auto-center content within the loaded image
                    img = self._center_content(img)

                    # Normalize to consistent target height
                    if img.get_height() != self.TARGET_HEIGHT:
                        ratio = self.TARGET_HEIGHT / img.get_height()
                        new_width = int(img.get_width() * ratio)
                        img = pygame.transform.smoothscale(img, (new_width, self.TARGET_HEIGHT))

                    print(f"[PetSprite] Loaded and normalized: {path.name} -> {img.get_size()}")
                    return img
                except Exception as e:
                    print(f"[PetSprite] Failed to load {path}: {e}")
                    continue

        print(f"[PetSprite] WARNING: No sprite found for '{sprite_name}' (pet_id={self.pet_id})")
        return None

    def _center_content(self, img: pygame.Surface) -> pygame.Surface:
        """Reposition visible (non-transparent) content so its centre aligns with the image centre.

        Returns a new surface of the same dimensions as the original.
        """
        data = img.tobytes()
        w, h = img.get_size()

        # Find bounding box of non-transparent pixels
        min_x, max_x, min_y, max_y = w, 0, h, 0
        for y in range(h):
            row_offset = y * w * 4
            for x in range(w):
                a = data[row_offset + x * 4 + 3]
                if a > 0:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y

        # No visible content — return as-is
        if max_x < min_x or max_y < min_y:
            return img

        content_w = max_x - min_x + 1
        content_h = max_y - min_y + 1
        # Create output surface same size, filled transparent
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        # Center the content box within the original frame
        dst_x = (w - content_w) // 2
        dst_y = (h - content_h) // 2

        src_rect = pygame.Rect(min_x, min_y, content_w, content_h)
        dst_rect = pygame.Rect(dst_x, dst_y, content_w, content_h)
        surface.blit(img, dst_rect, src_rect)
        return surface

    def set_position(self, x: int, y: int):
        self.rect.center = (x, y)

    def set_bob(self, bob_value: float):
        self.bob_offset = bob_value

    def set_selected(self, selected: bool):
        self.is_selected = selected

    def update(self, dt: float = 0.0):
        if dt > 0:
            self.bob_offset = (self.bob_offset + self.bob_speed * dt * 60) % (2 * math.pi)
        else:
            self.bob_offset = (self.bob_offset + self.bob_speed) % (2 * math.pi)

    def draw(self, surface: pygame.Surface):
        cx, cy = self.rect.center
        bob_y = int(5 * abs(math.pi - self.bob_offset) / math.pi) if self.is_selected else 0
        draw_y = cy + bob_y

        scale = self.size_scale

        if self.sprite_image:
            scaled = pygame.transform.smoothscale(
                self.sprite_image,
                (int(self.sprite_image.get_width() * scale),
                 int(self.sprite_image.get_height() * scale))
            )
            sprite_rect = scaled.get_rect(center=(cx, draw_y))
            surface.blit(scaled, sprite_rect)
        else:
            self._draw_pet_body(surface, cx, draw_y, scale)

        if self.name:
            font = pygame.font.SysFont("Arial", int(13 * scale))
            name_surf = font.render(self.name, True, (20, 20, 20))
            surface.blit(name_surf, (cx - name_surf.get_width() // 2, draw_y + int(42 * scale)))

        if self.is_selected:
            highlight_rect = pygame.Rect(cx - int(45 * scale), draw_y - int(55 * scale),
                                         int(90 * scale), int(105 * scale))
            pygame.draw.rect(surface, (255, 215, 0), highlight_rect, width=4, border_radius=12)

    def _draw_pet_body(self, surface, cx, cy, scale):
        pid = self.pet_id
        color = self.base_color

        if pid == 0:
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(220, 120, 150), cheek_color=(255, 130, 170))
        elif pid == 1:
            self._draw_cat_pet(surface, cx, cy, scale)
        elif pid == 2:
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(120, 170, 220), accent_color=(255, 215, 0))
        elif pid == 3:
            self._draw_plant_pet(surface, cx, cy, color, scale)
        elif pid == 4:
            self._draw_round_pet(surface, cx, cy, color, scale,
                                 ear_color=(220, 180, 130), cheek_color=(255, 180, 200))
        elif pid == 5:
            self._draw_star_pet(surface, cx, cy, color, scale)
        else:
            r = int(30 * scale)
            pygame.draw.circle(surface, color, (cx, cy), r)

    def _draw_round_pet(self, surface, cx, cy, color, scale, ear_color=None, cheek_color=None, accent_color=None):
        s = scale
        pygame.draw.ellipse(surface, color, (cx - int(34*s), cy - int(10*s), int(68*s), int(62*s)))
        pygame.draw.ellipse(surface, ear_color or (220, 120, 150),
                            (cx - int(34*s), cy - int(10*s), int(68*s), int(62*s)), int(4*s))
        pygame.draw.ellipse(surface, color, (cx - int(28*s), cy - int(40*s), int(56*s), int(42*s)))
        pygame.draw.ellipse(surface, ear_color or (255, 130, 170), (cx - int(30*s), cy - int(48*s), int(22*s), int(18*s)))
        pygame.draw.ellipse(surface, cheek_color or (255, 80, 140), (cx - int(26*s), cy - int(45*s), int(12*s), int(10*s)))
        pygame.draw.ellipse(surface, ear_color or (255, 130, 170), (cx + int(8*s), cy - int(48*s), int(22*s), int(18*s)))
        pygame.draw.ellipse(surface, cheek_color or (255, 80, 140), (cx + int(14*s), cy - int(45*s), int(12*s), int(10*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - int(16*s), cy - int(26*s), int(14*s), int(13*s)))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + int(2*s), cy - int(26*s), int(14*s), int(13*s)))
        pygame.draw.ellipse(surface, (60, 90, 200), (cx - int(12*s), cy - int(23*s), int(7*s), int(7*s)))
        pygame.draw.ellipse(surface, (60, 90, 200), (cx + int(6*s), cy - int(23*s), int(7*s), int(7*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(9*s), cy - int(21*s), int(4*s), int(4*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(9*s), cy - int(21*s), int(4*s), int(4*s)))
        pygame.draw.arc(surface, (80, 80, 80), (cx - int(8*s), cy - int(10*s), int(16*s), int(9*s)), 0, math.pi, int(2*s))

        if accent_color:
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
        pygame.draw.polygon(surface, (255, 215, 80), [
            (cx - int(8*s), cy - int(38*s)), (cx - int(5*s), cy - int(45*s)), (cx - int(2*s), cy - int(38*s))
        ])
        pygame.draw.polygon(surface, (255, 215, 80), [
            (cx + int(8*s), cy - int(38*s)), (cx + int(5*s), cy - int(45*s)), (cx + int(2*s), cy - int(38*s))
        ])
        pygame.draw.ellipse(surface, color, (cx - int(22*s), cy - int(40*s), int(12*s), int(12*s)))
        pygame.draw.ellipse(surface, color, (cx + int(10*s), cy - int(40*s), int(12*s), int(12*s)))
        pygame.draw.ellipse(surface, (90, 130, 255), (cx - int(9*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (90, 130, 255), (cx + int(6*s), cy - int(19*s), int(5*s), int(5*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx - int(7*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.ellipse(surface, (20, 20, 20), (cx + int(9*s), cy - int(17*s), int(3*s), int(3*s)))
        pygame.draw.arc(surface, (60, 60, 60), (cx - int(6*s), cy - int(8*s), int(12*s), int(7*s)), 0, math.pi, int(2*s))

    def get_current_mood(self) -> str:
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
        ps = PetSprite(cfg, size=1.0, pos=(x, y))
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
