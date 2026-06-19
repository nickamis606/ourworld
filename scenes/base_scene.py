#!/usr/bin/env python3
"""
BaseScene - Abstract base for all OurWorld scenes.

Provides common interface, lifecycle hooks, and shared utilities.

IMPORTANT: Subclasses MUST implement on_enter() / on_exit() to reset
any transient UI state (map_mode, open panels, active minigames, etc.)
so that state does not leak between scenes.
"""

import pygame
from typing import Optional, Any


class BaseScene:
    """
    Base class for all game scenes.

    Lifecycle:
        - on_enter(): Called by controller when this scene becomes the active one.
          Use to reset flags (e.g. map_mode=False), refresh UI, start music, etc.
        - on_exit(): Called by controller when leaving this scene.
          Use to close overlays (map, shop panels), stop animations, clean minigame state.

    Subclasses should implement:
        handle_event(event)
        update(dt)
        draw(surface)
        (and override on_enter/on_exit as needed)
    """

    def __init__(self, game_state: Any, screen: pygame.Surface):
        self.game_state = game_state
        self.screen = screen
        self.sprites = pygame.sprite.Group()  # Common sprite group
        self.active = True
        self.next_scene = None   # Scene switch request handled by controller

    def handle_event(self, event: pygame.event.Event):
        """Handle a single pygame event. Override in subclass."""
        pass

    def update(self, dt: float):
        """Update scene logic. Override in subclass."""
        self.sprites.update(dt)

    def draw(self, surface: pygame.Surface):
        """Draw the scene. Override in subclass. MUST start with full opaque background."""
        self.sprites.draw(surface)

    def on_enter(self):
        """Called when the scene becomes the current active scene.
        Override to reset transient state so nothing from previous visit leaks.
        """
        self.active = True

    def on_exit(self):
        """Called when leaving this scene (before switching away).
        Override to close any open overlays/panels (e.g. map_mode=False).
        """
        self.active = False

    def switch_to(self, new_scene: 'BaseScene'):
        """Helper to request a scene change (to be handled by main controller)."""
        self.next_scene = new_scene
