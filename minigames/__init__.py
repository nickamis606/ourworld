"""OurWorld minigames.

Each game exposes: handle_key(key), update(dt), draw(surface), score,
game_over. Scenes drive them through ``press(game, action)`` so they work
with the unified input layer (D-pad + A) without each game knowing about pads.
"""
import pygame

from .snake import SnakeGame
from .pet_dash import PetDash
from .frogger import FroggerGame

REGISTERED_GAMES = {"snake": SnakeGame, "pet_dash": PetDash, "frogger": FroggerGame}
GAME_INFO = {
    "snake": {"name": "Snake", "how": "D-pad to steer. Eat treats, don't bite yourself!",
              "color": (80, 190, 110)},
    "pet_dash": {"name": "Pet Dash", "how": "A or Up to jump (twice for a double jump).",
                 "color": (240, 150, 70)},
    "frogger": {"name": "Frogger", "how": "D-pad to hop. Ride logs, dodge cars, fill 5 homes.",
                "color": (90, 160, 240)},
}
_ACTION_KEYS = {"UP": pygame.K_UP, "DOWN": pygame.K_DOWN, "LEFT": pygame.K_LEFT,
                "RIGHT": pygame.K_RIGHT, "A": pygame.K_SPACE}


def get_minigame(name: str):
    name = name.lower()
    if name in REGISTERED_GAMES:
        return REGISTERED_GAMES[name]
    raise ValueError(f"Minigame '{name}' not found. Available: {list(REGISTERED_GAMES)}")


def create(name: str, screen, pet_color=None):
    cls = get_minigame(name)
    clock = pygame.time.Clock()
    if name == "pet_dash":
        return cls(screen, clock, pet_color)
    return cls(screen, clock)


def press(game, action: str) -> None:
    key = _ACTION_KEYS.get(action)
    if key is not None and not getattr(game, "game_over", False):
        game.handle_key(key)
