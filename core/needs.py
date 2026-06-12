from dataclasses import dataclass, asdict

@dataclass
class Needs:
    hunger: float = 80.0
    happiness: float = 80.0
    energy: float = 80.0
    cleanliness: float = 80.0

    def tick(self, delta_seconds: float = 2.0):
        self.hunger = max(0.0, self.hunger - 0.8 * delta_seconds / 2)
        self.happiness = max(0.0, self.happiness - 0.3 * delta_seconds / 2)
        self.energy = max(0.0, self.energy - 0.5 * delta_seconds / 2)
        self.cleanliness = max(0.0, self.cleanliness - 0.2 * delta_seconds / 2)

    def apply_action(self, action: str) -> bool:
        if action == "feed":
            self.hunger = min(100.0, self.hunger + 25)
            self.happiness = min(100.0, self.happiness + 5)
            self.cleanliness = max(0.0, self.cleanliness - 8)
            return True
        elif action == "play":
            self.happiness = min(100.0, self.happiness + 30)
            self.energy = max(0.0, self.energy - 15)
            self.hunger = max(0.0, self.hunger - 5)
            return True
        elif action == "clean":
            self.cleanliness = min(100.0, self.cleanliness + 35)
            self.happiness = min(100.0, self.happiness + 10)
            return True
        elif action == "rest":
            self.energy = min(100.0, self.energy + 35)
            self.happiness = min(100.0, self.happiness + 8)
            return True
        return False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)