# Changelog

## [Unreleased] - 2026-10-17 (round 4) - "do it all"

### Added
- **Sound and music.** `tools/make_audio.py` synthesizes 9 chiptune loops (home, town,
  shop, arcade, calm, woods, festival, night, winter) and 17 sound effects as 8-bit mono
  11 kHz WAVs (~1 MB, deterministic, nothing copyrighted). `engine/audio.py` picks a loop
  per place, time of day, season and festival and plays SFX for actions, coins, quests,
  stickers, level-ups, dialogue and the UI. It never crashes: if the mixer can't open,
  files are missing, or `OURWORLD_NOSOUND=1` is set, every call is a no-op.
- **Settings** (Pause > Settings): music volume, sound-effect volume, mute.
  **Parent settings** sit behind a 2-second hold of A: a play-time reminder
  (off/15/30/45/60 min, shown as a gentle story-style dialogue) and "slow needs"
  (needs drop at half speed). Saved in the save file.
- **Photo mode:** Pause > Take a photo, or hold L+R. Saves a HUD-free PNG to
  `photos/` next to the game (`OURWORLD_PHOTOS` overrides), with a flash and a click.
- **Quit** in the pause menu ("Quit game", saves first) and on the title screen,
  for handhelds without a keyboard. **Knulli/Batocera launcher**
  `tools/knulli/OurWorld.pygame` + install notes in the README.
- **Growth stages:** baby (bond Lv 1-2), kid (3-4), grown-up (5+). The sprite grows and
  gets a sprout / scarf / crown, with a short celebration the first time.
- **Personalities:** Playful, Sleepy, Picky, Curious (pick one or "Surprise me!" when
  adopting). Liked actions give extra joy and bond, needs drift differently, picky pets
  eat a little less of plain food, and one favorite wish is always in the Daily Wishes.
  Idle emote bubbles depend on personality, stage and mood. Old saves get a stable trait
  rolled from the pet's name.
- **Gentle stakes:** when needs stay low the pet gets mopey: it droops, shows a rain
  cloud, and the place looks a little gray. Care perks it back up (with a bond bonus).
  Nothing is ever lost and nothing bad happens.
- **Seasons and calendar events** (`core/calendar.py`, `OURWORLD_DATE=YYYY-MM-DD` to
  test): fall/winter/spring/summer tints, props baked into the cached backdrops, and
  light falling leaves/snow/petals outdoors. Events: Harvest Fair (Oct 10-31: double
  harvest coins, pumpkins and bunting in the Town Square), Snow Day (Dec 15-Jan 10:
  build a snowman in the Park; it stays there), Spring Egg Hunt (Mar 25-Apr 20: find 5
  eggs), Summer Splash (Jul 1-Aug 15: swim 3 times). Each one has a goal in the
  Journal and gives coins, a sticker and a furniture prize.
- **Fishing at Sunny Pond** (Fish tile): time the cast, wait for the bite, press A, then
  hold Left/Right to keep the fish in your green zone. 5 casts per trip, 11 fish
  (night-only Moonfish, winter Icefish, summer Sunny Perch, a rare Golden Koi, and an Old
  Boot). The Journal has a new **Fish** tab. Catch 6 kinds to earn the Ace Angler sticker
  and a Fish Bowl.
- **Weekly Challenge:** each ISO week one arcade game has a target score (banner in the
  picker plus a WEEKLY ribbon on the cabinet). Beat it for 40 coins and the Weekly Champ
  sticker (and an Arcade Trophy the first time).
- **2-player hot-seat** in the arcade: press X in the picker. Player 1 plays, then a
  "pass the console" card, then Player 2 plays, then both scores are compared. Rewards
  are paid once, for the better score.
- **Home decorating:** Furnish tile at Home. An 8x3 grid (wall row + 2 floor rows),
  D-pad cursor, L/R picks an item, A places or picks up, B finishes. There are 16
  code-drawn pieces from shops (Sweetie's and Gen's now sell some), quest rewards,
  events, fishing and the weekly challenge. Each placed piece makes Home a bit cozier
  (joy drops slower there). The layout is saved.
- **More pets after the ending:** Pause > Pets... adopts up to 3 more friends and switches
  who you're playing with. Coins, items, garden and furniture are shared. Napping pets
  sleep at Home and don't get hungry.

### Changed
- Save schema **v4**: adds a `settings` block and an `extras` block (events, fish book,
  weekly, furniture, layout, companions), plus `pet.trait/stage_seen/mopey`. v0-v3 saves
  load. Pre-v4 saves get the furniture for quests they already finished. Bad extras data
  falls back to defaults and never costs the pet.
- Backdrop tints now compose time of day x season x mopey and are still cached
  (LRU of 3).
- New-pet flow: species -> personality. The pause menu has Resume, Journal, Settings,
  Take a photo, Save now, (Pets...), New pet..., Quit game.

### Tests
- 127 tests (was 75): audio no-op paths, settings round-trip and the parent gate, the
  reminder, photos, Quit, launcher syntax, Python 3.7 parse of every file, growth,
  traits, mopey, seasons/events, fishing (core, minigame, by buttons), weekly,
  furniture, companions, hot-seat, and v0/v1/v2/v3 -> v4 migration. Tests pin
  `OURWORLD_DATE=2026-06-10` in conftest so holidays don't change results.

## [Unreleased] - 2026-10-17 (round 3) - a story and a reason to play

### Added
- **Story: "The Lights of Willowby."** Five chapters, 9 main quests + 2 side quests,
  an ending scene and a post-game. All rules in `core/story.py`, all content in
  `core/story_data.py` (pure Python, no pygame).
- **8 townsfolk** with code-drawn sprites and short dialogue: Mayor Maple (tortoise),
  Sweetie (bunny), Gen (hedgehog), Pixel Pete (raccoon), Captain Quack (duck),
  Olive (owl), Coco (cat), Fern (fox). They stand in their places with "!" (new quest)
  or "*" (come back) markers; Talk tile or Y to chat.
- **Quests** with steps driven by real play: care actions (optionally at a certain
  place), shop buys, planting, harvesting, decorating, travel, arcade games with a
  minimum score, place actions, plus bond/sticker conditions. Quests are offered by
  talking, tracked on a one-line HUD objective, and turned in to the giver for coins,
  items, stickers and **Sparks**.
- **Progression:** a new pet starts with Home, Backyard, Park and Town Square; each
  chapter opens more of the map (shops -> Arcade + Pond -> Library + Spa + Woods ->
  Lantern Hill). Locked map cards are dimmed with a padlock.
- **Bond levels** (1-8, "New Friends" to "Forever Friends"): XP from caring, place
  actions, games and quests. The final quest needs Bond level 4.
- **Stickers:** 19 code-drawn stickers. Quest rewards, plus 7 hidden in Willow Woods (Explore).
- **Journal** (X / Shift / I, or Pause -> Journal): Story tab (chapter, Sparks,
  quest list with steps), Sticker book, Friends (townsfolk, met/helped, places).
- **Daily Wishes** (from chapter 3, and the main post-game loop): 3 small tasks per
  calendar day, picked from a pool by date. 15 coins each, bonus + sticker for all 3.
- **New places:** Town Square (the Mayor; looks gray at first, wakes up as Sparks
  come in, festival bunting + lit windows after the ending), Willow Woods (Explore:
  find stickers/coins, 20 s cooldown), Lantern Hill (Light the Wish Lantern). Map is
  now 3x4.
- **Day/night:** evening and night tints baked into cached backdrop copies (LRU of 3),
  stars outdoors. Zero per-frame cost. `OURWORLD_HOUR` overrides the clock.
- Ending scene: lantern lit, fireworks, thank-you roll with your pet's name and stats.
- 19 new tests (75 total): story data consistency, quest gating by place/acceptance,
  gifts, unlocks, a full core playthrough to the ending, side quest, explore finds,
  daily-wish rotation/rewards, save v3 round trip, v2 -> v3 migration, garbage
  story data, and headless smoke runs: chapter 1 played entirely by buttons, a
  scripted run through the ending scene, journal tabs, every place at night.

### Changed
- Save schema v3 adds a `story` block and `pet.bond_xp`. v0/v1/v2 saves still load:
  a save without a story keeps every place it already had open ("free roam"), starts
  the story at chapter 1 and plays the intro once. Bad story data never costs the pet.
- `GameState` emits story events from every action; `change_location` refuses locked places.
- Pause menu gains Journal; keyboard adds I (X) and Y (Y).

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
