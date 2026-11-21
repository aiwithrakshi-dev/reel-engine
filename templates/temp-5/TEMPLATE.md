# /temp-5 — Bold Yellow Creator

**Reference:** @artzenmedia  ·  **Best for:** creator tips, tool walkthroughs, Canva/app tutorials  ·  **Energy:** high

## Look
Warm golden-hour grade; huge condensed yellow headline with a small caps label above the head; one white condensed word at a time on the chest; screen recordings on a white grid page; 3D phone on a purple grid with an iMessage bubble; glowing gradient comment CTA.

## Spec
| part | value |
|---|---|
| grade | sat: 1.08, contrast: 1.1, gain: (1.08, 1.0, 0.86), vignette: 0.35 |
| fonts | label: anton, head: anton, caption: anton, bubble: inter:600 |
| palette | accent: #F7E733, text: #FFFFFF, grid_bg: #FCFCFC, purple: ('#2A2F8F', '#05040F'), bubble: #1E8BFF, cta: ('#22E1FF', '#8E2BFF') |
| headline | zone: HEAD band above the cap, anim: letters drop in with motion blur + yellow glow |
| captions | style: single-word-condensed, zone: chest band, font_px: 60, case: UPPER |
| scenes | white grid page + screenshot card (slow push); purple grid + phone mockup + iMessage bubble |
| transitions | zoom-blur push 6 frames |
| hook | zoom_punch (yellow accent) |
| pace | scene every ~5 s |
| music | 120-130 BPM bright electronic / future bass |
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
{"template": 5, "aroll": "aroll_tight30.mp4", "dy": 60, "duration": 15.5,
 "face": {"cap_top": 505, "chin": 1100, "x0": 330, "x1": 750}, "words": "words_reel.json",
 "headlines": [{"label": "claude and codex inside", "big": "ANDROID STUDIO", "label_t": 0.0, "big_t": 2.26}],
 "scenes": [{"t0": 2.15, "t1": 6.12, "title": "...", "image": "shot.png"}], "hook": "zoom_punch", "vo": "vo.wav", "music": "bed.mp3"}
```
Demo: `examples/templates_demo/jobs/temp-5.json` → `samples/templates/temp-5.mp4`.
