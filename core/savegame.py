"""
SaveManager — Robust save/load for full OurWorld game state.

Responsibilities:
- Serialize / deserialize complete game state (PetState + needs + location).
- Track high scores per minigame (snake, pet_dash, frogger).
- Atomic writes (temp file + rename) to prevent corruption.
- Auto-save on important events via callback hooks.
- Schema versioning field for future migrations.
- Graceful degradation on corrupt/missing saves (start fresh).
"""

import json
import os
import time
import tempfile
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from .game_state import GameState

# Schema version — bump when save format changes incompatibly.
SAVE_SCHEMA_VERSION = 1

# Minimum interval between auto-saves (seconds) to avoid excessive I/O.
AUTO_SAVE_COOLDOWN = 3.0

# Save directory (relative to project root, not core/).
_SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
_SAVE_PATH = os.path.join(_SAVE_DIR, "savegame.json")
_SAVE_TMP = os.path.join(_SAVE_DIR, "savegame.json.tmp")


class SaveManager:
    """Manages saving and loading of game state with high scores."""

    def __init__(self, game_state: "GameState"):
        self.game_state = game_state
        # Auto-save hook: set this to a callable that triggers an in-game save.
        # Called with no args; should be non-blocking or safe to call from
        # the game loop.
        self.on_save: Optional[Callable] = None

        # High scores tracked here; synced to save file on save().
        self.high_scores: Dict[str, int] = {}

        # Auto-save throttling.
        self._last_save_time = 0.0

        # Save indicator: (start_monotonic_time, width, height) or None.
        self._save_indicator: Optional[tuple] = None

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def load(self) -> bool:
        """Load game state from disk. Returns True if a valid save was found."""
        if not os.path.exists(_SAVE_PATH):
            return False

        try:
            with open(_SAVE_PATH, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[SaveManager] Corrupt save file, starting fresh: {e}")
            return False

        # Schema version check (future-proofing).
        file_version = data.get("schema_version", 0)
        if file_version > SAVE_SCHEMA_VERSION:
            print(f"[SaveManager] Save format v{file_version} newer than expected v{SAVE_SCHEMA_VERSION}, starting fresh.")
            return False

        try:
            # Schema v0 (pre-SaveManager): flat PetState fields at top level.
            if "pet" not in data and "name" in data:
                # Legacy format — restore fields directly.
                from .pet_state import PetState, Needs
                legacy = data
                needs = Needs(**legacy.get("needs", {}))
                self.game_state.pet = PetState(
                    name=legacy.get("name", "Pixel"),
                    creature_type=legacy.get("creature_type", "fluff"),
                    needs=needs,
                    location=legacy.get("location", "home"),
                    days_alive=legacy.get("days_alive", 0),
                    coins=legacy.get("coins", 1000),
                    inventory=legacy.get("inventory", {}),
                    garden=legacy.get("garden", []),
                    home_decorated=legacy.get("home_decorated", False),
                    home_decoration_time=legacy.get("home_decoration_time", 0.0),
                )
                self._last_save_time = time.monotonic()
                return True

            # Schema v1+: nested "pet" object.
            pet_data = data.get("pet")
            if not pet_data:
                print("[SaveManager] Save file missing 'pet' data.")
                return False

            from .pet_state import PetState
            restored_pet = PetState.from_dict(pet_data)
            self.game_state.pet = restored_pet

            # Restore high scores if present.
            hs = data.get("high_scores", {})
            self.high_scores = {k: int(v) for k, v in hs.items()}

            # Restore last-saved timestamp.
            self._last_save_time = data.get("last_save_time", time.monotonic())

            return True
        except Exception as e:
            print(f"[SaveManager] Error during load: {e}")
            return False

    def save(self) -> bool:
        """Save game state + high scores to disk (atomic). Returns True on success."""
        now = time.monotonic()
        # Throttle auto-saves.
        if now - self._last_save_time < AUTO_SAVE_COOLDOWN:
            # Still update the timestamp so future saves are throttled correctly.
            self._last_save_time = now
            return False  # skipped, not an error.

        try:
            os.makedirs(_SAVE_DIR, exist_ok=True)

            payload = {
                "schema_version": SAVE_SCHEMA_VERSION,
                "last_save_time": now,
                "high_scores": {k: int(v) for k, v in self.high_scores.items()},
                "pet": self.game_state.pet.to_dict(),
            }

            # Atomic write: write to .tmp, then rename.
            with tempfile.NamedTemporaryFile(
                mode="w", dir=_SAVE_DIR, suffix=".tmp", delete=False
            ) as tmp:
                json.dump(payload, tmp, indent=2)
                tmp_path = tmp.name

            os.replace(tmp_path, _SAVE_PATH)

            self._last_save_time = now
            self._save_indicator = (now, 550, 440)  # bottom-right corner

            # Notify caller hook (if set) — e.g. play a subtle sound.
            if self.on_save:
                try:
                    self.on_save()
                except Exception:
                    pass

            return True
        except Exception as e:
            # Clean up tmp file on failure.
            try:
                os.unlink(_SAVE_PATH + ".tmp")
            except OSError:
                pass
            print(f"[SaveManager] Save failed: {e}")
            return False

    def trigger_auto_save(self) -> bool:
        """Call this from game-loop-adjacent code to auto-save if cooldown permits.
        Returns True if a save was actually written, False if throttled."""
        return self.save()

    # ------------------------------------------------------------------
    #  High scores
    # ------------------------------------------------------------------

    def update_high_score(self, minigame: str, score: int) -> bool:
        """Record a new high score for *minigame*. Returns True if the score improved the record."""
        key = minigame.lower()
        current = self.high_scores.get(key, 0)
        if score > current:
            self.high_scores[key] = score
            return True
        return False

    def get_high_score(self, minigame: str) -> int:
        """Return the high score for *minigame* (0 if none)."""
        return self.high_scores.get(minigame.lower(), 0)

    def get_high_scores(self) -> Dict[str, int]:
        """Return a copy of all high scores."""
        return dict(self.high_scores)

    # ------------------------------------------------------------------
    #  Convenience
    # ------------------------------------------------------------------

    def last_save_time(self) -> float:
        """Return the monotonic time of the last successful save."""
        return self._last_save_time

    def time_since_save(self) -> float:
        """Return seconds since last save (0 if never saved)."""
        return time.monotonic() - self._last_save_time

    # ------------------------------------------------------------------
    #  Save indicator
    # ------------------------------------------------------------------

    def get_save_indicator(self, surface: "pygame.Surface") -> Optional[tuple]:
        """Return (alpha, x, y) for a save-flash indicator, or None if expired.

        alpha fades from 200 → 0 over 1.5 seconds.
        Returns the tuple to the caller for rendering.
        """
        if self._save_indicator is None:
            return None
        start, x, y = self._save_indicator
        elapsed = time.monotonic() - start
        if elapsed >= 1.5:
            self._save_indicator = None
            return None
        # Fade: 200 alpha at 0s → 0 at 1.5s
        alpha = max(0, int(200 * (1 - elapsed / 1.5)))
        return (alpha, x, y)
