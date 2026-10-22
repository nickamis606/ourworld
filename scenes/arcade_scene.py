"""ArcadeScene: cabinet picker -> minigame -> results card with rewards.

Also hosts: the Weekly Challenge banner, 2-player hot-seat (X in the picker:
take turns, compare scores; rewards are paid once, for the best score), and
fishing at Sunny Pond (on_enter(game="fishing"), not listed in the picker).
"""
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
PICK_COLS = 3
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
        self.players = 1
        self.turn = 0
        self.scores = []
        self.toast = None

    def on_enter(self, game=None, **kw):
        self.phase = "pick"
        self.minigame = None
        self.result = None
        self.toast = None
        self.turn, self.scores = 0, []
        if game == "fishing":
            self.game.audio.music("calm")
            self._start("fishing")
            return
        self.game.audio.music("arcade")
        if game in ORDER:
            self.index = ORDER.index(game)
            self._start(game)

    @property
    def fishing(self):
        return self.kind == "fishing"

    def on_exit(self):
        self.minigame = None

    def is_animating(self):
        return True

    # -------------------------------------------------------------- flow
    def _start(self, kind, keep_turn=False):
        color = roster_entry(self.state.pet.species_id)["color"]
        if kind == "fishing":
            ok, why = self.state.can_fish()
            if not ok:
                self.kind = None
                self.toast = why
                self._leave()
                return
            import random
            from minigames.fishing import Fishing
            rng = random.Random()
            self.kind = kind
            from sprites.pet_sprite import PetSprite
            img = PetSprite(roster_entry(self.state.pet.species_id), height=84).base
            self.minigame = Fishing(self.game.screen, roll=lambda b: self.state.roll_fish(rng, b),
                                    pet_color=color, pet_img=img)
            self.phase = "play"
            self.end_t = 0.0
            return
        if self.state.pet.needs.energy < 8:
            self.result = None
            self.phase = "pick"
            self.toast = f"{self.state.pet.name} is too tired. Rest first!"
            return
        if not keep_turn:
            self.turn, self.scores = 0, []
        self.kind = kind
        self.minigame = minigames.create(kind, self.game.screen, color)
        self.phase = "play"
        self.end_t = 0.0

    def _finish(self):
        score = int(getattr(self.minigame, "score", 0))
        if self.fishing:
            catches = list(getattr(self.minigame, "catches", []))
            self.result = dict(self.state.finish_fishing(catches), score=score, catches=catches)
            self.phase = "result"
            self.game.sfx("catch" if catches else "splash")
            self.menu = Menu("", [("again", "Fish again"), ("back", "Back to the pond")], width=280)
            return
        if self.players == 2:
            self.scores.append(score)
            if self.turn == 0:
                self.turn = 1
                self.phase = "handoff"
                self.minigame = None
                self.game.sfx("select")
                return
            score = max(self.scores)
        self.result = dict(self.state.finish_minigame(self.kind, score), score=score,
                           scores=list(self.scores) if self.players == 2 else None)
        self.phase = "result"
        self.game.sfx("levelup" if self.result.get("weekly") else "coin")
        self.menu = Menu("", [("again", "Play again"), ("back", "Back to Arcade")], width=280)

    def _leave(self):
        default = "Back from fishing!" if self.kind == "fishing" else "Back from the arcade!"
        self.game.switch("main", message=self.toast or default)

    # -------------------------------------------------------------- input
    def handle_action(self, a):
        if self.phase == "pick":
            n = len(ORDER)
            if a == "LEFT":
                self.index = (self.index - 1) % n
            elif a == "RIGHT":
                self.index = (self.index + 1) % n
            elif a in ("UP", "DOWN"):
                self.index = (self.index + PICK_COLS) % n if a == "DOWN" else (self.index - PICK_COLS) % n
            elif a in ("A", "START"):
                self.toast = None
                self.game.sfx("select")
                self._start(ORDER[self.index])
            elif a == "X":
                self.players = 2 if self.players == 1 else 1
                self.toast = "2 players: take turns, then compare!" if self.players == 2 else "1 player"
                self.game.sfx("select")
            elif a == "B":
                self.toast = None
                self._leave()
            if a in ("LEFT", "RIGHT", "UP", "DOWN"):
                self.game.sfx("move")
        elif self.phase == "handoff":
            if a in ("A", "START"):
                self._start(self.kind, keep_turn=True)
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
                elif self.fishing:
                    self._leave()
                else:
                    self.phase = "pick"
            elif a == "B":
                if self.fishing:
                    self._leave()
                else:
                    self.phase = "pick"

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.phase == "pick":
                for i in range(len(ORDER)):
                    if self._cab_rect(i).collidepoint(e.pos):
                        self.index = i
                        self.handle_action("A")
            elif self.phase in ("play", "handoff"):
                self.handle_action("A")
            elif self.phase == "result":
                i = self.menu.hit(e.pos, (320, 322))
                if i is not None:
                    self.menu.index = i
                    self.handle_action("A")

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        # needs do not decay while a minigame runs (fair play)
        if self.phase == "play":
            # continuous-control games (paddles) read held directions
            self.minigame.held = {a for a in self.game.input.held if a in ("UP", "DOWN", "LEFT", "RIGHT", "A")}
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
        c, r = i % PICK_COLS, i // PICK_COLS
        return pygame.Rect(45 + c * 190, 112 + r * 136, 170, 124)

    def draw(self, surf):
        if self.phase == "handoff":
            self._draw_handoff(surf)
            return
        if self.phase in ("play", "paused", "result") and self.minigame:
            self.minigame.draw(surf)
            if self.phase == "play":
                if self.players == 2 and not self.fishing:
                    tag = assets.text_outlined(f"Player {self.turn + 1}", 22, (255, 240, 160), (40, 30, 60))
                    surf.blit(tag, tag.get_rect(midtop=(320, 10)))
                if not self.fishing:
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
        coins = assets.text(f"Coins {self.state.pet.coins}   Energy {int(self.state.pet.needs.energy)}", 19, (230, 230, 250))
        surf.blit(coins, (20, 82))
        wk = self.state.weekly_challenge()
        label = (f"Weekly: {GAME_INFO[wk['game']]['name']} {wk['target']}+  " +
                 ("DONE!" if wk["done"] else f"best {wk['best']}"))
        wt = assets.text(label, 19, (40, 30, 10), bold=True)
        wb = pygame.Rect(0, 0, wt.get_width() + 36, 26)
        wb.topright = (624, 78)
        pygame.draw.rect(surf, (120, 220, 140) if wk["done"] else (250, 210, 80), wb, border_radius=12)
        surf.blit(icon("spark", 18), (wb.x + 8, wb.y + 4))
        surf.blit(wt, (wb.x + 28, wb.y + 4))
        pl = assets.text("2P" if self.players == 2 else "1P", 20, (255, 255, 255), bold=True)
        pr = pygame.Rect(0, 0, 44, 26)
        pr.topleft = (wb.x - 52, 78)
        pygame.draw.rect(surf, (200, 80, 160) if self.players == 2 else (90, 90, 130), pr, border_radius=12)
        surf.blit(pl, pl.get_rect(center=pr.center))
        for i, key in enumerate(ORDER):
            info = GAME_INFO[key]
            r = self._cab_rect(i)
            sel = i == self.index
            if sel:
                r = r.move(0, -8 + int(3 * math.sin(self.t * 4)))
            c = info["color"]
            pygame.draw.rect(surf, tuple(v // 2 for v in c), r, border_radius=14)
            pygame.draw.rect(surf, c, (r.x + 6, r.y + 6, r.w - 12, 26), border_radius=8)
            name = assets.text(info["name"], 24, (255, 255, 255), bold=True)
            surf.blit(name, name.get_rect(center=(r.centerx, r.y + 19)))
            scr = pygame.Rect(r.x + 12, r.y + 38, r.w - 24, 56)
            pygame.draw.rect(surf, (12, 16, 24), scr, border_radius=6)
            ic = icon(key, 44)
            surf.blit(ic, ic.get_rect(center=scr.center))
            best = self.state.save_manager.get_high_score(key)
            bt = assets.text(f"Best: {best}", 20, (255, 240, 200))
            surf.blit(bt, bt.get_rect(center=(r.centerx, r.bottom - 15)))
            if key == wk["game"]:
                rib = assets.text("WEEKLY", 14, (60, 40, 0), bold=True)
                rr = rib.get_rect(topright=(r.right - 4, r.y + 36))
                pygame.draw.rect(surf, (250, 210, 80), rr.inflate(8, 4), border_radius=6)
                surf.blit(rib, rr)
            if sel:
                pygame.draw.rect(surf, FOCUS, r.inflate(6, 6), 4, border_radius=16)
        how = GAME_INFO[ORDER[self.index]]["how"]
        t = assets.text(how, 21, (255, 255, 255))
        surf.blit(t, t.get_rect(center=(320, 400)))
        toast = getattr(self, "toast", None)
        if toast:
            tt = assets.text_outlined(toast, 24, (255, 220, 210), (140, 30, 40))
            surf.blit(tt, tt.get_rect(center=(320, 428)))
        hint_bar(surf, [("D-pad", "Choose"), ("A", "Play"), ("X", "1P/2P"), ("B", "Leave")])

    def _draw_handoff(self, surf):
        surf.blit(backdrops.get("arcade"), (0, 0))
        surf.blit(panel((640, 480), (10, 6, 24, 170), 0, None), (0, 0))
        box = pygame.Rect(120, 120, 400, 220)
        surf.blit(panel(box.size, (255, 250, 240, 245), 18), box.topleft)
        t = assets.text(f"Player 1 scored {self.scores[0]}!", 30, (90, 70, 60), bold=True)
        surf.blit(t, t.get_rect(center=(320, 170)))
        t = assets.text("Pass the console to Player 2", 24, (200, 80, 160), bold=True)
        surf.blit(t, t.get_rect(center=(320, 230)))
        t = assets.text("Press A when you're ready!", 22, (110, 90, 80))
        surf.blit(t, t.get_rect(center=(320, 290)))
        hint_bar(surf, [("A", "Start Player 2")])

    def _draw_result(self, surf):
        if self.fishing:
            return self._draw_fish_result(surf)
        surf.blit(panel((640, 480), (10, 10, 20, 160), 0, None), (0, 0))
        box = pygame.Rect(140, 90, 360, 300)
        surf.blit(panel(box.size, (255, 250, 240, 245), 18), box.topleft)
        r = self.result
        if r.get("scores"):
            a, b = r["scores"]
            head = "It's a tie!" if a == b else f"Player {1 if a > b else 2} wins!"
            t = assets.text(head, 34, (200, 80, 160), bold=True)
            surf.blit(t, t.get_rect(center=(320, 118)))
            s = assets.text(f"P1: {a}    P2: {b}", 26, (70, 60, 60), bold=True)
        else:
            t = assets.text("New best!" if r["new_best"] else "Run over", 36,
                            (220, 120, 30) if r["new_best"] else (90, 70, 60), bold=True)
            surf.blit(t, t.get_rect(center=(320, 120)))
            s = assets.text(f"Score {r['score']}   (best {r['best']})", 26, (70, 60, 60))
        surf.blit(s, s.get_rect(center=(320, 156)))
        if r.get("weekly"):
            w = assets.text_outlined("Weekly Challenge won!", 22, (255, 230, 120), (120, 60, 20))
            surf.blit(w, w.get_rect(center=(320, 74)))
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
        self.menu.draw(surf, (320, 322), veil=False, box=False)

    def _draw_fish_result(self, surf):
        from core import fish_data
        surf.blit(panel((640, 480), (10, 10, 20, 160), 0, None), (0, 0))
        box = pygame.Rect(120, 60, 400, 340)
        surf.blit(panel(box.size, (255, 250, 240, 245), 18), box.topleft)
        r = self.result
        n = len(r["catches"])
        t = assets.text(f"You caught {n} fish!" if n else "No bites this time", 32, (60, 110, 160), bold=True)
        surf.blit(t, t.get_rect(center=(320, 92)))
        y = 124
        for key, size in r["catches"][:5]:
            name, _w, coins, col = fish_data.FISH[key][:4]
            pygame.draw.ellipse(surf, col, (160, y + 4, 30, 16))
            pygame.draw.polygon(surf, col, [(186, y + 12), (198, y + 4), (198, y + 20)])
            new = " NEW!" if key in r["new"] else ""
            surf.blit(assets.text(f"{name}  {size} cm{new}", 20, (80, 60, 50), bold=bool(new)), (208, y + 2))
            surf.blit(assets.text(f"+{coins}", 20, (170, 110, 20), bold=True), (448, y + 2))
            y += 28
        surf.blit(icon("coin", 24), (200, 274))
        surf.blit(assets.text(f"+{r['coins']} coins", 24, (170, 110, 20), bold=True), (232, 278))
        self.menu.draw(surf, (320, 342), veil=False, box=False)
