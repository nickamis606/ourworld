#!/usr/bin/env python3
"""
LocationBackground

- Auto-scales layers
- Excludes 'pot.png' and 'decorations.png' (they are conditional)
"""

import pygame
import os
from typing import Optional, Dict, Tuple


class LocationBackground:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.location: Optional[str] = None
        self.base_surface: Optional[pygame.Surface] = None
        self.layers: Dict[str, Dict] = {}
        self.use_asset = False
        self.assets_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "assets", "backgrounds"
        )
        self.max_layer_height = 200

    def load(self, location: str):
        self.location = location
        self.base_surface = None
        self.layers = {}
        self.use_asset = False

        base_path = os.path.join(self.assets_path, location, "base.png")

        layers_dir = os.path.join(self.assets_path, location, "layers")
        has_base = False
        if os.path.exists(base_path):
            try:
                img = pygame.image.load(base_path).convert_alpha()
                self.base_surface = pygame.transform.smoothscale(img, (self.width, self.height))
                self.use_asset = True
                has_base = True
            except Exception:
                pass

        has_layers = os.path.isdir(layers_dir)
        if has_layers:
            for filename in os.listdir(layers_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    name = os.path.splitext(filename)[0]

                    if name in ("decorations", "pot"):
                        # Conditional inclusion per location
                        if self.location == "home":
                            pass  # fall through to load below
                        else:
                            continue

                    layer_path = os.path.join(layers_dir, filename)
                    try:
                        layer_img = pygame.image.load(layer_path).convert_alpha()

                        # Scale to fit within the screen while preserving aspect ratio
                        layer_w, layer_h = layer_img.get_size()
                        scale_w = self.width / layer_w
                        scale_h = self.height / layer_h
                        scale = min(scale_w, scale_h, 1.0)  # never upscale
                        new_w = int(layer_w * scale)
                        new_h = int(layer_h * scale)
                        layer_img = pygame.transform.smoothscale(layer_img, (new_w, new_h))

                        self.layers[name] = {
                            "surface": layer_img,
                            "pos": self._get_home_position(name)
                        }
                    except Exception:
                        pass

    def _get_home_position(self, name: str) -> Tuple[int, int]:
        positions = {
            "rug": (120, 310),
            "window": (470, 55),
            "shelf": (30, 90),
            "table": (380, 295),
            "decorations": (200, 180),
            "pot": (500, 320),
        }
        return positions.get(name, (100, 200))

    def draw(self, surface: pygame.Surface):
        if self.base_surface:
            surface.blit(self.base_surface, (0, 0))
        elif self.use_asset:
            # Procedural fallback when no base image exists
            self._draw_procedural(surface)

        order = ["rug", "table", "shelf", "window", "pot", "decorations"]
        for name in order:
            if name in self.layers:
                data = self.layers[name]
                surface.blit(data["surface"], data["pos"])

    def _draw_procedural(self, surface: pygame.Surface):
        """Fill with a solid colour as procedural background fallback."""
        if self.location == "home":
            surface.fill((220, 200, 180))
        else:
            surface.fill((200, 220, 200))

    def has_asset(self) -> bool:
        return self.use_asset