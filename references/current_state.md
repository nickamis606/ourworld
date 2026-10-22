# current_state.md - OurWorld

_Last updated 2026-10-17, round 2 (branch `improve/2026-10-17`, based on `refactor-pygame-standards`)._

## Status
Playable end-to-end on keyboard or gamepad at 640x480: adopt/continue -> care for the
pet at nine places (3x3 map) -> travel via map -> shops, garden, decorating, swim at
the pond, read at the library, paid pampering at the spa -> six arcade games that pay
coins -> autosave + resume. 56 tests pass headless.

### Places
| Map | Place | Special | Care bonus / decay |
|---|---|---|---|
| (0,0) | Home | Decorate (5 flowers) | Rest bonus |
| (1,0) | Backyard | Plant / Harvest | Clean bonus |
| (2,0) | Park | - | Play bonus |
| (0,1) | Sweetie's | Candy shop | - |
| (1,1) | Gen's Garden | Seed shop | - |
| (2,1) | Arcade | Games tile -> picker | energy decays 1.3x |
| (0,2) | Sunny Pond | Swim | Play bonus; clean decays 1.4x |
| (1,2) | Bookworm Library | Read (30 s cooldown) | Rest bonus; energy decays 0.7x |
| (2,2) | Paws & Claws Spa | Pamper (18 coins) | Clean bonus |

Adding a place: entry in `core/world.LOCATIONS` with a free `map` cell (+ optional
`PLACE_ACTIONS` entry, `LOCATION_BONUS`), a builder in `sprites/backdrops.BUILDERS`,
optional ambient branch, a `FEET` entry in `scenes/main_scene.py`, an icon if new.

### Arcade
Snake, Pet Dash, Frogger, Brick Bop, Pet Pairs, Mole Pop. All subclass
`minigames.base.MinigameBase`; register in `minigames/__init__.py` (`REGISTERED_GAMES`,
`GAME_INFO`) and add a rule in `core/rewards._RULES`.

## Run / test
```bash
python main_pygame.py               # windowed
python main_pygame.py --fullscreen  # handheld
pip install pygame pytest && python -m pytest -q
SDL_VIDEODRIVER=dummy python -m pytest -q   # headless (CI / no display)
```
Save file: `saves/savegame.json` (override with `OURWORLD_SAVE=/path`).

## Architecture
```
main_pygame.py        Game: one loop/Clock/dt, scene switching + fades, idle FPS, save on exit
core/ (NO pygame)     needs.py, pet_state.py, game_state.py (all rules), world.py (places,
                      shop stock, plants), rewards.py, roster.py, savegame.py (v2, migrations)
engine/               input.py (keys+pads -> actions), assets.py (font/text/image caches)
scenes/               base_scene, title_scene, main_scene, travel_scene, arcade_scene
ui/                   stats_bar, action_bar, map_overlay, menu, icons, common
sprites/              pet_sprite (poses, cached transforms), backdrops (cached per place +
                      ambient), fx (float text, particles, pet_pose), action_animator (props)
minigames/            base (MinigameBase), snake, pet_dash, frogger, brick_bop, pet_pairs,
                      mole_pop + registry/adapter (create, press)
tools/shrink_assets.py  asset diet
tests/                test_core.py (rules, saves), test_smoke.py (headless scene runs)
```
Rules: scenes call `GameState` methods and render the returned dicts (`success`, `msg`,
`deltas`...). Scenes never edit needs directly. Scenes consume actions
(`UP/DOWN/LEFT/RIGHT/A/B/X/Y/L/R/START/SELECT`, plus keyboard-only `HOT_*`) via
`handle_action`; raw events are only used for mouse.

## Controls
| Action | Pad | Keyboard |
|---|---|---|
| Move focus / cursor | D-pad | Arrows / WASD |
| Confirm / jump | A | Space / Z |
| Back / close | B | Esc / X / Backspace |
| Map | Select (or Up) | M / Tab |
| Pause | Start | Enter |
| Care shortcuts | - | F / P / C / R |

Miyoo Mini (Onion/MiniUI) buttons arrive as keyboard events and match the defaults.
Anbernic/other: SDL game controller mapping is used if available, else raw joystick
indices (A=0, B=1, X=2, Y=3, L=4, R=5, Select=6, Start=7). If A/B are swapped on a
device, drop `{"swap_ab": true}` into `input_map.json` next to `main_pygame.py`.

## Performance (desktop, headless, for relative comparison)
- Boot to title: ~0.04 s (was ~0.8 s for pet select alone, dominated by a Python pixel loop).
- Main scene: 0.7-1.0 ms/frame at every location; Frogger ~2.8 ms/frame.
- Brick Bop ~0.23 ms/frame, Pet Pairs ~0.45, Mole Pop ~0.12 (update+draw, desktop).
- 9 cached backdrops = ~11 MB of surfaces (640x480x4 each), built lazily on first visit.
- Process RSS ~50 MB; Python heap ~3.5 MB. Assets on disk 0.6 MB (was 6.2 MB).

## Known issues / next priorities
1. **Test on real hardware.** Verify button mapping on Miyoo Mini + one Anbernic, and
   frame time (Frogger is the heaviest scene: per-frame alpha surfaces during flashes).
2. Sound: none yet (mixer is closed on purpose). Add tiny OGG blips for actions/UI.
3. Old minigames (Snake/Pet Dash/Frogger) now share MinigameBase but still draw their
   own in-game "game over" overlays; the arcade results card is the real one.
4. Home is the only painted place; the other eight are procedural. Drop art into
   `assets/backgrounds/<place>/base.png` and add a branch in `sprites/backdrops.py`.
5. `decorations.png` is a sprite sheet that was drawn whole; it is unused now. Slice it.
6. No pet aging/evolution or day/night yet (game_design.md ideas).
7. Old docs under references/ (pygame_patterns.md) describe the pre-2026-10 scene API.
8. New-game coin rates were tuned with bots, not people: watch Brick Bop (score/15)
   and Mole Pop (score/8) payouts in real play.
9. The pause menu in minigames is on Start/B; Pet Pairs and Mole Pop only use A, so
   B-to-pause is fine, but a future game that needs B will have to change that.
