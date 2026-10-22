"""Seasons, calendar events and week ids from a date. Pure Python.

The date comes from GameState.clock (injectable). OURWORLD_DATE=YYYY-MM-DD
overrides it for testing/screenshots.
"""
from __future__ import annotations

import datetime
import os

SEASONS = ("spring", "summer", "fall", "winter")
SEASON_NAMES = {"spring": "Spring", "summer": "Summer", "fall": "Fall", "winter": "Winter"}

# (start month, day) .. (end month, day) inclusive; ranges may wrap the new year.
EVENTS = {
    "harvest_fair": {"name": "Harvest Fair", "start": (10, 10), "end": (10, 31),
                     "desc": "Pumpkins in the Town Square! Harvests pay double.",
                     "goal": {"event": "harvest:*", "count": 3, "text": "Harvest 3 plants during the fair"},
                     "reward": {"coins": 30, "sticker": "pumpkin"}},
    "snow_day": {"name": "Snow Day", "start": (12, 15), "end": (1, 10),
                 "desc": "Snow everywhere! Build a snowman in the Park.",
                 "goal": {"event": "place:snowman", "count": 1, "text": "Build a snowman in the Park"},
                 "reward": {"coins": 30, "sticker": "snowman"}},
    "egg_hunt": {"name": "Spring Egg Hunt", "start": (3, 25), "end": (4, 20),
                 "desc": "Painted eggs are hidden in the Park. Find five!",
                 "goal": {"event": "place:egg_hunt", "count": 5, "text": "Find 5 painted eggs"},
                 "reward": {"coins": 30, "sticker": "egg"}},
    "summer_splash": {"name": "Summer Splash", "start": (7, 1), "end": (8, 15),
                      "desc": "Pond party! Swim three times.",
                      "goal": {"event": "place:swim", "count": 3, "text": "Swim 3 times"},
                      "reward": {"coins": 30, "sticker": "sun"}},
}


def date_from(ts: float) -> datetime.date:
    env = os.environ.get("OURWORLD_DATE")
    if env:
        try:
            return datetime.date.fromisoformat(env) if hasattr(datetime.date, "fromisoformat") \
                else datetime.datetime.strptime(env, "%Y-%m-%d").date()
        except ValueError:
            pass
    return datetime.date.fromtimestamp(ts)


def season_of(d: datetime.date) -> str:
    m = d.month
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    if m in (9, 10, 11):
        return "fall"
    return "winter"


def _in_range(d, start, end) -> bool:
    md = (d.month, d.day)
    if start <= end:
        return start <= md <= end
    return md >= start or md <= end    # wraps New Year


def active_event(d: datetime.date):
    for key, ev in EVENTS.items():
        if _in_range(d, ev["start"], ev["end"]):
            return key
    return None


def event_year(d: datetime.date, key: str) -> int:
    """Events that wrap the year (snow day) count as the year they started."""
    ev = EVENTS[key]
    if ev["start"] > ev["end"] and (d.month, d.day) <= ev["end"]:
        return d.year - 1
    return d.year


def week_id(d: datetime.date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def week_index(d: datetime.date) -> int:
    y, w, _ = d.isocalendar()
    return y * 53 + w
