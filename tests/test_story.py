"""Story, quests, unlocks, daily wishes and save migration (core only, no pygame)."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import story_script as S  # noqa: E402

from core import story_data as D
from core.game_state import GameState
from core.needs import Needs
from core.story import StoryState, bond_level
from core.world import LOCATIONS, PLACE_ACTIONS


@pytest.fixture
def gs(tmp_path):
    g = GameState(save_path=str(tmp_path / "s.json"), clock=lambda: 1792224000.0)  # 2026-10-17
    g.new_game("Pip", 0)
    return g


# ------------------------------------------------------------ data sanity
def test_story_data_is_consistent():
    for qid, q in D.QUESTS.items():
        assert q["giver"] in D.NPCS
        assert 1 <= q["chapter"] <= D.FINAL_CHAPTER
        for a in q.get("after", []):
            assert a in D.QUESTS
        if not q.get("auto"):
            assert qid + "_offer" in D.DIALOGUE, qid
        if not q.get("auto_turn_in"):
            assert qid + "_done" in D.DIALOGUE or q.get("auto"), qid
        r = q.get("reward", {})
        assert r.get("sticker") is None or r["sticker"] in D.STICKERS
        assert r.get("spark") is None or r["spark"] in D.SPARKS
        for st in q["steps"]:
            assert ("event" in st) != ("cond" in st)
            assert st.get("at") is None or st["at"] in LOCATIONS
    for npc in D.NPCS.values():
        assert npc["location"] in LOCATIONS
    reachable = set(D.START_UNLOCKED)
    for ch in D.CHAPTERS:
        reachable |= set(ch["unlock"])
    assert reachable == set(LOCATIONS)
    sparks = {q["reward"].get("spark") for q in D.QUESTS.values()} - {None}
    assert sparks == set(D.SPARKS) and len(sparks) == D.SPARKS_NEEDED
    for t in D.DAILY_POOL:
        assert t["needs"] in LOCATIONS


def test_bond_levels():
    assert bond_level(0) == 1
    assert bond_level(D.BOND_LEVELS[1]) == 2
    assert bond_level(10 ** 6) == len(D.BOND_LEVELS)


# ---------------------------------------------------------------- flow
def test_new_game_starts_small(gs):
    st = gs.story
    assert st.chapter == 1 and st.dialogue == ["intro"]
    assert st.unlocked == set(D.START_UNLOCKED)
    assert st.status("welcome") == "active" and st.status("sweet_tooth") == "locked"
    assert not gs.change_location("arcade") and gs.pet.location == "home"
    assert gs.change_location("town_square")
    assert "Feed" in st.objective("Pip")


def test_steps_respect_location_and_acceptance(gs):
    S.act(gs, gs.perform_care_action, "feed")
    S.act(gs, gs.perform_care_action, "play")
    assert gs.story.status("park_laughs") == "locked"
    S.go(gs, "town_square")
    assert gs.story.status("welcome") == "ready"
    assert gs.story.npc_marker("mayor") == "ready"
    S.talk(gs, "mayor")
    assert gs.story.status("welcome") == "done" and "town_key" in gs.story.stickers
    S.go(gs, "home")
    S.act(gs, gs.perform_care_action, "play")       # not at the park: doesn't count
    assert gs.story.quests["park_laughs"]["progress"][0] == 0
    S.go(gs, "park")
    S.act(gs, gs.perform_care_action, "play")
    assert gs.story.quests["park_laughs"]["progress"][0] == 1
    assert gs.talk("sweetie")["success"] is False   # not here


def test_quest_progress_waits_for_accept(gs):
    S.chapter1(gs)
    gs.pet.coins = 100
    S.go(gs, "sweeties_candy_shop")
    assert gs.story.status("sweet_tooth") == "available"
    S.act(gs, gs.buy_item, "sweeties_candy_shop", "lollipop")
    assert gs.story.quests["sweet_tooth"]["progress"][0] == 0
    S.talk(gs, "sweetie")
    assert gs.story.status("sweet_tooth") == "active"


def test_gifts_on_accept(gs):
    S.chapter1(gs)
    before = gs.pet.inventory.get("flower_seeds", 0)
    S.talk(gs, "gen")
    assert gs.pet.inventory["flower_seeds"] == before + 2


def test_light_needs_sparks_and_quest(gs):
    gs.story.unlocked.add("lantern_hill")
    gs.pet.location = "lantern_hill"
    ok, why = gs.can_place_action("light")
    assert not ok and "Sparks" in why


def test_full_playthrough_reaches_ending(gs):
    S.play_to_end(gs)
    st = gs.story
    assert st.finished and st.ending_pending and "ending" in st.dialogue
    assert set(st.sparks) == set(D.SPARKS)
    assert st.unlocked == set(LOCATIONS)
    assert all(st.status(q) == "done" for q in D.QUEST_ORDER if not D.QUESTS[q].get("side"))
    # dialogue queue plays intro, chapter outros, then the ending
    seen = []
    while True:
        lines = gs.next_dialogue()
        if not lines:
            break
        seen.append(lines[0][1])
    seen = [t for t in seen if "grew" not in t and "grown" not in t]   # growth stages
    assert len(seen) == 6 and "Pip" in " ".join(t for _, t in D.DIALOGUE["ending"]).replace("{pet}", "Pip")
    ok, why = gs.can_place_action("light")
    assert not ok and "already" in why
    assert st.daily_active() and len(st.daily["tasks"]) == D.DAILY_COUNT


def test_side_quest_fern(gs):
    S.chapter1(gs); S.chapter2(gs); S.chapter3(gs)
    S.talk(gs, "fern")
    assert gs.story.status("fern_hunt") == "active"
    for _ in range(25):
        S.go(gs, "willow_woods")
        S.fresh(gs)
        gs.perform_place_action("explore")
        S.wait(gs, 21)
        if gs.story.status("fern_hunt") == "ready":
            break
    assert gs.story.status("fern_hunt") == "ready"
    S.talk(gs, "fern")
    assert "fox" in gs.story.stickers


def test_explore_cooldown_and_finds(gs):
    gs.story.unlocked.add("willow_woods")
    gs.pet.location = "willow_woods"
    S.act(gs, gs.perform_place_action, "explore")
    assert not gs.perform_place_action("explore")["success"]
    found = 0
    for _ in range(12):
        S.wait(gs, 21)
        r = S.act(gs, gs.perform_place_action, "explore")
        found += "sticker" in r["msg"]
    assert found >= 4


# --------------------------------------------------------- daily wishes
def test_daily_wishes_rotate_by_date(tmp_path):
    now = [1792224000.0]
    g = GameState(save_path=str(tmp_path / "d.json"), clock=lambda: now[0])
    g.new_game("Pip", 0)
    S.play_to_end(g)
    day1 = [t["id"] for t in g.story.daily["tasks"]]
    assert len(day1) == 3 and g.story.daily["date"] == "2026-10-17"
    now[0] += 86400
    g.tick(1.0); g.tick(1.0)
    assert g.story.daily["date"] == "2026-10-18"
    # deterministic: a second state on the same day picks the same wishes
    h = GameState(save_path=str(tmp_path / "e.json"), clock=lambda: now[0])
    h.story = StoryState.from_dict(g.story.to_dict())
    h.pet = g.pet
    h.story.daily = {}
    h.story.ensure_daily(h)
    assert [t["id"] for t in h.story.daily["tasks"]] == [t["id"] for t in g.story.daily["tasks"]]


def test_daily_wish_rewards(gs):
    S.play_to_end(gs)
    gs.story.daily = {"date": gs.today(), "bonus": False, "tasks": [
        {"id": "feed3", "text": "x", "count": 3, "progress": 2, "done": False}]}
    coins = gs.pet.coins
    S.go(gs, "home")
    S.act(gs, gs.perform_care_action, "feed")
    t = gs.story.daily["tasks"][0]
    assert t["done"] and gs.story.daily["bonus"]
    assert gs.pet.coins >= coins + D.DAILY_REWARD["coins"] + D.DAILY_ALL_BONUS["coins"]
    assert "daily_star" in gs.story.stickers


# -------------------------------------------------------------- saves
def test_story_survives_save_and_load(gs, tmp_path):
    S.chapter1(gs)
    S.talk(gs, "sweetie")
    gs.pet.coins = 50
    S.act(gs, gs.buy_item, "sweeties_candy_shop", "lollipop")
    xp = gs.pet.bond_xp
    assert gs.save()
    data = json.loads(open(gs.save_manager.path).read())
    assert data["schema_version"] == 4 and "story" in data
    b = GameState(save_path=gs.save_manager.path)
    st = b.story
    assert st.chapter == 2 and st.status("sweet_tooth") == "active"
    assert st.quests["sweet_tooth"]["progress"][0] == 1
    assert "sweeties_candy_shop" in st.unlocked and "arcade" not in st.unlocked
    assert b.pet.bond_xp == xp and "town_key" in st.stickers
    assert st.dialogue == ["intro", "ch1_end"]   # unseen story scenes persist until shown


def test_v2_save_without_story_keeps_places_open(tmp_path):
    v2 = {"schema_version": 2, "saved_at": 1792224000.0, "high_scores": {"snake": 40},
          "pet": {"name": "Old", "species_id": 1, "location": "spa", "coins": 99,
                  "needs": {"hunger": 50, "happiness": 50, "energy": 50, "cleanliness": 50}}}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(v2))
    g = GameState(save_path=str(p))
    st = g.story
    assert g.has_save and g.pet.location == "spa" and st.free_roam
    for loc in ("home", "backyard", "park", "sweeties_candy_shop", "gens_garden", "arcade",
                "pond", "library", "spa", "town_square"):
        assert st.is_unlocked(loc), loc
    assert not st.is_unlocked("lantern_hill") and st.chapter == 1
    assert st.status("welcome") == "active" and st.dialogue == ["intro"]
    assert g.save()
    again = GameState(save_path=str(p))
    assert again.story.free_roam and again.story.is_unlocked("arcade")


def test_garbage_story_block_is_tolerated(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"schema_version": 3, "pet": {"name": "X"},
                             "story": {"chapter": "lots", "quests": {"welcome": {"status": "??"},
                                                                     "nope": {}},
                                       "unlocked": ["atlantis", "park"], "stickers": ["fake"],
                                       "sparks": 7, "daily": []}}))
    g = GameState(save_path=str(p))
    assert g.has_save and g.story.chapter == 1
    assert g.story.status("welcome") == "active"
    assert "atlantis" not in g.story.unlocked and g.story.stickers == []
