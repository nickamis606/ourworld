import tkinter as tk
from tkinter import messagebox
import random
from .minigame_base import MinigameBase


class SnakeGame(MinigameBase):
    def __init__(self, master: tk.Tk | tk.Toplevel | None = None, on_game_end=None):
        super().__init__(master)
        self.width = 400
        self.height = 400
        self.cell_size = 20
        self.cols = self.width // self.cell_size
        self.rows = self.height // self.cell_size

        self.snake = [(self.cols // 2, self.rows // 2)]
        self.direction = (1, 0)
        self.apple = self._place_apple()
        self.score = 0
        self.speed = 150
        self.on_game_end = on_game_end

        self._create_window()
        self.master.bind("<Key>", self.on_key)

    def _create_window(self):
        if not self.master.winfo_exists():
            self.master = tk.Tk()

        self.master.title("OurWorld - Snake")
        self.canvas = tk.Canvas(
            self.master,
            width=self.width,
            height=self.height,
            bg="#111111",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.score_label = tk.Label(
            self.master,
            text=f"Score: {self.score}",
            font=("TkDefaultFont", 14)
        )
        self.score_label.pack()

        tk.Button(
            self.master,
            text="Start / Restart",
            command=self.start
        ).pack(pady=5)

    def start(self):
        self.snake = [(self.cols // 2, self.rows // 2)]
        self.direction = (1, 0)
        self.apple = self._place_apple()
        self.score = 0
        self.game_over = False
        self.running = True
        self.score_label.config(text=f"Score: {self.score}")

        self.draw()
        self._game_loop()

    def _place_apple(self):
        while True:
            pos = (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
            if pos not in self.snake:
                return pos

    def update(self):
        if not self.running or self.game_over:
            return

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows):
            self._end_game()
            return

        if new_head in self.snake:
            self._end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.apple:
            self.score += 10
            self.score_label.config(text=f"Score: {self.score}")
            self.apple = self._place_apple()
        else:
            self.snake.pop()

    def draw(self):
        if not self.canvas:
            return

        self.canvas.delete("all")

        ax, ay = self.apple
        self.canvas.create_oval(
            ax * self.cell_size, ay * self.cell_size,
            (ax + 1) * self.cell_size, (ay + 1) * self.cell_size,
            fill="#ff4444", outline="#aa0000"
        )

        for i, (x, y) in enumerate(self.snake):
            color = "#44ff44" if i == 0 else "#228b22"
            self.canvas.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill=color, outline="#003300"
            )

    def on_key(self, event: tk.Event):
        key = event.keysym.lower()

        if key in ("up", "w") and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key in ("down", "s") and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key in ("left", "a") and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key in ("right", "d") and self.direction != (-1, 0):
            self.direction = (1, 0)
        elif key == "r" and self.game_over:
            self.start()

    def _game_loop(self):
        if not self.running or self.game_over:
            return

        self.update()
        self.draw()

        if not self.game_over:
            self.master.after(self.speed, self._game_loop)

    def _end_game(self):
        self.game_over = True
        self.running = False

        if self.on_game_end:
            self.on_game_end(self.score)

        messagebox.showinfo(
            "Game Over",
            f"Score: {self.score}\n\nPress R to restart or close the window."
        )


if __name__ == "__main__":
    game = SnakeGame()
    game.master.mainloop()