"""GameState: all game rules. Pure Python, no pygame imports.

The pygame layer calls ``tick(dt)`` once per frame and the action methods on
input. Every action returns a plain dict with at least ``success`` and ``msg``
so the UI can show feedback without knowing the rules.
"""
from __future__ import annotations
import os

from .needs import NEED_NAMES
from .pet_state import PetState
from .savegame import SaveManager
from .rewards import minigame_reward
from . import world
import random
import time

from .story import StoryState, today_str, bond_level
from . import story_data
from .world import (LOCATIONS, PLANTS, SEED_TO_PLANT, MAX_STAGE, GARDEN_SLOTS,
                    DECORATION_SECS, FLOWERS_TO_DECORATE, PLACE_ACTIONS)

DEFAULT_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "saves", "savegame.json")

# action -> (need that must have room, refusal text, base deltas)
CARE_ACTIONS = {
    "feed":  ("hunger", "{name} isn't hungry right now.",
              {"hunger": 25, "happiness": 4, "cleanliness": -5}),
    "play":  ("happiness", "{name} is already overjoyed!",
              {"happiness": 22, "energy": -12, "hunger": -6}),
    "clean": ("cleanliness", "{name} is already squeaky clean.",
              {"cleanliness": 35, "happiness": 4}),
    "rest":  ("energy", "{name} isn't sleepy.",
              {"energy": 35, "hunger": -4}),
}
# location -> (action, bonus deltas, label)
LOCATION_BONUS = {
    "park": ("play", {"happiness": 10}, "Park bonus!"),
    "home": ("rest", {"energy": 10}, "Cozy home bonus!"),
    "backyard": ("clean", {"happiness": 6}, "Fresh-air bonus!"),
    "pond": ("play", {"happiness": 6, "cleanliness": 4}, "Splashy bonus!"),
    "library": ("rest", {"happiness": 6}, "Quiet-corner bonus!"),
    "spa": ("clean", {"cleanliness": 10}, "Spa bonus!"),
}
FULL_THRESHOLD = 96.0
AUTOSAVE_EVERY = 60.0  # seconds of play between background autosaves


class GameState:
    LOCATIONS = LOCATIONS  # backwards compat for old UI code

    def __init__(self, save_path: str | None = None, autoload: bool = True, clock=None):
        self.clock = clock or time.time     # injectable for tests (daily wishes, day/night)
        self.pet = PetState()
        self.story = StoryState.new_game()
        self.save_manager = SaveManager(self, save_path or DEFAULT_SAVE_PATH)
        self._has_save = self.load() if autoload else False
        self._autosave_timer = 0.0
        self._story_timer = 0.0
        self.story.refresh(self)

    # ------------------------------------------------------------------ time
    def today(self) -> str:
        return today_str(self.clock())

    def time_of_day(self) -> str:
        """'day' | 'evening' | 'night' from the local clock (OURWORLD_HOUR overrides)."""
        hour = os.environ.get("OURWORLD_HOUR")
        h = int(hour) if hour and hour.isdigit() else time.localtime(self.clock()).tm_hour
        if 7 <= h < 18:
            return "day"
        if 18 <= h < 21 or 5 <= h < 7:
            return "evening"
        return "night"
    @property
    def has_save(self) -> bool:
        return self._has_save

    def decay_multipliers(self) -> dict:
        mult = {}
        loc = self.pet.location
        if self.pet.home_decorated and loc == "home":
            mult["happiness"] = 0.5
        if loc == "backyard":
            mature = sum(1 for p in self.pet.garden if p["stage"] >= MAX_STAGE)
            mult["happiness"] = max(0.4, 1.0 - 0.08 * mature)
        if loc == "arcade":
            mult["energy"] = 1.3
        if loc == "library":
            mult["energy"] = 0.7      # calm place: tires you out more slowly
        if loc == "pond":
            mult["cleanliness"] = 1.4  # sand gets everywhere
        return mult

    def tick(self, dt: float) -> None:
        """Advance the simulation by dt seconds (call every frame)."""
        if dt <= 0:
            return
        dt = min(dt, 5.0)  # a stall must not nuke the pet
        self.pet.play_seconds += dt
        self.pet.needs.tick(dt, self.decay_multipliers())
        self._grow_garden(dt)
        if self.pet.decoration_left > 0:
            self.pet.decoration_left = max(0.0, self.pet.decoration_left - dt)
        self._tick_cooldowns(dt)
        self._story_timer += dt
        if self._story_timer >= 1.0:
            self._story_timer = 0.0
            self.story.refresh(self)
        self._autosave_timer += dt
        if self._autosave_timer >= AUTOSAVE_EVERY:
            self._autosave_timer = 0.0
            self.trigger_auto_save()

    def apply_offline(self, seconds: float) -> None:
        """Gentle catch-up for time spent with the game closed.

        Decays at 15% speed, capped so a pet left for a week is hungry and
        grumpy but never at zero. Plants keep growing.
        """
        if seconds <= 0:
            return
        seconds = min(seconds, 7 * 24 * 3600)
        floors = {}
        for n in NEED_NAMES:
            floors[n] = min(getattr(self.pet.needs, n), 20.0)
        self.pet.needs.tick(seconds * 0.15)
        for n, floor in floors.items():
            if getattr(self.pet.needs, n) < floor:
                setattr(self.pet.needs, n, floor)
        self._grow_garden(seconds)
        self.pet.decoration_left = max(0.0, self.pet.decoration_left - seconds)
        self._tick_cooldowns(seconds)

    def _tick_cooldowns(self, dt: float) -> None:
        cds = self.pet.cooldowns
        for k in list(cds):
            cds[k] -= dt
            if cds[k] <= 0:
                del cds[k]

    def _grow_garden(self, dt: float) -> None:
        for plant in self.pet.garden:
            if plant["stage"] >= MAX_STAGE:
                continue
            plant["age"] = plant.get("age", 0.0) + dt
            need = PLANTS[plant["type"]]["stage_secs"]
            while plant["age"] >= need and plant["stage"] < MAX_STAGE:
                plant["age"] -= need
                plant["stage"] += 1
            if plant["stage"] >= MAX_STAGE:
                plant["age"] = 0.0

    # ------------------------------------------------------------- queries
    def mood(self) -> str:
        avg = self.pet.needs.average()
        low_name, low = self.pet.needs.lowest()
        if avg >= 70 and low >= 35:
            return "happy"
        if avg >= 40 and low >= 15:
            return "okay"
        return "sad"

    def wants(self) -> str | None:
        """The need the pet is asking for, if any is getting low."""
        name, value = self.pet.needs.lowest()
        return name if value < 40 else None

    def get_current_location_info(self) -> dict:
        return LOCATIONS.get(self.pet.location, LOCATIONS["home"])

    def mature_plants(self) -> int:
        return sum(1 for p in self.pet.garden if p["stage"] >= MAX_STAGE)

    def seed_count(self) -> int:
        return sum(self.pet.inventory.get(PLANTS[p]["seed"], 0) for p in PLANTS)

    # ------------------------------------------------------------- actions
    def is_unlocked(self, location: str) -> bool:
        return self.story.is_unlocked(location)

    def change_location(self, new_location: str) -> bool:
        if (new_location in LOCATIONS and new_location != self.pet.location
                and self.is_unlocked(new_location)):
            self.pet.location = new_location
            self._event("travel", new_location)
            self.trigger_auto_save()
            return True
        return False

    # --------------------------------------------------------------- story
    def _event(self, kind: str, key: str, score: int = 0) -> None:
        xp = story_data.BOND_XP.get(kind, 0)
        if xp:
            self.add_bond(xp)
        self.story.on_event(kind, key, self, score)

    def add_bond(self, xp: int) -> None:
        before = bond_level(self.pet.bond_xp)
        self.pet.bond_xp += int(xp)
        after = bond_level(self.pet.bond_xp)
        if after > before:
            title = story_data.BOND_TITLES[min(after, len(story_data.BOND_TITLES)) - 1]
            self.story.notices.append(f"Bond level {after}: {title}!")

    @property
    def bond_level(self) -> int:
        return bond_level(self.pet.bond_xp)

    def talk(self, npc: str) -> dict:
        info = story_data.NPCS.get(npc)
        if not info:
            return {"success": False, "msg": "Nobody's here", "lines": []}
        if info["location"] != self.pet.location:
            return {"success": False, "msg": f"{info['name']} isn't here", "lines": []}
        lines = self.story.talk(npc, self)
        self.trigger_auto_save()
        return {"success": True, "msg": "", "lines": lines}

    def next_dialogue(self) -> list:
        return self.story.pop_dialogue(self.pet.name)

    def can_perform(self, action: str) -> tuple[bool, str]:
        if action not in CARE_ACTIONS:
            return False, "Unknown action"
        need, refusal, deltas = CARE_ACTIONS[action]
        if getattr(self.pet.needs, need) >= FULL_THRESHOLD:
            return False, refusal.format(name=self.pet.name)
        if action == "play" and self.pet.needs.energy < 10:
            return False, f"{self.pet.name} is too tired to play."
        return True, ""

    def perform_care_action(self, action: str) -> dict:
        ok, why = self.can_perform(action)
        if not ok:
            return {"success": False, "msg": why, "deltas": {}}
        _, _, deltas = CARE_ACTIONS[action]
        deltas = dict(deltas)
        bonus = None
        b = LOCATION_BONUS.get(self.pet.location)
        if b and b[0] == action:
            for k, v in b[1].items():
                deltas[k] = deltas.get(k, 0) + v
            bonus = b[2]
        applied = self.pet.needs.apply(deltas)
        self.pet.care_count += 1
        self._event("care", action)
        self.trigger_auto_save()
        msg = bonus or {
            "feed": f"Yum! {self.pet.name} loved that.",
            "play": f"{self.pet.name} had a blast!",
            "clean": f"{self.pet.name} is all sparkly.",
            "rest": f"{self.pet.name} feels refreshed.",
        }[action]
        return {"success": True, "msg": msg, "deltas": applied, "bonus": bonus,
                "extra": 10 if bonus else 0}

    # ------------------------------------------------------- place actions
    def can_place_action(self, key: str) -> tuple:
        spec = PLACE_ACTIONS.get(key)
        if spec is None:
            return False, "Unknown action"
        name = self.pet.name
        if self.pet.location != spec["location"]:
            where = LOCATIONS[spec["location"]]["name"]
            return False, f"You can only do that at {where}"
        left = self.pet.cooldowns.get(key, 0)
        if left > 0:
            return False, f"{name} needs a little break first ({int(left) + 1}s)"
        if spec.get("need") and getattr(self.pet.needs, spec["need"]) >= FULL_THRESHOLD:
            return False, spec["refusal"].format(name=name)
        if key == "light":
            if self.story.finished:
                return False, "The Wish Lantern is already shining bright!"
            got = len(self.story.sparks)
            if got < spec["sparks"]:
                return False, f"The lantern needs {spec['sparks']} Sparks (you have {got})"
            if self.story.status("light_lantern") not in ("active", "ready"):
                return False, "Talk to Mayor Maple in the Town Square first"
            need = next(st["count"] for st in story_data.QUESTS["light_lantern"]["steps"]
                        if st.get("cond") == "bond")
            if self.bond_level < need:
                return False, f"Get closer to {name} first (Bond level {need})"
        if self.pet.needs.energy < spec["min_energy"]:
            return False, f"{name} is too tired for that."
        if self.pet.coins < spec["cost"]:
            return False, f"Not enough coins! ({spec['cost']} needed)"
        return True, ""

    def perform_place_action(self, key: str) -> dict:
        ok, why = self.can_place_action(key)
        if not ok:
            return {"success": False, "msg": why, "deltas": {}}
        spec = PLACE_ACTIONS[key]
        self.spend_coins(spec["cost"])
        applied = self.pet.needs.apply(spec["deltas"])
        if spec["cooldown"]:
            self.pet.cooldowns[key] = float(spec["cooldown"])
        self.pet.care_count += 1
        msg = spec["msg"].format(name=self.pet.name)
        found = None
        if key == "explore":
            found = self._explore_find()
            msg += " " + found
        self._event("place", key)
        self.trigger_auto_save()
        return {"success": True, "msg": msg, "deltas": applied, "cost": spec["cost"],
                "found": found}

    def _explore_find(self) -> str:
        st = self.story
        if st.status("lost_book") == "active" and st.quests["lost_book"]["progress"][0] == 0:
            return "Found Olive's storybook under a log!"
        rng = random.Random(f"{self.pet.care_count}-{len(st.stickers)}-{self.pet.bond_xp}")
        missing = [s for s in story_data.WOODS_STICKERS if s not in st.stickers]
        if missing and rng.random() < 0.7:
            s = rng.choice(missing)
            st.grant({"sticker": s}, self)
            return f"Found a sticker: {story_data.STICKERS[s][0]}!"
        coins = rng.randint(2, 6)
        self.earn_coins(coins)
        return f"Found {coins} shiny coins."

    def earn_coins(self, amount: int) -> None:
        self.pet.coins = max(0, min(99999, self.pet.coins + int(amount)))

    def spend_coins(self, amount: int) -> bool:
        if amount < 0 or self.pet.coins < amount:
            return False
        self.pet.coins -= amount
        return True

    def buy_item(self, shop_key: str, item_key: str) -> dict:
        item = next((i for i in world.shop_items(shop_key) if i["key"] == item_key), None)
        if not item:
            return {"success": False, "msg": "Item not found"}
        if self.pet.location != shop_key:
            return {"success": False, "msg": "You need to be in the shop"}
        if item.get("eat") and self.pet.needs.hunger >= FULL_THRESHOLD:
            return {"success": False, "msg": f"{self.pet.name} is too full for sweets."}
        if not self.spend_coins(item["price"]):
            return {"success": False, "msg": f"Not enough coins! ({item['price']} needed)"}
        applied = self.pet.needs.apply(item.get("effect", {}))
        if not item.get("eat"):
            self.pet.inventory[item_key] = self.pet.inventory.get(item_key, 0) + 1
        self._event("buy", item_key)
        self.trigger_auto_save()
        verb = "Ate" if item.get("eat") else "Bought"
        return {"success": True, "msg": f"{verb} {item['name']}!", "deltas": applied,
                "effect": item.get("effect", {}), "eat": bool(item.get("eat"))}

    def plant_seed(self, seed_type: str) -> dict:
        if self.pet.location != "backyard":
            return {"success": False, "msg": "Plant seeds in the Backyard"}
        if seed_type not in SEED_TO_PLANT:
            return {"success": False, "msg": "That's not a seed"}
        if len(self.pet.garden) >= GARDEN_SLOTS:
            return {"success": False, "msg": f"Garden is full ({GARDEN_SLOTS} plants)"}
        if self.pet.inventory.get(seed_type, 0) <= 0:
            return {"success": False, "msg": "No seeds left! Visit Gen's Garden."}
        self.pet.inventory[seed_type] -= 1
        if self.pet.inventory[seed_type] <= 0:
            self.pet.inventory.pop(seed_type, None)
        ptype = SEED_TO_PLANT[seed_type]
        self.pet.garden.append({"type": ptype, "stage": 0, "age": 0.0})
        applied = self.pet.needs.apply({"happiness": 5})
        self._event("plant", seed_type)
        self.trigger_auto_save()
        return {"success": True, "msg": f"Planted a {ptype}!", "deltas": applied}

    def harvest_plant(self) -> dict:
        for plant in self.pet.garden:
            if plant["stage"] >= MAX_STAGE:
                self.pet.garden.remove(plant)
                info = PLANTS[plant["type"]]
                self.pet.inventory["flowers"] = self.pet.inventory.get("flowers", 0) + 1
                self.earn_coins(info["coins"])
                applied = self.pet.needs.apply({"happiness": info["happiness"]})
                self._event("harvest", plant["type"])
                self.trigger_auto_save()
                return {"success": True, "deltas": applied, "coins": info["coins"],
                        "msg": f"Harvested a {plant['type']}! +{info['coins']} coins"}
        return {"success": False, "msg": "Nothing is ready to harvest yet"}

    def decorate_home(self) -> dict:
        if self.pet.location != "home":
            return {"success": False, "msg": "You can only decorate at home"}
        have = self.pet.inventory.get("flowers", 0)
        if have < FLOWERS_TO_DECORATE:
            return {"success": False,
                    "msg": f"Need {FLOWERS_TO_DECORATE} flowers to decorate (have {have})"}
        self.pet.inventory["flowers"] = have - FLOWERS_TO_DECORATE
        if self.pet.inventory["flowers"] <= 0:
            self.pet.inventory.pop("flowers", None)
        self.pet.decoration_left = float(DECORATION_SECS)
        applied = self.pet.needs.apply({"happiness": 20})
        self._event("decorate", "home")
        self.trigger_auto_save()
        return {"success": True, "msg": "Home decorated with flowers!", "deltas": applied}

    def finish_minigame(self, game: str, score: int) -> dict:
        reward = minigame_reward(game, score)
        new_best = self.save_manager.update_high_score(game, score)
        applied = self.pet.needs.apply({"happiness": reward["happiness"],
                                        "energy": reward["energy"]})
        self.earn_coins(reward["coins"])
        self._event("game", game, int(score))
        self.save()
        return {"success": True, "coins": reward["coins"], "deltas": applied,
                "new_best": new_best, "best": self.save_manager.get_high_score(game)}

    # ----------------------------------------------------------- persistence
    def save(self) -> bool:
        return self.save_manager.save(force=True)

    def trigger_auto_save(self) -> bool:
        return self.save_manager.save(force=False)

    def load(self) -> bool:
        return self.save_manager.load()

    def new_game(self, name: str, species_id: int) -> None:
        self.pet = PetState(name=name, species_id=species_id)
        self.story = StoryState.new_game()
        self.story.refresh(self)
        self._has_save = True
        self.save()

    def reset(self) -> None:
        self.pet = PetState()
        self.story = StoryState.new_game()
        self.save_manager.high_scores.clear()
        self._has_save = False
        self.save_manager.delete()
