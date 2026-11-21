# /temp-9 — Peach Premium

**Reference:** t-9 (video-editor tips)  ·  **Best for:** "3 ways / 3 tips" lists, creative-tool tips, premium tutorials  ·  **Energy:** medium

## Look
Neon room kept; white heavy chest captions with the key word in orange serif italic; orange 3D number tiles pop in on a spoken list; soft peach gradient pages with a sliding title and floating white shortcut cards; image card with an orange caps kicker.

## Spec
| part | value |
|---|---|
| grade | sat: 1.08, contrast: 1.08, gain: (1.0, 0.98, 1.02), vignette: 0.3 |
| fonts | caption: inter:800, key: playfair-i:700, tile: playfair:800, title: inter:700 |
| palette | accent: #F26B1D, key: #FF7A2E, page: #FFF6F0, tile: ('#F26A21', '#962E06') |
| headline | zone: captions carry the keyword; peach page titles, anim: slide-in from right with blur |
| captions | style: chest-line-serif-key, zone: caption band, font_px: 46, max_words: 3, case: as spoken |
| scenes | peach page + floating shortcut cards; peach page + kicker + image card |
| transitions | soft blur dissolve 10 frames |
| hook | pixel_assemble (orange accent) |
| pace | scene every ~3-4 s |
| music | 100-115 BPM bright pop / chill house |
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
{"template": 9, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "pixel_assemble", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-9.json` → `samples/templates/temp-9.mp4`.
