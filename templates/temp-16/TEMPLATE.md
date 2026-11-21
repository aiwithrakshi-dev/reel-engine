# /temp-16 — Lime Polaroid

**Reference:** sezz0283 (agency reel)  ·  **Best for:** agency / founder intros, client results, case studies, service offers  ·  **Energy:** medium

## Look
Soft white-to-green page; he shrinks into a white polaroid card with a "+ name" label and a black ribbon badge; words below with a lime highlighter on key words; a tree line to lime circles; phone mockups with results; full-frame talk with lime-boxed key words.

## Spec
| part | value |
|---|---|
| grade | sat: 1.02, contrast: 1.04, gain: (1.0, 1.02, 0.98), vignette: 0.0 |
| fonts | caption: inter:600, key: inter:700 on lime box, label: inter:700, badge: inter:800 |
| palette | accent: #C8F135, lime: #C8F135, page: #F5F8F2, ink: #161616 |
| headline | zone: words under the polaroid / chest line, anim: lime box sweeps open under the key word |
| captions | style: lime-highlight-line, zone: under the card or chin, font_px: 44, max_words: 3, case: as spoken |
| scenes | polaroid card + badge + highlighted words + tree; phone mockup with a result screen |
| transitions | scale cut 8 frames |
| hook | letterbox_open (lime accent) |
| pace | card/phone switch every ~3-4 s |
| music | 95-110 BPM feel-good house |
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
{"template": 16, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "letterbox_open", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-16.json` → `samples/templates/temp-16.mp4`.
