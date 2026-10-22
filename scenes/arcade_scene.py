"""ArcadeScene: cabinet picker -> minigame -> results card with rewards."""
import math

import pygame

import minigames
from minigames import GAME_INFO
from core.roster import roster_entry
from engine import assets
from scenes.base_scene import BaseScene
from sprites import backdrops
from ui.common import FOCUS, hint_bar, panel
from ui.icons import icon
from ui.menu import Menu

ORDER = list(GAME_INFO)
END_DELAY = 0.9  # let the crash/game-over moment land before the card


class ArcadeScene(BaseScene):
    low_power_ok = False

    def __init__(self, game):
        super().__init__(game)
        self.index = 0
        self.minigame = None
        self.kind = None
        self.phase = "pick"   # pick | play | paused | result
        self.end_t = 0.0
        self.result = None
        self.pause = None
        self.t = 0.0

    def on_enter(self, game=None, **kw):
        self.phase = "pick"
        self.minigame = None
        self.result = None
        if game in ORDER:
            self.index = ORDER.index(game)
            self._start(game)

    def on_exit(self):
        self.minigame = None

    def is_animating(self):
        return True

    # -------------------------------------------------------------- flow
    def _start(self, kind):
        if self.state.pet.needs.energy < 8:
            self.result = None
            self.phase = "pick"
            self.toast = f"{self.state.pet.name} is too tired. Rest first!"
            return
        self.kind = kind
        color = roster_entry(self.state.pet.species_id)["color"]
        self.minigame = minigames.create(kind, self.game.screen, color)
        self.phase = "play"
        self.end_t = 0.0

    def _finish(self):
        score = int(getattr(self.minigame, "score", 0))
        self.result = dict(self.state.finish_minigame(self.kind, score), score=score)
        self.phase = "result"
        self.menu = Menu("", [("again", "Play again"), ("back", "Back to Arcade")], width=280)

    def _leave(self):
        self.game.switch("main", message=getattr(self, "toast", None) or "Back from the arcade!")

    # -------------------------------------------------------------- input
    def handle_action(self, a):
        if self.phase == "pick":
            if a in ("LEFT", "UP"):
                self.index = (self.index - 1) % len(ORDER)
            elif a in ("RIGHT", "DOWN"):
                self.index = (self.index + 1) % len(ORDER)
            elif a in ("A", "START"):
                self.toast = None
                self._start(ORDER[self.index])
            elif a == "B":
                self.toast = None
                self._leave()
        elif self.phase == "play":
            if a in ("START", "B"):
                self.phase = "paused"
                self.pause = Menu("Paused", [("resume", "Resume"), ("quit", "End run")], width=260)
            else:
                minigames.press(self.minigame, a)
        elif self.phase == "paused":
            if a in ("UP", "DOWN"):
                self.pause.move(1)
            elif a in ("B", "START"):
                self.phase = "play"
            elif a == "A":
                if self.pause.selected == "resume":
                    self.phase = "play"
                else:
                    self._finish()
        elif self.phase == "result":
            if a in ("UP", "DOWN"):
                self.menu.move(1)
            elif a in ("A", "START"):
                if self.menu.selected == "again":
                    self._start(self.kind)
                else:
                    self.phase = "pick"
            elif a == "B":
                self.phase = "pick"

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.phase == "pick":
                for i in range(len(ORDER)):
                    if self._cab_rect(i).collidepoint(e.pos):
                        self.index = i
                        self.handle_action("A")
            elif self.phase == "play":
                self.handle_action("A")
            elif self.phase == "result":
                i = self.menu.hit(e.pos, (320, 330))
                if i is not None:
                    self.menu.index = i
                    self.handle_action("A")

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        self.state.pet.needs  # needs do not decay while a minigame runs (fair play)
        if self.phase == "play":
            self.minigame.update(dt)
            over = getattr(self.minigame, "game_over", False) or not getattr(self.minigame, "running", True)
            if over:
                self.end_t += dt
                if self.end_t >= END_DELAY:
                    self._finish()
        elif self.phase == "pick":
            self.state.tick(dt)

    # --------------------------------------------------------------- draw
    def _cab_rect(self, i):
        return pygame.Rect(60 + i * 180, 120, 160, 230)

    def draw(self, surf):
        if self.phase in ("play", "paused", "result") and self.minigame:
            self.minigame.draw(surf)
            if self.phase == "play":
                hint_bar(surf, [("Start", "Pause")], y=462)
            elif self.phase == "paused":
                self.pause.draw(surf)
            else:
                self._draw_result(surf)
            return
        surf.blit(backdrops.get("arcade"), (0, 0))
        surf.blit(panel((640, 480), (10, 6, 24, 150), 0, None), (0, 0))
        title = assets.text_outlined("ARCADE", 54, (255, 220, 110), (120, 40, 160))
        surf.blit(title, title.get_rect(center=(320, 50)))
        coins = assets.text(f"Coins: {self.state.pet.coins}    Energy: {int(self.state.pet.needs.energy)}", 22, (230, 230, 250))
        surf.blit(coins, coins.get_rect(center=(320, 92)))
        for i, key in enumerate(ORDER):
            info = GAME_INFO[key]
            r = self._cab_rect(i)
            sel = i == self.index
            if sel:
                r = r.move(0, -8 + int(3 * math.sin(self.t * 4)))
            c = info["color"]
            pygame.draw.rect(surf, tuple(v // 2 for v in c), r, border_radius=14)
            pygame.draw.rect(surf, c, (r.x + 8, r.y + 8, r.w - 16, 34), border_radius=8)
            name = assets.text(info["name"], 28, (255, 255, 255), bold=True)
            surf.blit(name, name.get_rect(center=(r.centerx, r.y + 25)))
            screen = pygame.Rect(r.x + 16, r.y + 52, r.w - 32, 100)
            pygame.draw.rect(surf, (12, 16, 24), screen, border_radius=6)
            ic = icon(key, 64)
            surf.blit(ic, ic.get_rect(center=screen.center))
            best = self.state.save_manager.get_high_score(key)
            surf.blit(assets.text(f"Best: {best}", 22, (255, 240, 200)), (r.x + 18, r.y + 166))
            pygame.draw.circle(surf, (255, 80, 80), (r.x + 50, r.y + 206), 9)
            pygame.draw.circle(surf, (255, 220, 70), (r.x + 80, r.y + 206), 9)
            pygame.draw.circle(surf, (90, 200, 255), (r.x + 110, r.y + 206), 9)
            if sel:
                pygame.draw.rect(surf, FOCUS, r.inflate(6, 6), 4, border_radius=16)
        how = GAME_INFO[ORDER[self.index]]["how"]
        t = assets.text(how, 21, (255, 255, 255))
        surf.blit(t, t.get_rect(center=(320, 390)))
        toast = getattr(self, "toast", None)
        if toast:
            tt = assets.text_outlined(toast, 24, (255, 220, 210), (140, 30, 40))
            surf.blit(tt, tt.get_rect(center=(320, 420)))
        hint_bar(surf, [("D-pad", "Choose"), ("A", "Play"), ("B", "Leave")])

    def _draw_result(self, surf):
        surf.blit(panel((640, 480), (10, 10, 20, 160), 0, None), (0, 0))
        box = pygame.Rect(140, 90, 360, 300)
        surf.blit(panel(box.size, (255, 250, 240, 245), 18), box.topleft)
        r = self.result
        t = assets.text("New best!" if r["new_best"] else "Run over", 36,
                        (220, 120, 30) if r["new_best"] else (90, 70, 60), bold=True)
        surf.blit(t, t.get_rect(center=(320, 120)))
        s = assets.text(f"Score {r['score']}   (best {r['best']})", 26, (70, 60, 60))
        surf.blit(s, s.get_rect(center=(320, 156)))
        y = 186
        surf.blit(icon("coin", 24), (210, y))
        surf.blit(assets.text(f"+{r['coins']} coins", 24, (170, 110, 20), bold=True), (242, y + 4))
        y += 30
        for need, label, col in (("happiness", "Joy", (220, 70, 120)), ("energy", "Energy", (180, 140, 20))):
            v = r["deltas"].get(need, 0)
            if v:
                surf.blit(icon(need, 24), (210, y))
                surf.blit(assets.text(f"{'+' if v > 0 else ''}{int(round(v))} {label}", 24, col, bold=True), (242, y + 4))
                y += 30
        self.menu.draw(surf, (320, 330), veil=False)
