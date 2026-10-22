"""PetState: everything that gets saved about the pet. No pygame imports."""
from dataclasses import dataclass, field
from typing import Dict, List

from .needs import Needs
from .world import LOCATIONS, PLANTS, MAX_STAGE

NEW_GAME_COINS = 60


@dataclass
class PetState:
    name: str = "Pixel"
    species_id: int = 0                 # index into the pet roster (sprite/look)
    needs: Needs = field(default_factory=Needs)
    location: str = "home"
    coins: int = NEW_GAME_COINS
    inventory: Dict[str, int] = field(default_factory=dict)
    garden: List[dict] = field(default_factory=list)   # {"type", "stage", "age"}
    decoration_left: float = 0.0        # seconds of home decoration remaining
    play_seconds: float = 0.0           # total active time
    care_count: int = 0
    cooldowns: Dict[str, float] = field(default_factory=dict)  # place action -> secs left
    bond_xp: int = 0
    trait: str = ""                     # personality (core.pets.TRAITS); "" -> rolled on load
    stage_seen: str = "baby"            # last growth stage we celebrated
    mopey: bool = False                 # gentle stakes: low needs for a while

    # -- derived --------------------------------------------------------
    @property
    def home_decorated(self) -> bool:
        return self.decoration_left > 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "species_id": self.species_id,
            "needs": self.needs.to_dict(),
            "location": self.location,
            "coins": int(self.coins),
            "inventory": {k: int(v) for k, v in self.inventory.items() if v > 0},
            "garden": [dict(p) for p in self.garden],
            "decoration_left": round(self.decoration_left, 2),
            "play_seconds": round(self.play_seconds, 2),
            "care_count": self.care_count,
            "bond_xp": self.bond_xp,
            "cooldowns": {k: round(v, 2) for k, v in self.cooldowns.items() if v > 0},
            "trait": self.trait,
            "stage_seen": self.stage_seen,
            "mopey": bool(self.mopey),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PetState":
        """Tolerant loader: accepts v0/v1 saves and ignores unknown keys."""
        d = dict(d or {})
        pet = cls()
        pet.name = str(d.get("name", pet.name))[:16] or "Pixel"
        try:
            pet.species_id = int(d.get("species_id", d.get("pet_id", 0)))
        except (TypeError, ValueError):
            pet.species_id = 0
        pet.needs = Needs.from_dict(d.get("needs"))
        loc = d.get("location", "home")
        pet.location = loc if loc in LOCATIONS else "home"
        try:
            pet.coins = max(0, int(d.get("coins", NEW_GAME_COINS)))
        except (TypeError, ValueError):
            pet.coins = NEW_GAME_COINS
        inv = d.get("inventory") or {}
        pet.inventory = {str(k): int(v) for k, v in inv.items()
                         if isinstance(v, (int, float)) and v > 0}
        pet.garden = []
        for p in (d.get("garden") or [])[:8]:
            if not isinstance(p, dict):
                continue
            ptype = p.get("type", "flower")
            if ptype not in PLANTS:
                ptype = "flower"
            stage = max(0, min(MAX_STAGE, int(p.get("stage", 0))))
            # v0/v1 stored a time.monotonic() "planted_time", which is
            # meaningless after a reboot and froze plants forever. Convert to
            # an "age within current stage" counter that survives restarts.
            age = float(p.get("age", 0.0)) if "age" in p else 0.0
            pet.garden.append({"type": ptype, "stage": stage, "age": age})
        # v1 had home_decorated + monotonic home_decoration_time; give a fresh window.
        if "decoration_left" in d:
            pet.decoration_left = max(0.0, float(d.get("decoration_left") or 0.0))
        elif d.get("home_decorated"):
            from .world import DECORATION_SECS
            pet.decoration_left = float(DECORATION_SECS)
        pet.play_seconds = max(0.0, float(d.get("play_seconds", 0.0) or 0.0))
        pet.care_count = max(0, int(d.get("care_count", 0) or 0))
        try:
            pet.bond_xp = max(0, int(d.get("bond_xp", 0) or 0))
        except (TypeError, ValueError):
            pet.bond_xp = 0
        from .pets import TRAITS, STAGE_KEYS, roll_trait, stage_for
        from .story import bond_level
        t = d.get("trait")
        pet.trait = t if t in TRAITS else roll_trait(pet.name)
        st = d.get("stage_seen")
        # older saves: treat the current stage as already celebrated
        pet.stage_seen = st if st in STAGE_KEYS else stage_for(bond_level(pet.bond_xp))
        pet.mopey = bool(d.get("mopey", False))
        cds = d.get("cooldowns") or {}
        if isinstance(cds, dict):
            pet.cooldowns = {str(k): float(v) for k, v in cds.items()
                             if isinstance(v, (int, float)) and v > 0}
        return pet
