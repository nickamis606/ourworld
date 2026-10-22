#!/usr/bin/env python3
"""OurWorld - entry point and thin scene controller.

One loop, one Clock, one dt. Input is translated to abstract actions by
engine.input.InputManager and handed to the active scene. Scene changes go
through Game.switch(), which fades out, calls on_exit/on_enter, fades in.

Run:  python main_pygame.py            (windowed 640x480)
      python main_pygame.py --fullscreen
Env:  OURWORLD_SAVE=/path/save.json    (default: saves/savegame.json)
      OURWORLD_PHOTOS=/path/dir         (default: photos/ next to this file)
      OURWORLD_NOSOUND=1                (skip the mixer entirely)
      OURWORLD_HOUR / OURWORLD_DATE     (pretend time, for testing)
"""
import time
import os
import sys

import pygame

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from core.game_state import GameState  # noqa: E402
from engine.input import InputManager  # noqa: E402

WIDTH, HEIGHT = 640, 480
FPS = 30
IDLE_FPS = 12          # after IDLE_AFTER seconds without input and nothing animating
IDLE_AFTER = 20.0
FADE = 0.22


class Game:
    def __init__(self, screen=None, save_path=None, fullscreen=False):
        pygame.init()
        from engine.audio import Audio
        self.audio = Audio()    # silently disabled if the mixer can't open
        if screen is None:
            flags = pygame.FULLSCREEN | pygame.SCALED if fullscreen else 0
            screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("OurWorld")
        pygame.mouse.set_visible(not fullscreen)
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.input = InputManager(os.path.join(ROOT, "input_map.json"))
        self.state = GameState(save_path=save_path or os.environ.get("OURWORLD_SAVE"))
        self.running = True
        self._scenes = {}
        self.scene = None
        self._pending = None      # (name, kwargs) waiting for fade-out
        self._fade = 0.0          # 0 = clear, 1 = black
        self._fade_dir = 0
        self._veil = pygame.Surface((WIDTH, HEIGHT)).convert()
        self._veil.fill((16, 12, 24))
        self._saved_flash = None
        self._photo_flash = 0.0
        self._combo_latched = False
        self.last_photo = None
        self.apply_settings()
        self.switch("title", fade=False)

    def apply_settings(self, settings=None):
        st = settings or self.state.settings
        self.audio.apply(st.music / 10.0, st.sfx / 10.0, st.muted)

    def sfx(self, name):
        self.audio.sfx(name)

    # ------------------------------------------------------------- photos
    def photo_dir(self):
        return os.environ.get("OURWORLD_PHOTOS") or os.path.join(ROOT, "photos")

    def take_photo(self):
        """Save the current scene without HUD to photos/. Returns the path or None."""
        d = self.photo_dir()
        try:
            os.makedirs(d, exist_ok=True)
            sc = self.scene
            had = getattr(sc, "hide_hud", None)
            if had is not None:
                sc.hide_hud = True
                sc.draw(self.screen)
                sc.hide_hud = had
            stamp = time.strftime("%Y%m%d_%H%M%S")
            path = os.path.join(d, f"ourworld_{stamp}.png")
            n = 1
            while os.path.exists(path):
                n += 1
                path = os.path.join(d, f"ourworld_{stamp}_{n}.png")
            pygame.image.save(self.screen, path)
        except (OSError, pygame.error) as e:
            print(f"[photo] failed: {e}")
            return None
        self.last_photo = path
        self._photo_flash = 0.25
        self.sfx("photo")
        return path

    # ------------------------------------------------------------ scenes
    def _get(self, name):
        sc = self._scenes.get(name)
        if sc is None:
            if name == "title":
                from scenes.title_scene import TitleScene as cls
            elif name == "main":
                from scenes.main_scene import MainScene as cls
            elif name == "travel":
                from scenes.travel_scene import TravelScene as cls
            elif name == "arcade":
                from scenes.arcade_scene import ArcadeScene as cls
            elif name == "ending":
                from scenes.ending_scene import EndingScene as cls
            else:
                raise KeyError(name)
            sc = self._scenes[name] = cls(self)
        return sc

    @property
    def transitioning(self):
        return self._pending is not None or self._fade_dir != 0

    def switch(self, name, fade=True, **kwargs):
        if self._pending is not None:
            return
        if not fade or self.scene is None:
            self._activate(name, kwargs)
            return
        self._pending = (name, kwargs)
        self._fade_dir = 1

    def _activate(self, name, kwargs):
        if self.scene is not None:
            self.scene.on_exit()
        self.scene = self._get(name)
        self.scene_name = name
        self.scene.on_enter(**kwargs)

    def quit(self):
        self.running = False

    # -------------------------------------------------------------- loop
    def step(self, dt, events=()):
        """One frame. Split out so tests can drive the game headlessly."""
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
                continue
            actions = self.input.process(e)
            if self.transitioning:
                continue
            for a in actions:
                self.scene.handle_action(a)
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.FINGERDOWN):
                self.scene.handle_event(e)
        for a in self.input.update(dt):
            if not self.transitioning:
                self.scene.handle_action(a)
        # photo combo: hold L + R
        held = self.input.held
        if "L" in held and "R" in held:
            if not self._combo_latched and not self.transitioning:
                self._combo_latched = True
                if self.take_photo() and hasattr(self.scene, "say"):
                    self.scene.say("Photo saved to photos/!")
        else:
            self._combo_latched = False

        if self._fade_dir:
            self._fade += self._fade_dir * dt / FADE
            if self._fade >= 1.0 and self._pending:
                self._fade, self._fade_dir = 1.0, -1
                name, kwargs = self._pending
                self._pending = None
                self._activate(name, kwargs)
            elif self._fade <= 0.0:
                self._fade, self._fade_dir = 0.0, 0

        self.scene.update(dt)
        self.scene.draw(self.screen)
        self._draw_overlays()

    def _draw_overlays(self):
        sm = self.state.save_manager
        if sm.last_saved_mono and sm.last_saved_mono != getattr(self, "_seen_save", None):
            self._seen_save = sm.last_saved_mono
            self._saved_flash = 1.2
        if (self._saved_flash and self._saved_flash > 0 and self.scene_name == "main"
                and not getattr(self.scene, "overlay_open", False)):
            from engine import assets
            t = assets.text("Saved", 16, (255, 255, 255))
            bg = pygame.Rect(0, 0, t.get_width() + 12, 18)
            bg.topright = (634, 82)
            pygame.draw.rect(self.screen, (60, 120, 80), bg, border_radius=8)
            self.screen.blit(t, (bg.x + 6, bg.y + 2))
        if self._photo_flash > 0:
            self._photo_flash -= 1 / 30
            flash = getattr(self, "_flash_surf", None)
            if flash is None:
                flash = self._flash_surf = pygame.Surface((WIDTH, HEIGHT)).convert()
                flash.fill((255, 255, 255))
            flash.set_alpha(int(200 * max(0.0, self._photo_flash) / 0.25))
            self.screen.blit(flash, (0, 0))
        if self._fade > 0:
            self._veil.set_alpha(int(255 * min(1.0, self._fade)))
            self.screen.blit(self._veil, (0, 0))

    def run(self):
        try:
            while self.running:
                idle = (self.input.idle_time > IDLE_AFTER and not self.transitioning
                        and self.scene.low_power_ok and not self.scene.is_animating())
                dt = self.clock.tick(IDLE_FPS if idle else FPS) / 1000.0
                dt = min(dt, 0.1)
                if self._saved_flash:
                    self._saved_flash -= dt
                self.step(dt, pygame.event.get())
                pygame.display.flip()
        finally:
            if self.state.has_save:
                self.state.save()
            self.audio.shutdown()
            pygame.quit()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    Game(fullscreen="--fullscreen" in argv).run()


if __name__ == "__main__":
    main()
