"""Fish of Sunny Pond. Pure data."""

# key: name, weight (how common), coins, color, size (1 = normal), pull (reel difficulty),
#      when: None | "night" | "winter" | "summer", blurb
FISH = {
    "minnow":   ("Minnow", 30, 2, (170, 190, 205), 0.6, 0.7, None, "Tiny and speedy."),
    "sunfish":  ("Sunfish", 22, 4, (240, 185, 60), 0.8, 0.9, None, "Shines like a little sun."),
    "bluegill": ("Bluegill", 18, 4, (90, 140, 215), 0.8, 1.0, None, "Has a blue chin!"),
    "goldfish": ("Goldfish", 10, 8, (250, 140, 40), 0.7, 1.1, None, "Somebody's lost pet? It looks happy here."),
    "catfish":  ("Catfish", 8, 10, (125, 112, 92), 1.25, 1.3, None, "Whiskers! But no meow."),
    "trout":    ("Rainbow Trout", 7, 12, (225, 125, 170), 1.0, 1.4, None, "All the colors of the rainbow."),
    "boot":     ("Old Boot", 6, 1, (115, 82, 60), 1.0, 0.5, None, "Not a fish. Still counts!"),
    "moonfish": ("Moonfish", 7, 15, (205, 212, 255), 1.0, 1.5, "night", "Only bites under the stars."),
    "icefish":  ("Icefish", 7, 15, (190, 232, 250), 0.9, 1.5, "winter", "Loves the cold winter water."),
    "sunny":    ("Sunny Perch", 7, 12, (250, 220, 90), 0.9, 1.3, "summer", "Comes out on hot summer days."),
    "koi":      ("Golden Koi", 2, 30, (255, 210, 60), 1.3, 1.9, None, "The pond's rare treasure!"),
}
FISH_ORDER = list(FISH)
ANGLER_SPECIES = 6           # different species for the Angler sticker
FISH_HAPPINESS = 4           # per catch
FISHING_ENERGY = 6           # one trip


def name(key):
    return FISH[key][0]


def available(period: str, season: str) -> list:
    out = []
    for k, f in FISH.items():
        when = f[6]
        if when is None or when == period or when == season:
            out.append(k)
    return out


def roll(rng, period: str, season: str, bonus: float = 0.0) -> str:
    """Pick a fish. bonus (0..1, a long cast) makes rare fish a bit likelier."""
    keys = available(period, season)
    weights = []
    for k in keys:
        w = FISH[k][1]
        if w <= 10:
            w *= 1.0 + bonus
        weights.append(w)
    x = rng.random() * sum(weights)
    for k, w in zip(keys, weights):
        x -= w
        if x <= 0:
            return k
    return keys[-1]
