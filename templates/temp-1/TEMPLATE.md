# /temp-1 — Red Kinetic (house style)

**Reference:** Rakshith: Kling 4.0 + Day 4 reels  ·  **Best for:** AI tool launches, news drops, hype explainers  ·  **Energy:** high

## Look
His room kept and dimmed; giant red 3D italic words type on BEHIND his head; neon streaks, halftone rings, pixel blocks, red-framed screen cutaways, chest-row tiles.

## Spec
| part | value |
|---|---|
| grade | sat: 0.8, contrast: 1.0, gain: (1.0, 1.0, 1.0), vignette: 0.0, blur_bg: 3 |
| fonts | head: intertight-i:900, label: intertight-i:400, caption: intertight-i:700 |
| palette | accent: #E3121B, text: #FFFFFF, bg: #000000 |
| headline | zone: above-cap, behind head (matte), anim: type-on 1 letter/frame, 3D extrude, pixel blocks |
| captions | style: karaoke, zone: caption band, font_px: 44, case: as spoken |
| scenes | red-framed screen window on blurred backdrop; chest-row tiles/pills |
| transitions | neon streak, halftone ring, smear, swoosh, negative/ghost cut |
| hook | any unused hook (red accent) |
| pace | event every 0.3-0.5 s; cut every ~3 s |
| music | 120-135 BPM dark trap / 808 |
| renderer | `examples/day4_android_studio/render_day4_60.py` |

## Alignment grid (all templates)
```
x: 0 ─ 65 ───────────── safe box ───────────── 960 ─ 1080   (6 columns, 20 px gutter, centre line x = 512)
y 0-270      Instagram top UI          → nothing readable
y 280-430    HEAD band                 → labels / headlines (above the cap)
y cap..chin  FACE band                 → nothing on the face oval (FaceZone + 24 px margin)
y chin+40..1245 CAPTION band           → captions, pills, chips (max 30 chars per line)
y 1250-1920  Instagram bottom UI       → nothing readable
```
Safe box (65, 270, 960, 1250). Every readable box is checked by the renderer (`Reel.check`): leaving the box or touching the face stops the render.
Pace: captions appear on the word's start frame (never early); one visual event every 0.3-0.6 s; every scene change has an SFX.

## Job file
```json
{"template": 1, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "pixel_assemble", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-1.json` → `samples/templates/temp-1.mp4`.
