#!/usr/bin/env python3
"""
OurWorld Phase 0 Skeleton — Minimal runnable Tkinter prototype.

This is the initial commit pushed to GitHub.
Follows the architecture and Tkinter patterns defined in the OurWorld skill.

Run with: python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field, asdict
import json
import os
import time
from typing import Dict

# ============== CORE LOGIC (pure, will be moved to core/ later) ==============

@dataclass
class Needs:
    hunger: float = 80.0
    happiness: float = 80.0
    energy: float = 80.0
    cleanliness: float = 80.0

    def tick(self, delta_seconds: float = 2.0):
        # Gentle decay rates (tunable)
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
        d = asdict(self)
        d["needs"] = self.needs.to_dict()
        d.pop("last_tick", None)  # don't persist timing
        return d

    @classmethod
    def from_dict(cls, d):
        needs = Needs.from_dict(d.pop("needs"))
        return cls(needs=needs, **d)


class GameState:
    SAVE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")

    def __init__(self):
        self.pet = PetState()
        self.load()

    def tick(self):
        self.pet.tick()

    def apply_action(self, action: str) -> bool:
        return self.pet.apply_action(action)

    def save(self):
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
                self.pet.last_tick = time.monotonic()  # reset timing
            except Exception as e:
                print("Load failed, starting fresh:", e)

    def reset(self):
        self.pet = PetState()
        if os.path.exists(self.SAVE_PATH):
            os.remove(self.SAVE_PATH)


# ============== UI LAYER ==============

class PetView(ttk.Frame):
    def __init__(self, parent, game_state: GameState, animator=None):
        super().__init__(parent)
        self.game_state = game_state
        self.animator = animator  # placeholder for Phase 1

        # Pet visualization area (simple for Phase 0)
        self.canvas = tk.Canvas(self, width=320, height=240, bg="#E8F4E8", highlightthickness=1)
        self.canvas.pack(pady=10)
        self._draw_simple_pet()

        # Needs display
        self.need_vars: Dict[str, tk.DoubleVar] = {}
        needs_frame = ttk.LabelFrame(self, text="Needs")
        needs_frame.pack(fill="x", padx=10, pady=5)

        for need_name in ["hunger", "happiness", "energy", "cleanliness"]:
            row = ttk.Frame(needs_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=need_name.title(), width=12).pack(side="left")
            var = tk.DoubleVar(value=80.0)
            self.need_vars[need_name] = var
            bar = ttk.Progressbar(row, variable=var, maximum=100, length=200)
            bar.pack(side="left", padx=5)
            val_label = ttk.Label(row, textvariable=var, width=5)
            val_label.pack(side="left")

        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        actions = [
            ("Feed", "feed"),
            ("Play", "play"),
            ("Clean", "clean"),
            ("Rest", "rest"),
        ]
        for label, action in actions:
            btn = ttk.Button(btn_frame, text=label, width=10,
                             command=lambda a=action: self._on_action(a))
            btn.pack(side="left", padx=4)

        # Status
        self.status_var = tk.StringVar(value="Welcome to OurWorld! Take care of Pixel.")
        ttk.Label(self, textvariable=self.status_var).pack(pady=5)

        self.refresh_ui()

    def _draw_simple_pet(self):
        self.canvas.delete("all")
        # Simple cute pet: body + head + eyes
        # Body
        self.canvas.create_oval(120, 140, 200, 200, fill="#FFB6C1", outline="#FF69B4", width=2, tags="pet")
        # Head
        self.canvas.create_oval(130, 100, 190, 150, fill="#FFB6C1", outline="#FF69B4", width=2, tags="pet")
        # Eyes
        self.canvas.create_oval(145, 115, 155, 130, fill="white", outline="black", tags="pet")
        self.canvas.create_oval(165, 115, 175, 130, fill="white", outline="black", tags="pet")
        # Pupils
        self.canvas.create_oval(148, 120, 152, 126, fill="black", tags="pet")
        self.canvas.create_oval(168, 120, 172, 126, fill="black", tags="pet")
        # Cute smile
        self.canvas.create_arc(148, 128, 172, 142, start=0, extent=180, style="arc", outline="#FF69B4", width=2, tags="pet")

    def _on_action(self, action: str):
        # For Phase 0: immediate effect, no animation yet
        success = self.game_state.apply_action(action)
        if success:
            self.status_var.set(f"Pixel enjoyed the {action}!")
            self.refresh_ui()
        else:
            self.status_var.set("Action failed.")

    def refresh_ui(self):
        needs = self.game_state.pet.needs
        for name, var in self.need_vars.items():
            val = getattr(needs, name)
            var.set(round(val, 1))

        # Simple mood indicator on canvas (update eye color or add text)
        self.canvas.delete("mood")
        avg = (needs.hunger + needs.happiness + needs.energy + needs.cleanliness) / 4
        if avg > 70:
            mood = "Happy"
            color = "#90EE90"
        elif avg > 40:
            mood = "Okay"
            color = "#FFD700"
        else:
            mood = "Sad"
            color = "#FFB6C1"
        self.canvas.create_text(160, 80, text=mood, fill=color, font=("TkDefaultFont", 14, "bold"), tags="mood")


class OurWorldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OurWorld — Phase 0 Skeleton")
        self.geometry("420x520")
        self.resizable(False, False)

        self.game_state = GameState()

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=5)
        ttk.Label(header, text="OurWorld", font=("TkDefaultFont", 18, "bold")).pack(side="left")
        ttk.Label(header, textvariable=tk.StringVar(value="  |  A cozy pet sim")).pack(side="left", padx=10)

        # Main view
        self.pet_view = PetView(self, self.game_state)
        self.pet_view.pack(expand=True, fill="both", padx=10, pady=5)

        # Bottom bar
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=5)
        ttk.Button(bottom, text="Save", command=self.game_state.save).pack(side="left")
        ttk.Button(bottom, text="Reset Pet", command=self._reset_pet).pack(side="left", padx=5)
        ttk.Button(bottom, text="Quit", command=self._on_quit).pack(side="right")

        # Start the game tick loop
        self._running = True
        self.after(1500, self._game_tick)

        # Save on close
        self.protocol("WM_DELETE_WINDOW", self._on_quit)

    def _game_tick(self):
        if not self._running:
            return
        self.game_state.tick()
        self.pet_view.refresh_ui()
        # Schedule next tick
        self.after(1500, self._game_tick)

    def _reset_pet(self):
        if messagebox.askyesno("Reset", "Reset pet to default state?"):
            self.game_state.reset()
            self.pet_view.refresh_ui()
            self.pet_view.status_var.set("Pet has been reset. Fresh start!")

    def _on_quit(self):
        self._running = False
        self.game_state.save()
        self.destroy()


if __name__ == "__main__":
    app = OurWorldApp()
    app.mainloop()
