# current_state.md — OurWorld Project Status

## Status
Throwaway project — procedural fallback for pet sprites not existing.

## Latest Changes

2026-08-17:
- **Frogger visual + feedback + level-flow polish** (`minigames/frogger.py`) — see details below.
- Bugfix in sprites/pet_sprite.py: fixed `_center_content()` which failed with `'pygame.surface.Surface' object has no attribute 'tobytes'`. The Surface object has no `.tobytes()` method; replaced with `pygame.image.tobytes(surface, "RGBA")` which is the correct API for extracting pixel data from a pygame Surface.
- Bugfix in sprites/location_background.py: `self.assets_path` used a relative path (`assets/backgrounds`) resolved against the runtime CWD, not the module directory — causing `os.path.exists(base_path)` to fail and the code to fall back to the procedural solid fill. Fixed by resolving `assets_path` relative to `__file__`. Also fixed `draw()` where the blit call for `base_surface` was inside an `elif self.use_asset:` branch (never reached when `base_surface` was set). Added debug prints for load/draw and included `decorations` in the draw order.
- Visual polish (Phase 2): Included `decorations.png` and `pot.png` for the home location only (Option A). They are now loaded via conditional logic in the layer loop — `location == "home"` allows them through, all other locations skip them. Positioned at `(200, 180)` for decorations, `(500, 320)` for pot. Draw order updated to `[rug, table, shelf, window, pot, decorations]`. Removed debug print statements from the now-solid load/draw paths. Layer positions are still hard-coded in `_get_home_position()`.

### Frogger improvements (2026-08-17)

1. **Death feedback** — Added `death_timer` (700 ms) and `death_type` (car vs water). Frog flashes white during the timer. A colored splash ring (red for car, blue for water) expands outward. Death no longer sets `running=False` immediately — the game continues so the game-over screen is drawn.
2. **Home-fill feedback** — Each filled home pulses from its normal gold to white at 100 ms intervals for 600 ms, plus a golden outer glow ring. Frog gets a brief 300 ms flash before resetting to the bottom.
3. **Level indicator** — Moved from small top-left text to a large centered `LEVEL N` banner at the top of the screen. Lives now render as heart symbols (`♥♥♥`).
4. **Level-advance moment** — When all 5 homes are filled, a 1800 ms pause occurs with a semi-transparent dark overlay and a "LEVEL N COMPLETE!" banner. Homes glow during the pause. After the pause the level counter increments and the next level starts.
5. **Restart path** — Game-over no longer exits the minigame loop (`running` stays `True`). The game-over screen shows "GAME OVER" with "R = Try Again / ESC = Quit". Input is blocked during death-flash and level-transition to prevent accidental moves.
6. **Bug fix** — The original code incremented `self.level` inside `_try_fill_home` before the transition timer, then incremented it again when the timer fired. Now `self.level` is only incremented inside the timer handler, matching the displayed level number.

**Frogger bug fix (2026-08-18):**
- **Issue:** Losing a life (or completing a level) could return the player to the Arcade instead of continuing the run. The `_try_fill_home()` method sets `self.won = True` when all 5 homes are filled. This flag is never cleared during the level transition. `ArcadeScene.update()` checks `getattr(self.minigame, 'won', False)` and calls `_handle_minigame_end()`, which clears the minigame and returns to the Arcade — even though the player still had lives and the level transition timer was still active.
- **Fix:** Clear `self.won = False` in `_tick_feedback()` when the level transition timer fires (same place where `self.level` is incremented and the level is reset). This ensures `won` only reflects the *current* game's state, not a lingering flag from the previous completed game.
- **Death flow after fix:**
  1. Collision → `_lose_life()` decrements lives, sets `death_timer = 700ms`, splash + flash drawn
  2. If lives > 0: after 700ms timer expires, gameplay resumes, frog respawns at bottom
  3. If lives == 0: `game_over = True`, game continues drawing the Game Over screen
  4. In ArcadeScene: 1800ms delay after game_over lets player see the screen and press 'R' to retry or ESC to quit

**Open Frogger polish:**
- Sound effects for death, home fill, and level complete (would require an assets directory for Frogger).
- Home-fill could show a small frog-silhouette icon in the filled home slot (currently just the glowing ellipse).
- Score popup animation when filling a home (+100 + level×20).
- "Press any key to start" overlay for level transitions instead of auto-advance (gives player a moment to prepare).
