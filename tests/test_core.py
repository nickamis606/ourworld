"""Pure-logic tests: no pygame needed."""
import json
import sys

import pytest

from core.game_state import GameState, FULL_THRESHOLD
from core.needs import Needs, DECAY_PER_SEC
from core.pet_state import PetState
from core.rewards import minigame_reward
from core import world


@pytest.fixture
def gs(tmp_path):
    return GameState(save_path=str(tmp_path / "save.json"))


def test_core_has_no_pygame_imports():
    import importlib, pathlib
    for f in (pathlib.Path(__file__).parent.parent / "core").glob("*.py"):
        src = f.read_text()
        assert "import pygame" not in src, f"{f} imports pygame"


def test_needs_decay_by_dt():
    n = Needs(hunger=50, happiness=50, energy=50, cleanliness=50)
    n.tick(10)
    assert n.hunger == pytest.approx(50 - DECAY_PER_SEC["hunger"] * 10)
    assert n.cleanliness == pytest.approx(50 - DECAY_PER_SEC["cleanliness"] * 10)


def test_needs_clamp_and_ignore_negative_dt():
    n = Needs(hunger=1)
    n.tick(10_000)
    assert n.hunger == 0.0
    n.tick(-5)
    assert n.hunger == 0.0
    n.apply({"hunger": 500, "bogus": 3})
    assert n.hunger == 100.0


def test_tick_clamps_huge_dt(gs):
    gs.pet.needs = Needs(80, 80, 80, 80)
    gs.tick(3600)  # a frozen frame must not wipe out the pet
    assert gs.pet.needs.hunger > 79


def test_feed_changes_needs(gs):
    gs.pet.needs = Needs(hunger=40, happiness=50, energy=50, cleanliness=50)
    res = gs.perform_care_action("feed")
    assert res["success"]
    assert gs.pet.needs.hunger == 65
    assert res["deltas"]["hunger"] == 25


def test_full_need_refuses(gs):
    gs.pet.needs.hunger = FULL_THRESHOLD + 1
    res = gs.perform_care_action("feed")
    assert not res["success"] and "hungry" in res["msg"]


def test_play_needs_energy(gs):
    gs.pet.needs.happiness = 10
    gs.pet.needs.energy = 5
    assert not gs.perform_care_action("play")["success"]


def test_location_bonus(gs):
    gs.pet.needs = Needs(50, 30, 50, 50)
    gs.pet.location = "park"
    res = gs.perform_care_action("play")
    assert res["bonus"] and gs.pet.needs.happiness == 30 + 22 + 10


def test_unknown_action(gs):
    assert not gs.perform_care_action("dance")["success"]


def test_shop_buy_and_eat(gs):
    gs.pet.location = "sweeties_candy_shop"
    gs.pet.coins = 30
    gs.pet.needs.hunger = 20
    res = gs.buy_item("sweeties_candy_shop", "lollipop")
    assert res["success"] and res["eat"]
    assert gs.pet.coins == 20 and gs.pet.needs.hunger == 50
    assert "lollipop" not in gs.pet.inventory


def test_shop_needs_coins_and_presence(gs):
    gs.pet.location = "gens_garden"
    gs.pet.coins = 5
    assert not gs.buy_item("gens_garden", "flower_seeds")["success"]
    gs.pet.location = "home"
    gs.pet.coins = 500
    assert not gs.buy_item("gens_garden", "flower_seeds")["success"]


def test_garden_cycle(gs):
    gs.pet.location = "gens_garden"
    gs.pet.coins = 100
    assert gs.buy_item("gens_garden", "flower_seeds")["success"]
    assert gs.pet.inventory["flower_seeds"] == 1
    assert not gs.plant_seed("flower_seeds")["success"]  # not in backyard
    gs.pet.location = "backyard"
    assert gs.plant_seed("flower_seeds")["success"]
    assert "flower_seeds" not in gs.pet.inventory
    assert not gs.harvest_plant()["success"]
    stage_secs = world.PLANTS["flower"]["stage_secs"]
    for _ in range(int(stage_secs * world.MAX_STAGE / 5) + 2):
        gs.tick(5)
    assert gs.mature_plants() == 1
    coins = gs.pet.coins
    res = gs.harvest_plant()
    assert res["success"] and gs.pet.inventory["flowers"] == 1
    assert gs.pet.coins == coins + world.PLANTS["flower"]["coins"]


def test_garden_full(gs):
    gs.pet.location = "backyard"
    gs.pet.inventory["flower_seeds"] = 20
    for _ in range(world.GARDEN_SLOTS):
        assert gs.plant_seed("flower_seeds")["success"]
    assert not gs.plant_seed("flower_seeds")["success"]


def test_decorate_and_expire(gs):
    gs.pet.location = "home"
    gs.pet.inventory["flowers"] = 4
    assert not gs.decorate_home()["success"]
    gs.pet.inventory["flowers"] = 5
    assert gs.decorate_home()["success"]
    assert gs.pet.home_decorated and "flowers" not in gs.pet.inventory
    gs.apply_offline(world.DECORATION_SECS + 1)
    assert not gs.pet.home_decorated


def test_mood_and_wants(gs):
    gs.pet.needs = Needs(90, 90, 90, 90)
    assert gs.mood() == "happy" and gs.wants() is None
    gs.pet.needs.hunger = 10
    assert gs.wants() == "hunger" and gs.mood() != "happy"


@pytest.mark.parametrize("game", ["snake", "pet_dash", "frogger", "brick_bop", "pet_pairs", "mole_pop"])
def test_minigame_rewards(game):
    zero = minigame_reward(game, 0)
    assert zero["coins"] == 0 and zero["happiness"] == 0 and zero["energy"] < 0
    small, big = minigame_reward(game, 30), minigame_reward(game, 3000)
    assert 0 < small["coins"] < big["coins"]
    assert big["happiness"] <= 40  # capped


def test_finish_minigame_records_best(gs):
    gs.pet.needs.energy = 50
    r = gs.finish_minigame("snake", 120)
    assert r["new_best"] and r["best"] == 120 and r["coins"] > 0
    assert not gs.finish_minigame("snake", 10)["new_best"]


def test_save_load_roundtrip(tmp_path):
    path = str(tmp_path / "s.json")
    a = GameState(save_path=path)
    a.new_game("Luna", 2)
    a.pet.needs = Needs(11, 22, 33, 44)
    a.pet.coins = 77
    a.pet.location = "park"
    a.pet.inventory = {"flower_seeds": 2}
    a.pet.garden = [{"type": "sunflower", "stage": 2, "age": 5.0}]
    a.save_manager.update_high_score("frogger", 999)
    assert a.save()
    b = GameState(save_path=path)
    assert b.has_save
    assert (b.pet.name, b.pet.species_id, b.pet.coins, b.pet.location) == ("Luna", 2, 77, "park")
    assert b.pet.needs.hunger == pytest.approx(11, abs=0.5)
    assert b.pet.garden[0]["type"] == "sunflower"
    assert b.save_manager.get_high_score("frogger") == 999


def test_quit_save_not_throttled(tmp_path):
    gs = GameState(save_path=str(tmp_path / "s.json"))
    assert gs.trigger_auto_save()
    assert not gs.trigger_auto_save()      # throttled autosave
    assert gs.save()                        # forced save always writes


def test_corrupt_save_is_quarantined(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{not json")
    gs = GameState(save_path=str(path))
    assert not gs.has_save
    assert (tmp_path / "s.json.corrupt").exists()


def test_newer_save_not_overwritten(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(json.dumps({"schema_version": 99, "pet": {"name": "Future"}}))
    gs = GameState(save_path=str(path))
    gs.save()
    assert json.loads(path.read_text())["schema_version"] == 99


def test_legacy_v0_save_migrates(tmp_path):
    """The flat format from main's saves/savegame.json, with monotonic stamps."""
    legacy = {"name": "Nova", "creature_type": "fluff",
              "needs": {"hunger": 82.3, "happiness": 97.7, "energy": 59.7, "cleanliness": 57.2},
              "location": "arcade", "days_alive": 0, "coins": 60,
              "inventory": {"flower_seeds": 3},
              "garden": [{"type": "sunflower", "stage": 1, "planted_time": 409894.59}],
              "home_decorated": True, "home_decoration_time": 410074.6}
    path = tmp_path / "s.json"
    path.write_text(json.dumps(legacy))
    gs = GameState(save_path=str(path))
    assert gs.has_save and gs.pet.name == "Nova" and gs.pet.location == "arcade"
    assert gs.pet.garden[0]["age"] == 0.0 and gs.pet.home_decorated
    gs.tick(1)  # must not crash on migrated data


def test_v1_save_migrates(tmp_path):
    v1 = {"schema_version": 1, "last_save_time": 123.0, "high_scores": {"snake": 40},
          "pet": {"name": "Pip", "needs": {"hunger": 50, "happiness": 50, "energy": 50, "cleanliness": 50},
                  "location": "nowhere", "coins": "lots", "garden": [{"type": "cactus", "stage": 9}]}}
    path = tmp_path / "s.json"
    path.write_text(json.dumps(v1))
    gs = GameState(save_path=str(path))
    assert gs.has_save and gs.pet.location == "home"
    assert gs.pet.garden[0] == {"type": "flower", "stage": 3, "age": 0.0}
    assert gs.save_manager.get_high_score("snake") == 40


def test_offline_decay_is_gentle(gs):
    gs.pet.needs = Needs(90, 90, 90, 90)
    gs.apply_offline(7 * 24 * 3600)
    assert gs.pet.needs.hunger >= 20  # hungry, never starved


# ----------------------------------------------------------- new places
def test_map_grid_is_complete_and_unique():
    cells = [d["map"] for d in world.LOCATIONS.values()]
    assert len(cells) == len(set(cells)) == world.MAP_COLS * world.MAP_ROWS
    for c in range(world.MAP_COLS):
        for r in range(world.MAP_ROWS):
            assert world.location_at(c, r) in world.LOCATIONS


def test_every_place_action_lives_somewhere():
    for key, spec in world.PLACE_ACTIONS.items():
        assert spec["location"] in world.LOCATIONS
        assert key in world.place_actions_for(spec["location"])
    for loc in ("pond", "library", "spa"):
        assert world.place_actions_for(loc), loc


def test_place_action_only_at_its_place(gs):
    gs.pet.location = "home"
    gs.pet.needs.cleanliness = 30
    r = gs.perform_place_action("swim")
    assert not r["success"] and "Sunny Pond" in r["msg"]
    assert gs.perform_place_action("nope")["success"] is False


def test_swim_cleans_and_tires(gs):
    gs.pet.location = "pond"
    gs.pet.needs = Needs(60, 50, 60, 30)
    r = gs.perform_place_action("swim")
    assert r["success"]
    assert gs.pet.needs.cleanliness > 50 and gs.pet.needs.happiness > 55 and gs.pet.needs.energy < 55
    gs.pet.needs.energy = 10
    gs.pet.needs.cleanliness = 30
    assert not gs.perform_place_action("swim")["success"]  # too tired to swim
    gs.pet.needs = Needs(60, 50, 60, 99)
    assert not gs.perform_place_action("swim")["success"]  # already clean


def test_read_has_cooldown_that_ticks_down(gs):
    gs.pet.location = "library"
    gs.pet.needs = Needs(80, 40, 50, 80)
    assert gs.perform_place_action("read")["success"]
    r = gs.perform_place_action("read")
    assert not r["success"] and "break" in r["msg"]
    for _ in range(world.PLACE_ACTIONS["read"]["cooldown"] + 1):
        gs.tick(1.0)      # tick() clamps big dt, so step like the game loop does
    assert "read" not in gs.pet.cooldowns
    assert gs.perform_place_action("read")["success"]


def test_spa_costs_coins(gs):
    gs.pet.location = "spa"
    gs.pet.needs = Needs(80, 50, 30, 20)
    cost = world.PLACE_ACTIONS["pamper"]["cost"]
    gs.pet.coins = cost - 1
    r = gs.perform_place_action("pamper")
    assert not r["success"] and "coins" in r["msg"]
    gs.pet.coins = cost + 5
    r = gs.perform_place_action("pamper")
    assert r["success"] and gs.pet.coins == 5 and r["cost"] == cost
    assert gs.pet.needs.cleanliness >= 60 and gs.pet.needs.energy >= 45


def test_new_place_bonuses_and_decay(gs):
    gs.pet.location = "spa"
    gs.pet.needs = Needs(80, 50, 50, 20)
    r = gs.perform_care_action("clean")
    assert r["success"] and "Spa bonus" in r["msg"]
    lib = GameState(save_path=gs.save_manager.path + ".b")
    lib.pet.location = "library"
    gs.pet.location = "park"
    gs.pet.needs = Needs(80, 80, 80, 80)
    lib.pet.needs = Needs(80, 80, 80, 80)
    for _ in range(60):
        gs.tick(1.0)
        lib.tick(1.0)
    assert lib.pet.needs.energy > gs.pet.needs.energy  # library is restful


def test_cooldowns_survive_save_and_old_saves_load(tmp_path):
    path = str(tmp_path / "s.json")
    a = GameState(save_path=path)
    a.new_game("Ivy", 1)
    a.pet.location = "library"
    a.pet.needs.happiness = 30
    assert a.perform_place_action("read")["success"]
    assert a.save()
    b = GameState(save_path=path)
    assert b.pet.location == "library" and b.pet.cooldowns.get("read", 0) > 0
    # a round-1 save has no cooldowns field at all
    data = json.loads(open(path).read())
    del data["pet"]["cooldowns"]
    data["pet"]["location"] = "spa"
    open(path, "w").write(json.dumps(data))
    c = GameState(save_path=path)
    assert c.pet.cooldowns == {} and c.pet.location == "spa"
    data["pet"]["cooldowns"] = {"read": "soon", "swim": -3}
    open(path, "w").write(json.dumps(data))
    assert GameState(save_path=path).pet.cooldowns == {}
