# Active Task — Care Action Animation Polish

**Goal:** Improve the visual feedback and timing of the four care action animations (Feed, Play, Clean, Rest) to make them feel more satisfying and clear on a 640×480 handheld screen.

## Current State Analysis

The four animations live in `core/action_animator.py` with a shared 1.3s duration:
- **Feed**: Brown bowl → rising food particles → heart pops up (only appears at 60%+ progress)
- **Play**: Orange ball bounces with motion lines → impact dust
- **Clean**: Blue circles rise with sine-wave drift
- **Rest**: Four "Z" characters float up with staggered offsets

Problems identified:
1. All animations share the same 1.3s duration — no personality differentiation
2. No action-specific easing — everything uses linear progress
3. Animations are drawn centered at pet rect center — not always optimal positioning
4. Feed: heart appears late (60%) and doesn't linger — too brief
5. Play: no squash/stretch on the ball impact, motion lines are static
6. Clean: no sparkle effect, just floating circles — not "clean" enough
7. Rest: Z characters are drawn with SysFont every frame (expensive!) and have no size fade
8. No screen-scale feedback (like a subtle screen flash or button pulse)
9. No "done" tail — animations just stop at progress=1.0

## Steps

- [ ] 1. Give each action its own duration and easing curve
- [ ] 2. Fix Rest animation: cache "Z" font surfaces, add size fade
- [ ] 3. Improve Feed: extend heart visibility, add heartbeat bounce
- [ ] 4. Improve Play: add squash/stretch on ball, add motion trail
- [ ] 5. Improve Clean: add sparkle/glow on bubbles, make them pop
- [x] 6. Add subtle button pulse feedback when action started
- [ ] 7. Add a brief "done" tail to each animation (linger 0.15s at peak)
- [ ] 8. Test via xvfb-run and verify no regressions
- [ ] 9. Update current_state.md and commit
