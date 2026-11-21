# /temp-15 — Clean White Split

**Reference:** t-15 (all-AI-in-one-app reel)  ·  **Best for:** cost comparisons, "replace N subscriptions", tool tours  ·  **Energy:** medium

## Look
Talking head with navy label boxes and a dark pill of tool logos; for features a white UI panel slides down from the top while he shrinks into the lower half; cream cost table with a navy header, rows typed as he names them, red italic total and an arrow to a navy answer box.

## Spec
| part | value |
|---|---|
| grade | sat: 0.95, contrast: 1.08, gain: (1.0, 1.0, 1.02), vignette: 0.35 |
| fonts | label: inter:700 / playfair-i:700, caption: inter:700, key: playfair-i:700, table: inter:500-800 |
| palette | accent: #1C2340, navy: #1C2340, total: #D62F2F, panel: #FBFBFC, cream: #EFE7DA |
| headline | zone: navy label y 370 (talk) / y 755 (panel), anim: box wipes open, then text |
| captions | style: chest-line-serif-key, zone: caption band, font_px: 42, max_words: 4, case: as spoken |
| scenes | white panel slides down + image + navy label; cream cost table typed row by row |
| transitions | hard cut (panel slide is the motion) |
| hook | red_wipe (navy accent) |
| pace | row per spoken item |
| music | 95-110 BPM clean corporate / lo-fi |
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
{"template": 15, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "red_wipe", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-15.json` → `samples/templates/temp-15.mp4`.
