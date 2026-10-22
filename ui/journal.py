"""Journal overlay: Story (chapter, sparks, quests, daily wishes, calendar event,
weekly challenge), Stickers, Friends, Fish (the Sunny Pond fish book).

D-pad Left/Right (or L/R) switch tabs, Up/Down move, B/X close.
Reads core.story state only; never changes it.
"""
import pygame

from core import story_data as D
from core.story import bond_progress
from core.world import LOCATIONS
from engine import assets
from ui.common import FOCUS, hint_bar, panel
from ui.dialogue_box import portrait, wrap
from ui.icons import icon, sticker

from core import fish_data

TABS = ("Story", "Stickers", "Friends", "Fish")
MARK = {"available": ("!", (240, 150, 40)), "active": ("o", (90, 140, 220)),
        "ready": ("*", (240, 190, 40)), "done": ("v", (90, 170, 90))}


class Journal:
    def __init__(self):
        self.open = False
        self.tab = 0
        self.cursor = 0
        self.t = 0.0
        self.gs = None          # GameState (set by the scene) for events/weekly/fish

    def show(self, tab=0):
        self.open, self.tab, self.cursor = True, tab, 0

    def hide(self):
        self.open = False

    def update(self, dt):
        self.t += dt

    def _entries(self, story):
        e = []
        if self.gs is not None and self.gs.event_status():
            e.append("event")
        if story.daily.get("tasks"):
            e.append("daily")
        if self.gs is not None and story.is_unlocked("arcade"):
            e.append("weekly")
        # newest first: ready, active, available, then done
        order = {"ready": 0, "active": 1, "available": 2, "done": 3}
        qs = sorted(story.visible_quests(), key=lambda q: (order[story.status(q)], D.QUEST_ORDER.index(q)))
        return e + qs

    def handle_action(self, a, story):
        n = {0: len(self._entries(story)), 1: len(D.STICKERS), 2: len(D.NPCS), 3: len(fish_data.FISH)}[self.tab]
        cols = {0: 1, 1: 6, 2: 2, 3: 4}[self.tab]
        if a in ("B", "X", "START", "SELECT"):
            self.hide()
        elif a in ("L",) or (a == "LEFT" and self.tab == 0):
            self.tab, self.cursor = (self.tab - 1) % len(TABS), 0
        elif a in ("R",) or (a == "RIGHT" and self.tab == 0):
            self.tab, self.cursor = (self.tab + 1) % len(TABS), 0
        elif a == "LEFT":
            if self.cursor % cols == 0:
                self.tab, self.cursor = (self.tab - 1) % len(TABS), 0
            else:
                self.cursor -= 1
        elif a == "RIGHT":
            if self.cursor % cols == cols - 1 or self.cursor + 1 >= n:
                self.tab, self.cursor = (self.tab + 1) % len(TABS), 0
            else:
                self.cursor += 1
        elif a == "UP" and n:
            self.cursor = (self.cursor - cols) % n if self.cursor - cols >= 0 else self.cursor
        elif a == "DOWN" and n:
            self.cursor = self.cursor + cols if self.cursor + cols < n else self.cursor

    # ---------------------------------------------------------------- draw
    def draw(self, surf, state):
        story, pet = state.story, state.pet
        surf.blit(panel((640, 480), (20, 24, 40, 215), 0, None), (0, 0))
        book = pygame.Rect(14, 14, 612, 436)
        surf.blit(panel(book.size, (255, 248, 232, 250), 16, (150, 100, 70)), book.topleft)
        for i, name in enumerate(TABS):
            r = pygame.Rect(30 + i * 130, 22, 120, 30)
            sel = i == self.tab
            pygame.draw.rect(surf, (220, 120, 90) if sel else (230, 210, 190), r, border_radius=10)
            t = assets.text(name, 20, (255, 255, 255) if sel else (120, 90, 80), bold=True)
            surf.blit(t, t.get_rect(center=r.center))
        lvl, into, need = bond_progress(pet.bond_xp)
        title = D.BOND_TITLES[min(lvl, len(D.BOND_TITLES)) - 1]
        bt = assets.text(f"Bond Lv {lvl}: {title}", 18, (190, 80, 110), bold=True)
        surf.blit(bt, (book.right - bt.get_width() - 16, 22))
        bar = pygame.Rect(book.right - 186, 44, 170, 8)
        pygame.draw.rect(surf, (230, 210, 210), bar, border_radius=4)
        if need:
            pygame.draw.rect(surf, (240, 110, 150), (bar.x, bar.y, int(bar.w * into / need), bar.h), border_radius=4)
        else:
            pygame.draw.rect(surf, (240, 110, 150), bar, border_radius=4)
        from core.pets import stage_label
        who = " - ".join(x for x in (pet.name, state.trait_info["name"], stage_label(state.stage)) if x)
        wt = assets.text(who, 15, (150, 110, 100), bold=True)
        surf.blit(wt, (book.right - wt.get_width() - 16, 56))
        self.gs = state
        [self._story, self._stickers, self._friends, self._fish][self.tab](surf, state)
        hint_bar(surf, [("L/R", "Tabs"), ("D-pad", "Look"), ("B", "Close")], y=458)

    def _story(self, surf, state):
        story = state.story
        ch = story.chapter_info()
        head = "The End... for now!" if story.finished else f"Chapter {ch['id']}: {ch['title']}"
        surf.blit(assets.text(head, 24, (110, 60, 50), bold=True), (32, 62))
        summary = "Willowby is glowing again. Visit friends and grant Daily Wishes!" if story.finished else ch["summary"]
        surf.blit(assets.text(summary, 17, (120, 100, 90)), (32, 92))
        # sparks
        x = 32
        surf.blit(assets.text("Sparks", 17, (120, 100, 90), bold=True), (x, 118))
        for i, key in enumerate(D.SPARKS):
            got = key in story.sparks
            c = D.SPARKS[key][1] if got else (200, 190, 185)
            cx = 110 + i * 30
            pygame.draw.circle(surf, c, (cx, 128), 11)
            if got:
                surf.blit(icon("spark", 16), (cx - 8, 120))
        entries = self._entries(story)
        if not entries:
            return
        self.cursor = min(self.cursor, len(entries) - 1)
        top = max(0, self.cursor - 7)
        y = 150
        for i, e in enumerate(entries[top:top + 8], start=top):
            r = pygame.Rect(26, y, 268, 32)
            sel = i == self.cursor
            pygame.draw.rect(surf, (255, 236, 200) if sel else (246, 236, 220), r, border_radius=8)
            if sel:
                pygame.draw.rect(surf, FOCUS, r, 3, border_radius=8)
            if e == "daily":
                done = sum(1 for t in story.daily["tasks"] if t["done"])
                surf.blit(icon("spark", 20), (r.x + 8, r.y + 6))
                label = f"Daily Wishes ({done}/{len(story.daily['tasks'])})"
                col = (60, 130, 170)
            elif e == "event":
                ev = state.event_status()
                surf.blit(icon("pumpkin" if ev["key"] == "harvest_fair" else "snowman" if ev["key"] == "snow_day"
                               else "egg" if ev["key"] == "egg_hunt" else "fish", 20), (r.x + 8, r.y + 6))
                label = ev["name"] + ("  (done!)" if ev["done"] else "")
                col = (190, 100, 40)
            elif e == "weekly":
                wk = state.weekly_challenge()
                surf.blit(icon("trophy", 20), (r.x + 8, r.y + 6))
                label = "Weekly Challenge" + ("  (won!)" if wk["done"] else "")
                col = (150, 110, 20)
            else:
                st = story.status(e)
                m, mc = MARK[st]
                pygame.draw.circle(surf, mc, (r.x + 17, r.centery), 10)
                surf.blit(assets.text(m, 16, (255, 255, 255), bold=True), (r.x + 12, r.y + 6))
                label = D.QUESTS[e]["title"] + ("  (side)" if D.QUESTS[e].get("side") else "")
                col = (130, 120, 110) if st == "done" else (80, 60, 50)
            surf.blit(assets.text(label, 18, col, bold=True), (r.x + 34, r.y + 7))
            y += 36
        self._detail(surf, state, entries[self.cursor])

    def _detail(self, surf, state, e):
        story, name = state.story, state.pet.name
        x, y, w = 312, 150, 296
        surf.blit(panel((w + 8, 290), (250, 242, 228, 255), 10, (200, 170, 140)), (x - 4, y - 4))
        if e == "daily":
            surf.blit(assets.text("Today's Daily Wishes", 20, (60, 110, 150), bold=True), (x + 8, y + 6))
            yy = y + 38
            for t in story.daily["tasks"]:
                txt = t["text"].replace("{pet}", name)
                self._check(surf, x + 8, yy, t["done"], f"{txt} ({min(t['progress'], t['count'])}/{t['count']})")
                yy += 30
            surf.blit(assets.text("New wishes every day. +15 coins each!", 16, (130, 110, 100)), (x + 8, yy + 10))
            return
        if e == "event":
            ev = state.event_status()
            surf.blit(assets.text(ev["name"], 20, (190, 100, 40), bold=True), (x + 8, y + 6))
            yy = y + 38
            for line in wrap(ev["desc"], 17, w - 16):
                surf.blit(assets.text(line, 17, (90, 80, 75)), (x + 8, yy))
                yy += 22
            yy += 8
            self._check(surf, x + 8, yy, ev["done"], f"{ev['text']} ({ev['progress']}/{ev['count']})")
            from core.furniture import FURNITURE
            prize = f"Prize: {ev['reward']['coins']} coins, a sticker"
            if ev.get("furniture"):
                prize += f", {FURNITURE[ev['furniture']][0]}"
            for line in wrap(prize, 16, w - 16):
                surf.blit(assets.text(line, 16, (130, 110, 100)), (x + 8, yy + 40))
                yy += 20
            return
        if e == "weekly":
            from minigames import GAME_INFO
            from core.weekly import REWARD
            wk = state.weekly_challenge()
            surf.blit(assets.text("Weekly Challenge", 20, (150, 110, 20), bold=True), (x + 8, y + 6))
            g = GAME_INFO[wk["game"]]["name"]
            yy = y + 40
            for line in wrap(f"This week: score {wk['target']} or more in {g} at the Arcade. "
                             "A new game every Monday!", 17, w - 16):
                surf.blit(assets.text(line, 17, (90, 80, 75)), (x + 8, yy))
                yy += 22
            yy += 8
            self._check(surf, x + 8, yy, wk["done"], f"Score {wk['target']}+ in {g} (best {wk['best']})")
            surf.blit(assets.text(f"Prize: {REWARD['coins']} coins + Weekly Champ sticker", 16, (130, 110, 100)),
                      (x + 8, yy + 40))
            surf.blit(assets.text(f"Trophies won: {state.extras.trophies}", 16, (130, 110, 100)), (x + 8, yy + 62))
            return
        spec, st = D.QUESTS[e], story.quests[e]
        surf.blit(assets.text(spec["title"], 20, (110, 60, 50), bold=True), (x + 8, y + 6))
        npc = D.NPCS[spec["giver"]]
        surf.blit(assets.text(f"From {npc['name']}", 16, (150, 120, 100)), (x + 8, y + 32))
        yy = y + 54
        for line in wrap(spec["desc"].replace("{pet}", name), 17, w - 16):
            surf.blit(assets.text(line, 17, (90, 80, 75)), (x + 8, yy))
            yy += 22
        yy += 8
        if st["status"] == "available":
            where = LOCATIONS[npc["location"]]["name"]
            surf.blit(assets.text(f"Talk to {npc['name']} at {where}", 17, (200, 120, 40), bold=True), (x + 8, yy))
            return
        for i, step in enumerate(spec["steps"]):
            p, c = st["progress"][i], step["count"]
            label = step["text"].replace("{pet}", name) + (f" ({min(p, c)}/{c})" if c > 1 else "")
            self._check(surf, x + 8, yy, p >= c or st["status"] == "done", label)
            yy += 28
        if st["status"] == "ready":
            surf.blit(assets.text(f"Done! Go see {npc['name']}.", 17, (200, 140, 30), bold=True), (x + 8, yy + 8))
        rw = spec.get("reward", {})
        bits = []
        if rw.get("coins"):
            bits.append(f"{rw['coins']} coins")
        if rw.get("spark"):
            bits.append(D.SPARKS[rw["spark"]][0])
        if rw.get("sticker"):
            bits.append("a sticker")
        if bits:
            surf.blit(assets.text("Reward: " + ", ".join(bits), 16, (130, 110, 100)), (x + 8, y + 256))

    def _check(self, surf, x, y, done, text):
        box = pygame.Rect(x, y + 2, 18, 18)
        pygame.draw.rect(surf, (255, 255, 255), box, border_radius=4)
        pygame.draw.rect(surf, (160, 130, 110), box, 2, border_radius=4)
        if done:
            pygame.draw.lines(surf, (70, 160, 80), False, [(x + 3, y + 11), (x + 8, y + 16), (x + 16, y + 5)], 3)
        size = 17 if assets.font(17).size(text)[0] < 260 else 15
        surf.blit(assets.text(text, size, (130, 130, 120) if done else (70, 60, 55)), (x + 26, y + 2))

    def _stickers(self, surf, state):
        owned = state.story.stickers
        keys = list(D.STICKERS)
        surf.blit(assets.text(f"Sticker Book  {len(owned)}/{len(keys)}", 22, (110, 60, 50), bold=True), (32, 62))
        self.cursor = min(self.cursor, len(keys) - 1)
        for i, k in enumerate(keys):
            name, shape, col = D.STICKERS[k]
            c, r = i % 6, i // 6
            cx, cy = 80 + c * 96, 130 + r * 78
            img = sticker(shape, col, 60, k in owned)
            surf.blit(img, img.get_rect(center=(cx, cy)))
            if i == self.cursor:
                pygame.draw.circle(surf, FOCUS, (cx, cy), 34, 3)
        k = keys[self.cursor]
        name = D.STICKERS[k][0] if k in owned else "???"
        hint = "" if k in owned else ("  - explore Willow Woods" if k in D.WOODS_STICKERS else "  - earn it from a friend")
        t = assets.text(name + hint, 20, (90, 70, 60), bold=True)
        surf.blit(t, t.get_rect(center=(320, 432)))

    def _friends(self, surf, state):
        story = state.story
        surf.blit(assets.text("Friends in Willowby", 22, (110, 60, 50), bold=True), (32, 62))
        keys = list(D.NPCS)
        self.cursor = min(self.cursor, len(keys) - 1)
        for i, k in enumerate(keys):
            npc = D.NPCS[k]
            c, r = i % 2, i // 2
            box = pygame.Rect(26 + c * 298, 96 + r * 86, 290, 80)
            sel = i == self.cursor
            pygame.draw.rect(surf, (255, 236, 200) if sel else (246, 236, 220), box, border_radius=10)
            if sel:
                pygame.draw.rect(surf, FOCUS, box, 3, border_radius=10)
            known = k in story.met or story.is_unlocked(npc["location"])
            img = portrait(k)
            small = _small(k, img)
            if not known:
                small = small.copy()
                small.fill((60, 50, 60, 255), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(small, small.get_rect(midbottom=(box.x + 40, box.bottom - 4)))
            surf.blit(assets.text(npc["name"] if known else "???", 19, (90, 60, 50), bold=True), (box.x + 80, box.y + 8))
            place = LOCATIONS[npc["location"]].get("short", LOCATIONS[npc["location"]]["name"])
            surf.blit(assets.text(npc["title"] if known else "Not met yet", 15, (130, 110, 100)), (box.x + 80, box.y + 32))
            mine = [q for q in D.QUEST_ORDER if D.QUESTS[q]["giver"] == k]
            helped = mine and all(story.status(q) == "done" for q in mine
                                  if not D.QUESTS[q].get("side") or story.status(q) == "done")
            tag = ("Helped!" if helped and k in story.met else ("Met" if k in story.met else "")) if known else ""
            surf.blit(assets.text(place + ("   " + tag if tag else ""), 15,
                                  (80, 150, 90) if tag == "Helped!" else (150, 130, 120), bold=bool(tag)),
                      (box.x + 80, box.y + 54))


    def _fish(self, surf, state):
        book = state.extras.fish
        keys = fish_data.FISH_ORDER
        surf.blit(assets.text(f"Fish Book  {len(book)}/{len(keys)}", 22, (110, 60, 50), bold=True), (32, 62))
        self.cursor = min(self.cursor, len(keys) - 1)
        for i, k in enumerate(keys):
            name, _w, coins, col, size = fish_data.FISH[k][:5]
            c, r = i % 4, i // 4
            box = pygame.Rect(30 + c * 146, 96 + r * 92, 138, 84)
            sel = i == self.cursor
            pygame.draw.rect(surf, (255, 236, 200) if sel else (232, 240, 246), box, border_radius=10)
            if sel:
                pygame.draw.rect(surf, FOCUS, box, 3, border_radius=10)
            got = k in book
            fc = col if got else (150, 150, 165)
            cx, cy = box.centerx, box.y + 32
            s = 0.7 + 0.3 * size
            pygame.draw.ellipse(surf, fc, (cx - 24 * s, cy - 11 * s, 40 * s, 22 * s))
            pygame.draw.polygon(surf, fc, [(cx + 13 * s, cy), (cx + 26 * s, cy - 12 * s), (cx + 26 * s, cy + 12 * s)])
            if got:
                pygame.draw.circle(surf, (30, 30, 30), (int(cx - 14 * s), int(cy - 3)), 2)
            t = assets.text(name if got else "???", 15, (80, 60, 50), bold=True)
            surf.blit(t, t.get_rect(center=(cx, box.bottom - 24)))
            if got:
                t = assets.text(f"x{book[k]['count']}  best {book[k]['best']}cm", 13, (120, 100, 90))
                surf.blit(t, t.get_rect(center=(cx, box.bottom - 9)))
        k = keys[self.cursor]
        info = fish_data.FISH[k]
        if k in book:
            line = f"{info[0]}: {info[7]}  (+{info[2]} coins)"
        else:
            when = {"night": "Try fishing at night.", "winter": "Only in winter.",
                    "summer": "Only in summer."}.get(info[6], "Keep fishing at Sunny Pond!")
            line = "Not caught yet. " + when
        t = assets.text(line, 18, (90, 70, 60), bold=True)
        surf.blit(t, t.get_rect(center=(320, 432)))


_small_cache: dict = {}


def _small(k, img):
    s = _small_cache.get(k)
    if s is None:
        s = pygame.transform.smoothscale(img, (int(img.get_width() * 0.75), int(img.get_height() * 0.75)))
        _small_cache[k] = s
    return s
