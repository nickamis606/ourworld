"""Round-4 rules mixed into GameState: calendar events, fishing, the weekly
challenge, home furniture and companion pets. Pure Python, no pygame."""
from __future__ import annotations

import random

from . import calendar, fish_data, weekly
from . import furniture as F
from . import story_data
from .extras import WorldExtras

EVENT_FURNITURE = {"harvest_fair": "pumpkin", "snow_day": "snowglobe",
                   "egg_hunt": "egg_basket", "summer_splash": "beach_ball"}
SHARED_FIELDS = ("coins", "inventory", "garden", "decoration_left", "location", "cooldowns")
MAX_PETS = 4            # the active pet + 3 napping at home


class FeaturesMixin:
    # --------------------------------------------------------- save hooks
    def extra_save(self) -> dict:
        return {"extras": self.extras.to_dict()}

    def extra_load(self, data: dict, version: int) -> None:
        raw = data.get("extras")
        try:
            self.extras = WorldExtras.from_dict(raw)
        except Exception as e:  # noqa: BLE001 - never lose a pet over decorations
            print(f"[extras] unreadable ({e}); starting fresh extras")
            self.extras = WorldExtras()
        if raw is None:
            # pre-v4 save: hand over furniture for quests already finished
            for q, item in F.QUEST_FURNITURE.items():
                if self.story.status(q) == "done":
                    self.extras.furniture[item] = self.extras.furniture.get(item, 0) + 1

    # ------------------------------------------------------ calendar events
    def event_key(self):
        ev = self.current_event()
        if not ev:
            return None
        return f"{ev}-{calendar.event_year(self.today_date(), ev)}"

    def event_status(self):
        ev = self.current_event()
        if not ev:
            return None
        spec = calendar.EVENTS[ev]
        rec = self.extras.events.get(self.event_key(), {"progress": 0, "done": False})
        return {"key": ev, "name": spec["name"], "desc": spec["desc"], "text": spec["goal"]["text"],
                "progress": min(rec["progress"], spec["goal"]["count"]), "count": spec["goal"]["count"],
                "done": rec["done"], "reward": spec["reward"], "furniture": EVENT_FURNITURE.get(ev)}

    def _event_progress(self, kind: str, key: str) -> None:
        ev = self.current_event()
        if not ev:
            return
        goal = calendar.EVENTS[ev]["goal"]
        gk, gv = goal["event"].split(":")
        if gk != kind or (gv != "*" and gv != key):
            return
        ek = self.event_key()
        rec = self.extras.events.setdefault(ek, {"progress": 0, "done": False})
        if rec["done"]:
            return
        rec["progress"] += 1
        if rec["progress"] >= goal["count"]:
            rec["done"] = True
            spec = calendar.EVENTS[ev]
            self.story.grant(spec["reward"], self)
            self.story.notices.append(f"{spec['name']} complete! +{spec['reward']['coins']} coins")
            item = EVENT_FURNITURE.get(ev)
            if item:
                self.add_furniture(item)

    def snowman_built(self) -> bool:
        ek = self.event_key()
        return bool(ek) and ek.startswith("snow_day") and f"snowman-{ek.split('-')[1]}" in self.extras.built

    def backdrop_extras(self, location: str) -> tuple:
        if location == "park" and self.current_event() == "snow_day" and self.snowman_built():
            return ("snowman",)
        return ()

    def place_actions_here(self, location=None) -> list:
        from .world import place_actions_for
        return place_actions_for(location or self.pet.location, self.current_event())

    def _event_action_check(self, key: str, spec: dict):
        ev = spec.get("event")
        if not ev:
            return True, ""
        if self.current_event() != ev:
            return False, f"Only during the {calendar.EVENTS[ev]['name']}"
        if key == "snowman" and self.snowman_built():
            return False, "Your snowman is already standing tall!"
        if key == "egg_hunt":
            st = self.event_status()
            if st and st["done"]:
                return False, "You found all the eggs this year!"
        return True, ""

    def _event_action_done(self, key: str) -> None:
        if key == "snowman":
            ek = self.event_key()
            self.extras.built.append(f"snowman-{ek.split('-')[1]}")

    # -------------------------------------------------------------- fishing
    def can_fish(self):
        if self.pet.location != "pond":
            return False, "Fish at Sunny Pond"
        if self.pet.needs.energy < 10:
            return False, f"{self.pet.name} is too tired to fish."
        return True, ""

    def roll_fish(self, rng=None, bonus: float = 0.0) -> str:
        rng = rng or random.Random()
        return fish_data.roll(rng, self.time_of_day(), self.season(), bonus)

    def finish_fishing(self, catches) -> dict:
        """catches: list of (fish_key, size_cm). One call per fishing trip."""
        coins, new = 0, []
        for key, size in catches:
            if key not in fish_data.FISH:
                continue
            rec = self.extras.fish.get(key)
            if rec is None:
                rec = self.extras.fish[key] = {"count": 0, "best": 0}
                new.append(key)
            rec["count"] += 1
            rec["best"] = max(rec["best"], int(size))
            coins += fish_data.FISH[key][2]
            self._event("fish", key)
        joy = min(20, fish_data.FISH_HAPPINESS * len(catches))
        applied = self.pet.needs.apply({"happiness": joy, "energy": -fish_data.FISHING_ENERGY})
        self.earn_coins(coins)
        species = sum(1 for k in self.extras.fish if k != "boot")
        if species >= fish_data.ANGLER_SPECIES and "angler" not in self.story.stickers:
            self.story.grant({"sticker": "angler"}, self)
            self.add_furniture("fishbowl")
        self.save()
        return {"success": True, "coins": coins, "new": new, "deltas": applied,
                "caught": len(catches)}

    # ---------------------------------------------------- weekly challenge
    def weekly_challenge(self) -> dict:
        ch = weekly.challenge_for(self.today_date())
        w = self.extras.weekly
        if w.get("week") != ch["week"]:
            w.clear()
            w.update({"week": ch["week"], "done": False, "best": 0})
        return dict(ch, done=w["done"], best=w["best"])

    def _weekly_score(self, game: str, score: int):
        ch = self.weekly_challenge()
        if game != ch["game"]:
            return None
        w = self.extras.weekly
        w["best"] = max(w["best"], int(score))
        if score >= ch["target"] and not w["done"]:
            w["done"] = True
            self.extras.trophies += 1
            self.story.grant(weekly.REWARD, self)
            self.story.notices.append(f"Weekly Challenge won! +{weekly.REWARD['coins']} coins")
            if self.extras.trophies == 1:
                self.add_furniture("trophy")
            return True
        return False

    # ------------------------------------------------------------ furniture
    def add_furniture(self, key: str) -> None:
        if key not in F.FURNITURE:
            return
        self.extras.furniture[key] = self.extras.furniture.get(key, 0) + 1
        self.story.notices.append(f"New furniture: {F.FURNITURE[key][0]}! Furnish your Home.")

    def furniture_owned(self) -> list:
        return [k for k in F.FURNITURE_ORDER if self.extras.furniture.get(k, 0) > 0]

    def furniture_at(self, col: int, row: int):
        for c, r, k in self.extras.layout:
            if c == col and r == row:
                return k
        return None

    def place_furniture(self, col: int, row: int, key: str) -> dict:
        if self.pet.location != "home":
            return {"success": False, "msg": "Furnish your Home"}
        if not F.valid_cell(col, row):
            return {"success": False, "msg": "That's off the grid"}
        if self.extras.furniture.get(key, 0) <= 0:
            return {"success": False, "msg": "You don't have that yet"}
        if not F.fits(key, row):
            where = "on the wall" if F.is_wall(key) else "on the floor"
            return {"success": False, "msg": f"{F.FURNITURE[key][0]} goes {where}"}
        if self.furniture_at(col, row):
            return {"success": False, "msg": "Something is already there"}
        self.extras.furniture[key] -= 1
        if self.extras.furniture[key] <= 0:
            del self.extras.furniture[key]
        self.extras.layout.append([col, row, key])
        self._event("furnish", key)
        self.trigger_auto_save()
        return {"success": True, "msg": f"Placed the {F.FURNITURE[key][0]}!"}

    def remove_furniture(self, col: int, row: int) -> dict:
        key = self.furniture_at(col, row)
        if not key:
            return {"success": False, "msg": "Nothing to pick up there"}
        self.extras.layout = [it for it in self.extras.layout if not (it[0] == col and it[1] == row)]
        self.extras.furniture[key] = self.extras.furniture.get(key, 0) + 1
        self.trigger_auto_save()
        return {"success": True, "msg": f"Put away the {F.FURNITURE[key][0]}"}

    def cozy_factor(self) -> float:
        return F.cozy_factor(len(self.extras.layout))

    # ----------------------------------------------------------- companions
    def all_pets(self) -> list:
        """[(index, name, species_id, active)] -- index -1 is the active pet."""
        out = [(-1, self.pet.name, self.pet.species_id, True)]
        for i, c in enumerate(self.extras.companions):
            out.append((i, c.get("name", "Pet"), int(c.get("species_id", 0) or 0), False))
        return out

    def can_adopt_companion(self):
        if not self.story.finished:
            return False, "Light the Wish Lantern first!"
        if len(self.extras.companions) + 1 >= MAX_PETS:
            return False, f"Your home is full ({MAX_PETS} pets)"
        return True, ""

    def _carry_shared(self, old, new) -> None:
        for f in SHARED_FIELDS:
            setattr(new, f, getattr(old, f))

    def adopt_companion(self, name: str, species_id: int, trait=None) -> dict:
        ok, why = self.can_adopt_companion()
        if not ok:
            return {"success": False, "msg": why}
        from .pet_state import PetState
        from . import pets as petsmod
        if trait not in petsmod.TRAITS:
            trait = petsmod.roll_trait(name + str(len(self.extras.companions)))
        used = {n for _, n, _, _ in self.all_pets()}
        base, k = name, 2
        while name in used:
            name, k = f"{base} {k}", k + 1
        new = PetState(name=name, species_id=species_id, trait=trait)
        self._carry_shared(self.pet, new)
        new.location = "home"
        self.extras.companions.append(self.pet.to_dict())
        self.pet = new
        self.story.notices.append(f"Welcome home, {name}!")
        self.save()
        return {"success": True, "msg": f"Say hi to {name}!"}

    def switch_pet(self, index: int) -> dict:
        from .pet_state import PetState
        if not (0 <= index < len(self.extras.companions)):
            return {"success": False, "msg": "No pet there"}
        nxt = PetState.from_dict(self.extras.companions[index])
        self._carry_shared(self.pet, nxt)
        self.extras.companions[index] = self.pet.to_dict()
        self.pet = nxt
        self.save()
        return {"success": True, "msg": f"{nxt.name} is ready to play!"}

    def napping_pets(self) -> list:
        """Companions drawn napping at Home: [(name, species_id, stage)]."""
        from . import pets as petsmod
        from .story import bond_level
        return [(c.get("name", "Pet"), int(c.get("species_id", 0) or 0),
                 petsmod.stage_for(bond_level(int(c.get("bond_xp", 0) or 0))))
                for c in self.extras.companions]
