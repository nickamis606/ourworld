"""MainScene: the pet at its current location.

Owns only presentation state (focus, effects, overlays). Every rule lives in
core.GameState; this scene turns input into GameState calls and turns the
returned result dicts into animation + feedback.
"""
import math

import pygame

from core import world
from core import story_data as SD
from core.game_state import CARE_ACTIONS, LOCATION_BONUS
from core.roster import roster_entry
from engine import assets
from scenes.base_scene import BaseScene
from sprites import backdrops
from sprites.action_animator import ActionAnimator
from sprites.fx import Effects, pet_pose, NEED_COLORS
from sprites.pet_sprite import PetSprite
from sprites import npc_sprite
from sprites import pet_extras, seasons
from core import pets as petsmod
from core import fish_data
from ui.dialogue_box import DialogueBox
from ui.journal import Journal
from ui.settings_menu import SettingsMenu
from ui.furnish import FurnishMode
from sprites import furniture as furniture_sprites
from engine.audio import track_for
from ui.action_bar import ActionBar, ActionItem
from ui.common import hint_bar, panel
from ui.icons import icon
from ui.map_overlay import MapOverlay
from ui.menu import Menu
from ui.stats_bar import StatsBar

CARE_LABELS = {"feed": "Feed", "play": "Play", "clean": "Clean", "rest": "Rest"}
CARE_COLORS = {"feed": (226, 128, 50), "play": (60, 160, 90), "clean": (60, 130, 200), "rest": (130, 100, 200)}
FEET = {"home": (320, 378), "backyard": (330, 352), "pond": (250, 356), "library": (330, 366), "spa": (250, 364),
        "willow_woods": (290, 376), "town_square": (300, 384), "lantern_hill": (250, 384)}
# where townsfolk stand (feet), and whether they face right
NPC_POS = {"town_square": (480, 384, False), "sweeties_candy_shop": (500, 372, False),
           "gens_garden": (500, 374, False), "arcade": (500, 380, False), "pond": (560, 336, False),
           "library": (470, 372, False), "spa": (100, 382, True), "willow_woods": (510, 360, False)}
DEFAULT_FEET = (320, 372)
MOOD_TEXT = {"happy": ("Happy", (60, 170, 80)), "okay": ("Okay", (200, 150, 30)), "sad": ("Sad", (210, 70, 70))}
TOAST_SECS = 2.6
PLACE_COLORS = {"swim": (40, 140, 200), "read": (140, 90, 170), "pamper": (210, 100, 160),
                "explore": (60, 130, 80), "light": (220, 160, 40), "snowman": (110, 160, 210),
                "egg_hunt": (210, 120, 170)}
PLACE_ANIM = {"swim": "clean", "read": "rest", "pamper": "clean", "explore": "play", "light": "play",
              "snowman": "play", "egg_hunt": "play"}


_shadow = []


def _npc_shadow():
    if not _shadow:
        sh = pygame.Surface((68, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 60), sh.get_rect())
        _shadow.append(sh)
    return _shadow[0]


def _fmt_deltas(d):
    names = {"hunger": "Food", "happiness": "Joy", "energy": "Energy", "cleanliness": "Clean"}
    return ", ".join(f"{'+' if v > 0 else ''}{v} {names[k]}" for k, v in d.items())


class MainScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.stats = StatsBar()
        self.bar = ActionBar()
        self.map = MapOverlay()
        self.pause = None
        self.fx = Effects()
        self.animator = ActionAnimator()
        self.anim_kind = None
        self.anim_t = 0.0
        self.anim_dur = 0.0
        self.toast = ""
        self.toast_t = 0.0
        self.toast_bad = False
        self.t = 0.0
        self.pet = None
        self._species = None
        self._bubble_t = 0.0
        self.dialog = None
        self.journal = Journal()
        self.settings_menu = None
        self.furnish = None
        self.pets_menu = None
        self._nap_sprites = {}
        self.hide_hud = False
        self._npc_flip = {}
        self._music_t = 0.0
        self._stage = None
        self._emote = None       # (kind, t)
        self._emote_tick = 0
        self._emote_wait = 6.0

    # ---------------------------------------------------------- lifecycle
    def on_enter(self, **kwargs):
        self._ensure_sprite()
        self.pet.set_feet(*FEET.get(self.state.pet.location, DEFAULT_FEET))
        self.map.hide()
        self.journal.hide()
        self.journal.gs = self.state
        self.pause = None
        self.dialog = None
        self.furnish = None
        self.pets_menu = None
        self.fx.clear()
        self.anim_kind = None
        self.animator.is_active = False
        msg = kwargs.get("message")
        ev = self.state.event_status()
        if ev and not ev["done"] and getattr(self.game, "_event_told", None) != ev["key"]:
            self.game._event_told = ev["key"]
            self.state.story.notices.append(f"The {ev['name']} is on! See your Journal (X).")
        if msg:
            self.say(msg)
        elif kwargs.get("arrived"):
            info = self.state.get_current_location_info()
            self.say(f"Welcome to {info['name']}!")
        self.refresh_items()
        self._update_music()
        self._maybe_story_dialogue()

    def on_exit(self):
        self.map.hide()
        self.pause = None

    def is_animating(self):
        return bool(self.anim_kind or self.fx.texts or self.fx.parts or self.toast_t > 0
                    or self.dialog or self.state.story.notices)

    @property
    def overlay_open(self):
        return bool(self.map.open or self.journal.open or self.dialog or self.pause or self.settings_menu
                    or self.furnish or self.pets_menu)

    def sfx(self, name):
        self.game.sfx(name)

    def _update_music(self):
        s = self.state
        self.game.audio.music(track_for(s.pet.location, s.time_of_day(), s.season(), s.story.finished))

    # -------------------------------------------------------------- story
    def open_dialog(self, lines):
        if not lines:
            return False
        self.dialog = DialogueBox(lines, self.state.pet.name, self._pet_portrait(), self._after_dialogue)
        self.sfx("talk")
        return True

    def _pet_portrait(self):
        if self.pet is None:
            return None
        base = self.pet.base
        h = 84
        return pygame.transform.smoothscale(base, (max(1, int(base.get_width() * h / base.get_height())), h))

    def _maybe_story_dialogue(self):
        if self.dialog:
            return True
        if self.open_dialog(self.state.next_dialogue()):
            return True
        if self.state.story.ending_pending:
            self.state.story.ending_pending = False
            self.state.save()
            self.game.switch("ending")
            return True
        return False

    def _after_dialogue(self):
        self.dialog = None
        self.refresh_items()
        if not self._maybe_story_dialogue():
            self.state.save()

    def talk(self, npc):
        res = self.state.talk(npc)
        if not res["success"]:
            self.say(res["msg"], bad=True)
            return
        self.open_dialog(res["lines"])

    # ------------------------------------------------------------ helpers
    def say(self, text, bad=False):
        self.toast, self.toast_t, self.toast_bad = text, TOAST_SECS, bad

    def refresh_items(self):
        s = self.state
        p = s.pet
        loc = p.location
        items = []
        for a in ("feed", "play", "clean", "rest"):
            ok, why = s.can_perform(a)
            deltas = dict(CARE_ACTIONS[a][2])
            desc = f"{CARE_LABELS[a]}: {_fmt_deltas(deltas)}"
            b = LOCATION_BONUS.get(loc)
            if b and b[0] == a:
                desc += f"  ({b[2]} {_fmt_deltas(b[1])})"
            if not ok:
                desc = why
            items.append(ActionItem(a, CARE_LABELS[a], a, desc, ok, color=CARE_COLORS[a]))
        if loc == "home":
            n = p.inventory.get("flowers", 0)
            items.append(ActionItem("decorate", "Decorate", "decorate",
                                    "Decorate with 5 flowers: joy decays slower at home for 30 min"
                                    if not p.home_decorated else
                                    f"Home is decorated ({int(p.decoration_left // 60)} min left)",
                                    n >= world.FLOWERS_TO_DECORATE, f"{n}/5", (200, 90, 150)))
            owned = sum(s.extras.furniture.values())
            placed = len(s.extras.layout)
            items.append(ActionItem("furnish", "Furnish", "furnish",
                                    f"Arrange your furniture ({owned} to place, {placed} placed)" if owned or placed
                                    else "No furniture yet - shops and quests give you some!",
                                    bool(owned or placed), str(owned) if owned else "", (170, 110, 70)))
        elif loc == "backyard":
            for seed, label, ic in (("flower_seeds", "Flower", "plant_flower"),
                                    ("sunflower_seeds", "Sunflwr", "plant_sunflower")):
                n = p.inventory.get(seed, 0)
                full = len(p.garden) >= world.GARDEN_SLOTS
                desc = ("Garden is full - harvest first" if full else
                        f"Plant {label.lower()} seeds ({n} left)" if n else "No seeds - buy some at Gen's Garden")
                items.append(ActionItem("plant:" + seed, label, ic, desc, n > 0 and not full, str(n), (90, 150, 70)))
            m = s.mature_plants()
            items.append(ActionItem("harvest", "Harvest", "harvest",
                                    f"Pick a grown plant for flowers + coins ({m} ready)" if m
                                    else "Nothing ready yet - plants grow while you play",
                                    m > 0, str(m) if m else "", (190, 130, 60)))
        elif loc in ("sweeties_candy_shop", "gens_garden"):
            for it in world.shop_items(loc):
                afford = p.coins >= it["price"]
                desc = f"{it['name']} - {it['price']} coins - {it['desc']}"
                if not afford:
                    desc = f"{it['name']} costs {it['price']} coins - win more at the Arcade"
                short = it.get("short") or it["name"].replace("Sunflower Seeds", "Sunflwr").replace(" Seeds", "").replace("Candy ", "")
                items.append(ActionItem("buy:" + it["key"], short, it["key"], desc, afford,
                                        str(it["price"]), (200, 70, 110) if it.get("eat") else (70, 140, 110)))
        if loc == "pond":
            ok, why = s.can_fish()
            n = len(s.extras.fish)
            items.append(ActionItem("fish", "Fish", "fish",
                                    f"Go fishing: 5 casts, coins for every catch ({n}/{len(fish_data.FISH)} in your Fish Book)"
                                    if ok else why, ok, f"{n}", (60, 130, 200)))
        for key in s.place_actions_here(loc):
            spec = world.PLACE_ACTIONS[key]
            ok, why = s.can_place_action(key)
            cost = f" - {spec['cost']} coins" if spec["cost"] else ""
            cd = f", then {spec['cooldown']}s break" if spec["cooldown"] else ""
            desc = f"{spec['label']}: {_fmt_deltas(spec['deltas'])}{cost}{cd}" if ok else why
            badge = str(spec["cost"]) if spec["cost"] else ""
            left = p.cooldowns.get(key, 0)
            if left > 0:
                badge = f"{int(left) + 1}s"
            items.append(ActionItem("place:" + key, spec["label"], spec["icon"], desc, ok, badge,
                                    PLACE_COLORS.get(key, (90, 120, 170))))
        if loc == "arcade":
            from minigames import GAME_INFO
            best = max([s.save_manager.get_high_score(k) for k in GAME_INFO] + [0])
            items.append(ActionItem("games", "Games", "games",
                                    f"Pick one of {len(GAME_INFO)} arcade games - win coins!"
                                    + (f" Top score: {best}" if best else ""), True, str(len(GAME_INFO)),
                                    (120, 70, 180)))
        for npc in s.story.npcs_at(loc):
            info = SD.NPCS[npc]
            mk = s.story.npc_marker(npc)
            desc = {"new": f"{info['name']} needs your help! (Y)", "ready": f"Tell {info['name']} the good news! (Y)"}.get(
                mk, f"Chat with {info['name']}, {info['title']} (Y)")
            items.append(ActionItem("talk:" + npc, "Talk", "talk", desc, True,
                                    {"new": "!", "ready": "*"}.get(mk, ""), (200, 120, 80)))
        items.append(ActionItem("map", "Map", "map", "Open the map (Select / M).  Journal: X", True, color=(80, 120, 190)))
        self.bar.set_items(items)

    # -------------------------------------------------------------- input
    def handle_action(self, a):
        if self.dialog:
            before = self.dialog.index
            self.dialog.handle_action(a)
            if self.dialog and self.dialog.index != before and not self.dialog.done:
                self.sfx("talk")
            return
        if self.settings_menu:
            self.settings_menu.handle_action(a)
            self.sfx("move" if a in ("UP", "DOWN", "LEFT", "RIGHT") else "select")
            if not self.settings_menu.open:
                self.settings_menu = None
                self.state.save()
            return
        if self.furnish:
            res = self.furnish.handle_action(a)
            if res is not None:
                self.sfx("place" if res.get("success") else "sad")
            else:
                self.sfx("move" if a in ("UP", "DOWN", "LEFT", "RIGHT", "L", "R") else "back")
            if not self.furnish.open:
                self.furnish = None
                self.refresh_items()
                self.state.trigger_auto_save()
            return
        if self.pets_menu:
            return self._pets_action(a)
        if self.journal.open:
            self.sfx("move" if a in ("UP", "DOWN", "LEFT", "RIGHT", "L", "R") else "back")
            return self.journal.handle_action(a, self.state.story)
        if self.pause:
            return self._pause_action(a)
        if self.map.open:
            return self._map_action(a)
        if a == "LEFT":
            self.bar.move(-1)
            self.sfx("move")
        elif a == "RIGHT":
            self.bar.move(1)
            self.sfx("move")
        elif a == "A":
            self.activate(self.bar.current.id if self.bar.current else None)
        elif a in ("SELECT", "UP"):
            self.map.show(self.state.pet.location)
        elif a == "START":
            self.open_pause()
        elif a == "X":
            self.journal.show()
        elif a == "Y":
            npcs = self.state.story.npcs_at(self.state.pet.location)
            if npcs:
                self.bar.focus_id("talk:" + npcs[0])
                self.activate("talk:" + npcs[0])
        elif a == "B":
            self.bar.focus_id("map")
        elif a == "L":
            self.bar.move(-1)
        elif a == "R":
            self.bar.move(1)
        elif a.startswith("HOT_"):
            act = a[4:].lower()
            self.bar.focus_id(act)
            self.activate(act)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.pause:
                i = self.pause.hit(e.pos, (320, 240))
                if i is not None:
                    self.pause.index = i
                    self._pause_action("A")
                return
            if self.map.open:
                key = self.map.hit(e.pos)
                if key:
                    self.map.cursor = world.LOCATIONS[key]["map"]
                    self._map_action("A")
                else:
                    self.map.hide()
                return
            i = self.bar.hit(e.pos)
            if i is not None:
                self.bar.focus = i
                self.activate(self.bar.current.id)

    def _map_action(self, a):
        moves = {"LEFT": (-1, 0), "RIGHT": (1, 0), "UP": (0, -1), "DOWN": (0, 1)}
        if a in moves:
            self.map.move(*moves[a])
            self.sfx("move")
        elif a in ("B", "SELECT", "START"):
            self.map.hide()
        elif a == "A":
            dest = self.map.selected
            self.map.hide()
            if dest and not self.state.is_unlocked(dest):
                self.say("That place is still asleep. Keep helping the townsfolk!", bad=True)
            elif dest and dest != self.state.pet.location:
                self.game.switch("travel", dest=dest)
            elif dest:
                self.say("You're already here!")

    def open_pause(self):
        opts = [("resume", "Resume"), ("journal", "Journal"), ("settings", "Settings"),
                ("photo", "Take a photo"), ("save", "Save now")]
        if self.state.story.finished:
            opts.append(("pets", "Pets..."))
        opts.append(("newpet", "New pet..."))
        opts.append(("quit", "Quit game"))
        self.pause = Menu("Paused", opts)
        self.sfx("select")

    def _pause_action(self, a):
        if a == "UP":
            self.pause.move(-1)
        elif a == "DOWN":
            self.pause.move(1)
        elif a in ("B", "START"):
            self.pause = None
        elif a == "A":
            sel = self.pause.selected
            self.pause = None
            if sel == "journal":
                self.journal.show()
            elif sel == "settings":
                self.settings_menu = SettingsMenu(self.state.settings, self.game.apply_settings)
            elif sel == "photo":
                path = self.game.take_photo()
                self.say("Photo saved to photos/!" if path else "Couldn't save the photo", bad=not path)
            elif sel == "pets":
                self.open_pets()
            elif sel == "save":
                self.say("Saved!" if self.state.save() else "Save failed!", bad=False)
            elif sel == "newpet":
                self.game.switch("title", mode="select")
            elif sel == "quit":
                self.game.quit()

    def open_pets(self):
        opts = []
        for idx, name, _sp, active in self.state.all_pets():
            opts.append((f"pet:{idx}", f"{name} (with you)" if active else f"{name} (napping)"))
        ok, _why = self.state.can_adopt_companion()
        if ok:
            opts.append(("adopt", "Adopt a new friend"))
        opts.append(("close", "Back"))
        self.pets_menu = Menu("Your pets", opts, width=340)

    def _pets_action(self, a):
        m = self.pets_menu
        if a in ("UP", "DOWN"):
            m.move(-1 if a == "UP" else 1)
            self.sfx("move")
        elif a in ("B", "START"):
            self.pets_menu = None
        elif a == "A":
            sel = m.selected
            self.pets_menu = None
            self.sfx("select")
            if sel == "adopt":
                self.game.switch("title", mode="companion")
            elif sel.startswith("pet:"):
                idx = int(sel[4:])
                if idx >= 0:
                    res = self.state.switch_pet(idx)
                    self._ensure_sprite()
                    self.pet.set_feet(*FEET.get(self.state.pet.location, DEFAULT_FEET))
                    self.say(res["msg"])
                    self.refresh_items()
                    self._update_music()

    def _draw_napping(self, surf):
        spots = [(92, 384), (548, 384), (196, 392)]
        for (name, sp, stage), (x, y) in zip(self.state.napping_pets(), spots):
            key = (sp, stage)
            img = self._nap_sprites.get(key)
            if img is None:
                h = int(70 * petsmod.stage_scale(stage))
                base = PetSprite(roster_entry(sp), height=h).base
                img = self._nap_sprites[key] = pygame.transform.rotate(base, 8)
            surf.blit(img, img.get_rect(midbottom=(x, y)))
            if int(self.t * 1.5 + x) % 3 == 0:
                z = assets.text("z", 18, (120, 120, 200), bold=True)
                surf.blit(z, (x + img.get_width() // 2 - 8, y - img.get_height() - 6))

    # ------------------------------------------------------------ actions
    def activate(self, item_id):
        if not item_id:
            return
        if self.anim_kind and item_id != "map":
            return  # one thing at a time; keeps feedback readable
        item = next((i for i in self.bar.items if i.id == item_id), None)
        if item_id == "map":
            self.map.show(self.state.pet.location)
            return
        self.bar.press(item_id)
        s = self.state
        if item_id in CARE_ACTIONS:
            res = s.perform_care_action(item_id)
            self._feedback(res, item_id)
        elif item_id.startswith("buy:"):
            res = s.buy_item(s.pet.location, item_id[4:])
            self._feedback(res, "feed" if res.get("eat") else "buy")
        elif item_id.startswith("plant:"):
            res = s.plant_seed(item_id[6:])
            self._feedback(res, "plant")
        elif item_id == "harvest":
            res = s.harvest_plant()
            self._feedback(res, "harvest")
            if res.get("success"):
                self.fx.float_text(f"+{res['coins']} coins", self.pet.feet.x + 60, self.pet.feet.y - 150,
                                   NEED_COLORS["coins"])
        elif item_id.startswith("talk:"):
            self.talk(item_id[5:])
        elif item_id.startswith("place:"):
            key = item_id[6:]
            res = s.perform_place_action(key)
            self._feedback(res, PLACE_ANIM.get(key, "play"))
            if res.get("success") and key == "light":
                self.fx.burst(self.pet.feet.x + 200, 200, (255, 210, 110), "sparkle", 30)
        elif item_id == "decorate":
            res = s.decorate_home()
            self._feedback(res, "decorate")
        elif item_id == "furnish":
            self.furnish = FurnishMode(self.state)
            self.sfx("select")
            return
        elif item_id == "fish":
            ok, why = s.can_fish()
            if not ok:
                self.say(why, bad=True)
                return
            self.game.switch("arcade", game="fishing")
            return
        elif item_id == "games" or item_id.startswith("game:"):
            if s.pet.needs.energy < 8:
                self.say(f"{s.pet.name} is too tired for games. Rest first!", bad=True)
                self._start_anim("sad", 0.6)
                return
            self.game.switch("arcade", game=item_id[5:] if item_id.startswith("game:") else None)
            return
        elif item and not item.enabled:
            self.say(item.desc, bad=True)
        self.refresh_items()
        if not self.dialog:
            self._maybe_story_dialogue()

    def _feedback(self, res, kind):
        hx, hy = self.pet.feet.x, self.pet.feet.y - self.pet.height - 10
        if not res.get("success"):
            self.say(res.get("msg", "Can't do that"), bad=True)
            self._start_anim("sad", 0.6)
            self.sfx("sad")
            return
        self.say(res.get("msg", ""))
        self.sfx({"feed": "eat", "play": "play", "clean": "splash", "rest": "rest", "plant": "place",
                  "harvest": "coin", "buy": "coin", "decorate": "sparkle"}.get(kind, "select"))
        self._start_anim(kind, None)
        self.fx.deltas(res.get("deltas", {}), hx, hy)
        burst = {"feed": ((255, 120, 160), "heart"), "play": ((255, 200, 80), "sparkle"),
                 "clean": ((170, 220, 255), "dot"), "rest": ((190, 170, 255), "sparkle"),
                 "plant": ((120, 200, 90), "dot"), "harvest": ((255, 140, 180), "heart"),
                 "decorate": ((255, 140, 180), "heart"), "buy": ((255, 220, 90), "sparkle")}
        if kind in burst:
            col, k = burst[kind]
            self.fx.burst(hx, hy + 40, col, k, 12)

    def _start_anim(self, kind, dur):
        prop = kind if kind in ("feed", "play", "clean", "rest", "plant") else None
        if prop:
            self.animator.start(prop)
            dur = self.animator.duration + self.animator.linger + 0.2
        self.anim_kind = kind
        self.anim_t = 0.0
        self.anim_dur = dur or 0.8

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        self.state.tick(dt)
        self.stats.update(dt, self.state.pet.needs)
        self.bar.update(dt)
        self.map.update(dt)
        self.journal.update(dt)
        if self.settings_menu:
            self.settings_menu.update(dt, self.game.input.held)
        if self.furnish:
            self.furnish.update(dt)
        if self.dialog:
            self.dialog.update(dt)
        elif self.state.reminder_due() and not self.overlay_open:
            self.state.ack_reminder()
            mins = int(self.state.session_secs // 60)
            self.open_dialog([("", f"You've been playing for {mins} minutes. Great job caring for {self.state.pet.name}!"),
                              ("pet", f"{self.state.pet.name} stretches. Maybe time for a little break?")])
        elif self.toast_t <= 0 and not self.anim_kind:
            note = self.state.story.pop_notice()
            if note:
                self.say(note)
                self.sfx("levelup" if note.startswith("Bond level") else
                         "quest" if "Quest complete" in note or "New quest" in note else
                         "sparkle" if ("sticker" in note or "Spark" in note) else "coin")
                self.refresh_items()
        self._music_t += dt
        if self._music_t > 2.0:
            self._music_t = 0.0
            self._update_music()
        self._ensure_sprite()
        self._update_emote(dt)
        self.pet.update(dt)
        self.animator.update(dt)
        self.fx.update(dt)
        if self.toast_t > 0:
            self.toast_t -= dt
        if self.anim_kind:
            self.anim_t += dt
            if self.anim_t >= self.anim_dur:
                self.anim_kind = None
        # refresh labels ~4x/second (needs and plants change continuously)
        self._bubble_t += dt
        if int(self.t * 4) != int((self.t - dt) * 4):
            self.refresh_items()

    def _ensure_sprite(self):
        sp = self.state.pet.species_id
        stage = self.state.stage
        if self.pet is None or self._species != sp or self._stage != stage:
            old_feet = tuple(self.pet.feet) if self.pet is not None else None
            self.pet = PetSprite(roster_entry(sp), height=int(128 * petsmod.stage_scale(stage)))
            self._species, self._stage = sp, stage
            if old_feet:
                self.pet.set_feet(*old_feet)

    def _update_emote(self, dt):
        if self._emote:
            kind, t = self._emote
            t += dt
            self._emote = (kind, t) if t < 1.8 else None
            return
        self._emote_wait -= dt
        if self._emote_wait <= 0 and not self.anim_kind and not self.overlay_open:
            self._emote_tick += 1
            kind = self.state.idle_reaction(self._emote_tick)
            self._emote = (kind, 0.0)
            self._emote_wait = 5.0 if self.state.pet.mopey else 8.0
            if kind == "bounce":
                self._start_anim("play", 0.5)

    # --------------------------------------------------------------- draw
    def draw(self, surf):
        s = self.state
        p = s.pet
        loc = p.location
        season = s.season()
        surf.blit(backdrops.get(loc, s.time_of_day(), self._variant(loc), season,
                                s.current_event() or "", p.mopey, s.backdrop_extras(loc)), (0, 0))
        backdrops.draw_ambient(surf, loc, self.t)
        seasons.draw_particles(surf, loc, season, self.t)
        self._draw_npcs(surf, loc)
        if loc == "backyard":
            self._draw_garden(surf)
        if loc == "home" and p.home_decorated:
            self._draw_decor(surf)
        if loc == "home":
            furniture_sprites.draw_layout(surf, s.extras.layout)
            self._draw_napping(surf)
        pose = pet_pose(self.anim_kind, min(1.0, self.anim_t / self.anim_dur)) if self.anim_kind else None
        if pose is None and p.mopey:
            pose = {"dy": 3.0, "sy": 0.93, "sx": 1.05, "angle": 3 * math.sin(self.t * 0.8)}
        self.pet.draw(surf, pose)
        pet_extras.draw_accessory(surf, self.pet.rect, self._stage, self.t)
        if self._emote and not self.hide_hud:
            kind, et = self._emote
            r = self.pet.rect
            pet_extras.draw_emote(surf, r.left + 4, r.top - 6, kind, et / 1.8)
        if self.animator.is_active:
            self.animator.draw(surf, int(self.pet.feet.x), int(self.pet.feet.y - self.pet.height * 0.55))
        if self.hide_hud:
            return
        if not self.anim_kind:
            self._draw_want_bubble(surf)
        self.fx.draw(surf)
        self.stats.draw(surf, p.needs, p.coins)
        self._draw_place_tag(surf)
        self._draw_tracker(surf)
        if self.dialog:
            self.dialog.draw(surf)
            return
        if self.furnish:
            self.furnish.draw(surf)
            return
        self._draw_message(surf)
        self.bar.draw(surf, busy=bool(self.anim_kind))
        if self.map.open:
            labels = {}
            for key in world.LOCATIONS:
                if key == "backyard":
                    labels[key] = f"{s.mature_plants()}/{len(p.garden)} plants ready"
                elif key == "arcade":
                    labels[key] = "Win coins"
                elif key == "home":
                    labels[key] = "Rest bonus"
                elif key == "park":
                    labels[key] = "Play bonus"
                elif world.shop_items(key):
                    labels[key] = "Shop"
                elif key == "town_square":
                    labels[key] = "Mayor Maple"
                elif key == "pond":
                    labels[key] = "Fishing"
                for act in s.place_actions_here(key):
                    spec = world.PLACE_ACTIONS[act]
                    labels[key] = spec["label"] + (f" ({spec['cost']}c)" if spec["cost"] else "")
            locked = {k for k in world.LOCATIONS if not s.is_unlocked(k)}
            markers = {}
            for npc, info in SD.NPCS.items():
                mk = s.story.npc_marker(npc)
                if mk and markers.get(info["location"]) != "ready":
                    markers[info["location"]] = mk
            self.map.draw(surf, loc, labels, locked, markers)
        elif self.settings_menu:
            self.settings_menu.draw(surf)
        elif self.pets_menu:
            self.pets_menu.draw(surf)
            hint_bar(surf, [("D-pad", "Choose"), ("A", "OK"), ("B", "Back")])
        elif self.journal.open:
            self.journal.draw(surf, s)
        elif self.pause:
            self.pause.draw(surf)
            hint_bar(surf, [("D-pad", "Choose"), ("A", "OK"), ("B", "Back")])

    def _variant(self, loc):
        st = self.state.story
        if loc == "town_square":
            return "v2" if st.finished else ("v1" if len(st.sparks) >= 2 else "v0")
        if loc == "lantern_hill":
            return "v1" if st.finished else ""
        return ""

    def _draw_npcs(self, surf, loc):
        for npc in self.state.story.npcs_at(loc):
            x, y, flip = NPC_POS.get(loc, (500, 372, False))
            img = npc_sprite.surface(npc)
            if flip:
                img = self._npc_flip.get(npc)
                if img is None:
                    img = self._npc_flip[npc] = pygame.transform.flip(npc_sprite.surface(npc), True, False)
            bob = int(2 * math.sin(self.t * 2.2 + len(npc)))
            surf.blit(_npc_shadow(), (x - 34, y - 8))
            surf.blit(img, img.get_rect(midbottom=(x, y + bob)))
            mk = self.state.story.npc_marker(npc)
            if mk:
                by = y - img.get_height() - 18 + int(4 * math.sin(self.t * 4))
                col = (240, 150, 40) if mk == "new" else (250, 200, 50)
                pygame.draw.circle(surf, (60, 40, 30), (x, by + 2), 15)
                pygame.draw.circle(surf, col, (x, by), 15)
                m = assets.text("!" if mk == "new" else "*", 26, (255, 255, 255), bold=True)
                surf.blit(m, m.get_rect(center=(x, by + 1)))

    def _draw_tracker(self, surf):
        text = self.state.story.objective(self.state.pet.name)
        if not text:
            return
        t = assets.text(text, 17, (255, 250, 220), bold=True)
        if t.get_width() > 330:
            t = assets.text(text, 15, (255, 250, 220), bold=True)
        w = t.get_width() + 40
        x = 632 - w
        surf.blit(panel((w, 28), (90, 50, 30, 205), 13, None), (x, 53))
        surf.blit(icon("spark", 18), (x + 8, 58))
        surf.blit(t, (x + 30, 58))

    def _draw_place_tag(self, surf):
        info = self.state.get_current_location_info()
        name = assets.text(info["name"], 24, (255, 255, 255), bold=True)
        mood, col = MOOD_TEXT[self.state.mood()]
        m = assets.text(mood, 22, col, bold=True)
        w = name.get_width() + m.get_width() + 46
        surf.blit(panel((w, 30), (40, 34, 56, 190), 14, None), (8, 52))
        surf.blit(name, (20, 58))
        pygame.draw.circle(surf, col, (28 + name.get_width(), 67), 5)
        surf.blit(m, (36 + name.get_width(), 59))

    def _draw_message(self, surf):
        if self.toast_t > 0:
            col = (255, 200, 190) if self.toast_bad else (255, 255, 230)
            text = self.toast
        else:
            col, text = (215, 210, 230), (self.bar.current.desc if self.bar.current else "")
        if not text:
            return
        t = assets.text(text, 21, col, bold=self.toast_t > 0)
        if t.get_width() > 620:
            t = assets.text(text, 17, col, bold=self.toast_t > 0)
        w = t.get_width() + 24
        bg = (120, 40, 50, 220) if (self.toast_t > 0 and self.toast_bad) else (40, 34, 56, 210)
        surf.blit(panel((w, 26), bg, 12, None), ((640 - w) // 2, 362))
        surf.blit(t, t.get_rect(center=(320, 375)))

    def _draw_want_bubble(self, surf):
        want = self.state.wants()
        if not want:
            return
        hx, hy = self.pet.feet.x + 58, self.pet.feet.y - self.pet.height - 8
        bob = int(3 * math.sin(self.t * 3))
        pygame.draw.circle(surf, (255, 255, 255), (int(hx - 26), int(hy + 30 + bob)), 4)
        pygame.draw.circle(surf, (255, 255, 255), (int(hx - 16), int(hy + 20 + bob)), 6)
        pygame.draw.ellipse(surf, (255, 255, 255), (hx - 22, hy - 26 + bob, 48, 40))
        pygame.draw.ellipse(surf, (200, 190, 200), (hx - 22, hy - 26 + bob, 48, 40), 2)
        surf.blit(icon(want, 26), (hx - 11, hy - 19 + bob))

    def _draw_garden(self, surf):
        bed_y = 370
        for i in range(world.GARDEN_SLOTS):
            x = 100 + i * 62
            pygame.draw.ellipse(surf, (70, 44, 26), (x - 14, bed_y - 4, 28, 10))
        for i, plant in enumerate(self.state.pet.garden[:world.GARDEN_SLOTS]):
            x = 100 + i * 62
            stage = plant["stage"]
            sway = math.sin(self.t * 2 + i) * (2 if stage >= 2 else 0)
            if stage == 0:
                pygame.draw.circle(surf, (120, 80, 40), (x, bed_y), 5)
                pygame.draw.line(surf, (90, 170, 80), (x, bed_y - 2), (x + 3, bed_y - 8), 2)
            else:
                h = 12 + stage * 10
                top = (int(x + sway), bed_y - h)
                pygame.draw.line(surf, (50, 140, 60), (x, bed_y), top, 3)
                pygame.draw.ellipse(surf, (80, 180, 80), (x - 12, bed_y - h // 2 - 4, 12, 7))
                pygame.draw.ellipse(surf, (80, 180, 80), (x, bed_y - h // 2 - 8, 12, 7))
                if stage == 2:
                    pygame.draw.circle(surf, (110, 190, 100), top, 6)
                elif stage >= 3:
                    big = 1.0 + 0.08 * math.sin(self.t * 4 + i)
                    if plant["type"] == "sunflower":
                        for k in range(8):
                            ang = k * math.tau / 8
                            pygame.draw.circle(surf, (250, 200, 40), (int(top[0] + math.cos(ang) * 9 * big), int(top[1] + math.sin(ang) * 9 * big)), 5)
                        pygame.draw.circle(surf, (130, 80, 30), top, 6)
                    else:
                        for k in range(5):
                            ang = k * math.tau / 5
                            pygame.draw.circle(surf, (250, 110, 160), (int(top[0] + math.cos(ang) * 6 * big), int(top[1] + math.sin(ang) * 6 * big)), 5)
                        pygame.draw.circle(surf, (255, 220, 90), top, 4)
                    if int(self.t * 2 + i) % 3 == 0:
                        pygame.draw.line(surf, (255, 255, 220), (top[0] + 12, top[1] - 10), (top[0] + 12, top[1] - 4), 2)
                        pygame.draw.line(surf, (255, 255, 220), (top[0] + 9, top[1] - 7), (top[0] + 15, top[1] - 7), 2)

    def _draw_decor(self, surf):
        pot = assets.image("assets/backgrounds/home/layers/pot.png")
        if pot is not None:
            surf.blit(pot, (70, 262))
        # bunting across the top of the room
        for i in range(8):
            x = 236 + i * 46
            y = 50 + int(10 * math.sin(i / 7 * math.pi))
            col = [(250, 120, 170), (250, 210, 70), (140, 200, 250)][i % 3]
            pygame.draw.polygon(surf, col, [(x, y), (x + 30, y), (x + 15, y + 22)])
