"""Unified input: keyboard + gamepad -> abstract actions.

Every scene consumes actions ("UP", "A", "START", ...) instead of raw keys,
so the whole game plays the same on a desktop keyboard, a Miyoo Mini
(whose buttons arrive as keyboard events) and an Anbernic/RG device
(SDL game controller or raw joystick).

Override any mapping by dropping an ``input_map.json`` next to main_pygame.py:
    {"keyboard": {"A": ["space"], "B": ["left ctrl"]},
     "joystick_buttons": {"0": "B", "1": "A"},   # raw joystick index -> action
     "swap_ab": false}
"""
from __future__ import annotations
import json
import os

import pygame

DIRS = ("UP", "DOWN", "LEFT", "RIGHT")
ACTIONS = DIRS + ("A", "B", "X", "Y", "L", "R", "START", "SELECT")

# Miyoo Mini (OnionOS/MiniUI) sends: D-pad=arrows, A=Space, B=LCtrl, X=LShift,
# Y=LAlt, L=E, R=T, Start=Return, Select=RCtrl, Menu=Escape.
# Desktop extras: WASD, Z/X, Enter, Esc, M for map, F/P/C/R care hotkeys.
DEFAULT_KEYS = {
    "UP": ["up", "w"], "DOWN": ["down", "s"], "LEFT": ["left", "a"], "RIGHT": ["right", "d"],
    "A": ["space", "z", "j"],
    "B": ["left ctrl", "x", "k", "escape", "backspace"],
    "X": ["left shift", "i"], "Y": ["left alt", "y"],
    "L": ["e", "page up", "q"], "R": ["t", "page down"],
    "START": ["return", "keypad enter"],
    "SELECT": ["right ctrl", "tab", "m"],
    # Keyboard-only shortcuts for care actions (old F/P/C/R bindings)
    "HOT_FEED": ["f"], "HOT_PLAY": ["p"], "HOT_CLEAN": ["c"], "HOT_REST": ["r"],
}
# Raw joystick fallback (Xbox-style indices, also what most SDL handheld builds use)
DEFAULT_JOY_BUTTONS = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "L", 5: "R",
                       6: "SELECT", 7: "START", 8: "SELECT", 9: "START"}
REPEAT_DELAY, REPEAT_RATE = 0.32, 0.11
AXIS_DEADZONE = 0.55


class InputManager:
    def __init__(self, config_path: str | None = None):
        self.key_map: dict[int, str] = {}
        self.joy_buttons = dict(DEFAULT_JOY_BUTTONS)
        self.swap_ab = False
        keys = {k: list(v) for k, v in DEFAULT_KEYS.items()}
        cfg = self._read_config(config_path)
        if cfg:
            for action, names in (cfg.get("keyboard") or {}).items():
                keys[action] = list(names)
            for idx, action in (cfg.get("joystick_buttons") or {}).items():
                self.joy_buttons[int(idx)] = action
            self.swap_ab = bool(cfg.get("swap_ab", False))
        for action, names in keys.items():
            for name in names:
                try:
                    self.key_map[pygame.key.key_code(name)] = action
                except (ValueError, pygame.error):
                    print(f"[Input] unknown key name {name!r}")
        self.held: set[str] = set()
        self._repeat: dict[str, float] = {}
        self._axis_state: dict[tuple, str | None] = {}
        self._controllers = {}     # instance_id -> Controller
        self._joysticks = {}       # instance_id -> Joystick
        self.last_device = "keyboard"
        self.idle_time = 0.0
        self._init_pads()

    @staticmethod
    def _read_config(path):
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as e:
            print(f"[Input] ignoring bad {path}: {e}")
            return None

    # ------------------------------------------------------------ devices
    def _init_pads(self):
        try:
            pygame.joystick.init()
        except pygame.error:
            return
        self._controller_mod = None
        try:
            from pygame._sdl2 import controller as ctl
            ctl.init()
            self._controller_mod = ctl
        except Exception:  # noqa: BLE001 - optional on old pygame builds
            self._controller_mod = None
        for i in range(pygame.joystick.get_count()):
            self._open(i)

    def _open(self, device_index):
        ctl = self._controller_mod
        try:
            if ctl and ctl.is_controller(device_index):
                c = ctl.Controller(device_index)
                js = c.as_joystick()
                self._controllers[js.get_instance_id()] = c
                return
            js = pygame.joystick.Joystick(device_index)
            js.init()
            self._joysticks[js.get_instance_id()] = js
        except pygame.error as e:
            print(f"[Input] could not open pad {device_index}: {e}")

    def _map_ab(self, action):
        if self.swap_ab and action in ("A", "B"):
            return "B" if action == "A" else "A"
        return action

    # ------------------------------------------------------------- events
    def process(self, event) -> list[str]:
        """Translate one pygame event into a list of pressed actions."""
        out: list[str] = []
        t = event.type
        if t == pygame.KEYDOWN:
            a = self.key_map.get(event.key)
            if a:
                out.append(a)
                self._press(a)
            self.last_device = "keyboard"
        elif t == pygame.KEYUP:
            a = self.key_map.get(event.key)
            if a:
                self._release(a)
        elif t == pygame.JOYDEVICEADDED:
            self._open(event.device_index)
        elif t == pygame.JOYDEVICEREMOVED:
            self._controllers.pop(event.instance_id, None)
            self._joysticks.pop(event.instance_id, None)
        elif t in (getattr(pygame, "CONTROLLERBUTTONDOWN", -1), getattr(pygame, "CONTROLLERBUTTONUP", -1)):
            a = self._controller_button(event.button)
            if a:
                if t == pygame.CONTROLLERBUTTONDOWN:
                    out.append(a)
                    self._press(a)
                    self.last_device = "pad"
                else:
                    self._release(a)
        elif t in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            if getattr(event, "instance_id", None) in self._controllers:
                return out  # handled via CONTROLLER* events
            a = self.joy_buttons.get(event.button)
            if a:
                a = self._map_ab(a)
                if t == pygame.JOYBUTTONDOWN:
                    out.append(a)
                    self._press(a)
                    self.last_device = "pad"
                else:
                    self._release(a)
        elif t == pygame.JOYHATMOTION:
            if getattr(event, "instance_id", None) not in self._controllers:
                x, y = event.value
                want = set()
                if x < 0: want.add("LEFT")
                if x > 0: want.add("RIGHT")
                if y > 0: want.add("UP")
                if y < 0: want.add("DOWN")
                for d in DIRS:
                    if d in want and d not in self.held:
                        out.append(d)
                        self._press(d)
                    elif d not in want and d in self.held:
                        self._release(d)
                self.last_device = "pad"
        elif t in (pygame.JOYAXISMOTION, getattr(pygame, "CONTROLLERAXISMOTION", -1)):
            if t == pygame.JOYAXISMOTION and getattr(event, "instance_id", None) in self._controllers:
                return out
            axis, value = event.axis, event.value
            if t != pygame.JOYAXISMOTION:
                value = value / 32767.0
            if axis in (0, 1):
                neg, pos = ("LEFT", "RIGHT") if axis == 0 else ("UP", "DOWN")
                key = (getattr(event, "instance_id", 0), axis)
                new = neg if value < -AXIS_DEADZONE else pos if value > AXIS_DEADZONE else None
                old = self._axis_state.get(key)
                if new != old:
                    if old:
                        self._release(old)
                    if new:
                        out.append(new)
                        self._press(new)
                        self.last_device = "pad"
                    self._axis_state[key] = new
        if out:
            self.idle_time = 0.0
        return out

    def _controller_button(self, button):
        C = pygame
        table = {
            getattr(C, "CONTROLLER_BUTTON_A", 0): "A",
            getattr(C, "CONTROLLER_BUTTON_B", 1): "B",
            getattr(C, "CONTROLLER_BUTTON_X", 2): "X",
            getattr(C, "CONTROLLER_BUTTON_Y", 3): "Y",
            getattr(C, "CONTROLLER_BUTTON_BACK", 4): "SELECT",
            getattr(C, "CONTROLLER_BUTTON_GUIDE", 5): "START",
            getattr(C, "CONTROLLER_BUTTON_START", 6): "START",
            getattr(C, "CONTROLLER_BUTTON_LEFTSHOULDER", 9): "L",
            getattr(C, "CONTROLLER_BUTTON_RIGHTSHOULDER", 10): "R",
            getattr(C, "CONTROLLER_BUTTON_DPAD_UP", 11): "UP",
            getattr(C, "CONTROLLER_BUTTON_DPAD_DOWN", 12): "DOWN",
            getattr(C, "CONTROLLER_BUTTON_DPAD_LEFT", 13): "LEFT",
            getattr(C, "CONTROLLER_BUTTON_DPAD_RIGHT", 14): "RIGHT",
        }
        a = table.get(button)
        return self._map_ab(a) if a else None

    def _press(self, a):
        self.held.add(a)
        if a in DIRS:
            self._repeat[a] = REPEAT_DELAY

    def _release(self, a):
        self.held.discard(a)
        self._repeat.pop(a, None)

    def update(self, dt: float) -> list[str]:
        """Auto-repeat for held directions (menus). Returns repeated actions."""
        self.idle_time += dt
        out = []
        for a in list(self._repeat):
            self._repeat[a] -= dt
            if self._repeat[a] <= 0:
                self._repeat[a] = REPEAT_RATE
                out.append(a)
        return out

    def is_held(self, a: str) -> bool:
        return a in self.held

    def label(self, action: str) -> str:
        """Button name to show in on-screen hints."""
        if self.last_device == "pad":
            return {"START": "Start", "SELECT": "Select"}.get(action, action)
        return {"A": "Space", "B": "Esc", "START": "Enter", "SELECT": "M",
                "L": "Q", "R": "T", "X": "Shift", "Y": "Alt"}.get(action, action)
