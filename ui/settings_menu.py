"""Settings overlay: volume/mute for everyone, parent settings behind a hold-A gate.

D-pad Up/Down choose, Left/Right change, B closes. "Parent settings" opens only
after holding A for HOLD_SECS (kids can see it, but it takes intent).
"""
import pygame

from core.settings import REMINDER_CHOICES
from engine import assets
from ui.common import FOCUS, hint_bar, panel

HOLD_SECS = 2.0


class SettingsMenu:
    def __init__(self, settings, on_change=None):
        self.s = settings
        self.on_change = on_change
        self.index = 0
        self.parent_open = False
        self.hold = 0.0
        self.open = True

    def rows(self):
        r = [("music", "Music"), ("sfx", "Sound effects"), ("muted", "Mute all")]
        if self.parent_open:
            r += [("reminder", "Play-time reminder"), ("slow", "Slow needs (gentler)")]
        else:
            r += [("parent", "Parent settings")]
        return r + [("close", "Back")]

    def value(self, key):
        s = self.s
        if key == "music":
            return f"{s.music}/10"
        if key == "sfx":
            return f"{s.sfx}/10"
        if key == "muted":
            return "On" if s.muted else "Off"
        if key == "reminder":
            return f"{s.reminder_min} min" if s.reminder_min else "Off"
        if key == "slow":
            return "On" if s.slow_needs else "Off"
        if key == "parent":
            return "Hold A"
        return ""

    def _changed(self):
        if self.on_change:
            self.on_change(self.s)

    def handle_action(self, a):
        rows = self.rows()
        key = rows[self.index][0]
        if a == "UP":
            self.index = (self.index - 1) % len(rows)
            self.hold = 0.0
        elif a == "DOWN":
            self.index = (self.index + 1) % len(rows)
            self.hold = 0.0
        elif a in ("B", "START"):
            self.open = False
        elif a in ("LEFT", "RIGHT", "A"):
            d = -1 if a == "LEFT" else 1
            s = self.s
            if key == "music":
                s.music = max(0, min(10, s.music + d)) if a != "A" else (s.music + 1) % 11
            elif key == "sfx":
                s.sfx = max(0, min(10, s.sfx + d)) if a != "A" else (s.sfx + 1) % 11
            elif key == "muted":
                s.muted = not s.muted
            elif key == "reminder":
                s.cycle_reminder(d)
            elif key == "slow":
                s.slow_needs = not s.slow_needs
            elif key == "close" and a == "A":
                self.open = False
                return
            else:
                return
            self._changed()

    def update(self, dt, held):
        rows = self.rows()
        if rows[self.index][0] == "parent" and "A" in held:
            self.hold += dt
            if self.hold >= HOLD_SECS:
                self.parent_open = True
                self.hold = 0.0
        else:
            self.hold = 0.0

    def draw(self, surf):
        surf.blit(panel((640, 480), (10, 10, 20, 160), 0, None), (0, 0))
        rows = self.rows()
        box = pygame.Rect(70, 60, 500, 70 + len(rows) * 50)
        surf.blit(panel(box.size, (255, 250, 240, 248), 16, (120, 90, 70)), box.topleft)
        t = assets.text("Settings", 30, (80, 60, 50), bold=True)
        surf.blit(t, t.get_rect(center=(box.centerx, box.y + 28)))
        for i, (key, label) in enumerate(rows):
            r = pygame.Rect(box.x + 20, box.y + 56 + i * 50, box.w - 40, 42)
            sel = i == self.index
            pygame.draw.rect(surf, (255, 230, 170) if sel else (240, 232, 220), r, border_radius=10)
            if sel:
                pygame.draw.rect(surf, FOCUS, r, 3, border_radius=10)
            surf.blit(assets.text(label, 22, (60, 50, 50), bold=sel), (r.x + 14, r.y + 10))
            v = self.value(key)
            if v:
                vt = assets.text(("< " + v + " >") if key not in ("parent",) else v, 22, (120, 80, 60), bold=True)
                surf.blit(vt, (r.right - vt.get_width() - 14, r.y + 10))
            if key in ("music", "sfx"):
                n = self.s.music if key == "music" else self.s.sfx
                for k in range(10):
                    c = (240, 150, 90) if k < n else (220, 210, 200)
                    pygame.draw.rect(surf, c, (r.x + 180 + k * 14, r.y + 14, 10, 14), border_radius=3)
            if key == "parent" and self.hold > 0:
                w = int((r.w - 28) * min(1.0, self.hold / HOLD_SECS))
                pygame.draw.rect(surf, (120, 190, 120), (r.x + 14, r.bottom - 8, w, 4), border_radius=2)
        hint_bar(surf, [("D-pad", "Choose / change"), ("A", "Toggle"), ("B", "Back")])
