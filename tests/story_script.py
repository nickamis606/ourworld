"""Scripted playthrough of the whole story using only core GameState calls.

Shared by tests/test_story.py (core) and the headless smoke test.
"""
from core.needs import Needs


def fresh(gs):
    gs.pet.needs = Needs(50, 50, 60, 50)


def wait(gs, secs):
    for _ in range(int(secs)):
        gs.tick(1.0)


def go(gs, loc):
    assert gs.is_unlocked(loc), loc
    if gs.pet.location != loc:
        assert gs.change_location(loc), loc


def act(gs, fn, *a):
    fresh(gs)
    r = fn(*a)
    assert r.get("success"), (fn.__name__, a, r)
    return r


def talk(gs, npc):
    from core.story_data import NPCS
    go(gs, NPCS[npc]["location"])
    r = gs.talk(npc)
    assert r["success"] and r["lines"], npc
    return r["lines"]


def chapter1(gs):
    act(gs, gs.perform_care_action, "feed")
    act(gs, gs.perform_care_action, "play")
    go(gs, "town_square")
    assert gs.story.status("welcome") == "ready"
    talk(gs, "mayor")                       # turn in welcome + accept park_laughs
    assert gs.story.status("park_laughs") == "active"
    go(gs, "park")
    act(gs, gs.perform_care_action, "play")
    act(gs, gs.perform_care_action, "play")
    go(gs, "home")
    act(gs, gs.perform_care_action, "rest")
    talk(gs, "mayor")
    assert gs.story.chapter == 2


def chapter2(gs):
    gs.pet.coins = max(gs.pet.coins, 100)
    talk(gs, "sweetie")
    act(gs, gs.buy_item, "sweeties_candy_shop", "lollipop")
    act(gs, gs.buy_item, "sweeties_candy_shop", "lollipop")
    act(gs, gs.perform_care_action, "feed")
    talk(gs, "gen")                          # gifts 2 flower seeds
    go(gs, "backyard")
    act(gs, gs.plant_seed, "flower_seeds")
    act(gs, gs.plant_seed, "flower_seeds")
    wait(gs, 200)
    act(gs, gs.harvest_plant)
    act(gs, gs.harvest_plant)
    talk(gs, "sweetie")
    talk(gs, "gen")
    assert gs.story.chapter == 3 and gs.is_unlocked("arcade")


def chapter3(gs):
    talk(gs, "pete")
    fresh(gs)
    gs.finish_minigame("snake", 50)
    gs.finish_minigame("mole_pop", 20)
    talk(gs, "quack")
    for _ in range(2):
        act(gs, gs.perform_place_action, "swim")
    act(gs, gs.perform_care_action, "play")
    talk(gs, "pete")
    talk(gs, "quack")
    assert gs.story.chapter == 4 and gs.is_unlocked("willow_woods")


def chapter4(gs):
    talk(gs, "olive")
    go(gs, "willow_woods")
    r = act(gs, gs.perform_place_action, "explore")
    assert "storybook" in r["msg"]
    go(gs, "library")
    act(gs, gs.perform_place_action, "read")
    wait(gs, 31)
    act(gs, gs.perform_place_action, "read")
    talk(gs, "coco")                          # gifts 18 coins
    act(gs, gs.perform_place_action, "pamper")
    act(gs, gs.perform_care_action, "clean")
    talk(gs, "olive")
    talk(gs, "coco")
    assert gs.story.chapter == 5 and gs.is_unlocked("lantern_hill")
    assert len(gs.story.sparks) == 6


def chapter5(gs):
    talk(gs, "mayor")
    assert gs.story.status("light_lantern") == "active"
    if gs.bond_level < 4:
        gs.add_bond(200)
    go(gs, "lantern_hill")
    act(gs, gs.perform_place_action, "light")
    assert gs.story.finished and gs.story.status("light_lantern") == "done"


def play_to_end(gs):
    chapter1(gs); chapter2(gs); chapter3(gs); chapter4(gs); chapter5(gs)
