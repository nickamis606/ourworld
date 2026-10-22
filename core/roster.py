"""Pet roster (pure data)."""
PET_ROSTER = [
    {"id": 0, "name": "Bubbles", "color": (255, 182, 193), "style": "round"},
    {"id": 1, "name": "Milo", "color": (150, 200, 240), "style": "cat"},
    {"id": 2, "name": "Luna", "color": (190, 170, 230), "style": "round"},
    {"id": 3, "name": "Sprout", "color": (180, 230, 150), "style": "plant"},
    {"id": 4, "name": "Pip", "color": (255, 190, 120), "style": "round"},
    {"id": 5, "name": "Nova", "color": (140, 200, 140), "style": "star"},
]


def roster_entry(species_id: int) -> dict:
    if 0 <= species_id < len(PET_ROSTER):
        return PET_ROSTER[species_id]
    return PET_ROSTER[0]
