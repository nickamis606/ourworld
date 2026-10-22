#!/usr/bin/env python3
"""Asset diet: trim transparent borders and downscale PNGs to the size the
game actually draws them at. Run once on a desktop after adding art:

    python tools/shrink_assets.py

The full-resolution originals (832x1248 etc., ~6 MB total, ~4 MB RAM each
once decoded) stay in git history; the device only ever loads the small ones.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# path -> (max_width, max_height, trim)
TARGETS = {
    "assets/pets/*.png": (140, 128, True),
    "assets/backgrounds/home/base.png": (640, 480, False),
    "assets/backgrounds/home/layers/window.png": (170, 170, True),
    "assets/backgrounds/home/layers/shelf.png": (180, 150, True),
    "assets/backgrounds/home/layers/rug.png": (330, 170, True),
    "assets/backgrounds/home/layers/table.png": (170, 130, True),
    "assets/backgrounds/home/layers/pot.png": (100, 110, True),
    "assets/backgrounds/home/layers/decorations.png": (200, 300, True),
}


def shrink(path, max_w, max_h, trim):
    img = pygame.image.load(path)
    img = img.convert_alpha() if img.get_alpha() is not None or trim else img.convert()
    if trim:
        br = img.get_bounding_rect(min_alpha=8)
        if br.w and br.h:
            img = img.subsurface(br).copy()
    w, h = img.get_size()
    if not trim and (w, h) != (max_w, max_h):
        img = pygame.transform.smoothscale(img, (max_w, max_h))
    else:
        s = min(max_w / w, max_h / h, 1.0)
        if s < 1.0:
            img = pygame.transform.smoothscale(img, (max(1, round(w * s)), max(1, round(h * s))))
    before = os.path.getsize(path)
    pygame.image.save(img, path)
    print(f"{os.path.relpath(path, ROOT):50s} {w}x{h} -> {img.get_width()}x{img.get_height()}  "
          f"{before // 1024}KB -> {os.path.getsize(path) // 1024}KB")


def main():
    import glob
    pygame.init()
    pygame.display.set_mode((1, 1))
    for pattern, spec in TARGETS.items():
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            shrink(path, *spec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
