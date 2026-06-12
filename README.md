# OurWorld

A cozy hybrid of Tamagotchi and a simplified The Sims — care for a cute virtual pet living in a small neighborhood.

**Current Status:** Phase 0 skeleton (fully working Tkinter prototype).

This project is developed using the persistent **OurWorld skill**, which maintains the full game design, current implementation state, safe Tkinter patterns, and efficient iteration workflow.

## How to Run the Desktop Prototype

1. Clone this repo:
   ```bash
   git clone https://github.com/nickamis606/ourworld.git
   cd ourworld
   ```
2. Make sure you have Python 3 (with Tkinter, which is included by default on most installs).
3. Run:
   ```bash
   python main.py
   ```

The pet (Pixel) has four needs that decay over real time. Use the big buttons to Feed, Play, Clean, or Rest. The simple Canvas pet updates its mood automatically. Close the window to auto-save your progress.

## What This Phase 0 Includes

- Pure Python game logic (`Needs`, `PetState`, `GameState`)
- Real-time need decay using `after()` loops (no blocking sleeps)
- Safe Tkinter patterns (bound methods, single `refresh_ui()`, Canvas with tags)
- Basic persistence (JSON save/load)
- Cute (if primitive) pet drawing that reflects mood

## Project Vision

- Phase 1: Animated care actions on the Canvas
- Phase 2: Map / neighborhood exploration
- Phase 3: Arcade with Snake minigame
- Later: Full polish + port to Raspberry Pi Pico + ST7789 color screen

We are building this incrementally and safely, following the detailed roadmap and anti-regression rules in the OurWorld skill.

## Getting Started with Development

If you're continuing work on this project, just say "OurWorld" in chat and the skill will load the current design + state automatically.

---

Built with care as a long-term cozy game project. Version control + clean architecture from day one.