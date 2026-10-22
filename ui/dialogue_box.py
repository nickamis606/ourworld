"""Story text box: speaker portrait + name tag + wrapped, typewritten text.

A reveals the whole line, then advances; B skips to the end of the line too.
Text is wrapped once per line and every rendered line is cached by assets.text.
"""
import pygame

from core.story_data import NPCS
from engine import assets
from sprites import npc_sprite
from ui.common import panel

BOX = pygame.Rect(10, 312, 620, 160)
SIZE = 21
CPS = 70          # characters per second
_portraits: dict = {}


def wrap(text, size, width):
    f = assets.font(size)
    out, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if f.size(test)[0] <= width or not cur:
            cur = test
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def portrait(npc):
    p = _portraits.get(npc)
    if p is None:
        src = npc_sprite.surface(npc)
        p = pygame.transform.smoothscale(src, (int(src.get_width() * 0.8), int(src.get_height() * 0.8)))
        _portraits[npc] = p
    return p


class DialogueBox:
    def __init__(self, lines, pet_name="Pet", pet_image=None, on_done=None):
        self.lines = [l for l in lines if l and l[1]]
        self.index = 0
        self.shown = 0.0
        self.t = 0.0
        self.pet_name = pet_name
        self.pet_image = pet_image
        self.on_done = on_done
        self.done = not self.lines
        self._wrapped = {}

    # -------------------------------------------------------------- flow
    @property
    def current(self):
        return self.lines[self.index] if not self.done else ("", "")

    def _full(self):
        return self.shown >= len(self.current[1])

    def advance(self):
        if self.done:
            return
        if not self._full():
            self.shown = len(self.current[1])
            return
        self.index += 1
        self.shown = 0.0
        if self.index >= len(self.lines):
            self.done = True
            if self.on_done:
                self.on_done()

    def handle_action(self, a):
        if a in ("A", "START"):
            self.advance()
        elif a == "B":
            if not self._full():
                self.shown = len(self.current[1])
            else:
                self.advance()

    def update(self, dt):
        self.t += dt
        if not self.done:
            self.shown = min(len(self.current[1]), self.shown + CPS * dt)

    # -------------------------------------------------------------- draw
    def _lines_for(self, i, width):
        w = self._wrapped.get(i)
        if w is None:
            w = wrap(self.lines[i][1], SIZE, width)
            self._wrapped[i] = w
        return w

    def draw(self, surf):
        if self.done:
            return
        speaker, text = self.current
        surf.blit(panel(BOX.size, (255, 250, 240, 245), 16, (120, 90, 70)), BOX.topleft)
        tx = BOX.x + 20
        if speaker in NPCS:
            img = portrait(speaker)
            surf.blit(img, img.get_rect(midbottom=(BOX.x + 60, BOX.bottom - 10)))
            tx = BOX.x + 122
            name, col = NPCS[speaker]["name"], NPCS[speaker]["color"]
        elif speaker == "pet":
            if self.pet_image is not None:
                surf.blit(self.pet_image, self.pet_image.get_rect(midbottom=(BOX.x + 60, BOX.bottom - 10)))
                tx = BOX.x + 122
            name, col = self.pet_name, (240, 140, 170)
        else:
            name, col = "", None
        if name:
            tag = assets.text(name, 20, (255, 255, 255), bold=True)
            r = pygame.Rect(0, 0, tag.get_width() + 22, 28)
            r.bottomleft = (tx - 6, BOX.y + 6)
            pygame.draw.rect(surf, tuple(max(0, c - 60) for c in col), r, border_radius=10)
            surf.blit(tag, tag.get_rect(center=r.center))
        width = BOX.right - tx - 24
        left = int(self.shown)
        y = BOX.y + 22
        for line in self._lines_for(self.index, width):
            part = line[:max(0, left)]
            left -= len(line) + 1
            if part == line:
                surf.blit(assets.text(part, SIZE, (60, 50, 50)), (tx, y))
            elif part:   # typing: render uncached so partial strings don't flood the cache
                surf.blit(assets.font(SIZE).render(part, True, (60, 50, 50)), (tx, y))
            y += 28
        if self._full() and int(self.t * 3) % 2 == 0:
            arrow = assets.text("A >", 18, (150, 110, 90), bold=True)
            surf.blit(arrow, (BOX.right - arrow.get_width() - 14, BOX.bottom - 26))
        page = assets.text(f"{self.index + 1}/{len(self.lines)}", 15, (170, 150, 140))
        surf.blit(page, (BOX.right - page.get_width() - 14, BOX.y + 8))
