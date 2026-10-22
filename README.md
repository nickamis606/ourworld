# OurWorld

A cozy hybrid of Tamagotchi and a simplified The Sims — care for a cute virtual pet living in a small neighborhood.

**The story:** you and your pet move to Willowby, a town that went sleepy and gray when its
Wish Lantern went dark. Help six townsfolk, earn six Sparks, and light the lantern for the
Festival of Lights. After the ending, Daily Wishes keep the town busy.

**Current Status:** Pygame build for 640x480 Linux handhelds (Miyoo Mini, Anbernic RG). The old Tkinter prototype lives in git history.

This project is developed using the persistent **OurWorld skill**, which maintains the full game design, current implementation state, and iteration workflow.

## Run it

```bash
git clone https://github.com/nickamis606/ourworld.git
cd ourworld
pip install pygame
python main_pygame.py               # add --fullscreen on a handheld
```

Controls: D-pad/arrows move, A/Space confirms, B/Esc goes back, Select/M opens the
map, X/Shift/I opens the Journal, Y/Alt talks to whoever is here, Start/Enter pauses. Full table and device notes: `references/current_state.md`.

Tests: `pip install pytest && python -m pytest -q` (headless-safe).

## Project Vision
- Phase 5 (current): Pygame prototype with custom pets + selection screen
- Next: on-device testing, sound, more painted locations

We are building this incrementally with clean architecture.

## Getting Started with Development

Just say "OurWorld" in chat and the skill will load the current design + state automatically.

---

Built with care as a long-term cozy game project.