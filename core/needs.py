"""Pet needs: pure data + rules. No pygame imports."""
from __future__ import annotations
from dataclasses import dataclass, asdict, fields

NEED_NAMES = ("hunger", "happiness", "energy", "cleanliness")

# Points lost per second of active play. Tuned so a full bar empties in
# roughly 12-30 minutes: long enough to be cosy, short enough to matter.
DECAY_PER_SEC = {
    "hunger": 0.11,
    "happiness": 0.07,
    "energy": 0.06,
    "cleanliness": 0.05,
}


def clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return lo if v < lo else hi if v > hi else v


@dataclass
class Needs:
    hunger: float = 80.0
    happiness: float = 80.0
    energy: float = 80.0
    cleanliness: float = 80.0

    def tick(self, dt: float, multipliers: dict | None = None) -> None:
        """Decay every need by dt seconds of game time."""
        if dt <= 0:
            return
        multipliers = multipliers or {}
        for name in NEED_NAMES:
            rate = DECAY_PER_SEC[name] * multipliers.get(name, 1.0)
            setattr(self, name, clamp(getattr(self, name) - rate * dt))

    def apply(self, deltas: dict) -> dict:
        """Apply deltas, clamped. Returns the deltas that actually happened."""
        applied = {}
        for name, delta in deltas.items():
            if name not in NEED_NAMES:
                continue
            before = getattr(self, name)
            after = clamp(before + delta)
            setattr(self, name, after)
            if round(after - before, 3):
                applied[name] = after - before
        return applied

    def average(self) -> float:
        return sum(getattr(self, n) for n in NEED_NAMES) / len(NEED_NAMES)

    def lowest(self) -> tuple[str, float]:
        name = min(NEED_NAMES, key=lambda n: getattr(self, n))
        return name, getattr(self, name)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict | None) -> "Needs":
        d = d or {}
        known = {f.name for f in fields(cls)}
        out = cls()
        for k, v in d.items():
            if k in known:
                try:
                    setattr(out, k, clamp(float(v)))
                except (TypeError, ValueError):
                    pass
        return out
