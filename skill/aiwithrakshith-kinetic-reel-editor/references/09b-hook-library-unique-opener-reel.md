<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 9b. Hook library — a unique opener for every reel (`engine/hooks.py`)

The first 0.2–0.3 s decides the scroll-stop, so no two recent reels may open the same way.

| Hook | Frames @60 | Energy | Look | SFX |
|---|---|---|---|---|
| `neg_flash` | 12 | high | negative frame + cyan→red blocks, scale-in 92→100 % | impact + glitch burst |
| `pixel_assemble` | 12 | high | giant red mosaic (144→12 px) resolves into the frame | digital crunch + impact |
| `strip_slam` | 18 | high | 5 horizontal strips slam in from alternate sides, red edges | 5 fast slams + sub hit |
| `red_wipe` | 16 | medium | diagonal red light band sweeps and reveals the frame | whoosh + impact |
| `zoom_punch` | 14 | high | white pop, 135 % → 98 % → 100 % zoom-blur punch with RGB split | reverse whoosh into punch |
| `rgb_converge` | 12 | medium | R/G/B channels fly in from 90 px offsets and lock, scanlines fade | glitch zap + soft hit |
| `halftone_iris` | 16 | calm | iris opens from his face through a red halftone dot ring | riser tail + boom |
| `slice_glitch` | 14 | high | horizontal slices displaced, cyan/red tints, settle in 7 steps | data glitch + impact |
| `letterbox_open` | 14 | calm | black bars part from the face line, red edge lines | cinematic hit + sub |
| `shutter_blinds` | 18 | medium | 12 vertical blinds snap open from the centre outwards | shutter clicks + pop |

Rules:
- Read `references/hook_log.md` first. Never use a hook from the last 5 reels; never the same energy hook 3 times in a row.
  The log lives in the private GitHub repo `rakshithgowdams/aiwithrakshith-reel-engine` (skill/…/references/hook_log.md).
  As of 21 Nov 2026 the Kling 4.0 and Day 4 reels both used `neg_flash`, so it is blocked for the next reels.
- Match energy to the topic (news/launch → high, tutorial → medium, story → calm); `pick_hook(energy, recent)` does it.
- The first headline still types on its first spoken word; the hook only frames the opening.
- Set it with `HOOK=<name>` when rendering; pair the SFX from the table; add the row to `hook_log.md` on delivery
  (and push it to the repo).
- Preview all hooks on the new reel's own frames with `tools/hook_preview.py` when choosing.
- New hooks may be added to `engine/hooks.py` (same style: red/pink/cyan palette, stepped or punchy, ≤ 0.3 s, inside the
  frame logic, no AI generation); add them to this table and the log.
