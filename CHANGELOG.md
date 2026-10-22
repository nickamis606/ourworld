# Changelog

## [Unreleased] - 2026-10-17 (round 2) - more places, more arcade

### Added
- Three new places on a 3x3 neighborhood map (third row), each with a code-drawn
  backdrop built once and cached, a little ambient animation, and its own action:
  - **Sunny Pond** - *Swim*: +28 Clean, +12 Joy, -10 Energy, -5 Food (needs 15 energy).
    Play here gets a "Splashy bonus"; sand makes Clean decay 1.4x faster. Duck + ripples.
  - **Bookworm Library** - *Read*: +14 Joy, +6 Energy, 30 s cooldown. Rest gets a
    "Quiet-corner bonus"; energy decays 0.7x here. Lamp flicker + drifting page.
  - **Paws & Claws Spa** - *Pamper* (18 coins): +45 Clean, +20 Energy, +10 Joy.
    Clean gets a "Spa bonus". Rising steam.
- Place actions are data (`core/world.PLACE_ACTIONS`) applied by
  `GameState.can_place_action/perform_place_action` (pure Python, same result dict
  shape as care actions). Cooldowns tick in `tick()` and `apply_offline()`.
- Three new arcade games (all D-pad + A, 30 FPS, one cached background blit/frame):
  - **Brick Bop** - breakout: hold Left/Right, A launches; 50 bricks, waves, 3 lives.
  - **Pet Pairs** - 4x4 memory match of pet icons, 75 s; 25/pair + 2 per second left.
  - **Mole Pop** - 3x3 whack-a-mole, 40 s; golden moles +30, misses stun 0.4 s.
- `minigames/base.py` `MinigameBase`: shared state (running/game_over/score/held),
  action->key mapping, cached score text (`CachedFont` over `engine.assets.text`),
  HUD helper and standalone `run()`. Snake, Pet Dash and Frogger now use it.
- Arcade picker is a 3x2 cabinet grid (Left/Right +-1, Up/Down +-row); the arcade
  place shows one **Games** tile instead of a tile per game.
- 20 new tests (56 total): map grid completeness, place gating/costs/cooldowns,
  bonuses, decay multipliers, save compat for `cooldowns`, rewards for all 6 games,
  headless runs of every game, place actions via keys, map travel to the third row,
  arcade picker navigation, Brick Bop paddle follows held input.

### Changed
- Saves gain an optional `pet.cooldowns` dict. Older saves (no field) load with no
  cooldowns; junk values are dropped. Schema version unchanged (2).
- Map cards are shorter (180x112) to fit three rows on 640x480.
- Rewards: zero score still pays 0 coins / 0 joy and costs 4 energy for every game.

### Fixed
- Brick Bop could fall into an endless dead-vertical bounce; paddle hits now keep a
  minimum angle. Its background was rebuilt every frame (now cached per instance).

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
