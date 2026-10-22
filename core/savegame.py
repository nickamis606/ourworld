"""SaveManager: atomic JSON save/load with migration. No pygame imports.

Save format v4 (v3 + "settings", personality/growth/companions/home layout;
see CHANGELOG). Older formats:
Save format v3:
    {"schema_version": 3, "saved_at": <unix time>, "high_scores": {...}, "pet": {...},
     "story": {...}}
v0 (flat pet fields), v1 (nested pet, monotonic timestamps) and v2 (no story)
still load; saves without a story keep every place they had open (free roam)
and start the story at chapter 1.
"""
import json
import os
import tempfile
import time
from typing import Dict, Optional

SAVE_SCHEMA_VERSION = 4
AUTO_SAVE_COOLDOWN = 3.0


class SaveManager:
    def __init__(self, game_state, path: str):
        self.game_state = game_state
        self.path = path
        self.high_scores: Dict[str, int] = {}
        self._last_save_mono = -1e9
        self.last_saved_mono: Optional[float] = None   # UI reads this for the "Saved" flash
        self.last_error: Optional[str] = None

    # ---------------------------------------------------------------- load
    def load(self) -> bool:
        if not os.path.exists(self.path):
            return False
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("save root is not an object")
        except (OSError, ValueError) as e:
            self._quarantine(f"unreadable: {e}")
            return False

        version = data.get("schema_version", 0)
        if not isinstance(version, int) or version > SAVE_SCHEMA_VERSION:
            # Do not overwrite a save from a newer build.
            self.last_error = f"save is v{version}, this build reads up to v{SAVE_SCHEMA_VERSION}"
            print(f"[SaveManager] {self.last_error}; starting fresh in memory")
            self.path = self.path + ".from-newer-build"
            return False

        from .pet_state import PetState
        try:
            pet_data = data if "pet" not in data else data["pet"]
            if not isinstance(pet_data, dict) or "name" not in pet_data:
                raise ValueError("missing pet data")
            self.game_state.pet = PetState.from_dict(pet_data)
            hs = data.get("high_scores") or {}
            self.high_scores = {str(k): int(v) for k, v in hs.items()
                                if isinstance(v, (int, float))}
            from .settings import Settings
            self.game_state.settings = Settings.from_dict(data.get("settings"))
            from .story import StoryState
            if isinstance(data.get("story"), dict):
                try:
                    self.game_state.story = StoryState.from_dict(data["story"])
                except Exception as e:  # noqa: BLE001 - never lose a pet over story data
                    print(f"[SaveManager] story data unreadable ({e}); keeping places open")
                    self.game_state.story = StoryState.for_existing_save(self.game_state.pet.location)
            else:
                self.game_state.story = StoryState.for_existing_save(self.game_state.pet.location)
            hook = getattr(self.game_state, "extra_load", None)
            if hook:
                hook(data, version)
        except Exception as e:  # noqa: BLE001 - any bad field means bad save
            self._quarantine(f"invalid: {e}")
            return False

        saved_at = data.get("saved_at")
        if isinstance(saved_at, (int, float)):
            away = time.time() - saved_at
            if 0 < away < 10 * 365 * 24 * 3600:
                self.game_state.apply_offline(away)
        return True

    def _quarantine(self, why: str) -> None:
        """Keep a broken save aside instead of silently overwriting it."""
        self.last_error = why
        bad = self.path + ".corrupt"
        try:
            os.replace(self.path, bad)
            print(f"[SaveManager] Save {why}; moved to {bad}, starting fresh")
        except OSError:
            print(f"[SaveManager] Save {why}; starting fresh")

    # ---------------------------------------------------------------- save
    def save(self, force: bool = False) -> bool:
        now = time.monotonic()
        if not force and now - self._last_save_mono < AUTO_SAVE_COOLDOWN:
            return False  # throttled; do NOT move the timestamp
        payload = {
            "schema_version": SAVE_SCHEMA_VERSION,
            "saved_at": time.time(),
            "high_scores": {k: int(v) for k, v in self.high_scores.items()},
            "pet": self.game_state.pet.to_dict(),
            "story": self.game_state.story.to_dict(),
            "settings": self.game_state.settings.to_dict(),
        }
        extra = getattr(self.game_state, "extra_save", None)
        if extra:
            payload.update(extra())
        directory = os.path.dirname(self.path) or "."
        tmp_path = None
        try:
            os.makedirs(directory, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", dir=directory, suffix=".tmp",
                                             delete=False, encoding="utf-8") as tmp:
                json.dump(payload, tmp, indent=1)
                tmp.flush()
                os.fsync(tmp.fileno())  # SD cards + sudden power-off
                tmp_path = tmp.name
            os.replace(tmp_path, self.path)
        except OSError as e:
            self.last_error = str(e)
            print(f"[SaveManager] Save failed: {e}")
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            return False
        self._last_save_mono = now
        self.last_saved_mono = now
        return True

    def trigger_auto_save(self) -> bool:
        return self.save(force=False)

    def delete(self) -> None:
        try:
            os.remove(self.path)
        except OSError:
            pass

    # --------------------------------------------------------- high scores
    def update_high_score(self, minigame: str, score: int) -> bool:
        key = minigame.lower()
        if score > self.high_scores.get(key, 0):
            self.high_scores[key] = int(score)
            return True
        return False

    def get_high_score(self, minigame: str) -> int:
        return self.high_scores.get(minigame.lower(), 0)

    def get_high_scores(self) -> Dict[str, int]:
        return dict(self.high_scores)
