"""Static world data: locations, shop stock, map layout. No pygame imports."""

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
}

MAP_COLS, MAP_ROWS = 3, 2


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
