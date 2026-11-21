# /temp-10 — Card Stage

**Reference:** t-10 (Submagic)  ·  **Best for:** app / AI-tool reviews, "this tool just ..." launches, SaaS features  ·  **Energy:** high

## Look
Light stage: he lives inside a big rounded card on an off-white page with the brand pill top-left; the headline word appears as giant outlined purple type behind the card; for features he drops into a dome at the bottom while the UI card sits on top; key words in a purple gradient.

## Spec
| part | value |
|---|---|
| grade | sat: 1.05, contrast: 1.06, gain: (1.0, 0.98, 1.04), vignette: 0.0 |
| fonts | caption: inter:700, key: intertight:800 gradient, outline: intertight:900 outline, brand: intertight:800 |
| palette | accent: #8A3BFF, brand: #FF5A1F, page: #F7F6FA |
| headline | zone: giant outline word behind the card, anim: fade-in 0.3 s |
| captions | style: chest-line-purple-key, zone: on the card, under the chin, font_px: 42, max_words: 3, case: as spoken |
| scenes | UI card on top + speaker in a dome at the bottom |
| transitions | scale cut 8 frames |
| hook | strip_slam (purple accent) |
| pace | scene every ~3-5 s |
| music | 120-128 BPM upbeat tech house |
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
{"template": 10, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "strip_slam", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-10.json` → `samples/templates/temp-10.mp4`.
