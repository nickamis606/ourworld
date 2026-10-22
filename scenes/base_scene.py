"""BaseScene: interface every scene implements.

The controller (main_pygame.Game) is the only thing that switches scenes;
it calls on_exit() on the old scene and on_enter(**kwargs) on the new one.
"""


class BaseScene:
    low_power_ok = True  # may the controller drop to idle FPS while here?

    def __init__(self, game):
        self.game = game
        self.state = game.state

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def handle_action(self, action: str):
        pass

    def handle_event(self, event):
        """Raw events (mouse/touch). Keys and pads arrive via handle_action."""
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface):
        raise NotImplementedError

    def is_animating(self) -> bool:
        return False
