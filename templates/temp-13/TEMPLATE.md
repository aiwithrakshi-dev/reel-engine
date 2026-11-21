# /temp-13 — Kanglish Tech Split

**Reference:** t-13 (Hinglish tech reel)  ·  **Best for:** KANNADA / Kanglish tool news, app walkthroughs, "free alternative" reels  ·  **Energy:** high

## Look
Dark-teal room; a navy panel across the top with a small label and a neon glowing keyword; uppercase romanised captions in blue highlight chips; full-screen app windows on a navy grid that bend in like paper.

## Spec
| part | value |
|---|---|
| grade | sat: 0.9, contrast: 1.1, gain: (0.92, 1.0, 1.06), vignette: 0.4 |
| fonts | label: inter:700, neon: intertight:900 glow, chip: inter:800 |
| palette | accent: #8A5CFF, chip: #4A4AE8, panel: #0A0E1C, grid: #1A2240 |
| headline | zone: navy panel y 285-655, anim: pop + violet glow |
| captions | style: uppercase-chip, zone: under the chin, font_px: 32, max_words: 4, case: UPPER |
| scenes | navy grid page + app window card + title |
| transitions | paper bend 12 frames |
| hook | zoom_punch (violet accent) |
| pace | chip every phrase, window every ~2-3 s |
| music | 110-125 BPM Indian pop-tech / upbeat |
| renderer | `engine/template_render.py` |

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
{"template": 13, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "zoom_punch", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-13.json` → `samples/templates/temp-13.mp4`.
