<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 9. Device library & timing (`engine/fx.py`; frame counts are 30-fps units → at 60 fps use `n * FPS // 30`)

| Device | Frames (30 fps units) | Use |
|---|---|---|
| Hook opener | 6–9 (12–18 at 60 fps) — one of the 10 hooks in §9b, never repeated within 5 reels | frame 0 |
| Big word type-on | **1 letter per frame**; newest letter 1.22× ghost → 1.06× → lock; each part starts on its own spoken word | every keyword |
| Label scatter-in | words stagger 2, snap home in 2-frame steps | small labels |
| Pixel blocks | 2–5 each, 18–42 px on a 6 px grid, reds/pinks | on the letter being revealed / dissolves |
| Neon squiggle streak | 6 (white core + #FF1A2A glow) | hides a jump cut |
| Halftone ring (dots / lines) | 5, op 0.6–0.75 (+3-fr radial blur) | hides a jump cut / reset |
| Vertical smear | 3 | hides a jump cut |
| Red light swoosh | 7 | into a cutaway |
| Cutaway entry / exit | RGB ghost 3 / magenta 1 + negative 2 (or negative 2) | screen & B-roll cutaways |
| Card / pill pop | 4 (0→62→108→100 %) | chest row, cards |
| Marker highlight | red→cyan→green, 2 per word | label emphasis |
| Hold + pixel flicker, hard cut | last 0.8 s | ending |

Budget per ~40 s: ≈ 3 streaks, 6 rings, 1 smear, 2 swooshes, 4 negative flashes. Every jump cut hidden by one.
- A new visual event every 0.3–0.5 s on a spoken word; ~75 % talking head, ~25 % cutaways.
- **Every headline fully typed ≥ 0.25 s before its scene changes** — if speech is too dense, move the cut later or
  shorten the word. `word_on()` writes `<out>.tlog.json` (start / fully typed / on-screen-until).
- End: VO end + 0.28 s final hit; reel ends VO end + 0.82 s, hard cut.
