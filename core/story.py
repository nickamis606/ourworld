"""StoryState: chapters, quests, dialogue queue, stickers, sparks, daily wishes.

Pure Python, no pygame. GameState owns one StoryState and feeds it events
("care:feed" at "park", "game:snake" with a score ...). Scenes only read it
and call GameState.talk(npc) / GameState.next_dialogue().
"""
from __future__ import annotations

import datetime
import random

from . import story_data as D

STATUS = ("locked", "available", "active", "ready", "done")


def _list(x):
    return x if isinstance(x, list) else []


def _dict(x):
    return x if isinstance(x, dict) else {}


def _match(step: dict, kind: str, key: str, loc: str, score: int) -> bool:
    ev = step.get("event")
    if not ev:
        return False
    k, _, want = ev.partition(":")
    if k != kind or (want not in ("*", key)):
        return False
    if step.get("at") and step["at"] != loc:
        return False
    if score < step.get("min_score", 0):
        return False
    return True


def bond_level(xp: int) -> int:
    lvl = 0
    for i, need in enumerate(D.BOND_LEVELS):
        if xp >= need:
            lvl = i
    return lvl + 1


def bond_progress(xp: int) -> tuple:
    """(level, xp into level, xp needed for next level or 0 at max)."""
    lvl = bond_level(xp)
    base = D.BOND_LEVELS[lvl - 1]
    nxt = D.BOND_LEVELS[lvl] if lvl < len(D.BOND_LEVELS) else None
    return lvl, xp - base, (nxt - base) if nxt else 0


class StoryState:
    def __init__(self):
        self.chapter = 1
        self.quests: dict = {}          # id -> {"status": str, "progress": [int...]}
        self.unlocked: set = set(D.START_UNLOCKED)
        self.stickers: list = []        # ordered by discovery
        self.sparks: list = []
        self.met: list = []             # npc ids talked to
        self.talks: dict = {}           # npc -> idle rotation counter
        self.dialogue: list = []        # queued dialogue keys / line lists
        self.notices: list = []         # short toasts for the scene
        self.finished = False           # lantern lit
        self.ending_pending = False     # scene should play the ending
        self.daily: dict = {}           # {"date": "YYYY-MM-DD", "tasks": [...], "bonus": bool}
        self.free_roam = False          # migrated saves: every old place stays open
        for qid in D.QUEST_ORDER:
            self.quests[qid] = {"status": "locked", "progress": [0] * len(D.QUESTS[qid]["steps"])}
        self._refresh_availability()

    # ------------------------------------------------------------ factory
    @classmethod
    def new_game(cls) -> "StoryState":
        s = cls()
        s.dialogue.append("intro")
        return s

    @classmethod
    def for_existing_save(cls, location: str = "home") -> "StoryState":
        """Older saves had every place open. Keep it that way (no one gets
        locked out of their garden), but still start the story at chapter 1."""
        from .world import LOCATIONS
        s = cls()
        s.free_roam = True
        old = ("home", "backyard", "park", "sweeties_candy_shop", "gens_garden", "arcade",
               "pond", "library", "spa")
        s.unlocked |= {k for k in old if k in LOCATIONS}
        s.unlocked.add(location)
        s.dialogue.append("intro")
        return s

    # -------------------------------------------------------- persistence
    def to_dict(self) -> dict:
        return {"chapter": self.chapter,
                "quests": {k: {"status": v["status"], "progress": list(v["progress"])}
                           for k, v in self.quests.items()},
                "unlocked": sorted(self.unlocked), "stickers": list(self.stickers),
                "sparks": list(self.sparks), "met": list(self.met), "talks": dict(self.talks),
                "dialogue": [d for d in self.dialogue if isinstance(d, str)],
                "finished": self.finished, "ending_pending": self.ending_pending,
                "daily": self.daily, "free_roam": self.free_roam}

    @classmethod
    def from_dict(cls, d: dict) -> "StoryState":
        from .world import LOCATIONS
        s = cls()
        if not isinstance(d, dict):
            return s
        try:
            s.chapter = max(1, min(D.FINAL_CHAPTER + 1, int(d.get("chapter", 1))))
        except (TypeError, ValueError):
            s.chapter = 1
        for qid, q in _dict(d.get("quests")).items():
            if qid in s.quests and isinstance(q, dict) and q.get("status") in STATUS:
                n = len(D.QUESTS[qid]["steps"])
                prog = [int(x) if isinstance(x, (int, float)) else 0 for x in _list(q.get("progress"))]
                s.quests[qid] = {"status": q["status"], "progress": (prog + [0] * n)[:n]}
        s.unlocked = set(D.START_UNLOCKED) | {k for k in _list(d.get("unlocked")) if k in LOCATIONS}
        s.stickers = [k for k in _list(d.get("stickers")) if k in D.STICKERS]
        s.sparks = [k for k in _list(d.get("sparks")) if k in D.SPARKS]
        s.met = [k for k in _list(d.get("met")) if k in D.NPCS]
        s.talks = {k: int(v) for k, v in _dict(d.get("talks")).items() if isinstance(v, (int, float))}
        s.dialogue = [k for k in _list(d.get("dialogue")) if isinstance(k, str) and k in D.DIALOGUE]
        s.finished = bool(d.get("finished"))
        s.ending_pending = bool(d.get("ending_pending"))
        daily = _dict(d.get("daily"))
        tasks = [t for t in _list(daily.get("tasks")) if isinstance(t, dict)
                 and {"id", "text", "count", "progress", "done"} <= set(t)]
        s.daily = {"date": str(daily.get("date", "")), "bonus": bool(daily.get("bonus")),
                   "tasks": tasks} if tasks else {}
        s.free_roam = bool(d.get("free_roam"))
        s._refresh_availability()
        return s

    # --------------------------------------------------------------- query
    def status(self, qid: str) -> str:
        return self.quests[qid]["status"]

    def is_unlocked(self, loc: str) -> bool:
        return loc in self.unlocked

    def chapter_info(self) -> dict:
        idx = min(self.chapter, D.FINAL_CHAPTER) - 1
        return D.CHAPTERS[idx]

    def quests_for(self, npc: str, statuses=("available", "active", "ready")) -> list:
        return [q for q in D.QUEST_ORDER
                if D.QUESTS[q]["giver"] == npc and self.status(q) in statuses]

    def npc_marker(self, npc: str) -> str:
        """'ready' (turn in), 'new' (quest to offer) or ''."""
        if self.quests_for(npc, ("ready",)):
            return "ready"
        if self.quests_for(npc, ("available",)):
            return "new"
        return ""

    def npcs_at(self, loc: str) -> list:
        return [k for k, v in D.NPCS.items() if v["location"] == loc]

    def visible_quests(self) -> list:
        return [q for q in D.QUEST_ORDER if self.status(q) in ("available", "active", "ready", "done")]

    def objective(self, pet_name: str = "your pet") -> str:
        """One line telling the player what to do next (HUD tracker)."""
        for q in D.QUEST_ORDER:
            if self.status(q) == "ready" and not D.QUESTS[q].get("side"):
                npc = D.NPCS[D.QUESTS[q]["giver"]]
                return f"Talk to {npc['name']}"
        for q in D.QUEST_ORDER:
            if self.status(q) == "active" and not D.QUESTS[q].get("side"):
                for i, st in enumerate(D.QUESTS[q]["steps"]):
                    if self.quests[q]["progress"][i] < st["count"]:
                        txt = st["text"].format(pet=pet_name)
                        return f"{txt} ({self.quests[q]['progress'][i]}/{st['count']})" if st["count"] > 1 else txt
        for q in D.QUEST_ORDER:
            if self.status(q) == "available" and not D.QUESTS[q].get("side"):
                npc = D.NPCS[D.QUESTS[q]["giver"]]
                from .world import LOCATIONS
                where = LOCATIONS[npc["location"]].get("short", LOCATIONS[npc["location"]]["name"])
                return f"Meet {npc['name']} ({where})"
        if self.finished:
            left = [t for t in self.daily.get("tasks", []) if not t.get("done")]
            if left:
                return "Wish: " + left[0]["text"].format(pet=pet_name)
            return "All wishes granted today!"
        return ""

    # ---------------------------------------------------------------- flow
    def _refresh_availability(self) -> None:
        for q in D.QUEST_ORDER:
            spec = D.QUESTS[q]
            st = self.quests[q]
            if st["status"] != "locked":
                continue
            if spec["chapter"] > self.chapter:
                continue
            if any(self.status(a) != "done" for a in spec.get("after", [])):
                continue
            st["status"] = "active" if spec.get("auto") else "available"

    def _step_done(self, q: str, i: int) -> bool:
        return self.quests[q]["progress"][i] >= D.QUESTS[q]["steps"][i]["count"]

    def _check_ready(self, q: str, gs) -> list:
        """Update cond steps; mark ready. Returns quest ids that auto-turned-in."""
        spec, st = D.QUESTS[q], self.quests[q]
        if st["status"] != "active":
            return []
        for i, step in enumerate(spec["steps"]):
            c = step.get("cond")
            if c:
                val = {"bond": bond_level(gs.pet.bond_xp), "stickers": len(self.stickers),
                       "sparks": len(self.sparks)}[c]
                st["progress"][i] = min(step["count"], val)
        if all(self._step_done(q, i) for i in range(len(spec["steps"]))):
            st["status"] = "ready"
            if spec.get("auto_turn_in"):
                self.turn_in(q, gs)
                return [q]
            giver = D.NPCS[spec["giver"]]["name"]
            self.notices.append(f"Quest complete! Talk to {giver}.")
        return []

    def on_event(self, kind: str, key: str, gs, score: int = 0) -> None:
        loc = gs.pet.location
        for q in D.QUEST_ORDER:
            st = self.quests[q]
            if st["status"] != "active":
                continue
            for i, step in enumerate(D.QUESTS[q]["steps"]):
                if self._step_done(q, i) or not _match(step, kind, key, loc, score):
                    continue
                st["progress"][i] += 1
                if self._step_done(q, i):
                    self.notices.append("Done: " + step["text"].format(pet=gs.pet.name))
            self._check_ready(q, gs)
        self._daily_event(kind, key, loc, score, gs)

    def refresh(self, gs) -> None:
        """Re-check condition steps (bond, stickers) and the daily list."""
        for q in D.QUEST_ORDER:
            self._check_ready(q, gs)
        self.ensure_daily(gs)

    def accept(self, q: str, gs) -> None:
        st = self.quests[q]
        if st["status"] != "available":
            return
        st["status"] = "active"
        gift = D.QUESTS[q].get("gift") or {}
        for k, v in gift.items():
            if k == "coins":
                gs.earn_coins(v)
            else:
                gs.pet.inventory[k] = gs.pet.inventory.get(k, 0) + v
        self.notices.append("New quest: " + D.QUESTS[q]["title"])
        self._check_ready(q, gs)

    def turn_in(self, q: str, gs) -> dict:
        st = self.quests[q]
        if st["status"] != "ready":
            return {}
        st["status"] = "done"
        reward = dict(D.QUESTS[q].get("reward") or {})
        self.grant(reward, gs)
        if q == "light_lantern":
            self.finished = True
            self.ending_pending = True
            self.dialogue.append("ending")
            self.chapter = D.FINAL_CHAPTER + 1
            self.unlocked.add("lantern_hill")
        self._advance_chapter(gs)
        self._refresh_availability()
        return reward

    def grant(self, reward: dict, gs) -> None:
        if reward.get("coins"):
            gs.earn_coins(reward["coins"])
        for k, v in (reward.get("items") or {}).items():
            gs.pet.inventory[k] = gs.pet.inventory.get(k, 0) + v
        if reward.get("bond"):
            gs.add_bond(reward["bond"])
        s = reward.get("sticker")
        if s and s not in self.stickers:
            self.stickers.append(s)
            self.notices.append(f"New sticker: {D.STICKERS[s][0]}!")
        sp = reward.get("spark")
        if sp and sp not in self.sparks:
            self.sparks.append(sp)
            self.notices.append(f"You got the {D.SPARKS[sp][0]}! ({len(self.sparks)}/{D.SPARKS_NEEDED})")
        for loc in reward.get("unlock") or []:
            self.unlocked.add(loc)
        f = reward.get("furniture")
        if f and hasattr(gs, "add_furniture"):
            gs.add_furniture(f)

    def _advance_chapter(self, gs) -> None:
        while self.chapter <= D.FINAL_CHAPTER:
            main = [q for q in D.QUEST_ORDER
                    if D.QUESTS[q]["chapter"] == self.chapter and not D.QUESTS[q].get("side")]
            if not main or any(self.status(q) != "done" for q in main):
                return
            ch = D.CHAPTERS[self.chapter - 1]
            for loc in ch["unlock"]:
                self.unlocked.add(loc)
            if ch.get("outro"):
                self.dialogue.append(ch["outro"])
            self.chapter += 1
            self._refresh_availability()
            self.ensure_daily(gs)

    # ------------------------------------------------------------ dialogue
    def talk(self, npc: str, gs) -> list:
        """Talk to a townsperson: turn in ready quests, offer new ones.
        Returns the lines to show [(speaker, text), ...] with {pet} filled."""
        lines = []
        if npc not in self.met:
            self.met.append(npc)
        for q in self.quests_for(npc, ("ready",)):
            lines += D.DIALOGUE.get(q + "_done", [(npc, "Thank you so much!")])
            self.turn_in(q, gs)
        for q in self.quests_for(npc, ("available",)):
            lines += D.DIALOGUE.get(q + "_offer", [])
            self.accept(q, gs)
        if not lines:
            busy = self.quests_for(npc, ("active",))
            if busy:
                lines = D.DIALOGUE.get(busy[0] + "_busy", [])
            else:
                pool = D.DIALOGUE.get(npc + "_idle") or [[(npc, "Hello again!")]]
                n = self.talks.get(npc, 0)
                self.talks[npc] = n + 1
                lines = pool[n % len(pool)]
                if self.finished and n % 3 == 2:
                    lines = [(npc, t.format(name=D.NPCS[npc]["name"], pet="{pet}"))
                             for _, t in D.DIALOGUE["post_idle"][0]]
        return self.fill(lines, gs.pet.name)

    @staticmethod
    def fill(lines, pet_name: str) -> list:
        return [(sp, txt.replace("{pet}", pet_name)) for sp, txt in lines]

    def pop_dialogue(self, pet_name: str) -> list:
        """Next queued story dialogue (intro, chapter outros, ending) or []."""
        while self.dialogue:
            key = self.dialogue.pop(0)
            lines = D.DIALOGUE.get(key)
            if lines:
                return self.fill(lines, pet_name)
        return []

    def pop_notice(self) -> str:
        return self.notices.pop(0) if self.notices else ""

    # -------------------------------------------------------- daily wishes
    def daily_active(self) -> bool:
        return self.chapter >= 3 or self.finished

    def ensure_daily(self, gs) -> None:
        if not self.daily_active():
            return
        today = gs.today()
        if self.daily.get("date") == today:
            return
        rng = random.Random("ourworld-" + today)
        pool = [t for t in D.DAILY_POOL if t["needs"] in self.unlocked]
        # personality: one of the pet's favorite wishes is always in the list
        favs = getattr(gs, "favorite_wishes", lambda: [])()
        fav = [t for t in pool if t["id"] in favs]
        first = [rng.choice(fav)] if fav else []
        rest = [t for t in pool if t not in first]
        picks = first + rng.sample(rest, min(D.DAILY_COUNT - len(first), len(rest)))
        self.daily = {"date": today, "bonus": False,
                      "tasks": [{"id": t["id"], "text": t["text"], "count": t["count"],
                                 "progress": 0, "done": False} for t in picks]}

    def _daily_event(self, kind, key, loc, score, gs) -> None:
        tasks = self.daily.get("tasks") or []
        spec = {t["id"]: t for t in D.DAILY_POOL}
        for t in tasks:
            sp = spec.get(t["id"])
            if not sp or t["done"] or not _match(sp, kind, key, loc, score):
                continue
            t["progress"] += 1
            if t["progress"] >= t["count"]:
                t["done"] = True
                self.grant(D.DAILY_REWARD, gs)
                self.notices.append("Daily wish granted! +%d coins" % D.DAILY_REWARD["coins"])
        if tasks and all(t["done"] for t in tasks) and not self.daily.get("bonus"):
            self.daily["bonus"] = True
            self.grant(D.DAILY_ALL_BONUS, gs)
            self.notices.append("All of today's wishes granted! Bonus coins!")


def today_str(ts: float) -> str:
    return datetime.date.fromtimestamp(ts).isoformat()
