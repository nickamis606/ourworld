import json
import os
import time
from .pet_state import PetState
from .savegame import SaveManager


class GameState:
    SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saves", "savegame.json")

    LOCATIONS = {
        "home": {"name": "Home", "desc": "Cozy and familiar", "color": (139, 69, 19), "icon": "home", "type": "residential"},
        "park": {"name": "Park", "desc": "Fresh air and open space", "color": (46, 139, 87), "icon": "park", "type": "recreation"},
        "arcade": {"name": "Arcade", "desc": "Lights and games", "color": (65, 105, 225), "icon": "arcade", "type": "entertainment"},
        "backyard": {"name": "Backyard", "desc": "Garden spot and fresh air", "color": (85, 140, 80), "icon": "backyard", "type": "residential"},
        "sweeties_candy_shop": {
            "name": "Sweetie's Candy Shop",
            "desc": "Buy and eat delicious treats",
            "color": (220, 60, 80),
            "icon": "candy_shop",
            "type": "shop",
            "items": [
                {"key": "lollipop", "name": "Lollipop", "price": 10, "effect": {"hunger": 40}, "desc": "+40 Hunger"},
                {"key": "candy_apple", "name": "Candy Apple", "price": 25, "effect": {"hunger": 75}, "desc": "+75 Hunger"},
            ]
        },
        "gens_garden": {
            "name": "Gen's Garden",
            "desc": "Plants and seeds for your backyard",
            "color": (70, 130, 180),
            "icon": "gens_garden",
            "type": "shop",
            "items": [
                {"key": "flower_seeds", "name": "Flower Seeds", "price": 12, "effect": {"happiness": 45}, "desc": "+45 Happiness"},
                {"key": "sunflower_seeds", "name": "Sunflower Seeds", "price": 20, "effect": {"happiness": 60, "energy": 15}, "desc": "+60 Happiness"},
            ]
        },
    }

    def __init__(self):
        self.pet = PetState()
        self.save_manager = SaveManager(self)
        self._has_save = self.load()

    @property
    def has_save(self) -> bool:
        """True when a valid previous save exists."""
        return self._has_save

    def tick(self):
        self.pet.tick()
        self._grow_garden()
        self._decay_home_decoration()

    def _grow_garden(self):
        now = time.monotonic()
        for plant in self.pet.garden:
            if plant.get("stage", 0) >= 3:
                continue
            planted_time = plant.get("planted_time", now)
            time_since = now - planted_time
            if time_since > 60 * (plant.get("stage", 0) + 1):
                plant["stage"] = plant.get("stage", 0) + 1

    def change_location(self, new_location: str) -> bool:
        """Change pet location. Returns True if the location changed."""
        if new_location in self.LOCATIONS:
            self.pet.location = new_location
            self.trigger_auto_save()
            return True
        return False

    def get_current_location_info(self):
        return self.LOCATIONS.get(self.pet.location, self.LOCATIONS["home"])

    def perform_care_action(self, action: str) -> dict:
        location = self.pet.location
        bonus_applied = None
        extra = 0

        success = self.pet.apply_action(action)
        if not success:
            return {"success": False}

        if action == "play" and location == "park":
            self.pet.needs.happiness = min(100.0, self.pet.needs.happiness + 10)
            bonus_applied = "Play in the Park"
            extra = 10
        elif action == "rest" and location == "home":
            self.pet.needs.energy = min(100.0, self.pet.needs.energy + 10)
            bonus_applied = "Resting at Home"
            extra = 10

        result = {"success": True, "bonus": bonus_applied, "extra": extra}
        # Auto-save on successful care action.
        if result["success"]:
            self.trigger_auto_save()
        return result

    def earn_coins(self, amount: int):
        self.pet.coins = min(99999, self.pet.coins + amount)

    def spend_coins(self, amount: int) -> bool:
        if self.pet.coins >= amount:
            self.pet.coins -= amount
            return True
        return False

    def buy_item(self, shop_key: str, item_key: str) -> dict:
        loc_data = self.LOCATIONS.get(shop_key, {})
        items = loc_data.get("items", [])
        item = next((i for i in items if i["key"] == item_key), None)

        if not item:
            return {"success": False, "msg": "Item not found"}

        if not self.spend_coins(item["price"]):
            return {"success": False, "msg": "Not enough coins!"}

        effect = item.get("effect", {})
        for stat, val in effect.items():
            if hasattr(self.pet.needs, stat):
                current = getattr(self.pet.needs, stat)
                setattr(self.pet.needs, stat, min(100.0, current + val))

        if "seeds" in item_key:
            self.pet.inventory[item_key] = self.pet.inventory.get(item_key, 0) + 1

        return {"success": True, "msg": f"Bought {item['name']}!", "effect": effect}

    def plant_seed(self, seed_type: str) -> dict:
        if len(self.pet.garden) >= 8:
            return {"success": False, "msg": "Garden is full (max 8 plants)"}

        if self.pet.inventory.get(seed_type, 0) <= 0:
            return {"success": False, "msg": "No seeds left!"}

        self.pet.inventory[seed_type] -= 1
        if self.pet.inventory[seed_type] <= 0:
            self.pet.inventory.pop(seed_type, None)

        plant_type = "flower" if seed_type == "flower_seeds" else "sunflower"
        self.pet.garden.append({
            "type": plant_type,
            "stage": 0,
            "planted_time": time.monotonic()
        })

        bonus = 45 if plant_type == "flower" else 60
        self.pet.needs.happiness = min(100.0, self.pet.needs.happiness + bonus)

        return {"success": True, "msg": f"Planted! +{bonus} Happiness", "bonus": bonus}

    def get_garden_bonus(self) -> float:
        if self.pet.location != "backyard":
            return 0.0
        mature = sum(1 for p in self.pet.garden if p.get("stage", 0) >= 3)
        return min(0.8, mature * 0.1)

    def harvest_plant(self) -> dict:
        """Harvest one mature plant. Returns success + message."""
        mature_plants = [p for p in self.pet.garden if p.get("stage", 0) >= 3]

        if not mature_plants:
            return {"success": False, "msg": "No mature plants to harvest"}

        # Harvest the first mature plant
        plant = mature_plants[0]
        self.pet.garden.remove(plant)

        # Add to flowers inventory
        self.pet.inventory["flowers"] = self.pet.inventory.get("flowers", 0) + 1

        return {"success": True, "msg": "Harvested 1 flower!"}

    def decorate_home(self) -> dict:
        """Decorate home with flowers. Costs 5 flowers."""
        if self.pet.location != "home":
            return {"success": False, "msg": "You can only decorate at home"}

        if self.pet.inventory.get("flowers", 0) < 5:
            return {"success": False, "msg": "You need at least 5 flowers to decorate"}

        self.pet.inventory["flowers"] -= 5
        if self.pet.inventory["flowers"] <= 0:
            self.pet.inventory.pop("flowers", None)

        self.pet.home_decorated = True
        self.pet.home_decoration_time = time.monotonic()
        self.trigger_auto_save()
        return {"success": True, "msg": "Home decorated with flowers!"}

    def _decay_home_decoration(self):
        if not self.pet.home_decorated:
            return

        # Decoration lasts ~30 real minutes (you can change this number)
        decay_time = 30 * 60   # seconds

        if time.monotonic() - self.pet.home_decoration_time > decay_time:
            self.pet.home_decorated = False
            self.pet.home_decoration_time = 0.0

    def save(self):
        """Delegate to SaveManager. Returns True if a save was written."""
        return self.save_manager.save()

    def trigger_auto_save(self) -> bool:
        """Convenience: trigger an auto-save if cooldown allows.
        Returns True if a save was actually written, False if throttled."""
        return self.save_manager.trigger_auto_save()

    def load(self) -> bool:
        """Load from SaveManager. Returns True if a valid save was found."""
        return self.save_manager.load()

    def reset(self):
        """Reset all game state and delete save file."""
        self.pet = PetState()
        self.save_manager.high_scores.clear()
        self._has_save = False
        save_dir = os.path.dirname(self.SAVE_PATH)
        save_path = self.SAVE_PATH
        if os.path.exists(save_path):
            os.remove(save_path)