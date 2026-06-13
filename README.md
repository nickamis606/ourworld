# OurWorld

A cozy hybrid of Tamagotchi and a simplified The Sims — care for a cute virtual pet living in a small neighborhood.

**Current Status:** Two prototypes available — Tkinter (original) and Pygame (new, recommended for handheld targets).

This project is developed using the persistent **OurWorld skill**, which maintains the full game design, current implementation state, and iteration workflow.

## Available Versions

### Pygame Version (Recommended)
- Modern renderer targeting handheld devices (Miyoo Mini+, Anbernic, etc.)
- Custom pet roster with 6 distinct characters (Bubbles, Milo, Luna, Sprout, Pip, Nova)
- Pet selection screen at launch
- Thin top stats bar, map system, Snake minigame
- Clean architecture reusing `core/` logic

**Run it:**
```bash
git clone https://github.com/nickamis606/ourworld.git
cd ourworld
python main_pygame.py
```

### Tkinter Version (Legacy)
- Original desktop prototype
```bash
python main.py
```

## Project Vision
- Phase 5 (current): Pygame prototype with custom pets + selection screen
- Future: Polish, gamepad support, and port to Raspberry Pi Pico + ST7789

We are building this incrementally with clean architecture.

## Getting Started with Development

Just say "OurWorld" in chat and the skill will load the current design + state automatically.

---

Built with care as a long-term cozy game project.