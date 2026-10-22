"""Round-4 world state saved in the "extras" block (v4): calendar events,
fish book, weekly challenge, furniture and companion pets. Pure Python."""
from __future__ import annotations


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


class WorldExtras:
    def __init__(self):
        self.events = {}        # "harvest_fair-2026" -> {"progress": n, "done": bool}
        self.built = []         # e.g. "snowman-2026"
        self.fish = {}          # fish key -> {"count": n, "best": size_cm}
        self.weekly = {}        # {"week": "2026-W42", "done": bool, "best": n}
        self.trophies = 0       # weekly challenges won
        self.furniture = {}     # owned, not placed: key -> count
        self.layout = []        # placed: [col, row, key]
        self.companions = []    # inactive pets (PetState dicts)

    def to_dict(self) -> dict:
        return {"events": self.events, "built": self.built, "fish": self.fish,
                "weekly": self.weekly, "trophies": self.trophies,
                "furniture": self.furniture, "layout": self.layout,
                "companions": self.companions}

    @classmethod
    def from_dict(cls, d) -> "WorldExtras":
        x = cls()
        d = _d(d)
        x.events = {str(k): {"progress": int(_d(v).get("progress", 0) or 0), "done": bool(_d(v).get("done"))}
                    for k, v in _d(d.get("events")).items()}
        x.built = [str(b) for b in _l(d.get("built"))]
        from .fish_data import FISH
        x.fish = {}
        for k, v in _d(d.get("fish")).items():
            if k in FISH:
                v = _d(v)
                x.fish[k] = {"count": max(0, int(v.get("count", 0) or 0)),
                             "best": max(0, int(v.get("best", 0) or 0))}
        w = _d(d.get("weekly"))
        x.weekly = {"week": str(w.get("week", "")), "done": bool(w.get("done")),
                    "best": max(0, int(w.get("best", 0) or 0))} if w else {}
        x.trophies = max(0, int(d.get("trophies", 0) or 0))
        from .furniture import FURNITURE, valid_cell
        x.furniture = {k: int(v) for k, v in _d(d.get("furniture")).items()
                       if k in FURNITURE and isinstance(v, int) and v > 0}
        seen = set()
        for item in _l(d.get("layout")):
            if (isinstance(item, list) and len(item) == 3 and item[2] in FURNITURE
                    and valid_cell(item[0], item[1]) and (item[0], item[1]) not in seen):
                seen.add((item[0], item[1]))
                x.layout.append([int(item[0]), int(item[1]), item[2]])
        x.companions = [c for c in _l(d.get("companions")) if isinstance(c, dict) and "name" in c][:3]
        return x
