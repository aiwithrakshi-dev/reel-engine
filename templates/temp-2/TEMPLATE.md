# /temp-2 — Minimal Cinematic

**Reference:** @tahacreate  ·  **Best for:** calm tutorials, design/process explainers, "how to" talks  ·  **Energy:** calm

## Look
Cool teal grade with soft vignette; small clean white words appear one by one on the chest band; hook on a blurred abstract frame; white explainer pages with black type and a growing tree diagram; accent words in serif italic; soft blur dissolves.

## Spec
| part | value |
|---|---|
| grade | sat: 0.72, contrast: 1.08, gain: (0.86, 1.0, 1.02), lift: (4, 10, 12), vignette: 0.45 |
| fonts | caption: inter:600, accent: playfair-i:600, title: inter:700, sub: inter:500 |
| palette | accent: #FFFFFF, text: #FFFFFF, bg: #FDFDFD, ink: #111111 |
| headline | zone: none on talk (keywords become larger caption words), anim: blur-in fade 6 frames |
| captions | style: minimal-words, zone: chest band (chin+70), font_px: 44, max_words: 3, case: as spoken, keyword: Playfair italic 76 px |
| scenes | abstract blurred hook page; white explainer page: title + sub + tree diagram; white page + rounded image card |
| transitions | blur dissolve 8 frames |
| hook | letterbox_open (white accent) |
| pace | scene every ~4 s, word every 0.3 s |
| music | 70-95 BPM cinematic pulse / soft piano |
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
{"template": 2, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "letterbox_open", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-2.json` → `samples/templates/temp-2.mp4`.
