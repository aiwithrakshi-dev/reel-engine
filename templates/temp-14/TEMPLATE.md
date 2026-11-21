# /temp-14 — Glass Dock

**Reference:** t-14 (Hinglish AI-tools reel)  ·  **Best for:** "N free AI tools" roundups, app recommendations, creator tool stacks  ·  **Energy:** high

## Look
Warm amber grade; a frosted glass dock on the chest where app icons pop in one by one; big yellow gradient word with a small white line above it; dark page where a folder tile shoots coloured light beams and icons; UI card in the top half with him below.

## Spec
| part | value |
|---|---|
| grade | sat: 1.05, contrast: 1.08, gain: (1.12, 1.0, 0.8), vignette: 0.4 |
| fonts | big: intertight:900 gradient, small: inter:600, caption: inter:600 |
| palette | accent: #F5B70F, big: ('#FFEA5C', '#F2A20A'), page: #14161C |
| headline | zone: caption band (small line + big yellow word), anim: pop 0.8 -> 1.06 -> 1 |
| captions | style: chest-line-yellow-key, zone: caption band, font_px: 38, max_words: 4, case: as spoken |
| scenes | dark page + light-beam burst; UI card top half + speaker below |
| transitions | zoom-blur 8 frames |
| hook | halftone_iris (amber accent) |
| pace | icon every spoken name, scene every ~3 s |
| music | 100-115 BPM Indian indie / lo-fi |
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
{"template": 14, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "halftone_iris", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-14.json` → `samples/templates/temp-14.mp4`.
