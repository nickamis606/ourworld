#!/usr/bin/env python3
"""
BaseScene - Abstract base for all OurWorld scenes.

Provides common interface and shared utilities.
"""

import pygame
from typing import Optional, Any


class BaseScene:
    """
    Base class for all game scenes.

    Subclasses should implement:
        handle_event(event)
        update(dt)
        draw(surface)
    """

    def __init__(self, game_state: Any, screen: pygame.Surface):
        self.game_state = game_state
        self.screen = screen
        self.sprites = pygame.sprite.Group()  # Common sprite group
        self.active = True

    def handle_event(self, event: pygame.event.Event):
        """Handle a single pygame event. Override in subclass."""
        pass

    def update(self, dt: float):
        """Update scene logic. Override in subclass."""
        self.sprites.update(dt)

    def draw(self, surface: pygame.Surface):
        """Draw the scene. Override in subclass."""
        self.sprites.draw(surface)

    def on_enter(self):
        """Called when the scene becomes active."""
        pass

    def on_exit(self):
        """Called when leaving the scene."""
        pass

    def switch_to(self, new_scene: 'BaseScene'):
        """Helper to request a scene change (to be handled by main controller)."""
        self.next_scene = new_scene
