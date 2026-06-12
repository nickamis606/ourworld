import tkinter as tk
from typing import Optional, Callable

class ActionAnimator:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.current_job: Optional[str] = None

    def cancel(self):
        if self.current_job:
            try:
                self.canvas.after_cancel(self.current_job)
            except Exception:
                pass
            self.current_job = None
        self.canvas.delete("anim_temp")

    # (All the play_ methods remain exactly the same as before)
    def play_feed(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_oval(200, 160, 240, 190, fill="#8B4513", outline="#5D3A1A", width=2, tags="anim_temp")
        self.canvas.create_oval(205, 155, 235, 175, fill="#DEB887", tags="anim_temp")
        self.current_job = self.canvas.after(400, lambda: self._feed_frame_2(on_complete))

    def _feed_frame_2(self, on_complete):
        self.canvas.itemconfig("pet", outline="#FF69B4")
        self.current_job = self.canvas.after(600, lambda: self._feed_complete(on_complete))

    def _feed_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_play(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_oval(210, 170, 235, 195, fill="#FF6347", outline="#CD5C5C", width=2, tags="anim_temp")
        self.canvas.move("pet", 0, -8)
        self.current_job = self.canvas.after(350, lambda: self._play_frame_2(on_complete))

    def _play_frame_2(self, on_complete):
        self.canvas.move("pet", 0, 8)
        self.current_job = self.canvas.after(400, lambda: self._play_complete(on_complete))

    def _play_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_clean(self, on_complete: Optional[Callable] = None):
        self.cancel()
        for x, y in [(180, 140), (195, 130), (210, 145)]:
            self.canvas.create_oval(x, y, x+18, y+18, outline="#87CEEB", width=2, tags="anim_temp")
        self.current_job = self.canvas.after(300, lambda: self._clean_frame_2(on_complete))

    def _clean_frame_2(self, on_complete):
        self.canvas.move("anim_temp", 0, -25)
        self.current_job = self.canvas.after(500, lambda: self._clean_complete(on_complete))

    def _clean_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None

    def play_rest(self, on_complete: Optional[Callable] = None):
        self.cancel()
        self.canvas.create_text(175, 95, text="Z", fill="#9370DB", font=("TkDefaultFont", 16, "bold"), tags="anim_temp")
        self.canvas.create_text(190, 85, text="z", fill="#9370DB", font=("TkDefaultFont", 12), tags="anim_temp")
        self.current_job = self.canvas.after(400, lambda: self._rest_frame_2(on_complete))

    def _rest_frame_2(self, on_complete):
        self.canvas.move("anim_temp", 0, -12)
        self.current_job = self.canvas.after(500, lambda: self._rest_complete(on_complete))

    def _rest_complete(self, on_complete):
        self.canvas.delete("anim_temp")
        if on_complete:
            on_complete()
        self.current_job = None