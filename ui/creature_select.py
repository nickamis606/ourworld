# ui/creature_select.py
import tkinter as tk
from tkinter import ttk
import random
from ..core.pet_state import PetState  # adjust if your import path differs

class CreatureSelector(ttk.Frame):
    def __init__(self, parent, on_selected):
        super().__init__(parent)
        self.on_selected = on_selected

        ttk.Label(self, text="Choose Your Companion!", font=("TkDefaultFont", 18, "bold")).pack(pady=20)

        preview_frame = ttk.Frame(self)
        preview_frame.pack(pady=10, fill="x")

        self.creatures = {
            "stickbug": ("Stick Bug Alien", "#A7D96E", self._draw_stick_bug),
            "sheep": ("Sheep", "#F8F8F8", self._draw_sheep),
            "squirrel": ("Squirrel Alien", "#C68642", self._draw_squirrel),
            "glow": ("Glow", "#9370DB", self._draw_glow),
        }

        self.selected_type = tk.StringVar(value="stickbug")

        for ctype, (name, color, drawer) in self.creatures.items():
            frame = ttk.LabelFrame(preview_frame, text=name)
            frame.pack(side="left", padx=12, pady=8, fill="y")

            canvas = tk.Canvas(frame, width=140, height=140, bg="#F0F8FF", highlightthickness=0)
            canvas.pack(pady=8)
            drawer(canvas, 70, 80, scale=1.1, color=color)

            ttk.Radiobutton(frame, text="Select", variable=self.selected_type,
                            value=ctype).pack(pady=5)

        # Name input
        name_frame = ttk.Frame(self)
        name_frame.pack(pady=15)
        ttk.Label(name_frame, text="Pet Name:", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
        self.name_var = tk.StringVar(value="Pixel")
        ttk.Entry(name_frame, textvariable=self.name_var, width=25).pack(side="left", padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Start Adventure!", command=self._confirm).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Random", command=self._random_choice).pack(side="left", padx=10)

    def _draw_stick_bug(self, canvas, x, y, scale=1.0, color="#A7D96E"):
        # Body
        canvas.create_line(x-25*scale, y, x+25*scale, y, width=14*scale, fill=color)
        # Head
        canvas.create_oval(x-32*scale, y-18*scale, x-12*scale, y+8*scale, fill="#6B9E4E")
        # Eyes
        canvas.create_oval(x-27*scale, y-12*scale, x-20*scale, y-5*scale, fill="white")
        canvas.create_oval(x-27*scale, y-12*scale, x-22*scale, y-7*scale, fill="black")
        # Legs
        for ox in [-18, -8, 8, 18]:
            canvas.create_line(x+ox*scale, y, x+ox*scale-12*scale, y+28*scale, width=5*scale, fill=color)
            canvas.create_line(x+ox*scale, y, x+ox*scale+12*scale, y+28*scale, width=5*scale, fill=color)
        # Arms
        canvas.create_line(x-12*scale, y-8*scale, x-30*scale, y-25*scale, width=6*scale, fill=color)
        canvas.create_line(x+12*scale, y-8*scale, x+30*scale, y-25*scale, width=6*scale, fill=color)

    def _draw_sheep(self, canvas, x, y, scale=1.0, color="#F8F8F8"):
        canvas.create_oval(x-35*scale, y-22*scale, x+35*scale, y+22*scale, fill=color, outline="#333", width=3)
        canvas.create_oval(x-22*scale, y-32*scale, x+22*scale, y-8*scale, fill=color)
        canvas.create_oval(x-20*scale, y-25*scale, x+5*scale, y-8*scale, fill="#E5C8A0")
        canvas.create_oval(x-13*scale, y-18*scale, x-7*scale, y-12*scale, fill="black")
        canvas.create_oval(x-2*scale, y-18*scale, x+4*scale, y-12*scale, fill="black")

    def _draw_squirrel(self, canvas, x, y, scale=1.0, color="#C68642"):
        canvas.create_oval(x-22*scale, y-18*scale, x+22*scale, y+28*scale, fill=color)  # body
        canvas.create_oval(x-20*scale, y-32*scale, x+20*scale, y-10*scale, fill=color)  # head
        canvas.create_oval(x-13*scale, y-25*scale, x-5*scale, y-17*scale, fill="white")
        canvas.create_oval(x+5*scale, y-25*scale, x+13*scale, y-17*scale, fill="white")
        canvas.create_oval(x-11*scale, y-23*scale, x-7*scale, y-19*scale, fill="black")
        canvas.create_oval(x+7*scale, y-23*scale, x+11*scale, y-19*scale, fill="black")
        # Tail
        canvas.create_oval(x+18*scale, y-5*scale, x+48*scale, y+28*scale, fill="#A0522D")
        # Antennae
        canvas.create_line(x-10*scale, y-32*scale, x-18*scale, y-42*scale, width=3*scale, fill="#4ECDC4")
        canvas.create_line(x+10*scale, y-32*scale, x+18*scale, y-42*scale, width=3*scale, fill="#4ECDC4")

    def _draw_glow(self, canvas, x, y, scale=1.0, color="#9370DB"):
        canvas.create_oval(x-30*scale, y-30*scale, x+30*scale, y+30*scale, fill=color, outline="#BA55D3", width=6)
        canvas.create_oval(x-20*scale, y-20*scale, x+20*scale, y+20*scale, fill="#E0B0FF")
        canvas.create_oval(x-12*scale, y-12*scale, x-3*scale, y-3*scale, fill="white")
        canvas.create_oval(x+3*scale, y-12*scale, x+12*scale, y-3*scale, fill="white")
        # Particles
        for i in range(10):
            px = x + (i % 5 - 2) * 12 * scale
            py = y - 25*scale + (i % 4) * 10 * scale
            canvas.create_oval(px-4*scale, py-4*scale, px+4*scale, py+4*scale, fill="#BA55D3")

    def _confirm(self):
        pet = PetState(
            name=self.name_var.get().strip() or "Pixel",
            creature_type=self.selected_type.get()
        )
        self.on_selected(pet)

    def _random_choice(self):
        ctype = random.choice(list(self.creatures.keys()))
        self.selected_type.set(ctype)
        self.name_var.set(random.choice(["Pixel", "Ziggy", "Luna", "Buzzy", "Fluff", "Spark"]))