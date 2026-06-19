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
        self.assets_path = os.path.join("assets", "backgrounds")
        self.max_layer_height = 200

    def load(self, location: str):
        self.location = location
        self.base_surface = None
        self.layers = {}
        self.use_asset = False

        base_path = os.path.join(self.assets_path, location, "base.png")

        if os.path.exists(base_path):
            try:
                img = pygame.image.load(base_path).convert_alpha()
                self.base_surface = pygame.transform.smoothscale(img, (self.width, self.height))
                self.use_asset = True
            except Exception:
                return

            layers_dir = os.path.join(self.assets_path, location, "layers")
            if os.path.isdir(layers_dir):
                for filename in os.listdir(layers_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        name = os.path.splitext(filename)[0]

                        # These are handled conditionally elsewhere
                        if name in ("decorations", "pot"):
                            continue

                        layer_path = os.path.join(layers_dir, filename)
                        try:
                            layer_img = pygame.image.load(layer_path).convert_alpha()

                            if layer_img.get_height() > self.max_layer_height:
                                scale = self.max_layer_height / layer_img.get_height()
                                new_width = int(layer_img.get_width() * scale)
                                layer_img = pygame.transform.smoothscale(layer_img, (new_width, self.max_layer_height))

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
        }
        return positions.get(name, (100, 200))

    def draw(self, surface: pygame.Surface):
        if not self.use_asset or not self.base_surface:
            return

        surface.blit(self.base_surface, (0, 0))

        order = ["rug", "table", "shelf", "window"]
        for name in order:
            if name in self.layers:
                data = self.layers[name]
                surface.blit(data["surface"], data["pos"])

    def has_asset(self) -> bool:
        return self.use_asset