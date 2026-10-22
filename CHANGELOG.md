# Changelog

## [Unreleased] - 2026-10-17 - "make it actually play" pass (branch `improve/2026-10-17`)

Based on `refactor-pygame-standards` (the newest work; `main` is ~100 commits behind).

### Fixed (game-breaking)
- Care actions did nothing: the Pygame scenes only played an animation and never
  called `GameState.perform_care_action`. Feed/Play/Clean/Rest now change needs.
- Needs never decayed, plants never grew, decorations never expired: nothing
  called `GameState.tick`. The loop now ticks the simulation every frame with dt.
- Garden and decoration timers used `time.monotonic()` stamps saved to disk, which
  are meaningless after a reboot (plants froze forever). Now stored as elapsed seconds.
- Quit-save could be silently skipped by the 3 s autosave throttle (and the throttle
  moved its own timestamp when skipping). Quit and manual saves are forced.
- The chosen pet wasn't saved; every launch forced pet select and renamed the pet.
- Non-home locations drew on a transparent surface, so the top half showed stale
  pixels from the previous frame or location.
- Pet Dash physics were per-frame and tuned for 60 FPS but run at 30: half speed.
- Frogger log riding rounded the frog to the grid every frame, so it either stuck
  or outran the log and drowned.
- Startup scanned every pet PNG pixel-by-pixel in Python (6 x 1 MP) and loaded the
  home pot PNG from disk every frame.

### Added
- Unified input (`engine/input.py`): keyboard, SDL game controllers and raw
  joysticks (hat/axis/buttons) map to D-pad/A/B/X/Y/L/R/Start/Select, with
  auto-repeat. Defaults match Miyoo Mini key events; `input_map.json` overrides.
  The whole game is playable with D-pad + A/B/Start/Select; mouse still works.
- Title screen with Continue / New pet (asks twice before replacing a pet).
- Scene controller with fade transitions and a short, skippable travel walk.
- Location identity: painted Home plus procedural Backyard (fence, garden bed),
  Park (pond, bench, butterflies), Sweetie's (striped shop, candy jars), Gen's
  Garden (greenhouse, seed rack), Arcade (neon, cabinets). Cached, one blit/frame.
- Per-location action bar (shops, planting, harvest, decorate, games) with a
  description line for the focused tile, toasts, and on-screen button hints.
- Care feel: pet squash/stretch/hop/wiggle/sink poses, floating +/- need popups,
  particle bursts, tweened meters, low-need blink, "wants" thought bubble, mood tag.
- Arcade: cabinet picker with best scores, in-game pause, results card with
  coins/joy/energy and new-best callout, retry.
- Map: 3x2 grid of live location thumbnails with "you are here" pin.
- Game rules: refusals when a need is full, Park/Home/Backyard bonuses, energy
  cost for arcade games, harvest pays coins, decorations slow joy decay,
  gentle offline catch-up (never starves the pet).
- Idle FPS drop (30 -> 12) after 20 s without input when nothing is animating.
- `tools/shrink_assets.py` asset diet: assets 6.2 MB -> 0.6 MB.
- pytest suite (36 tests) incl. headless smoke runs of every scene.

### Removed
- Tkinter prototype files, `main_pygame_RETIRED.py`, tracked `__pycache__`.
- Old per-widget UI classes (ActionButtons, ShopUI, ContextActions, ArcadePanel,
  LocationBackground), replaced by `ui/action_bar.py` and `sprites/backdrops.py`.
