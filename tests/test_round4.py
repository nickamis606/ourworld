"""Round 4: audio, settings, parent tools, photos, quit, launcher, and later features."""
import ast
import json
import os

import pygame
import pytest

from core.game_state import GameState
from core.settings import Settings
from tests.test_smoke import adopt, key, run, skip_dialogue  # noqa: F401  (fixtures/helpers)
from tests.test_smoke import game  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fresh(tmp_path, **kw):
    gs = GameState(save_path=str(tmp_path / "s.json"), autoload=False, **kw)
    gs.new_game("Mochi", 0)
    gs.story.dialogue.clear()
    return gs


# ------------------------------------------------------------------ audio
def test_audio_files_generated_and_small():
    d = os.path.join(ROOT, "assets", "audio")
    files = os.listdir(d)
    assert sum(f.startswith("music_") for f in files) >= 9
    assert sum(f.startswith("sfx_") for f in files) >= 15
    total = sum(os.path.getsize(os.path.join(d, f)) for f in files)
    assert total < 1500 * 1024


def test_audio_nosound_env_is_silent_noop(monkeypatch):
    monkeypatch.setenv("OURWORLD_NOSOUND", "1")
    from engine.audio import Audio
    a = Audio()
    assert not a.enabled
    a.apply(0.5, 0.5, False)
    a.music("home")
    a.sfx("coin")
    a.stop_music()
    a.shutdown()
    assert a.played == ["coin"]


def test_audio_survives_mixer_init_failure(monkeypatch):
    from engine import audio as audio_mod

    def boom(*a, **k):
        raise pygame.error("no audio device")
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "init", boom)
    a = audio_mod.Audio()
    assert not a.enabled
    a.music("town")
    a.sfx("quest")


def test_track_for_places_and_times():
    from engine.audio import track_for
    assert track_for("arcade") == "arcade"
    assert track_for("park", "night") == "night"
    assert track_for("home", "night") == "home"
    assert track_for("park", "day", "winter") == "winter"
    assert track_for("town_square", "day", "fall", True) == "festival"


def test_actions_play_sound_effects(game):
    adopt(game)
    game.state.pet.needs.hunger = 30
    game.audio.played.clear()
    game.scene.bar.index = 0     # Feed
    run(game, 3, key(pygame.K_SPACE))
    run(game, 40)
    assert "eat" in game.audio.played


# --------------------------------------------------------------- settings
def test_settings_roundtrip_and_clamp(tmp_path):
    gs = fresh(tmp_path)
    gs.settings.music, gs.settings.sfx, gs.settings.muted = 3, 0, True
    gs.settings.reminder_min, gs.settings.slow_needs = 30, True
    assert gs.save()
    gs2 = GameState(save_path=gs.save_manager.path)
    assert gs2.settings.to_dict() == gs.settings.to_dict()
    s = Settings.from_dict({"music": 99, "sfx": "x", "reminder_min": 7, "muted": 1})
    assert s.music == 10 and s.sfx == 8 and s.reminder_min in (0, 15, 30, 45, 60) and s.muted


def test_slow_needs_halves_decay(tmp_path):
    a, b = fresh(tmp_path), fresh(tmp_path)
    b.settings.slow_needs = True
    for _ in range(60):
        a.tick(1.0)
        b.tick(1.0)
    lost_a = 80 - a.pet.needs.hunger
    lost_b = 80 - b.pet.needs.hunger
    assert lost_a > 0 and abs(lost_b - lost_a / 2) < 0.6


def test_reminder_due_and_ack(tmp_path):
    gs = fresh(tmp_path)
    assert not gs.reminder_due()
    gs.settings.reminder_min = 15
    gs.session_secs = 14 * 60
    assert not gs.reminder_due()
    gs.session_secs = 15 * 60 + 1
    assert gs.reminder_due()
    gs.ack_reminder()
    assert not gs.reminder_due()


def test_reminder_shows_gentle_dialogue(game):
    adopt(game)
    game.state.settings.reminder_min = 15
    game.state.session_secs = 15 * 60 + 5
    run(game, 3)
    assert game.scene.dialog is not None
    text = " ".join(t for _, t in game.scene.dialog.lines)
    assert "playing for 15 minutes" in text


def _open_pause_item(game, item):
    run(game, 2, key(pygame.K_RETURN))
    menu = game.scene.pause
    keys = [k for k, _ in menu.options]
    menu.index = keys.index(item)
    run(game, 2, key(pygame.K_SPACE))


def test_settings_overlay_volume_and_parent_gate(game):
    adopt(game)
    _open_pause_item(game, "settings")
    sm = game.scene.settings_menu
    assert sm is not None and not sm.parent_open
    before = game.state.settings.music
    run(game, 1, key(pygame.K_LEFT))
    assert game.state.settings.music == before - 1
    assert abs(game.audio.music_vol - (before - 1) / 10) < 1e-6
    # move to "Parent settings" and hold A for 2+ seconds
    sm.index = [k for k, _ in sm.rows()].index("parent")
    game.input.held.add("A")
    run(game, 70)
    game.input.held.discard("A")
    assert sm.parent_open
    keys = [k for k, _ in sm.rows()]
    sm.index = keys.index("slow")
    run(game, 1, key(pygame.K_RIGHT))
    assert game.state.settings.slow_needs
    sm.index = keys.index("reminder")
    run(game, 1, key(pygame.K_RIGHT))
    assert game.state.settings.reminder_min == 15
    run(game, 2, key(pygame.K_x))   # B closes
    assert game.scene.settings_menu is None


def test_parent_gate_needs_a_real_hold():
    from ui.settings_menu import SettingsMenu
    sm = SettingsMenu(Settings())
    sm.index = [k for k, _ in sm.rows()].index("parent")
    sm.handle_action("A")           # a tap does nothing
    sm.update(0.5, {"A"})
    sm.update(0.5, set())           # let go: progress resets
    sm.update(1.5, {"A"})
    assert not sm.parent_open
    sm.update(0.6, {"A"})
    assert sm.parent_open


# ------------------------------------------------------------------ photo
def test_photo_from_pause_menu_and_combo(game, tmp_path, monkeypatch):
    monkeypatch.setenv("OURWORLD_PHOTOS", str(tmp_path / "photos"))
    adopt(game)
    _open_pause_item(game, "photo")
    files = os.listdir(tmp_path / "photos")
    assert len(files) == 1 and files[0].endswith(".png")
    img = pygame.image.load(str(tmp_path / "photos" / files[0]))
    assert img.get_size() == (640, 480)
    assert "photo" in game.audio.played
    assert game.scene.hide_hud is False
    # hold L + R: one photo, not one per frame
    game.input.held.update({"L", "R"})
    run(game, 10)
    game.input.held.difference_update({"L", "R"})
    run(game, 2)
    assert len(os.listdir(tmp_path / "photos")) == 2


# ------------------------------------------------------------- quit/title
def test_title_menu_has_quit(game):
    adopt(game)
    game.state.save()
    game.switch("title", fade=False)
    run(game, 2)
    keys = [k for k, _ in game.scene.menu.options]
    assert keys[-1] == "quit"
    game.scene.menu.index = len(keys) - 1
    run(game, 1, key(pygame.K_SPACE))
    assert not game.running


def test_knulli_launcher_is_valid_python37():
    p = os.path.join(ROOT, "tools", "knulli", "OurWorld.pygame")
    src = open(p).read()
    ast.parse(src, feature_version=(3, 7))
    assert "--fullscreen" in src and "main_pygame.py" in src


def test_all_code_parses_as_python37():
    for base, _dirs, files in os.walk(ROOT):
        if "venv" in base or "/." in base:
            continue
        for f in files:
            if f.endswith(".py"):
                ast.parse(open(os.path.join(base, f)).read(), feature_version=(3, 7))


# ------------------------------------------------------- growth stages
def test_growth_stages_follow_bond(tmp_path):
    from core import pets
    from core.story_data import BOND_LEVELS
    gs = fresh(tmp_path)
    assert gs.stage == "baby"
    gs.add_bond(BOND_LEVELS[2] - gs.pet.bond_xp)   # level 3
    gs.tick(1.0)
    assert gs.stage == "kid" and gs.pet.stage_seen == "kid"
    assert "grow_kid" in gs.story.dialogue
    assert any("grew" in n for n in gs.story.notices)
    n = gs.story.dialogue.count("grow_kid")
    gs.tick(1.0)
    assert gs.story.dialogue.count("grow_kid") == n      # celebrated once
    gs.add_bond(BOND_LEVELS[4] - gs.pet.bond_xp)
    gs.tick(1.0)
    assert gs.stage == "adult" and "grow_adult" in gs.story.dialogue
    assert pets.stage_scale("baby") < pets.stage_scale("kid") < pets.stage_scale("adult") == 1.0


def test_stage_sprites_and_accessories_draw(game):
    from core.story_data import BOND_LEVELS
    adopt(game)
    heights = []
    for lvl in (0, 2, 4):
        game.state.pet.bond_xp = BOND_LEVELS[lvl]
        game.state.pet.stage_seen = game.state.stage
        run(game, 2)
        heights.append(game.scene.pet.height)
    assert heights[0] < heights[1] < heights[2] == 128


# --------------------------------------------------------- personality
def test_new_pet_trait_choice_and_effects(tmp_path):
    from core.pets import TRAITS
    gs = GameState(save_path=str(tmp_path / "t.json"), autoload=False)
    gs.new_game("Milo", 1, "sleepy")
    assert gs.pet.trait == "sleepy"
    assert gs.decay_multipliers()["energy"] == pytest.approx(TRAITS["sleepy"]["mult"]["energy"])
    gs.pet.needs.energy = 40
    before = gs.pet.needs.happiness
    res = gs.perform_care_action("rest")
    assert res["liked"] and "loves" in res["msg"]
    assert gs.pet.needs.happiness - before == pytest.approx(6, abs=0.01)
    gs.new_game("Luna", 2, "picky")
    gs.pet.needs.hunger = 40
    r = gs.perform_care_action("feed")
    assert r["deltas"]["hunger"] == 25 - 7 and "sniffs" in r["msg"]


def test_trait_shapes_daily_wishes(tmp_path):
    from tests import story_script as S
    for trait in ("playful", "sleepy", "picky", "curious"):
        gs = GameState(save_path=str(tmp_path / f"{trait}.json"), autoload=False, clock=lambda: 1792224000.0)
        gs.new_game("Pip", 0, trait)
        S.play_to_end(gs)
        ids = [t["id"] for t in gs.story.daily["tasks"]]
        assert any(i in gs.favorite_wishes() for i in ids), (trait, ids)


def test_title_lets_you_pick_a_personality(game):
    run(game, 2, key(pygame.K_SPACE))
    assert game.scene.mode == "trait"
    run(game, 1, key(pygame.K_DOWN))     # Sleepy
    run(game, 2, key(pygame.K_SPACE))
    run(game, 20)
    assert game.scene_name == "main" and game.state.pet.trait == "sleepy"


def test_old_save_gets_a_stable_trait(tmp_path):
    from core.pet_state import PetState
    from core.pets import TRAITS
    a = PetState.from_dict({"name": "Bubbles", "bond_xp": 200})
    b = PetState.from_dict({"name": "Bubbles"})
    assert a.trait in TRAITS and a.trait == b.trait
    assert a.stage_seen == "adult"     # no surprise growth cut-scene after migrating


# -------------------------------------------------------- gentle stakes
def test_mopey_comes_and_goes_gently(tmp_path):
    gs = fresh(tmp_path)
    xp = gs.pet.bond_xp
    for n in ("hunger", "happiness", "energy", "cleanliness"):
        setattr(gs.pet.needs, n, 20)
    gs.tick(1.0)
    assert gs.pet.mopey and gs.idle_reaction(0) == "rain"
    assert gs.pet.bond_xp == xp          # never takes anything away
    for n in ("hunger", "happiness", "energy", "cleanliness"):
        setattr(gs.pet.needs, n, 35)     # better, but not yet perked up (hysteresis)
    gs.tick(1.0)
    assert gs.pet.mopey
    for n in ("hunger", "happiness", "energy", "cleanliness"):
        setattr(gs.pet.needs, n, 60)
    gs.tick(1.0)
    assert not gs.pet.mopey and gs.pet.bond_xp > xp
    assert any("perked" in m for m in gs.story.notices)


def test_mopey_dims_the_town_and_droops(game):
    from sprites import backdrops
    adopt(game)
    p = game.state.pet
    for n in ("hunger", "happiness", "energy", "cleanliness"):
        setattr(p.needs, n, 10)
    run(game, 40)
    assert p.mopey
    loc = p.location
    period = game.state.time_of_day()
    bright = backdrops.get(loc, period, "", "", "", False)
    dim = backdrops.get(loc, period, "", "", "", True)
    c1, c2 = bright.get_at((320, 200)), dim.get_at((320, 200))
    assert sum(c2[:3]) < sum(c1[:3])
    game.scene.draw(game.screen)


# --------------------------------------------------- seasons & events
def test_seasons_and_event_dates():
    import datetime as dt
    from core import calendar as C
    assert C.season_of(dt.date(2026, 10, 17)) == "fall"
    assert C.season_of(dt.date(2026, 1, 2)) == "winter"
    assert C.active_event(dt.date(2026, 10, 17)) == "harvest_fair"
    assert C.active_event(dt.date(2026, 12, 25)) == "snow_day"
    assert C.active_event(dt.date(2027, 1, 3)) == "snow_day"
    assert C.event_year(dt.date(2027, 1, 3), "snow_day") == 2026
    assert C.active_event(dt.date(2026, 4, 1)) == "egg_hunt"
    assert C.active_event(dt.date(2026, 7, 4)) == "summer_splash"
    assert C.active_event(dt.date(2026, 6, 10)) is None
    assert C.week_id(dt.date(2026, 10, 17)) == "2026-W42"


def test_date_override_env(monkeypatch, tmp_path):
    monkeypatch.setenv("OURWORLD_DATE", "2026-12-24")
    gs = fresh(tmp_path)
    assert gs.season() == "winter" and gs.current_event() == "snow_day"
    monkeypatch.setenv("OURWORLD_DATE", "not-a-date")
    assert gs.season() in ("spring", "summer", "fall", "winter")


def test_harvest_fair_doubles_coins_and_rewards(monkeypatch, tmp_path):
    monkeypatch.setenv("OURWORLD_DATE", "2026-10-17")
    gs = fresh(tmp_path)
    gs.pet.location = "backyard"
    coins = []
    for _ in range(3):
        gs.pet.garden.append({"type": "flower", "stage": 3, "age": 0.0})
        r = gs.harvest_plant()
        coins.append(r["coins"])
    from core.world import PLANTS
    assert coins[0] == 2 * PLANTS["flower"]["coins"]
    st = gs.event_status()
    assert st["done"] and "pumpkin" in gs.story.stickers
    assert gs.extras.furniture.get("pumpkin") == 1


def test_snow_day_snowman_once(monkeypatch, tmp_path):
    monkeypatch.setenv("OURWORLD_DATE", "2026-12-28")
    gs = fresh(tmp_path)
    gs.story.unlocked.add("park")
    assert "snowman" in gs.place_actions_here("park")
    gs.pet.location = "park"
    r = gs.perform_place_action("snowman")
    assert r["success"] and gs.snowman_built()
    assert gs.backdrop_extras("park") == ("snowman",)
    assert "snowman" in gs.story.stickers
    ok, why = gs.can_place_action("snowman")
    assert not ok and "already" in why
    monkeypatch.setenv("OURWORLD_DATE", "2026-06-10")
    assert "snowman" not in gs.place_actions_here("park")
    ok, why = gs.can_place_action("snowman")
    assert not ok and "Snow Day" in why


def test_egg_hunt_needs_five(monkeypatch, tmp_path):
    monkeypatch.setenv("OURWORLD_DATE", "2026-04-02")
    gs = fresh(tmp_path)
    gs.pet.location = "park"
    for i in range(5):
        gs.pet.cooldowns.clear()
        gs.pet.needs.energy = 80
        assert gs.perform_place_action("egg_hunt")["success"], i
    assert gs.event_status()["done"] and "egg" in gs.story.stickers
    gs.pet.cooldowns.clear()
    assert not gs.can_place_action("egg_hunt")[0]


@pytest.mark.parametrize("date", ["2026-10-17", "2026-12-24", "2026-04-02", "2026-07-04"])
def test_every_place_draws_in_every_season(game, monkeypatch, date):
    from core import world
    from sprites import backdrops
    monkeypatch.setenv("OURWORLD_DATE", date)
    adopt(game)
    for loc in world.LOCATIONS:
        game.state.story.unlocked.add(loc)
        game.state.pet.location = loc
        game.switch("main", fade=False)
        run(game, 2)
    run(game, 1, key(pygame.K_LSHIFT))
    assert game.scene.journal.open and "event" in game.scene.journal._entries(game.state.story)
    run(game, 2)
    plain = backdrops.get("park", "day")
    tinted = backdrops.get("park", "day", "", game.state.season(), game.state.current_event() or "")
    assert plain is not tinted


def test_winter_music_outdoors():
    from engine.audio import track_for
    assert track_for("pond", "day", "winter") == "winter"
    assert track_for("willow_woods", "day", "winter") == "woods"


# --------------------------------------------------------------- fishing
def test_fish_pool_depends_on_time_and_season():
    import random
    from core import fish_data as FD
    assert "moonfish" in FD.available("night", "fall")
    assert "moonfish" not in FD.available("day", "fall")
    assert "icefish" in FD.available("day", "winter")
    rng = random.Random(1)
    got = {FD.roll(rng, "day", "summer") for _ in range(400)}
    assert "sunny" in got and "moonfish" not in got and "koi" in got


def test_finish_fishing_fills_the_book(tmp_path):
    gs = fresh(tmp_path)
    gs.pet.location = "pond"
    c0 = gs.pet.coins
    r = gs.finish_fishing([("minnow", 12), ("sunfish", 15), ("minnow", 14)])
    assert r["coins"] == 2 + 4 + 2 and gs.pet.coins == c0 + 8
    assert gs.extras.fish["minnow"] == {"count": 2, "best": 14}
    assert r["new"] == ["minnow", "sunfish"]
    gs.finish_fishing([(k, 10) for k in ("bluegill", "goldfish", "catfish", "trout")])
    assert "angler" in gs.story.stickers and gs.extras.furniture.get("fishbowl") == 1
    gs.finish_fishing([("not_a_fish", 3)])     # ignored, no crash


def _play_fishing(mg, catch=True):
    """Drive the Fishing minigame by hand: cast, wait for the bite, hook, reel."""
    mg.handle_action("A")                      # cast
    for _ in range(200):
        mg.update(1 / 30)
        if mg.phase == "bite":
            break
    assert mg.phase == "bite"
    mg.handle_action("A")                      # hook
    assert mg.phase == "reel"
    for _ in range(600):
        if catch:
            mg.zone_x = mg.fish_x              # perfect tracking
        else:
            mg.zone_x = 0.15 if mg.fish_x > 0.5 else 0.85
        mg.held = set()
        mg.update(1 / 30)
        if mg.phase != "reel":
            break


def test_fishing_minigame_catch_and_escape():
    from minigames.fishing import Fishing, CASTS
    screen = pygame.display.set_mode((640, 480))
    mg = Fishing(screen, seed=4)
    _play_fishing(mg, catch=True)
    assert mg.catches and mg.score > 0
    mg.draw(screen)
    for _ in range(60):
        mg.update(1 / 30)
    assert mg.phase == "aim"
    _play_fishing(mg, catch=False)
    assert len(mg.catches) == 1               # the second one wiggled free
    while not mg.game_over:                   # use up casts (too-early presses)
        if mg.phase == "aim":
            mg.handle_action("A")
            mg.handle_action("A")
        mg.update(1 / 30)
        mg.draw(screen)
    assert mg.casts_left == 0 and CASTS == 5


def test_fishing_from_the_pond_by_buttons(game):
    adopt(game)
    st = game.state
    st.story.unlocked.add("pond")
    st.change_location("pond")
    game.switch("main", fade=False)
    run(game, 3)
    game.scene.bar.focus_id("fish")
    run(game, 3, key(pygame.K_SPACE))
    run(game, 20)
    assert game.scene_name == "arcade" and game.scene.fishing
    mg = game.scene.minigame
    _play_fishing(mg, catch=True)
    mg.casts_left = 0
    for _ in range(80):
        run(game, 1)
        if mg.phase == "aim":
            break
    for _ in range(140):
        run(game, 1)
        if game.scene.phase == "result":
            break
    assert game.scene.phase == "result" and st.extras.fish
    run(game, 1, key(pygame.K_x))              # B: back to the pond
    run(game, 20)
    assert game.scene_name == "main" and st.pet.location == "pond"
    run(game, 1, key(pygame.K_LSHIFT))
    j = game.scene.journal
    j.tab = 3
    run(game, 2)                               # Fish tab draws


# ------------------------------------------------------ weekly challenge
def test_weekly_challenge_rotates_and_pays_once(tmp_path):
    t = [1792224000.0]   # 2026-10-17
    gs = GameState(save_path=str(tmp_path / "w.json"), autoload=False, clock=lambda: t[0])
    os.environ.pop("OURWORLD_DATE", None)
    try:
        gs.new_game("Pip", 0)
        a = gs.weekly_challenge()
        t[0] += 7 * 86400
        b = gs.weekly_challenge()
        assert a["week"] != b["week"] and a["game"] != b["game"]
        coins = gs.pet.coins
        r = gs.finish_minigame(b["game"], b["target"] - 1)
        assert not r["weekly"]
        r = gs.finish_minigame(b["game"], b["target"])
        assert r["weekly"] and "trophy" in gs.story.stickers and gs.extras.trophies == 1
        assert gs.extras.furniture.get("trophy") == 1
        r = gs.finish_minigame(b["game"], b["target"] + 50)
        assert r["weekly"] is False and gs.extras.trophies == 1
        assert gs.pet.coins > coins
    finally:
        os.environ["OURWORLD_DATE"] = "2026-06-10"


def test_arcade_picker_shows_weekly_banner(game):
    adopt(game)
    game.state.story.unlocked.add("arcade")
    game.switch("arcade", fade=False)
    run(game, 3)
    wk = game.state.weekly_challenge()
    from minigames import GAME_INFO
    assert wk["game"] in GAME_INFO and wk["target"] > 0
    game.scene.draw(game.screen)


# ------------------------------------------------------- home decorating
def test_furniture_rules(tmp_path):
    gs = fresh(tmp_path)
    gs.pet.location = "home"
    assert not gs.place_furniture(0, 1, "plant")["success"]          # don't own it
    gs.extras.furniture.update({"plant": 1, "picture": 1})
    r = gs.place_furniture(0, 0, "plant")
    assert not r["success"] and "floor" in r["msg"]
    assert not gs.place_furniture(0, 1, "picture")["success"]       # wall item
    assert gs.place_furniture(0, 1, "plant")["success"]
    assert gs.place_furniture(3, 0, "picture")["success"]
    assert gs.furniture_at(0, 1) == "plant" and "plant" not in gs.extras.furniture
    gs.extras.furniture["lamp"] = 1
    assert not gs.place_furniture(0, 1, "lamp")["success"]          # occupied
    assert not gs.place_furniture(9, 1, "lamp")["success"]          # off grid
    assert gs.cozy_factor() < 1.0
    assert gs.decay_multipliers()["happiness"] < 1.0
    assert gs.remove_furniture(0, 1)["success"] and gs.extras.furniture["plant"] == 1
    gs.pet.location = "park"
    assert not gs.place_furniture(0, 1, "plant")["success"]


def test_furniture_from_shop_and_quests(tmp_path):
    from tests import story_script as S
    gs = fresh(tmp_path)
    S.chapter1(gs)                      # welcome quest -> family picture
    assert gs.extras.furniture.get("picture") == 1
    gs.story.unlocked.add("gens_garden")
    gs.pet.location = "gens_garden"
    gs.pet.coins = 100
    r = gs.buy_item("gens_garden", "plant")
    assert r["success"] and gs.extras.furniture.get("plant") == 1
    assert "plant" not in gs.pet.inventory


def test_layout_survives_save_and_load(tmp_path):
    gs = fresh(tmp_path)
    gs.pet.location = "home"
    gs.extras.furniture.update({"lamp": 2, "clock": 1})
    gs.place_furniture(2, 1, "lamp")
    gs.place_furniture(5, 0, "clock")
    gs.extras.fish["koi"] = {"count": 1, "best": 30}
    assert gs.save()
    g2 = GameState(save_path=gs.save_manager.path)
    assert sorted(map(tuple, g2.extras.layout)) == [(2, 1, "lamp"), (5, 0, "clock")]
    assert g2.extras.furniture == {"lamp": 1}
    assert g2.extras.fish["koi"]["best"] == 30


def test_furnish_mode_by_buttons(game):
    adopt(game)
    st = game.state
    st.extras.furniture.update({"plant": 1, "picture": 1})
    st.pet.location = "home"
    game.switch("main", fade=False)
    run(game, 3)
    game.scene.bar.focus_id("furnish")
    run(game, 2, key(pygame.K_SPACE))
    fm = game.scene.furnish
    assert fm is not None and game.scene.overlay_open
    assert fm.selected() == "picture"          # FURNITURE order: wall items first
    fm.col, fm.row = 4, 1
    run(game, 1, key(pygame.K_t))              # R: next item (plant)
    assert fm.selected() == "plant"
    run(game, 1, key(pygame.K_SPACE))          # place
    assert st.furniture_at(4, 1) == "plant"
    run(game, 1, key(pygame.K_UP))             # wall row
    run(game, 1, key(pygame.K_SPACE))          # picture is the only one left
    assert st.furniture_at(4, 0) == "picture"
    run(game, 1, key(pygame.K_SPACE))          # pick it back up
    assert st.furniture_at(4, 0) is None and st.extras.furniture.get("picture") == 1
    run(game, 2, key(pygame.K_x))              # B: done
    assert game.scene.furnish is None
    game.scene.draw(game.screen)


# ------------------------------------------------------------- more pets
def test_companions_after_the_ending(tmp_path):
    from tests import story_script as S
    gs = fresh(tmp_path)
    assert not gs.adopt_companion("Milo", 1)["success"]     # story first
    S.play_to_end(gs)
    gs.pet.coins = 77
    gs.pet.location = "park"
    first = gs.pet.name
    xp = gs.pet.bond_xp
    r = gs.adopt_companion("Milo", 1, "curious")
    assert r["success"] and gs.pet.name == "Milo" and gs.pet.trait == "curious"
    assert gs.pet.coins == 77 and gs.pet.location == "home" and gs.pet.bond_xp == 0
    assert gs.stage == "baby"
    gs.pet.coins = 90
    assert gs.switch_pet(0)["success"]
    assert gs.pet.name == first and gs.pet.bond_xp == xp and gs.pet.coins == 90
    assert [n for _, n, _, _ in gs.all_pets()] == [first, "Milo"]
    gs.adopt_companion("Milo", 1)                            # same name -> "Milo 2"
    gs.adopt_companion("Luna", 2)
    assert len(gs.all_pets()) == 4
    assert not gs.adopt_companion("Nova", 5)["success"]      # home is full
    assert gs.save()
    g2 = GameState(save_path=gs.save_manager.path)
    assert [n for _, n, _, _ in g2.all_pets()] == [n for _, n, _, _ in gs.all_pets()]
    assert len(g2.napping_pets()) == 3


def test_pets_menu_adopt_and_switch_by_buttons(game):
    from tests import story_script as S
    adopt(game)
    st = game.state
    S.play_to_end(st)
    st.story.dialogue.clear()
    st.story.ending_pending = False
    st.story.notices.clear()
    st.pet.location = "home"
    game.switch("main", fade=False)
    run(game, 3)
    _open_pause_item(game, "pets")
    m = game.scene.pets_menu
    assert m is not None
    m.index = [k for k, _ in m.options].index("adopt")
    run(game, 2, key(pygame.K_SPACE))
    run(game, 20)
    assert game.scene_name == "title" and game.scene.companion
    run(game, 1, key(pygame.K_RIGHT))          # second species
    run(game, 2, key(pygame.K_SPACE))
    assert game.scene.mode == "trait"
    run(game, 2, key(pygame.K_SPACE))
    run(game, 20)
    assert game.scene_name == "main" and len(st.extras.companions) == 1
    new_name = st.pet.name
    run(game, 3)
    game.scene.draw(game.screen)               # napping pet drawn at home
    game.scene.open_pets()
    game.scene.pets_menu.index = 1             # the napping first pet
    run(game, 2, key(pygame.K_SPACE))
    assert st.pet.name != new_name
    assert game.scene.pet.height <= 128


# ------------------------------------------------------------ hot-seat
def test_two_player_hot_seat(game):
    adopt(game)
    st = game.state
    st.story.unlocked.add("arcade")
    st.pet.needs.energy = 80
    game.switch("arcade", fade=False)
    run(game, 3)
    sc = game.scene
    run(game, 1, key(pygame.K_LSHIFT))         # X toggles 2 players
    assert sc.players == 2
    sc.index = 0
    run(game, 2, key(pygame.K_SPACE))
    assert sc.phase == "play" and sc.turn == 0
    sc.minigame.score = 30
    sc.minigame.game_over = True
    run(game, 40)
    assert sc.phase == "handoff" and sc.scores == [30]
    energy_mid = st.pet.needs.energy
    sc.draw(game.screen)
    run(game, 2, key(pygame.K_SPACE))
    assert sc.phase == "play" and sc.turn == 1
    sc.minigame.score = 50
    sc.minigame.game_over = True
    coins = st.pet.coins
    run(game, 40)
    assert sc.phase == "result" and sc.result["scores"] == [30, 50]
    assert sc.result["score"] == 50
    assert st.pet.coins > coins
    assert st.pet.needs.energy < energy_mid       # charged once, at the end
    sc.draw(game.screen)
    run(game, 1, key(pygame.K_LSHIFT))
    run(game, 2, key(pygame.K_x))
    assert sc.phase == "pick"


# ------------------------------------------------------------ migration
V1 = {"schema_version": 1, "high_scores": {"snake": 40},
      "pet": {"name": "Bubbles", "species_id": 0, "coins": 33, "location": "park",
              "needs": {"hunger": 50, "happiness": 60, "energy": 70, "cleanliness": 80},
              "home_decorated": True, "garden": [{"type": "flower", "stage": 1, "planted_time": 123.4}]}}
V2 = {"schema_version": 2, "high_scores": {}, "pet": dict(V1["pet"], bond_xp=0, cooldowns={})}


@pytest.mark.parametrize("data", [V1, V2, {"name": "Flat", "coins": 9, "species_id": 2}], ids=["v1", "v2", "v0"])
def test_old_saves_migrate_to_v4(tmp_path, data):
    p = tmp_path / "old.json"
    p.write_text(json.dumps(data))
    gs = GameState(save_path=str(p))
    assert gs.has_save
    from core.pets import TRAITS
    assert gs.pet.trait in TRAITS and gs.extras.layout == [] and gs.settings.music == 6
    assert gs.save()
    out = json.loads(p.read_text())
    assert out["schema_version"] == 4 and "extras" in out and "settings" in out
    assert out["pet"]["trait"] == gs.pet.trait


def test_v3_save_migrates_and_gets_quest_furniture(tmp_path):
    from tests import story_script as S
    gs = fresh(tmp_path)
    S.chapter1(gs)
    assert gs.save()
    data = json.loads(open(gs.save_manager.path).read())
    data["schema_version"] = 3
    for k in ("extras", "settings"):
        data.pop(k)
    for k in ("trait", "stage_seen", "mopey"):
        data["pet"].pop(k)
    open(gs.save_manager.path, "w").write(json.dumps(data))
    g2 = GameState(save_path=gs.save_manager.path)
    assert g2.has_save and g2.story.status("welcome") == "done"
    assert g2.extras.furniture.get("picture") == 1      # given for the finished quest
    assert g2.pet.trait


def test_garbage_extras_never_lose_the_pet(tmp_path):
    gs = fresh(tmp_path)
    assert gs.save()
    data = json.loads(open(gs.save_manager.path).read())
    data["extras"] = {"layout": [[1, 1, "nope"], "x", [99, 0, "lamp"]], "fish": {"koi": "big"},
                      "furniture": {"lamp": "two"}, "companions": [1, {"bad": 1}]}
    data["settings"] = "loud"
    open(gs.save_manager.path, "w").write(json.dumps(data))
    g2 = GameState(save_path=gs.save_manager.path)
    assert g2.has_save and g2.pet.name == "Mochi"
    assert g2.extras.layout == [] and g2.extras.companions == []
