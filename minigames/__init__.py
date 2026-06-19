"""
OurWorld Minigames Package
"""
from .snake import SnakeGame
from .pet_dash import PetDash
from .frogger import FroggerGame

REGISTERED_GAMES = {
    "snake": SnakeGame,
    "pet_dash": PetDash,
    "frogger": FroggerGame,
}

def get_minigame(name: str):
    """Get a minigame class by name"""
    name = name.lower()
    if name in REGISTERED_GAMES:
        return REGISTERED_GAMES[name]
    raise ValueError(f"Minigame '{name}' not found. Available: {list(REGISTERED_GAMES.keys())}")