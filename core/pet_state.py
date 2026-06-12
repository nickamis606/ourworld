from dataclasses import dataclass, field
import time
from .needs import Needs

@dataclass
class PetState:
    name: str = "Pixel"
    needs: Needs = field(default_factory=Needs)
    location: str = "home"
    days_alive: int = 0
    last_tick: float = field(default_factory=time.monotonic)

    def tick(self):
        now = time.monotonic()
        delta = now - self.last_tick
        self.last_tick = now
        self.needs.tick(delta)

    def apply_action(self, action: str) -> bool:
        return self.needs.apply_action(action)

    def to_dict(self):
        d = {"name": self.name, "needs": self.needs.to_dict(), "location": self.location, "days_alive": self.days_alive}
        return d

    @classmethod
    def from_dict(cls, d):
        needs = Needs.from_dict(d["needs"])
        return cls(name=d.get("name", "Pixel"), needs=needs, location=d.get("location", "home"), days_alive=d.get("days_alive", 0))