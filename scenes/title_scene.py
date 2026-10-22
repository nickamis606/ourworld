"""TitleScene: Continue an existing pet, or pick a new companion."""
import math

import pygame

from core.roster import PET_ROSTER, roster_entry
from engine import assets
from scenes.base_scene import BaseScene
from sprites.pet_sprite import PetSprite
from ui.common import FOCUS, hint_bar
from ui.menu import Menu

COLS = 3
CELL_W, CELL_H = 180, 150
GRID_X, GRID_Y = 50, 110


class TitleScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.mode = "menu"
        self.index = 0
        self.sprites = None
        self.menu = None
        self.confirm_new = False

    def on_enter(self, mode=None, **kw):
        if self.sprites is None:
            self.sprites = [PetSprite(p, height=104) for p in PET_ROSTER]
        has = self.state.has_save
        self.mode = mode or ("menu" if has else "select")
        self.index = self.state.pet.species_id if has else 0
        self.menu = Menu("", [("continue", f"Continue with {self.state.pet.name}"),
                              ("new", "New pet")], width=360)

    def is_animating(self):
        return True

    # -------------------------------------------------------------- input
    def handle_action(self, a):
        if self.mode == "menu":
            if a in ("UP", "DOWN"):
                self.menu.move(1 if a == "DOWN" else -1)
            elif a in ("A", "START"):
                if self.menu.selected == "continue":
                    self.game.switch("main", message=f"Welcome back! {self.state.pet.name} missed you.")
                else:
                    self.mode = "select"
            return
        moves = {"LEFT": -1, "RIGHT": 1, "UP": -COLS, "DOWN": COLS}
        if a in moves:
            self.index = (self.index + moves[a]) % len(PET_ROSTER)
            self.confirm_new = False
        elif a in ("A", "START"):
            self._choose()
        elif a == "B" and self.state.has_save:
            self.mode = "menu"
            self.confirm_new = False

    def handle_event(self, e):
        if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
            return
        if self.mode == "menu":
            i = self.menu.hit(e.pos, (320, 360))
            if i is not None:
                self.menu.index = i
                self.handle_action("A")
            return
        for i in range(len(PET_ROSTER)):
            if self._cell(i).collidepoint(e.pos):
                if self.index == i:
                    self._choose()
                self.index = i

    def _choose(self):
        if self.state.has_save and not self.confirm_new:
            self.confirm_new = True   # starting over replaces the old pet: ask twice
            return
        entry = PET_ROSTER[self.index]
        self.state.new_game(entry["name"], entry["id"])
        self.game.switch("main", message=f"Say hi to {entry['name']}! Try Feed and Play.")

    def _cell(self, i):
        return pygame.Rect(GRID_X + (i % COLS) * (CELL_W + 10), GRID_Y + (i // COLS) * (CELL_H + 10), CELL_W, CELL_H)

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        for s in self.sprites:
            s.update(dt)

    def _bg(self, surf):
        for y in range(0, 480, 4):
            k = y / 480
            pygame.draw.rect(surf, (int(255 - 30 * k), int(236 - 20 * k), int(214 + 20 * k)), (0, y, 640, 4))
        for i in range(14):
            x = (i * 97 + self.t * 14) % 700 - 30
            y = 40 + (i * 53) % 400
            pygame.draw.circle(surf, (255, 250, 240), (int(x), y), 3 + i % 3)

    def draw(self, surf):
        self._bg(surf)
        title = assets.text_outlined("OurWorld", 64, (255, 200, 90), (110, 60, 40))
        surf.blit(title, title.get_rect(center=(320, 52 + 4 * math.sin(self.t * 2))))
        if self.mode == "menu":
            sp = self.sprites[self.state.pet.species_id]
            sp.set_feet(320, 270)
            sp.draw(surf, {"dy": -10 * abs(math.sin(self.t * 3))})
            self.menu.draw(surf, (320, 360), veil=False)
            hint_bar(surf, [("D-pad", "Choose"), ("A", "OK")])
            return
        sub = assets.text("Choose your companion", 28, (110, 70, 50), bold=True)
        surf.blit(sub, sub.get_rect(center=(320, 94)))
        for i, entry in enumerate(PET_ROSTER):
            r = self._cell(i)
            sel = i == self.index
            pygame.draw.rect(surf, (255, 252, 246) if sel else (250, 240, 228), r, border_radius=14)
            pygame.draw.rect(surf, FOCUS if sel else (220, 200, 180), r, 4 if sel else 2, border_radius=14)
            sp = self.sprites[i]
            sp.set_feet(r.centerx, r.bottom - 30)
            pose = {"dy": -12 * abs(math.sin(self.t * 4))} if sel else None
            sp.draw(surf, pose, idle=sel)
            name = assets.text(entry["name"], 24, (90, 60, 50), bold=sel)
            surf.blit(name, name.get_rect(center=(r.centerx, r.bottom - 14)))
        if self.confirm_new:
            msg = assets.text_outlined(f"Replace {self.state.pet.name}? Press A again to confirm",
                                       24, (255, 230, 220), (150, 40, 40))
            surf.blit(msg, msg.get_rect(center=(320, 440)))
        else:
            hint_bar(surf, [("D-pad", "Choose"), ("A", "Adopt")] + ([("B", "Back")] if self.state.has_save else []))
