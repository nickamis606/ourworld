import tkinter as tk
from tkinter import ttk, messagebox

from core.game_state import GameState          # ← changed
from .pet_view import PetView

class OurWorldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OurWorld — Refactored")
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