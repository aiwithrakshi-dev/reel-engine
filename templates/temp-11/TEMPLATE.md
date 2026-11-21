# /temp-11 — Green Terminal

**Reference:** t-11 (Claude Code reel)  ·  **Best for:** money / numbers stories, dev & AI-agent tools, "I built X" breakdowns  ·  **Energy:** high

## Look
Black page with a green dot grid and glow; facecam in a green-bordered card at the bottom, graphics on top: white label + green glowing slot-machine counter or serif italic word, red rotated stamp for "not / irrelevant" beats, cream stat pages with a big red number counting up.

## Spec
| part | value |
|---|---|
| grade | sat: 0.95, contrast: 1.06, gain: (1.0, 1.0, 1.0), vignette: 0.0 |
| fonts | label: inter:800, counter: intertight:900 glow, accent: playfair-i:700, stat: intertight:900 |
| palette | accent: #36F06A, stamp: #E5322D, page: #040605, cream: #F2EEE6, stat: #E23B2E |
| headline | zone: graphics area y 280-620 above the facecam card, anim: slot-machine roll 0.45 s / stamp slam |
| captions | style: single-word, zone: y 660 between graphics and facecam, font_px: 42, case: as spoken |
| scenes | cream stat page (count-up); green-bordered image card above the facecam |
| transitions | RGB glitch 6 frames |
| hook | slice_glitch (green accent) |
| pace | graphic change every ~1.5-2 s |
| music | 130-145 BPM dark synth / hacker |
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
{"template": 11, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "slice_glitch", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-11.json` → `samples/templates/temp-11.mp4`.
