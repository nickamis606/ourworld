"""Headless smoke tests: boot every scene and run frames through the real loop."""
import os

import pygame
import pytest


@pytest.fixture
def game(tmp_path):
    os.environ["OURWORLD_SAVE"] = str(tmp_path / "save.json")
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    import main_pygame
    g = main_pygame.Game(screen=screen)
    yield g
    os.environ.pop("OURWORLD_SAVE", None)


def key(k):
    return [pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0),
            pygame.event.Event(pygame.KEYUP, key=k, mod=0, unicode="", scancode=0)]


def run(g, n, events=()):
    g.step(1 / 30, list(events))
    for _ in range(n):
        g.step(1 / 30, [])


def adopt(g):
    run(g, 2, key(pygame.K_SPACE))
    run(g, 20)
    assert g.scene_name == "main"


def test_boot_and_adopt(game):
    run(game, 10)
    assert game.scene_name == "title"
    adopt(game)
    assert game.state.has_save and os.path.exists(game.state.save_manager.path)


def test_every_location_draws(game):
    adopt(game)
    from core.world import LOCATIONS
    for loc in LOCATIONS:
        game.state.pet.location = loc
        game.scene.on_enter()
        run(game, 30)
        for _ in range(len(game.scene.bar.items) + 1):
            run(game, 1, key(pygame.K_RIGHT))


def test_care_action_via_keys_changes_needs(game):
    adopt(game)
    game.state.pet.needs.hunger = 30
    game.scene.bar.focus_id("feed")
    run(game, 60, key(pygame.K_SPACE))
    assert game.state.pet.needs.hunger > 50


def test_map_travel_to_park(game):
    adopt(game)
    run(game, 2, key(pygame.K_m))
    assert game.scene.map.open
    run(game, 2, key(pygame.K_RIGHT))
    run(game, 2, key(pygame.K_RIGHT))
    run(game, 2, key(pygame.K_SPACE))
    run(game, 20)
    assert game.scene_name == "travel"
    run(game, 80)
    assert game.scene_name == "main" and game.state.pet.location == "park"


@pytest.mark.parametrize("which", ["snake", "pet_dash", "frogger", "brick_bop", "pet_pairs", "mole_pop"])
def test_minigames_run_and_pay_out(game, which):
    adopt(game)
    game.state.pet.needs.energy = 80
    game.switch("arcade", game=which)
    run(game, 20)
    assert game.scene_name == "arcade" and game.scene.phase == "play"
    for i in range(300):
        run(game, 0, key([pygame.K_UP, pygame.K_SPACE, pygame.K_LEFT, pygame.K_DOWN][i % 4]))
        if game.scene.phase == "result":
            break
    if game.scene.phase != "result":   # survived 10 s: end the run from the pause menu
        run(game, 1, key(pygame.K_RETURN))
        run(game, 1, key(pygame.K_DOWN))
        run(game, 1, key(pygame.K_SPACE))
    assert game.scene.phase == "result"
    run(game, 2, key(pygame.K_ESCAPE))
    run(game, 2, key(pygame.K_ESCAPE))
    run(game, 20)
    assert game.scene_name == "main"


@pytest.mark.parametrize("place,action", [("pond", "swim"), ("library", "read"), ("spa", "pamper")])
def test_new_place_action_via_keys(game, place, action):
    adopt(game)
    st = game.state
    st.pet.location = place
    st.pet.coins = 100
    st.pet.needs.cleanliness = 30
    st.pet.needs.happiness = 30
    st.pet.needs.energy = 60
    game.scene.on_enter(arrived=True)
    run(game, 5)
    before = st.pet.care_count
    assert game.scene.bar.focus_id("place:" + action) is not False
    assert game.scene.bar.current.id == "place:" + action
    run(game, 60, key(pygame.K_SPACE))
    assert st.pet.care_count == before + 1
    from sprites import backdrops
    assert backdrops.get(place).get_size() == (640, 480)
    assert backdrops.get(place) is backdrops.get(place)  # built once, cached


def test_map_travel_to_pond_and_back_row(game):
    adopt(game)
    run(game, 2, key(pygame.K_m))
    run(game, 2, key(pygame.K_DOWN))
    run(game, 2, key(pygame.K_DOWN))
    assert game.scene.map.selected == "pond"
    run(game, 2, key(pygame.K_SPACE))
    run(game, 100)
    assert game.scene_name == "main" and game.state.pet.location == "pond"
    run(game, 2, key(pygame.K_m))
    run(game, 2, key(pygame.K_DOWN))   # wraps to the top row
    assert game.scene.map.selected == "home"


def test_arcade_place_opens_picker_with_all_games(game):
    adopt(game)
    from minigames import GAME_INFO
    game.state.pet.location = "arcade"
    game.state.pet.needs.energy = 80
    game.scene.on_enter()
    game.scene.bar.focus_id("games")
    run(game, 2, key(pygame.K_SPACE))
    run(game, 30)
    assert game.scene_name == "arcade" and game.scene.phase == "pick"
    seen = set()
    from scenes.arcade_scene import ORDER
    for _ in range(len(GAME_INFO)):
        seen.add(ORDER[game.scene.index])
        run(game, 1, key(pygame.K_RIGHT))
    assert seen == set(GAME_INFO) and len(seen) >= 6
    run(game, 1, key(pygame.K_DOWN))
    assert game.scene.index == 3


def test_brick_bop_paddle_follows_held_input(game):
    adopt(game)
    game.state.pet.needs.energy = 80
    game.switch("arcade", game="brick_bop")
    run(game, 20)
    mg = game.scene.minigame
    x0 = mg.paddle_x
    game.step(1 / 30, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)])
    run(game, 15)
    assert mg.paddle_x > x0
    game.step(1 / 30, [pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT, mod=0, unicode="", scancode=0)])


def test_gamepad_hat_and_buttons(game):
    adopt(game)
    start = game.scene.bar.focus
    run(game, 1, [pygame.event.Event(pygame.JOYHATMOTION, value=(1, 0), joy=0, instance_id=99, hat=0),
                  pygame.event.Event(pygame.JOYHATMOTION, value=(0, 0), joy=0, instance_id=99, hat=0)])
    assert game.scene.bar.focus == (start + 1) % len(game.scene.bar.items)
    game.state.pet.needs.hunger = 30
    game.scene.bar.focus_id("feed")
    run(game, 40, [pygame.event.Event(pygame.JOYBUTTONDOWN, button=0, joy=0, instance_id=99),
                   pygame.event.Event(pygame.JOYBUTTONUP, button=0, joy=0, instance_id=99)])
    assert game.state.pet.needs.hunger > 50


def test_pause_and_quit_saves(game):
    adopt(game)
    run(game, 2, key(pygame.K_RETURN))
    assert game.scene.pause is not None
    for _ in range(3):
        run(game, 1, key(pygame.K_DOWN))
    run(game, 1, key(pygame.K_SPACE))
    assert not game.running


def test_continue_skips_select(tmp_path):
    os.environ["OURWORLD_SAVE"] = str(tmp_path / "save.json")
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    import main_pygame
    g = main_pygame.Game(screen=screen)
    adopt(g)
    g.state.save()
    g2 = main_pygame.Game(screen=screen)
    assert g2.scene_name == "title" and g2.scene.mode == "menu"
    run(g2, 2, key(pygame.K_SPACE))
    run(g2, 20)
    assert g2.scene_name == "main" and g2.state.pet.name == g.state.pet.name
    os.environ.pop("OURWORLD_SAVE", None)
