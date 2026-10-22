"""Static world data: locations, shop stock, map layout. No pygame imports."""
from __future__ import annotations

LOCATIONS = {
    "home": {
        "name": "Home", "desc": "Cozy and familiar. Resting here is extra restful.",
        "color": (139, 90, 43), "icon": "home", "type": "residential", "map": (0, 0),
    },
    "backyard": {
        "name": "Backyard", "desc": "Your garden bed. Plant seeds and harvest flowers.",
        "color": (101, 67, 33), "icon": "backyard", "type": "residential", "map": (1, 0),
    },
    "park": {
        "name": "Park", "desc": "Fresh air and open space. Playing here is extra fun.",
        "color": (34, 139, 34), "icon": "park", "type": "recreation", "map": (2, 0),
    },
    "sweeties_candy_shop": {
        "name": "Sweetie's Candy Shop", "short": "Sweeties", "desc": "Buy and eat delicious treats.",
        "color": (200, 50, 70), "icon": "candy_shop", "type": "shop", "map": (0, 1),
        "items": [
            {"key": "lollipop", "name": "Lollipop", "price": 10,
             "effect": {"hunger": 30, "happiness": 5}, "desc": "+30 Hunger", "eat": True},
            {"key": "candy_apple", "name": "Candy Apple", "price": 25,
             "effect": {"hunger": 65, "happiness": 10}, "desc": "+65 Hunger", "eat": True},
        ],
    },
    "gens_garden": {
        "name": "Gen's Garden", "short": "Gen's Garden", "desc": "Seeds for your backyard.",
        "color": (70, 130, 180), "icon": "gens_garden", "type": "shop", "map": (1, 1),
        "items": [
            {"key": "flower_seeds", "name": "Flower Seeds", "price": 12,
             "effect": {}, "desc": "Plant in Backyard", "eat": False},
            {"key": "sunflower_seeds", "name": "Sunflower Seeds", "price": 20,
             "effect": {}, "desc": "Plant in Backyard", "eat": False},
        ],
    },
    "arcade": {
        "name": "Arcade", "desc": "Lights and games. Win coins!",
        "color": (100, 149, 237), "icon": "arcade", "type": "entertainment", "map": (2, 1),
    },
    "pond": {
        "name": "Sunny Pond", "short": "Pond", "desc": "Sand, ducks and cool water. Swimming cleans and cheers.",
        "color": (40, 140, 190), "icon": "pond", "type": "recreation", "map": (0, 2),
    },
    "library": {
        "name": "Bookworm Library", "short": "Library", "desc": "Quiet stories lift the mood and rest the mind.",
        "color": (130, 80, 150), "icon": "library", "type": "civic", "map": (1, 2),
    },
    "spa": {
        "name": "Paws & Claws Spa", "short": "Spa", "desc": "Pampering for a price: the full refresh.",
        "color": (200, 100, 160), "icon": "spa", "type": "service", "map": (2, 2),
    },
}

MAP_COLS, MAP_ROWS = 3, 3

# One special action per new place. Pure data; GameState applies the rules.
#   need: refuse when this need is already full; min_energy: refuse when tired;
#   cost: coins; cooldown: seconds before it can be done again.
PLACE_ACTIONS = {
    "swim": {"location": "pond", "label": "Swim", "icon": "swim",
             "deltas": {"cleanliness": 28, "happiness": 12, "energy": -10, "hunger": -5},
             "need": "cleanliness", "min_energy": 15, "cost": 0, "cooldown": 0,
             "msg": "{name} splashed around. Wheee!",
             "refusal": "{name} is already clean and dry."},
    "read": {"location": "library", "label": "Read", "icon": "read",
             "deltas": {"happiness": 14, "energy": 6},
             "need": "happiness", "min_energy": 0, "cost": 0, "cooldown": 30,
             "msg": "{name} loved that story!",
             "refusal": "{name} is too giddy to sit still and read."},
    "pamper": {"location": "spa", "label": "Pamper", "icon": "spa",
               "deltas": {"cleanliness": 45, "energy": 20, "happiness": 10},
               "need": "cleanliness", "min_energy": 0, "cost": 18, "cooldown": 0,
               "msg": "Bubbles, brushing and a nap. {name} feels brand new!",
               "refusal": "{name} is already pampered and spotless."},
}


def place_actions_for(location: str) -> list:
    return [k for k, v in PLACE_ACTIONS.items() if v["location"] == location]


def location_at(col: int, row: int) -> str | None:
    for key, data in LOCATIONS.items():
        if data["map"] == (col, row):
            return key
    return None


def shop_items(location: str) -> list:
    return LOCATIONS.get(location, {}).get("items", [])


# Plants: seconds per growth stage, harvest reward.
PLANTS = {
    "flower": {"seed": "flower_seeds", "stage_secs": 45, "coins": 4, "happiness": 10},
    "sunflower": {"seed": "sunflower_seeds", "stage_secs": 70, "coins": 8, "happiness": 14},
}
SEED_TO_PLANT = {v["seed"]: k for k, v in PLANTS.items()}
MAX_STAGE = 3
GARDEN_SLOTS = 8
DECORATION_SECS = 30 * 60
FLOWERS_TO_DECORATE = 5
