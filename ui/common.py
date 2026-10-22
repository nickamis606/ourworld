"""Shared UI drawing helpers (pygame)."""
import pygame

from engine import assets

INK = (40, 36, 52)
PANEL = (255, 250, 240)
PANEL_EDGE = (120, 90, 70)
FOCUS = (255, 196, 40)
_panels: dict = {}


def panel(size, color=(255, 250, 240, 235), radius=12, edge=(120, 90, 70)) -> pygame.Surface:
    """Cached translucent rounded panel."""
    key = (size, color, radius, edge)
    s = _panels.get(key)
    if s is None:
        s = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
        if edge:
            pygame.draw.rect(s, edge, s.get_rect(), 2, border_radius=radius)
        _panels[key] = s
    return s


def draw_rounded_rect(surface, rect, color, radius=8, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def draw_text_centered(surface, text, size, color, center, bold=False):
    t = assets.text(text, size, color, bold)
    surface.blit(t, t.get_rect(center=center))


def draw_progress_bar(surface, rect, value, max_value=100.0, bg_color=(80, 70, 80),
                      fill_color=(100, 200, 100), border_radius=4):
    pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
    ratio = max(0.0, min(1.0, value / max_value)) if max_value else 0
    w = int(rect.width * ratio)
    if w > 0:
        pygame.draw.rect(surface, fill_color, (rect.x, rect.y, w, rect.height), border_radius=border_radius)


def hint_bar(surface, items, y=462):
    """Draw a row of [button] label hints, centred, e.g. [("A", "Choose"), ("B", "Back")]."""
    surfs = []
    for btn, label in items:
        b = assets.text(btn, 18, (255, 255, 255), bold=True)
        l = assets.text(label, 18, (250, 246, 236))
        surfs.append((b, l))
    total = sum(b.get_width() + l.get_width() + 30 for b, l in surfs)
    x = (surface.get_width() - total) // 2
    bg = panel((total + 16, 22), (30, 26, 40, 170), 10, None)
    surface.blit(bg, (x - 8, y - 4))
    for b, l in surfs:
        pill = pygame.Rect(x, y - 2, b.get_width() + 10, 18)
        pygame.draw.rect(surface, (90, 80, 120), pill, border_radius=8)
        surface.blit(b, (x + 5, y))
        x += pill.width + 4
        surface.blit(l, (x, y))
        x += l.get_width() + 16
