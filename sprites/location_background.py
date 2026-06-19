#!/usr/bin/env python3
"""
LocationBackground - Asset-based background system for scenes.

Similar pattern to PetSprite:
- Tries to load PNG assets from assets/backgrounds/{location}/base.png
- Falls back to procedural drawing if no asset exists yet.
- Designed to support layered decorations in the future.
"""

import pygame
import os
from typing import Optional, Any


class LocationBackground:
    """
    Handles loading and drawing location backgrounds.
    
    Usage:
        bg = LocationBackground()
        bg.load("home")                    # or in MainScene __init__
        bg.draw(surface)
    """

    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.location: Optional[str] = None
        self.base_surface: Optional[pygame.Surface] = None
        self.use_asset = False

        # Base path for background assets
        self.assets_path = os.path.join("assets", "backgrounds")

    def load(self, location: str, procedural_fallback: Optional[callable] = None):
        """
        Load background for a location.
        Tries asset first, falls back to procedural if not found.
        """
        self.location = location
        self.base_surface = None
        self.use_asset = False

        # Try to load asset
        asset_path = os.path.join(self.assets_path, location, "base.png")

        if os.path.exists(asset_path):
            try:
                self.base_surface = pygame.image.load(asset_path).convert_alpha()
                # Scale to screen size if needed
                if self.base_surface.get_size() != (self.width, self.height):
                    self.base_surface = pygame.transform.smoothscale(
                        self.base_surface, (self.width, self.height)
                    )
                self.use_asset = True
                return
            except Exception:
                pass  # Fall through to procedural

        # Fallback to procedural (will be drawn by caller or stored)
        self.use_asset = False
        self.procedural_fallback = procedural_fallback

    def draw(self, surface: pygame.Surface):
        """Draw the background."""
        if self.use_asset and self.base_surface:
            surface.blit(self.base_surface, (0, 0))
        else:
            # Let the caller handle procedural drawing
            # or we can call a stored fallback if provided
            pass

    def has_asset(self) -> bool:
        return self.use_asset

    def get_current_location(self) -> Optional[str]:
        return self.location