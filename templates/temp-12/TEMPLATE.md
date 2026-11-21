# /temp-12 — Cream Editorial

**Reference:** t-12 (OmniRoute reel)  ·  **Best for:** "free / unlimited" reveals, dev-tool deep dives, documentary tone  ·  **Energy:** medium

## Look
Cream panel across the top with condensed serif-italic caps words (spoken word in black, the big word in a coral gradient); he sits lower in his darkened room; dark pages with a terminal/image card and big white condensed italic words.

## Spec
| part | value |
|---|---|
| grade | sat: 0.88, contrast: 1.12, gain: (1.02, 0.98, 0.95), vignette: 0.5 |
| fonts | word: playfair-i:800 condensed 0.7x, big: playfair-i:800 condensed gradient |
| palette | accent: #E8603C, panel: #E7DCCF, big: ('#FFB09A', '#E8603C'), page: #111111 |
| headline | zone: cream panel y 270-640 above his head, anim: pop 0.85 -> 1.05 -> 1 |
| captions | style: one-word-condensed-italic, zone: cream panel y 575, font_px: 84, case: UPPER |
| scenes | dark page + image card + big italic word |
| transitions | blur dissolve 8 frames |
| hook | shutter_blinds (coral accent) |
| pace | word every 0.3 s, scene every ~3 s |
| music | 90-110 BPM moody electronic |
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
{"template": 12, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "shutter_blinds", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-12.json` → `samples/templates/temp-12.mp4`.
