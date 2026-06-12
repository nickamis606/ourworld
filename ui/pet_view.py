import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from core.game_state import GameState
from core.action_animator import ActionAnimator
from core.snake_game import SnakeGame


class PetView(ttk.Frame):
    def __init__(self, parent, game_state: GameState):
        super().__init__(parent)
        self.game_state = game_state

        # Current location display
        self.location_var = tk.StringVar()
        loc_frame = ttk.Frame(self)
        loc_frame.pack(fill="x", padx=10, pady=(5, 0))
        ttk.Label(loc_frame, text="Location:").pack(side="left")
        ttk.Label(loc_frame, textvariable=self.location_var, font=("TkDefaultFont", 11, "bold")).pack(side="left", padx=5)

        # Map button (main navigation)
        map_frame = ttk.Frame(self)
        map_frame.pack(pady=5)
        self.map_btn = ttk.Button(map_frame, text="Map", width=10, command=self._open_map)
        self.map_btn.pack()

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

        # Play Snake button (only visible in Arcade)
        self.snake_btn = ttk.Button(btn_frame, text="Play Snake", width=12, command=self._launch_snake)

        self.status_var = tk.StringVar(value="Use the Map button to change locations.")
        ttk.Label(self, textvariable=self.status_var).pack(pady=5)

        self.refresh_ui()

    def _change_location(self, new_loc: str):
        self.game_state.change_location(new_loc)
        self._draw_pet_and_environment()
        self.refresh_ui()
        info = self.game_state.get_current_location_info()
        self.status_var.set(f"Moved to {info['name']}. {info['desc']}")

    def _launch_snake(self):
        """Launch Snake minigame. Gives Happiness bonus when finished."""
        def apply_bonus(final_score):
            bonus = final_score // 5
            if bonus > 0:
                self.game_state.pet.needs.happiness = min(
                    100.0, self.game_state.pet.needs.happiness + bonus
                )
                self.refresh_ui()
                self.status_var.set(f"Snake bonus! +{bonus} Happiness")

        snake_window = tk.Toplevel(self)
        snake = SnakeGame(master=snake_window, on_game_end=apply_bonus)
        snake_window.title("OurWorld - Snake")
        snake_window.focus_force()

    def _open_map(self):
        """Open a visual map popup with recognizable icons."""
        map_window = tk.Toplevel(self)
        map_window.title("Map")
        map_window.geometry("420x320")
        map_window.resizable(False, False)

        canvas = tk.Canvas(map_window, width=400, height=260, bg="#f0f0f0")
        canvas.pack(pady=10)

        # Draw locations with simple recognizable icons
        self._draw_map_location(canvas, 70, 120, "home", "Home", "#8B4513")
        self._draw_map_location(canvas, 200, 120, "park", "Park", "#228B22")
        self._draw_map_location(canvas, 330, 120, "arcade", "Arcade", "#4169E1")

        # Connecting paths
        canvas.create_line(110, 130, 160, 130, fill="#555555", width=3)
        canvas.create_line(240, 130, 290, 130, fill="#555555", width=3)

        # Current location indicator
        current = self.game_state.pet.location
        if current == "home":
            canvas.create_text(70, 180, text="You are here", fill="#8B4513", font=("TkDefaultFont", 10, "bold"))
        elif current == "park":
            canvas.create_text(200, 180, text="You are here", fill="#228B22", font=("TkDefaultFont", 10, "bold"))
        elif current == "arcade":
            canvas.create_text(330, 180, text="You are here", fill="#4169E1", font=("TkDefaultFont", 10, "bold"))

    def _draw_map_location(self, canvas, x, y, location_key, label, color):
        """Draw a simple recognizable icon for each location."""
        tag = f"loc_{location_key}"

        if location_key == "home":
            # House
            canvas.create_rectangle(x-20, y, x+20, y+30, fill="#DEB887", outline="#8B4513", width=2, tags=tag)
            canvas.create_polygon(x-25, y, x, y-25, x+25, y, fill="#8B4513", outline="#5D3A1A", tags=tag)

        elif location_key == "park":
            # Tree
            canvas.create_rectangle(x-5, y+5, x+5, y+25, fill="#8B4513", outline="#5D3A1A", tags=tag)
            canvas.create_polygon(x-20, y+5, x, y-20, x+20, y+5, fill="#228B22", outline="#006400", tags=tag)
            canvas.create_polygon(x-15, y-5, x, y-25, x+15, y-5, fill="#32CD32", outline="#228B22", tags=tag)

        elif location_key == "arcade":
            # Game machine
            canvas.create_rectangle(x-18, y-10, x+18, y+25, fill="#333333", outline="#111111", width=2, tags=tag)
            canvas.create_rectangle(x-12, y-5, x+12, y+5, fill="#00ff00", outline="#00aa00", tags=tag)
            canvas.create_oval(x-8, y+10, x-2, y+18, fill="#ff0000", tags=tag)
            canvas.create_oval(x+2, y+10, x+8, y+18, fill="#ffff00", tags=tag)

        canvas.create_text(x, y+40, text=label, font=("TkDefaultFont", 11, "bold"), tags=tag)

        # Make only this location's items clickable
        def on_click(event, loc=location_key):
            self._change_location(loc)
            canvas.winfo_toplevel().destroy()

        canvas.tag_bind(tag, "<Button-1>", on_click)

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
        self.snake_btn.config(state="disabled")

    def _enable_all_buttons(self):
        for btn in self.buttons.values():
            btn.config(state="normal")
        if self.game_state.pet.location == "arcade":
            self.snake_btn.config(state="normal")

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

        # Show or hide Snake button based on location
        if self.game_state.pet.location == "arcade":
            self.snake_btn.pack(side="left", padx=8)
            self.snake_btn.config(state="normal")
        else:
            self.snake_btn.pack_forget()

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