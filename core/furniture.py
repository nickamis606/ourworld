"""Home decorating: furniture data and the Home grid. Pure Python.

The Home has an 8x3 grid: row 0 is the wall (pictures, clocks, lights),
rows 1-2 are the floor. Each placed item makes Home a little cozier
(joy drops a bit slower there, up to a cap).
"""
from __future__ import annotations

GRID_COLS, GRID_ROWS = 8, 3
WALL_ROW = 0
COZY_PER_ITEM = 0.04
COZY_MAX = 0.32

# key: name, wall?, color, where to get it
FURNITURE = {
    "picture":    ("Family Picture", True, (230, 170, 90), "Mayor Maple's welcome gift"),
    "clock":      ("Cuckoo Clock", True, (170, 110, 70), "Olive's thank-you"),
    "star_lights": ("Star Lights", True, (250, 220, 90), "Sweetie's shop"),
    "garland":    ("Leaf Garland", True, (220, 120, 50), "Harvest Fair prize"),
    "plant":      ("Potted Fern", False, (90, 170, 90), "Gen's Garden"),
    "lamp":       ("Cozy Lamp", False, (250, 210, 120), "Gen's Garden"),
    "toy_box":    ("Toy Box", False, (220, 90, 90), "a Park friend's gift"),
    "cushion":    ("Pet Cushion", False, (180, 130, 220), "Sweetie's shop"),
    "beanbag":    ("Bean Bag", False, (90, 160, 230), "Gen's Garden"),
    "bookshelf":  ("Little Bookshelf", False, (150, 100, 60), "Olive's library prize"),
    "fishbowl":   ("Fish Bowl", False, (140, 210, 250), "catch 6 kinds of fish"),
    "trophy":     ("Arcade Trophy", False, (250, 200, 60), "win a Weekly Challenge"),
    "pumpkin":    ("Big Pumpkin", False, (240, 130, 40), "Harvest Fair prize"),
    "snowglobe":  ("Snow Globe", False, (200, 230, 255), "Snow Day prize"),
    "egg_basket": ("Egg Basket", False, (250, 190, 210), "Spring Egg Hunt prize"),
    "beach_ball": ("Beach Ball", False, (250, 100, 100), "Summer Splash prize"),
}
FURNITURE_ORDER = list(FURNITURE)

# quest -> furniture handed over with the quest reward
QUEST_FURNITURE = {"welcome": "picture", "park_laughs": "toy_box", "lost_book": "bookshelf",
                   "spa_day": "cushion", "festival_prep": "clock"}


def is_wall(key: str) -> bool:
    return FURNITURE[key][1]


def valid_cell(col, row) -> bool:
    return isinstance(col, int) and isinstance(row, int) and 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS


def fits(key: str, row: int) -> bool:
    return (row == WALL_ROW) == is_wall(key)


def cozy_factor(n_placed: int) -> float:
    return 1.0 - min(COZY_MAX, COZY_PER_ITEM * n_placed)
