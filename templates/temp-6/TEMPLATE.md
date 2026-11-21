# /temp-6 — Orange Explainer

**Reference:** @hammadkhalid8  ·  **Best for:** business, money, book lessons, frameworks  ·  **Energy:** high

## Look
Dark studio talking head; two-line bold italic captions below the chin, the key line in a gold gradient; full-screen orange grid-paper scenes with white swooshes, white serif titles, tweet/quote cards, image cards and icon tiles.

## Spec
| part | value |
|---|---|
| grade | sat: 0.95, contrast: 1.12, gain: (1.03, 1.0, 0.95), vignette: 0.4 |
| fonts | caption: montserrat-i:900, title: playfair:800, card: inter:600 |
| palette | accent: #FFC93C, accent2: #F29E12, text: #FFFFFF, bg: #FC8F00, grid: #FFA42E |
| headline | zone: captions carry the headline (two-line block), anim: words pop in as spoken |
| captions | style: two-line-gold, zone: caption band (chin+24 .. 1245): gold 62 px + white 38 px, font_px: 62, case: UPPER |
| scenes | orange grid page + serif title + quote/tweet card; orange grid page + image card |
| transitions | orange swoosh wipe 8 frames |
| hook | strip_slam (orange accent) |
| pace | scene every ~3 s |
| music | 100-118 BPM confident hip-hop / groove |
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
{"template": 6, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "strip_slam", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-6.json` → `samples/templates/temp-6.mp4`.
