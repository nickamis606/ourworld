"""Player + parent settings. Pure data, saved inside the save file."""
from __future__ import annotations

REMINDER_CHOICES = (0, 15, 30, 45, 60)   # minutes; 0 = off


class Settings:
    def __init__(self):
        self.music = 6          # 0..10
        self.sfx = 8            # 0..10
        self.muted = False
        self.reminder_min = 0   # parent: play-time reminder
        self.slow_needs = False  # parent: needs drop at half speed

    def to_dict(self) -> dict:
        return {"music": self.music, "sfx": self.sfx, "muted": self.muted,
                "reminder_min": self.reminder_min, "slow_needs": self.slow_needs}

    @classmethod
    def from_dict(cls, d) -> "Settings":
        s = cls()
        if not isinstance(d, dict):
            return s

        def num(key, lo, hi, default):
            try:
                return max(lo, min(hi, int(d.get(key, default))))
            except (TypeError, ValueError):
                return default
        s.music = num("music", 0, 10, s.music)
        s.sfx = num("sfx", 0, 10, s.sfx)
        s.muted = bool(d.get("muted", False))
        r = num("reminder_min", 0, 120, 0)
        s.reminder_min = r if r in REMINDER_CHOICES else 0
        s.slow_needs = bool(d.get("slow_needs", False))
        return s

    def cycle_reminder(self, step: int = 1) -> None:
        i = REMINDER_CHOICES.index(self.reminder_min) if self.reminder_min in REMINDER_CHOICES else 0
        self.reminder_min = REMINDER_CHOICES[(i + step) % len(REMINDER_CHOICES)]
