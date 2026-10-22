"""Minigame scoring -> pet rewards. No pygame imports."""

# (score divisor for happiness, happiness cap, score divisor for coins, minimum coins)
_RULES = {
    "snake": (3, 40, 2, 5),
    "pet_dash": (4, 30, 3, 5),
    "frogger": (3, 35, 2, 5),
}
ENERGY_COST = 8  # playing an arcade game is tiring


def minigame_reward(game: str, score: int) -> dict:
    """Return {'happiness', 'coins', 'energy'} for a finished run.

    A zero score still costs energy but pays nothing, so mashing
    start/quit is not a coin farm (the old code paid 15-20 coins minimum).
    """
    h_div, h_cap, c_div, c_min = _RULES.get(game, (4, 25, 3, 5))
    score = max(0, int(score))
    if score <= 0:
        return {"happiness": 0, "coins": 0, "energy": -ENERGY_COST // 2}
    return {
        "happiness": min(h_cap, max(2, score // h_div)),
        "coins": max(c_min, score // c_div),
        "energy": -ENERGY_COST,
    }
