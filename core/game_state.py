import json
import os
from .pet_state import PetState

class GameState:
    SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saves", "savegame.json")

    LOCATIONS = {
        "home":  {"name": "Home",   "bg": "#F5E6D3", "desc": "Cozy and familiar"},
        "park":  {"name": "Park",   "bg": "#90EE90", "desc": "Fresh air and open space"},
        "arcade":{"name": "Arcade", "bg": "#DDA0DD", "desc": "Lights and games"},
    }

    def __init__(self):
        self.pet = PetState()
        self.load()

    def tick(self):
        self.pet.tick()

    def change_location(self, new_location: str):
        if new_location in self.LOCATIONS:
            self.pet.location = new_location

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

        return {"success": True, "bonus": bonus_applied, "extra": extra}

    def save(self):
        os.makedirs(os.path.dirname(self.SAVE_PATH), exist_ok=True)
        try:
            with open(self.SAVE_PATH, "w") as f:
                json.dump(self.pet.to_dict(), f, indent=2)
        except Exception as e:
            print("Save failed:", e)

    def load(self):
        if os.path.exists(self.SAVE_PATH):
            try:
                with open(self.SAVE_PATH) as f:
                    data = json.load(f)
                self.pet = PetState.from_dict(data)
                self.pet.last_tick = __import__("time").monotonic()
            except Exception as e:
                print("Load failed, starting fresh:", e)

    def reset(self):
        self.pet = PetState()
        if os.path.exists(self.SAVE_PATH):
            os.remove(self.SAVE_PATH)