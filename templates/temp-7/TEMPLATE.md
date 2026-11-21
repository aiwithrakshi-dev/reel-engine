# /temp-7 — SaaS Split-Screen

**Reference:** @marcel_grauu  ·  **Best for:** product demos, SaaS / app features, before-after workflows  ·  **Energy:** medium

## Look
Split screen: product panel on top over a soft lavender page with blue glow blobs, face cam below; big blue kinetic word on the panel synced to speech; full-blue word flashes; UI cards with a blue word highlight.

## Spec
| part | value |
|---|---|
| grade | sat: 0.92, contrast: 1.05, gain: (0.98, 1.0, 1.03), vignette: 0.2 |
| fonts | word: intertight:800, ui: inter:500 |
| palette | accent: #0000FB, text: #0000FB, bg: #F6F6FC, blob: #C9C6FF |
| headline | zone: top panel y 280-700, anim: word pop 0.85->1.06->1.0 |
| captions | style: panel-kinetic-word, zone: top panel (face cam below, nothing on it), font_px: 120, case: as spoken |
| scenes | top panel UI card (image) over lavender; full-blue word flash |
| transitions | soft scale cut |
| hook | halftone_iris (blue accent) |
| pace | panel change every ~3 s |
| music | 100-115 BPM clean tech house / lo-fi |
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
{"template": 7, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "halftone_iris", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-7.json` → `samples/templates/temp-7.mp4`.
