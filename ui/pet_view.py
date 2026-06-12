import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from core.game_state import GameState           # ← changed
from core.action_animator import ActionAnimator # ← changed

class PetView(ttk.Frame):
    def __init__(self, parent, game_state: GameState):
        super().__init__(parent)
        self.game_state = game_state

        # Location display
        self.location_var = tk.StringVar()
        loc_frame = ttk.Frame(self)
        loc_frame.pack(fill="x", padx=10, pady=(5, 0))
        ttk.Label(loc_frame, text="Location:").pack(side="left")
        ttk.Label(loc_frame, textvariable=self.location_var, font=("TkDefaultFont", 11, "bold")).pack(side="left", padx=5)

        # Location buttons
        btn_loc_frame = ttk.Frame(self)
        btn_loc_frame.pack(pady=5)
        for loc_key in ["home", "park", "arcade"]:
            btn = ttk.Button(btn_loc_frame, text=game_state.LOCATIONS[loc_key]["name"],
                             command=lambda l=loc_key: self._change_location(l))
            btn.pack(side="left", padx=3)

        # Canvas
        self.canvas = tk.Canvas(self, width=320, height=240, highlightthickness=1)
        self.canvas.pack(pady=10)
        self._draw_pet_and_environment()

        self.animator = ActionAnimator(self.canvas)

        # Needs
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

        # Pet
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
        if self.animator.current_job:
            return
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
        if self.animator.current_job:
            return
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
        if self.animator.current_job:
            return
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
        if self.animator.current_job:
            return
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