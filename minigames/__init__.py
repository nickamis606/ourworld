"""OurWorld minigames.

Each game exposes: handle_key(key), update(dt), draw(surface), score,
game_over. Scenes drive them through ``press(game, action)`` so they work
with the unified input layer (D-pad + A) without each game knowing about pads.
"""
import pygame

from .snake import SnakeGame
from .pet_dash import PetDash
from .frogger import FroggerGame
from .brick_bop import BrickBop
from .pet_pairs import PetPairs
from .mole_pop import MolePop

REGISTERED_GAMES = {"snake": SnakeGame, "pet_dash": PetDash, "frogger": FroggerGame,
                    "brick_bop": BrickBop, "pet_pairs": PetPairs, "mole_pop": MolePop}
GAME_INFO = {
    "snake": {"name": "Snake", "how": "D-pad to steer. Eat treats, don't bite yourself!",
              "color": (80, 190, 110)},
    "pet_dash": {"name": "Pet Dash", "how": "A or Up to jump (twice for a double jump).",
                 "color": (240, 150, 70)},
    "frogger": {"name": "Frogger", "how": "D-pad to hop. Ride logs, dodge cars, fill 5 homes.",
                "color": (90, 160, 240)},
    "brick_bop": {"name": "Brick Bop", "how": "Hold Left/Right to move the paddle, A to launch.",
                  "color": (230, 100, 140)},
    "pet_pairs": {"name": "Pet Pairs", "how": "D-pad + A to flip cards. Match all 8 pairs fast!",
                  "color": (120, 140, 230)},
    "mole_pop": {"name": "Mole Pop", "how": "D-pad to aim, A to bop. Golden moles are worth 3x.",
                 "color": (170, 120, 70)},
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
    if getattr(game, "game_over", False):
        return
    if hasattr(game, "handle_action"):
        game.handle_action(action)
        return
    key = _ACTION_KEYS.get(action)
    if key is not None:
        game.handle_key(key)
