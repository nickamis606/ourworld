# Active Task — Save/Load System for Full Game State

**Goal:** Implement robust JSON-based save/load for complete game state (PetState + needs + location + high scores) with auto-save on important events.

## Steps
- [x] DONE: 1. Fix circular import between `core/game_state.py` and `core/savegame.py` — use TYPE_CHECKING guard + string forward reference
- [x] DONE: 2. Add `to_dict()`/`from_dict()` round-trip verification for PetState + Needs — verified JSON serializable
- [x] DONE: 3. Extend `SaveManager.load()` to restore `location` and high scores from file — done; also added legacy format (v0) migration
- [x] DONE: 4. Implement `SaveManager.save()` with atomic write — already done, verified temp+rename works
- [x] DONE: 5. Wire auto-save triggers: on action performed, location changed, minigame end, window close
- [x] DONE: 6. Wire auto-save into `arcade_scene.py` (`_handle_minigame_end`) — update high scores, trigger save
- [x] DONE: 7. Add save indicator to UI (subtle "💾 Saved" flash that fades)
- [x] DONE: 8. Test: unit tests for PetState round-trip, SaveManager save/load, v0 migration, high scores, auto-save cooldown, save indicator timing, corrupt/missing file handling — all 9 tests pass
- [x] DONE: Update `references/current_state.md` and commit

## Notes / Blockers
- Auto-save triggers to wire:
  - `GameState.perform_care_action()` → call `trigger_auto_save()` after successful action
  - `GameState.change_location()` → call `trigger_auto_save()` after location change
  - `ArcadeScene._handle_minigame_end()` → update high scores via `SaveManager.update_high_score()`, then trigger auto-save
  - `OurWorldPygame.run()` → already has `self.game_state.save()` on quit
- `SAVE_COOLDOWN = 3.0s` prevents spam
- High scores synced to disk on every save() call
