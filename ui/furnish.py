"""Furnish mode at Home: D-pad moves the cursor on the 8x3 grid, L/R choose an
item you own, A places it (or picks up what's there), B is done."""
import pygame

from core.furniture import FURNITURE, GRID_COLS, GRID_ROWS, fits
from engine import assets
from sprites import furniture as FS
from ui.common import FOCUS, hint_bar, panel


class FurnishMode:
    def __init__(self, state):
        self.state = state
        self.col, self.row = 3, 1
        self.pick = 0
        self.open = True
        self.msg = ""
        self.t = 0.0

    def owned(self):
        return self.state.furniture_owned()

    def selected(self):
        o = self.owned()
        if not o:
            return None
        self.pick %= len(o)
        return o[self.pick]

    def handle_action(self, a):
        """Returns a result dict for place/pick-up so the scene can play feedback."""
        if a == "LEFT":
            self.col = (self.col - 1) % GRID_COLS
        elif a == "RIGHT":
            self.col = (self.col + 1) % GRID_COLS
        elif a == "UP":
            self.row = (self.row - 1) % GRID_ROWS
        elif a == "DOWN":
            self.row = (self.row + 1) % GRID_ROWS
        elif a == "L":
            self.pick -= 1
            self.selected()
        elif a == "R":
            self.pick += 1
            self.selected()
        elif a in ("B", "START", "SELECT"):
            self.open = False
        elif a in ("A", "Y", "X"):
            here = self.state.furniture_at(self.col, self.row)
            if here:
                res = self.state.remove_furniture(self.col, self.row)
            else:
                key = self.selected()
                if key is None:
                    res = {"success": False, "msg": "No furniture yet - buy some or finish quests!"}
                else:
                    res = self.state.place_furniture(self.col, self.row, key)
            self.msg = res["msg"]
            return res
        return None

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        # grid
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rect = FS.cell_rect(c, r)
                pygame.draw.rect(surf, (255, 255, 255), rect, 1, border_radius=6)
        rect = FS.cell_rect(self.col, self.row)
        key = self.selected()
        here = self.state.furniture_at(self.col, self.row)
        if not here and key:
            ghost = FS.surface(key, 64 if self.row == 0 else 58).copy()
            ghost.set_alpha(150)
            surf.blit(ghost, ghost.get_rect(midbottom=(rect.centerx, rect.bottom)))
            ok = fits(key, self.row)
        else:
            ok = True
        pulse = 3 if int(self.t * 4) % 2 else 4
        pygame.draw.rect(surf, FOCUS if ok else (230, 80, 80), rect, pulse, border_radius=8)
        # top panel
        surf.blit(panel((600, 54), (60, 40, 30, 220), 14, None), (20, 50))
        if key:
            n = self.state.extras.furniture.get(key, 0)
            where = "wall" if FURNITURE[key][1] else "floor"
            label = f"< {FURNITURE[key][0]} x{n} >   ({where})"
        else:
            label = "No furniture to place yet"
        surf.blit(assets.text(label, 20, (255, 240, 200), bold=True), (36, 56))
        sub = self.msg or (f"Here: {FURNITURE[here][0]} (A picks it up)" if here else
                           f"{len(self.state.extras.layout)} placed - each one makes Home cozier")
        surf.blit(assets.text(sub, 16, (240, 220, 200)), (36, 80))
        hint_bar(surf, [("D-pad", "Move"), ("L/R", "Item"), ("A", "Place / pick up"), ("B", "Done")])
