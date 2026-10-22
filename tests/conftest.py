import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Seasons/calendar events follow the real date; pin a quiet day (summer, no event)
# so tests don't change behavior around holidays. Tests that need a season or an
# event set OURWORLD_DATE themselves (monkeypatch).
os.environ.setdefault("OURWORLD_DATE", "2026-06-10")
