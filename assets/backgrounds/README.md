# Background Assets Structure

This folder contains visual assets for scene backgrounds.

## Recommended Structure

```
assets/backgrounds/
├── home/
│   ├── base.png                 # Main background image
│   └── layers/                  # Optional extra decoration layers
├── park/
│   ├── base.png
│   └── layers/
├── backyard/
│   ├── base.png
│   └── layers/
├── sweeties_candy_shop/
│   ├── base.png
│   └── layers/
├── gens_garden/
│   ├── base.png
│   └── layers/
└── shared/                      # Reusable decorative elements
    ├── tree.png
    ├── furniture.png
    └── etc.
```

## Usage

`LocationBackground` class in `sprites/location_background.py` will:
- Try to load `assets/backgrounds/{location}/base.png`
- Fall back to procedural drawing if no asset exists

This allows gradual migration from procedural to asset-based visuals without breaking the game.

## Current Status

- Foundation class created
- No base images added yet
- Procedural drawing still active as fallback
