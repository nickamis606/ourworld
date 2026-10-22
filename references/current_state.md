# current_state.md - OurWorld

_Last updated 2026-10-17, round 3 (branch `improve/2026-10-17`, based on `refactor-pygame-standards`)._

## Status
Playable end-to-end on keyboard or gamepad at 640x480, now with a story: adopt ->
intro -> five chapters of townsfolk quests that open the 3x4 map step by step ->
light the Wish Lantern -> ending -> Daily Wishes post-game. Care, garden, shops,
pond/library/spa actions, Willow Woods exploring and six arcade games all feed
quests. Autosave + resume. 75 tests pass headless.

## Story outline - "The Lights of Willowby"
Premise: Willowby glowed every autumn at the Festival of Lights when the Wish Lantern
on Lantern Hill was lit. The lantern went dark and the town got sleepy and gray. You
and your pet move in. Mayor Maple: the lantern runs on friendship. Help six friends,
get six Sparks, light the lantern.

| Ch | Title | Quests (giver: steps) | Opens |
|---|---|---|---|
| 1 | A Sleepy Town | Hello, Willowby! (auto; Mayor: feed, play, walk to Town Square) -> Laughter in the Park (Mayor: play at Park x2, nap at Home) | Sweetie's, Gen's Garden |
| 2 | Sweet and Green | A Sweet Hello (Sweetie: buy 2 treats, feed) - Sweet Spark; Green Thumbs (Gen gives 2 seeds: plant 2, harvest 2) - Bloom Spark | Arcade, Sunny Pond |
| 3 | Fun and Splash | Insert Coin (Pete: play 2 games, score 40+) - Joy Spark; Splash Day (Quack: swim x2, play on the beach) - Splash Spark | Library, Spa, Willow Woods |
| 4 | Quiet and Cozy | The Lost Storybook (Olive: find it exploring the Woods, read x2) - Wisdom Spark; Bubble Trouble (Coco gives 18 coins: pamper, bath) - Calm Spark; side: Sticker Scout (Fern: explore x3, own 8 stickers) | Lantern Hill |
| 5 | Festival of Lights | Light the Wish Lantern (Mayor: Bond Lv 4, climb Lantern Hill, Light) -> ending; side: Dress Up Your Home (decorate) | - |

Post-game: Town Square in festival dress, 3 Daily Wishes per day, sticker hunting,
high scores. Daily Wishes also start at chapter 3 so there's always something small to do.

Typical first run: ~25-40 minutes (garden growth ~2-3 min is the longest wait).

### Story systems (where things live)
- `core/story_data.py` - NPCS, CHAPTERS, QUESTS, SPARKS, STICKERS, BOND_*, DAILY_*, DIALOGUE.
  Add a quest = one QUESTS entry + `<id>_offer/_busy/_done` dialogue. Steps are
  `{"event": "kind:key", "at": place, "min_score": n, "count": n}` or `{"cond": "bond"|"stickers"|"sparks"}`.
  Event kinds: care, place, buy, plant, harvest, decorate, travel, game.
- `core/story.py` - StoryState (statuses locked -> available -> active -> ready -> done),
  `on_event`, `talk`, `turn_in`, chapter advance + unlocks, dialogue queue, notices, daily wishes, to/from dict.
- `core/game_state.py` - emits events, bond XP, `talk()`, `next_dialogue()`, `is_unlocked()`,
  explore finds, lantern gating, `today()` / `time_of_day()` (clock injectable).
- UI: `ui/dialogue_box.py` (typewriter, A/B), `ui/journal.py`, `sprites/npc_sprite.py`,
  quest tracker + NPC markers in `scenes/main_scene.py`, `scenes/ending_scene.py`,
  locked cards in `ui/map_overlay.py`, tinted/variant backdrops in `sprites/backdrops.py`.

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
| (0,3) | Willow Woods | Explore (stickers/coins, 20 s cooldown) | Fern |
| (1,3) | Town Square | Mayor Maple; changes look as the town wakes | - |
| (2,3) | Lantern Hill | Light the Wish Lantern (6 Sparks, Bond 4) | - |

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
| Journal | X | Shift / I |
| Talk to townsfolk here | Y | Alt / Y |
| Care shortcuts | - | F / P / C / R |

Miyoo Mini (Onion/MiniUI) buttons arrive as keyboard events and match the defaults.
Anbernic/other: SDL game controller mapping is used if available, else raw joystick
indices (A=0, B=1, X=2, Y=3, L=4, R=5, Select=6, Start=7). If A/B are swapped on a
device, drop `{"swap_ab": true}` into `input_map.json` next to `main_pygame.py`.

## Performance (desktop, headless, for relative comparison)
- Boot to title: ~0.04 s (was ~0.8 s for pet select alone, dominated by a Python pixel loop).
- Main scene: 0.7-1.0 ms/frame at every location; Frogger ~2.8 ms/frame.
- Brick Bop ~0.23 ms/frame, Pet Pairs ~0.45, Mole Pop ~0.12 (update+draw, desktop).
- 12 cached day backdrops (+2 story variants) = ~17 MB of surfaces, built lazily on first
  visit; tinted evening/night copies are an LRU of 3 (~3.7 MB).
- Story UI: town square + NPC + tracker 0.5 ms/frame, typing dialogue 0.4, journal 1.3,
  map 1.6 (desktop, headless). RSS ~62 MB.
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
10. Story pacing is untested with kids: watch for the garden wait in chapter 2 and the
    Bond Lv 4 gate in chapter 5 (most runs hit it naturally by chapter 3-4).
11. Dialogue is English-only and hard-wrapped by pixel width; long names (>12 chars)
    may wrap more. No voice/sound.
12. Old saves get "free roam" (all old places open) and still see the intro; the story
    still opens Willow Woods and Lantern Hill in order.
13. Daily Wishes use the device clock; a handheld with no RTC (clock resets on boot)
    will reroll wishes per boot date. Harmless but worth knowing.
