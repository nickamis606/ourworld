"""Weekly arcade challenge: one game per ISO week with a target score."""
from __future__ import annotations

from . import calendar

WEEKLY_GAMES = ["snake", "pet_dash", "frogger", "brick_bop", "pet_pairs", "mole_pop"]
TARGETS = {"snake": 60, "pet_dash": 80, "frogger": 120, "brick_bop": 200,
           "pet_pairs": 150, "mole_pop": 150}
REWARD = {"coins": 40, "sticker": "trophy"}


def challenge_for(d) -> dict:
    game = WEEKLY_GAMES[calendar.week_index(d) % len(WEEKLY_GAMES)]
    return {"week": calendar.week_id(d), "game": game, "target": TARGETS[game]}
