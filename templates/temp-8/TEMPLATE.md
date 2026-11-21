# /temp-8 — Warm Cinematic

**Reference:** t-8 (Amazon-seller explainer)  ·  **Best for:** expert explainers, "most people never see this" insights, calm authority  ·  **Energy:** medium

## Look
Warm golden grade; headline words blur in one by one at the top-left, the key word in an orange gradient; punch-in cuts (1.14x) on every second headline; small lowercase word captions under the chin; dark checklist page with typed check items and a rounded live picture-in-picture of him; warm light-leak flash transitions.

## Spec
| part | value |
|---|---|
| grade | sat: 1.04, contrast: 1.08, gain: (1.1, 1.0, 0.84), vignette: 0.45 |
| fonts | head: inter:600, key: inter:700 gradient, caption: inter:600, checklist: inter:500 |
| palette | accent: #F0782A, key: ('#FFD36A', '#F0782A'), text: #FFFFFF, page: #1D1D1F |
| headline | zone: HEAD band, left-aligned x 92, anim: word-by-word blur-in 0.18 s |
| captions | style: single-word-lowercase, zone: under the chin (punch-in aware), font_px: 36, case: lower |
| scenes | dark checklist page + live PiP card; image card + live PiP |
| transitions | warm light-leak flash 12 frames, punch-in cut |
| hook | rgb_converge (orange accent) |
| pace | headline every ~2-3 s, punch-in on alternate headlines |
| music | 85-100 BPM warm lo-fi / soft house |
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
{"template": 8, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "rgb_converge", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-8.json` → `samples/templates/temp-8.mp4`.
