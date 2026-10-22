"""Pet growth stages, personality traits and gentle-stakes moods. Pure Python."""
from __future__ import annotations

import zlib

# ----------------------------------------------------------------- growth
# (stage, first bond level, sprite scale, label)
STAGES = [
    ("baby", 1, 0.74, "Baby"),
    ("kid", 3, 0.87, "Kid"),
    ("adult", 5, 1.0, "Grown-up"),
]
STAGE_KEYS = [s[0] for s in STAGES]


def stage_for(level: int) -> str:
    cur = STAGES[0][0]
    for key, first, _scale, _label in STAGES:
        if level >= first:
            cur = key
    return cur


def stage_scale(stage: str) -> float:
    return next((s[2] for s in STAGES if s[0] == stage), 1.0)


def stage_label(stage: str) -> str:
    return next((s[3] for s in STAGES if s[0] == stage), stage.title())


GROW_DIALOGUE = {
    "kid": [("", "Whoa! {pet} grew bigger! {pet} is a Kid now."),
            ("pet", "{pet} shows off a brand-new scarf and does a little spin.")],
    "adult": [("", "Look at that! {pet} is all grown up now."),
              ("pet", "{pet} puffs up proudly. Best friends forever, right?")],
}

# ----------------------------------------------------------------- traits
TRAITS = {
    "playful": {
        "name": "Playful", "desc": "Loves games and splashing. Gets bored fast!",
        "likes": {"play", "swim"},
        "mult": {"happiness": 1.2, "energy": 1.1},
        "wishes": ["play_park", "games2"],
        "emotes": ["note", "heart", "bounce"],
    },
    "sleepy": {
        "name": "Sleepy", "desc": "Loves naps and quiet stories. Yawns a lot.",
        "likes": {"rest", "read"},
        "mult": {"energy": 1.25, "happiness": 0.9},
        "wishes": ["read", "feed3"],
        "emotes": ["zzz", "heart", "zzz"],
    },
    "picky": {
        "name": "Picky", "desc": "Fussy about food, loves being squeaky clean.",
        "likes": {"clean", "pamper"},
        "mult": {"cleanliness": 0.8, "hunger": 1.1},
        "wishes": ["clean2", "treat"],
        "emotes": ["hmph", "sparkle", "heart"],
    },
    "curious": {
        "name": "Curious", "desc": "Wants to see everything. Loves exploring!",
        "likes": {"explore", "read"},
        "mult": {"happiness": 1.1, "energy": 0.9},
        "wishes": ["explore", "swim"],
        "emotes": ["question", "sparkle", "note"],
    },
}
TRAIT_KEYS = list(TRAITS)
NO_TRAIT = {"name": "", "desc": "", "likes": set(), "mult": {}, "wishes": [],
            "emotes": ["heart", "note"]}
LIKE_BONUS = {"happiness": 6}
PICKY_FEED_PENALTY = 7      # picky pets eat a little less of plain food


def roll_trait(seed: str) -> str:
    """Deterministic pick (same name -> same trait), used for migrated saves."""
    return TRAIT_KEYS[zlib.crc32(seed.encode("utf-8")) % len(TRAIT_KEYS)]


# ----------------------------------------------------------- gentle stakes
MOPEY_AVG, MOPEY_LOW = 30.0, 15.0        # get mopey below these
PERK_AVG, PERK_LOW = 45.0, 25.0          # perk back up above these (hysteresis)


def next_mopey(was: bool, avg: float, low: float) -> bool:
    if was:
        return not (avg >= PERK_AVG and low >= PERK_LOW)
    return avg < MOPEY_AVG or low < MOPEY_LOW


def reaction(stage: str, trait: str, mood: str, mopey: bool, tick: int) -> str:
    """Idle emote to pop above the pet now and then."""
    if mopey:
        return "rain"
    if mood == "sad":
        return "sigh"
    pool = list(TRAITS.get(trait, NO_TRAIT)["emotes"])
    if stage == "baby":
        pool += ["babble", "heart"]
    elif stage == "adult":
        pool += ["star"]
    return pool[tick % len(pool)]
