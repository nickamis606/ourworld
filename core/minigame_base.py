from abc import ABC, abstractmethod
import tkinter as tk


class MinigameBase(ABC):
    """
    Base class for all minigames in OurWorld.
    Future minigames should inherit from this.
    """

    def __init__(self, master: tk.Tk | tk.Toplevel | None = None):
        self.master = master or tk.Tk()
        self.canvas: tk.Canvas | None = None
        self.score = 0
        self.running = False
        self.game_over = False

    @abstractmethod
    def start(self):
        """Initialize and start the game."""
        pass

    @abstractmethod
    def update(self):
        """Main game logic update (called periodically)."""
        pass

    @abstractmethod
    def draw(self):
        """Draw the current game state on the canvas."""
        pass

    @abstractmethod
    def on_key(self, event: tk.Event):
        """Handle keyboard input."""
        pass

    def end(self):
        """End the game cleanly."""
        self.running = False
        self.game_over = True