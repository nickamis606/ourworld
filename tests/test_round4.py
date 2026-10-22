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
