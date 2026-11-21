# /temp-4 — Listicle Chapters

**Reference:** @weblyfe  ·  **Best for:** "N tips/steps/tools" lists, book or course summaries  ·  **Energy:** medium

## Look
Clean daylight talking head; white rounded pill captions with word-by-word reveal (spoken words black, next words grey); torn-paper title banner on the hook; full-screen gradient chapter cards with "TIP #n" in mono, a serif uppercase title typing on and a floating image card; big gold numbers.

## Spec
| part | value |
|---|---|
| grade | sat: 1.0, contrast: 1.04, gain: (1.0, 1.0, 1.03), vignette: 0.15 |
| fonts | caption: montserrat:700, mono: spacemono-b, title: playfair:800, number: playfair:900 |
| palette | accent: #F4B73F, text: #111111, pill: #FFFFFF, chapters: [('#6CA8DB', '#18385F'), ('#6969D7', '#171760'), ('#D96B93', '#601831'), ('#71D0E1', '#1F5966'), ('#CB6ED2', '#571A5B'), ('#A7C6B5', '#3A4A42')] |
| headline | zone: torn banner y 270-560 on the hook; chapter cards full screen, anim: letter type-on |
| captions | style: pill-reveal, zone: caption band (y 1150-1230), font_px: 36, max_words: 5, case: as spoken |
| scenes | torn-paper banner; gradient chapter card: TIP #n + serif title + image card; gold number at top |
| transitions | whip slide 6 frames |
| hook | shutter_blinds (chapter colour) |
| pace | chapter every ~8-10 s |
| music | 100-118 BPM upbeat house / groove |
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
{"template": 4, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "shutter_blinds", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-4.json` → `samples/templates/temp-4.mp4`.
