#!/usr/bin/env python3
"""
OurWorld — Location Bonuses Added (Phase 2B)
Play is better in the Park. Rest is better at Home.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field, asdict
import json
import os
import time
from typing import Dict, Optional, Callable


# ============== CORE LOGIC ==============

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
        d.pop("last_tick", None)
        return d

    @classmethod
    def from_dict(cls, d):
        needs = Needs.from_dict(d.pop("needs"))
        return cls(needs=needs, **d)


class GameState:
    SAVE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")

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
        """
        Performs an action and returns info about bonuses applied.
        """
        location = self.pet.location
        bonus_applied = None
        extra = 0

        # Apply base effect
        success = self.pet.apply_action(action)

        if not success:
            return {"success": False}

        # Location bonuses
        if action == "play" and location == "park":
            self.pet.needs.happiness = min(100.0, self.pet.needs.happiness + 10)
            bonus_applied = "Play in the Park"
            extra = 10
        elif action == "rest" and location == "home":
            self.pet.needs.energy = min(100.0, self.pet.needs.energy + 10)
            bonus_applied = "Resting at Home"
            extra = 10

        return {
            "success": True,
            "bonus": bonus_applied,
            "extra": extra
        }

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
                self.pet.last_tick = time.monotonic()
            except Exception as e:
                print("Load failed, starting fresh:", e)

    def reset(self):
        self.pet = PetState()
        if os.path.exists(self.SAVE_PATH):
            os.remove(self.SAVE_PATH)


# ============== ANIMATION SYSTEM ==============

class ActionAnimator:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.current_job: Optional[str] = None

    def cancel(self):
        if self.current_job:
            try:
                self.canvas.after_cancel(self.current_job)
            except Exception:
                pass
            self.current_job = None
        self.canvas.delete("anim_temp")

    def play_feed(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_oval(200, 160, 240, 190, fill="#8B4513", outline="#5D3A1A", width=2, tags="anim_temp")
        self.canvas.create_oval(205, 155, 235, 175, fill="#DEB887", tags="anim_temp")
        self.current_job = self.canvas.after(400, lambda: self._feed_frame_2(on_complete))

    def _feed_frame_2(self, on_complete):
        self.canvas.itemconfig("pet", outline="#FF69B4")
        self.current_job = self.canvas.after(600, lambda: self._feed_complete(on_complete))

    def _feed_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_play(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_oval(210, 170, 235, 195, fill="#FF6347", outline="#CD5C5C", width=2, tags="anim_temp")
        self.canvas.move("pet", 0, -8)
        self.current_job = self.canvas.after(350, lambda: self._play_frame_2(on_complete))

    def _play_frame_2(self, on_complete):
        self.canvas.move("pet", 0, 8)
        self.current_job = self.canvas.after(400, lambda: self._play_complete(on_complete))

    def _play_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_clean(self, on_complete: Optional[Callable] = None):
        self.cancel()
        for x, y in [(180, 140), (195, 130), (210, 145)]:
            self.canvas.create_oval(x, y, x+18, y+18, outline="#87CEEB", width=2, tags="anim_temp")
        self.current_job = self.canvas.after(300, lambda: self._clean_frame_2(on_complete))

    def _clean_frame_2(self, on_complete):
        self.canvas.move("anim_temp", 0, -25)
        self.current_job = self.canvas.after(500, lambda: self._clean_complete(on_complete))

    def _clean_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_rest(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_text(175, 95, text="Z", fill="#9370DB", font=("TkDefaultFont", 16, "bold"), tags="anim_temp")
        self.canvas.create_text(190, 85, text="z", fill="#9370DB", font=("TkDefaultFont", 12), tags="anim_temp")
        self.current_job = self.canvas.after(400, lambda: self._rest_frame_2(on_complete))

    def _rest_frame_2(self, on_complete):
        self.canvas.move("anim_temp", 0, -12)
        self.current_job = self.canvas.after(500, lambda: self._rest_complete(on_complete))

    def _rest_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None


# ============== UI LAYER ==============

class PetView(ttk.Frame):
    def __init__(self, parent, game_state: GameState):
        super().__init__(parent)
        self.game_state = game_state

        self.location_var = tk.StringVar()
        loc_frame = ttk.Frame(self)
        loc_frame.pack(fill="x", padx=10, pady=(5, 0))
        ttk.Label(loc_frame, text="Location:").pack(side="left")
        ttk.Label(loc_frame, textvariable=self.location_var, font=("TkDefaultFont", 11, "bold")).pack(side="left", padx=5)

        btn_loc_frame = ttk.Frame(self)
        btn_loc_frame.pack(pady=5)
        for loc_key in ["home", "park", "arcade"]:
            btn = ttk.Button(btn_loc_frame, text=game_state.LOCATIONS[loc_key]["name"],
                             command=lambda l=loc_key: self._change_location(l))
            btn.pack(side="left", padx=3)

        self.canvas = tk.Canvas(self, width=320, height=240, highlightthickness=1)
        self.canvas.pack(pady=10)
        self._draw_pet_and_environment()

        self.animator = ActionAnimator(self.canvas)

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

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        self.buttons = {}
        actions = [
            ("Feed", "feed", self._on_feed),
            ("Play", "play", self._on_play),
            ("Clean", "clean", self._on_clean),
            ("Rest", "rest", self._on_rest),
        ]
        for label, action, handler in actions:
            btn = ttk.Button(btn_frame, text=label, width=10, command=handler)
            btn.pack(side="left", padx=4)
            self.buttons[action] = btn

        self.status_var = tk.StringVar(value="Try playing in the Park or resting at Home for bonuses!")
        ttk.Label(self, textvariable=self.status_var).pack(pady=5)

        self.refresh_ui()

    def _change_location(self, new_loc: str):
        self.game_state.change_location(new_loc)
        self._draw_pet_and_environment()
        self.refresh_ui()
        info = self.game_state.get_current_location_info()
        self.status_var.set(f"Moved to {info['name']}. {info['desc']}")

    def _draw_pet_and_environment(self):
        self.canvas.delete("all")
        loc = self.game_state.pet.location
        bg_color = self.game_state.LOCATIONS[loc]["bg"]
        self.canvas.configure(bg=bg_color)

        if loc == "home":
            self.canvas.create_rectangle(0, 0, 320, 240, fill="#F5E6D3", outline="")
            self.canvas.create_rectangle(0, 180, 320, 240, fill="#D2B48C", outline="")
            self.canvas.create_rectangle(240, 40, 290, 90, fill="#87CEEB", outline="#8B4513", width=2, tags="env")
            self.canvas.create_line(265, 40, 265, 90, fill="#8B4513", width=2, tags="env")
            self.canvas.create_line(240, 65, 290, 65, fill="#8B4513", width=2, tags="env")
            self.canvas.create_oval(100, 160, 220, 210, fill="#CD853F", outline="#8B4513", width=2, tags="env")
            self.canvas.create_rectangle(60, 175, 110, 200, fill="#FFB6C1", outline="#FF69B4", width=2, tags="env")
            self.canvas.create_oval(65, 170, 105, 185, fill="#FF69B4", outline="#FF69B4", tags="env")

        elif loc == "park":
            self.canvas.create_rectangle(0, 200, 320, 240, fill="#228B22", outline="", tags="env")
            self.canvas.create_oval(50, 180, 90, 210, fill="#32CD32", tags="env")
            self.canvas.create_oval(230, 175, 280, 215, fill="#32CD32", tags="env")

        elif loc == "arcade":
            self.canvas.create_rectangle(20, 150, 60, 200, fill="#4169E1", outline="white", tags="env")
            self.canvas.create_rectangle(260, 150, 300, 200, fill="#FF4500", outline="white", tags="env")

        self.canvas.create_oval(120, 140, 200, 200, fill="#FFB6C1", outline="#FF69B4", width=2, tags="pet")
        self.canvas.create_oval(130, 100, 190, 150, fill="#FFB6C1", outline="#FF69B4", width=2, tags="pet")
        self.canvas.create_oval(145, 115, 155, 130, fill="white", outline="black", tags="pet")
        self.canvas.create_oval(165, 115, 175, 130, fill="white", outline="black", tags="pet")
        self.canvas.create_oval(148, 120, 152, 126, fill="black", tags="pet")
        self.canvas.create_oval(168, 120, 172, 126, fill="black", tags="pet")
        self.canvas.create_arc(148, 128, 172, 142, start=0, extent=180, style="arc", outline="#FF69B4", width=2, tags="pet")

    def _disable_all_buttons(self):
        for btn in self.buttons.values():
            btn.config(state="disabled")

    def _enable_all_buttons(self):
        for btn in self.buttons.values():
            btn.config(state="normal")

    def _on_feed(self):
        if self.animator.current_job: return
        self._disable_all_buttons()
        self.status_var.set("Feeding Pixel...")

        def after_anim():
            result = self.game_state.perform_care_action("feed")
            self.refresh_ui()
            if result.get("bonus"):
                self.status_var.set(f"{result['bonus']} bonus applied!")
            else:
                self.status_var.set("Pixel loved the food!")
            self._enable_all_buttons()
        self.animator.play_feed(on_complete=after_anim)

    def _on_play(self):
        if self.animator.current_job: return
        self._disable_all_buttons()
        self.status_var.set("Playing with Pixel...")

        def after_anim():
            result = self.game_state.perform_care_action("play")
            self.refresh_ui()
            if result.get("bonus"):
                self.status_var.set(f"{result['bonus']} (+{result['extra']} Happiness)!")
            else:
                self.status_var.set("Pixel had fun!")
            self._enable_all_buttons()
        self.animator.play_play(on_complete=after_anim)

    def _on_clean(self):
        if self.animator.current_job: return
        self._disable_all_buttons()
        self.status_var.set("Cleaning Pixel...")

        def after_anim():
            result = self.game_state.perform_care_action("clean")
            self.refresh_ui()
            if result.get("bonus"):
                self.status_var.set(f"{result['bonus']} bonus applied!")
            else:
                self.status_var.set("Pixel feels fresh!")
            self._enable_all_buttons()
        self.animator.play_clean(on_complete=after_anim)

    def _on_rest(self):
        if self.animator.current_job: return
        self._disable_all_buttons()
        self.status_var.set("Pixel is resting...")

        def after_anim():
            result = self.game_state.perform_care_action("rest")
            self.refresh_ui()
            if result.get("bonus"):
                self.status_var.set(f"{result['bonus']} (+{result['extra']} Energy)!")
            else:
                self.status_var.set("Pixel feels rested.")
            self._enable_all_buttons()
        self.animator.play_rest(on_complete=after_anim)

    def refresh_ui(self):
        needs = self.game_state.pet.needs
        for name, var in self.need_vars.items():
            val = getattr(needs, name)
            var.set(round(val, 1))

        info = self.game_state.get_current_location_info()
        self.location_var.set(f"{info['name']} — {info['desc']}")

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
        self.title("OurWorld — Location Bonuses")
        self.geometry("440x560")
        self.resizable(False, False)

        self.game_state = GameState()

        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=5)
        ttk.Label(header, text="OurWorld", font=("TkDefaultFont", 18, "bold")).pack(side="left")
        ttk.Label(header, text="  |  A cozy pet sim").pack(side="left", padx=10)

        self.pet_view = PetView(self, self.game_state)
        self.pet_view.pack(expand=True, fill="both", padx=10, pady=5)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=5)
        ttk.Button(bottom, text="Save", command=self.game_state.save).pack(side="left")
        ttk.Button(bottom, text="Reset Pet", command=self._reset_pet).pack(side="left", padx=5)
        ttk.Button(bottom, text="Quit", command=self._on_quit).pack(side="right")

        self._running = True
        self.after(1500, self._game_tick)
        self.protocol("WM_DELETE_WINDOW", self._on_quit)

    def _game_tick(self):
        if not self._running:
            return
        self.game_state.tick()
        self.pet_view.refresh_ui()
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