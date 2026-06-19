#!/usr/bin/env python3
"""
LocationBackground - Asset-based background system for scenes.

Supports base image + multiple layers with positioning.
"""

import pygame
import os
from typing import Optional, Dict, Tuple


class LocationBackground:
    """
    Handles loading and drawing location backgrounds with layers.
    
    For Home, it loads base.png + all images in layers/ folder.
    """

    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.location: Optional[str] = None
        self.base_surface: Optional[pygame.Surface] = None
        self.layers: Dict[str, Dict] = {}   # name -> {'surface': Surface, 'pos': (x, y)}
        self.use_asset = False
        self.assets_path = os.path.join("assets", "backgrounds")

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
            except Exception as e:
                print(f"Failed to load base.png for {location}: {e}")
                return

            # Load layers if they exist
            layers_dir = os.path.join(self.assets_path, location, "layers")
            if os.path.isdir(layers_dir):
                for filename in os.listdir(layers_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        layer_path = os.path.join(layers_dir, filename)
                        try:
                            layer_img = pygame.image.load(layer_path).convert_alpha()
                            # Store with default positioning (can be improved later)
                            name = os.path.splitext(filename)[0]
                            self.layers[name] = {
                                "surface": layer_img,
                                "pos": self._get_default_position(name)
                            }
                        except Exception as e:
                            print(f"Failed to load layer {filename}: {e}")

    def _get_default_position(self, layer_name: str) -> Tuple[int, int]:
        """Reasonable default positions for Home layers."""
        defaults = {
            "rug": (180, 340),
            "window": (480, 60),
            "table": (280, 320),
            "shelf": (40, 100),
            "decorations": (480, 280),
        }
        return defaults.get(layer_name, (100, 200))

    def draw(self, surface: pygame.Surface):
        if not self.use_asset or not self.base_surface:
            return

        # Draw base
        surface.blit(self.base_surface, (0, 0))

        # Draw layers in a sensible order
        draw_order = ["rug", "table", "shelf", "window", "decorations"]

        for name in draw_order:
            if name in self.layers:
                data = self.layers[name]
                surface.blit(data["surface"], data["pos"])

    def has_asset(self) -> bool:
        return self.use_asset