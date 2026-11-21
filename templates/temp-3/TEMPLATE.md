# /temp-3 — Editorial Script

**Reference:** @ahmadjamilofficial1  ·  **Best for:** mindset, creativity, storytelling, motivational takes  ·  **Energy:** medium

## Look
Moody low-key grade; headline above the head mixes a heavy white sans word with an overlapping red script/serif-italic word; B-roll inside big rounded cards on black; colour-wash flashes between scenes.

## Spec
| part | value |
|---|---|
| grade | sat: 0.9, contrast: 1.15, gain: (1.04, 0.97, 0.92), lift: (0, 0, 0), vignette: 0.55 |
| fonts | label: inter:800, head: intertight:900, script: playfair-i:700, caption: inter:700 |
| palette | accent: #E8132E, text: #FFFFFF, bg: #070707 |
| headline | zone: HEAD band above the cap, anim: word pop 1.15->1.0, script word wipes in left->right |
| captions | style: single-word, zone: chest band, font_px: 40, case: as spoken |
| scenes | rounded B-roll card (radius 40) on black with headline overlapping its top |
| transitions | colour wash (red->orange->yellow) 5 frames, hard cut on beat |
| hook | face_punch (red accent) |
| pace | cut every ~1.7 s (fastest template) |
| music | 85-105 BPM moody lo-fi / cinematic |
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
{"template": 3, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "face_punch", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-3.json` → `samples/templates/temp-3.mp4`.
