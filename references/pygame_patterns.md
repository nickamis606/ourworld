## 4. Scene / State Management Pattern (Updated 2026-06-19)

Use a thin controller + scene objects. Each scene owns its own sprites, UI components, and transient state.

**Critical Rule (hard-won lesson):** Scenes **must** cleanly isolate their transient UI state. Failure to do so causes bugs like:
- Map overlay staying visible when returning from Arcade
- Arcade minigame selection or running game "leaking" into main view
- Buttons or panels remaining active after scene change

### Mandatory Lifecycle Hooks

`BaseScene` provides `on_enter()` and `on_exit()`.

- **Controller MUST call them** on every switch (see `main_pygame.py` `OurWorldPygame.run()`).
- `on_exit()` in a scene should **reset all transient flags**:
  - `map_mode = False`
  - Close any open panels / dialogs
  - `minigame = None` (in ArcadeScene)
  - Stop active animations if they shouldn't persist
- `on_enter()` can re-initialize or refresh state for the visit.

**Anti-pattern (recurring bug):** Just reassigning `current_scene = NewScene(...)` without calling lifecycle hooks or resetting flags in the old scene. The old scene's `map_mode`, `show_instructions`, or minigame instance stays in memory and can draw on top later.

### Every Scene.draw() MUST Start With Full Opaque Background

```python
class MyScene(BaseScene):
    def draw(self, surface):
        surface.fill((R, G, B))   # or draw full background sprite/layer
        # then draw everything else
```

Never assume "the previous frame will be overwritten." Always clear or fully cover the screen. This is especially important when a minigame inside ArcadeScene returns early from draw().

### Recommended Controller Switch Pattern

```python
# in thin controller
if current.next_scene == "arcade":
    old = current
    current = arcade_scene
    old.on_exit()
    current.on_enter()
    old.next_scene = None
    current.next_scene = None
```

See `main_pygame.py` and `scenes/base_scene.py` for the canonical implementation.

### Files to keep in sync
- `scenes/base_scene.py` — define hooks + document their purpose
- `scenes/main_scene.py` — implement on_exit() that does `self.map_mode = False`
- `scenes/arcade_scene.py` — clean minigame state on exit/return
- `main_pygame.py` — the only place that should ever change `current_scene`

This pattern was reinforced after multiple regressions of the "map stays in background" / "arcade leaks" bug.

---

## 5. Input Handling