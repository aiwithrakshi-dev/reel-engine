# Changelog

## v9 — 21 Nov 2026 (Magnific asset library)
- Private asset library in Drive `Editing Pack › Magnific Asset Library`: 98 licensed icons (AI, code, app, money,
  social-outline; SVG + PNG 512), 2 vectors, contact sheet, "Asset Index" Google Sheet. The account's stock download
  cap stopped the session at ~100 files.
- `tools/magnific_library.py` (build / upload / pull / index): official API downloads only, resumable manifest, stops at
  the download cap, skips AI-generated stock, ZIPs per theme into Drive. `assets/plan.json` targets ~2,240 files.
- `engine/assets.py`: `icon:<theme>/<n>`, `vector:<theme>/<n>`, `photo:<theme>/<n>` references in jobs; outline icons
  tint for dark templates. Dock tiles (temp-14/15) and scene images resolve library assets.
- Skill: "Assets" section — Drive library recommended, Magnific connector as fallback; watermark and licence rules.

## v8 — 21 Nov 2026 (9 more templates: /temp-8 … /temp-16)
- Nine new styles deconstructed frame by frame from the second reference batch (t-8 … t-15, sezz0283): Warm Cinematic,
  Peach Premium, Card Stage, Green Terminal, Cream Editorial, Kanglish Tech Split, Glass Dock, Clean White Split, Lime Polaroid.
  Code in `engine/template_styles_b.py` (mixed into the same renderer: guards, hooks, audio, QC unchanged).
- Layout helpers `fit()` (scaled A-roll + blurred room fill) and `crop_card()` (PiP, card, dome, facecam, polaroid), each
  returning the face zone of that layout; `check()` accepts it so face-clear holds in every layout.
- New transitions: warm light leak, RGB glitch, paper bend, hard cut. New components: blur-in headline words, number tiles,
  floating shortcut cards, outlined background word, slot-machine counter, stamp, count-up stat page, condensed italic words,
  uppercase caption chips, glass/dark icon dock, light-beam burst, navy labels, typed cost table, polaroid + ribbon badge + tree.
- ASR fixes before drawing: hyphen-split merge + job `glossary` (Juni → Junie, Anti -Gravity → Antigravity). Demos 2-7
  re-rendered with the corrected spellings.

## v7 — 21 Nov 2026 (7 templates, Drive delivery, memory, portable setup)
- **7 templates** selectable with `/temp-1` … `/temp-7`: house Red Kinetic + six styles deconstructed frame by frame from
  reference reels (@tahacreate, @ahmadjamilofficial1, @weblyfe, @artzenmedia, @hammadkhalid8, @marcel_grauu).
  Specs in `engine/templates.py`, renderer `engine/template_render.py` (60 fps, grade, scenes, transitions, hooks tinted
  with the template accent, per-template music + SFX mix), docs generated into `templates/`.
- **Alignment enforced while rendering:** every text/card/chip box is checked against the safe box and the face oval;
  a violation stops the render with the element and time. Bands: HEAD 280–430, FACE (nothing), CAPTION chin+24…1245.
- **Drive delivery:** `tools/reel_package.py` (video, thumbnail + 3:4 grid crop, caption.html, timeline.html with QC) and
  `tools/drive_publish.py` (Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / title; caption + timeline as Google Docs).
- **Memory:** `memory/content_log.json`, `memory/lessons.md`, generated `memory/CONTEXT.md`, `memory/drive_index.json`;
  `tools/memory.py suggest` picks the next template + an unused hook.
- **Portable:** `./setup.sh` (deps, 11 OFL fonts, model) + `tools/doctor.py`; every path via `engine/paths.py` + env vars
  (no hard-coded /home/claude paths needed).
- New skill `skill/aiwithrakshith-reel-templates/` (the /temp-N router). Demo jobs: `examples/templates_demo/`.

## v3 — 21 Nov 2026 (Day 4 "Claude & Codex in Android Studio", English)
- Instagram safe zone mandatory: x 65–960, y 270–1250 (was x 80–1000, y 160–1450). `tools/safe_zone_check.py` added.
- Responsive layout: head measured from the matte, `stack()` headline built upward from the cap, label 20 px above the
  word, auto-shrink; secondary components in one auto-width chest row (`chest_row()`, `ctile()`).
- Text follows speech: 1 frame per letter (was 2), each headline part on its own word, TLOG audit (≥ 0.25 s hold before cuts).
- Captions now on every reel (English; Kannada videos get English translated captions + Kanglish headlines).
- Official web media + licensed stock as B-roll; no AI generation; topic-matched music per video; 60 fps delivery.
- `cap_logo_fix.py` for the AI-cap white-logo artifact.
- Full details: `docs/day4-safe-zone-and-official-broll.md`, `skill/.../SKILL.md`.

## v1 — 19–21 Nov 2026 (Kling 4.0, Kannada)
- First approved build: ORIGINAL room background, DY 230 layout, kinetic device library, Black_Asphalt 129 BPM bed,
  synthesised SFX, −14 LUFS master. Timeline: `examples/kling40/render_kling40.py`.

## 21 Nov 2026 — 60 fps + samples
- `examples/day4_android_studio/render_day4_60.py`: true 60 fps render (effects keep 30-fps timing; rings, streaks,
  swooshes, push-ins and grain get in-between frames).
- README hero image, workflow flowchart, Day 4 contact sheet, compressed sample reels in `samples/`.
- `docs/WORKFLOW_GUIDE.md`: shareable step-by-step guide with the flowchart, Instagram safe zone and rules checklist.

## v4 — 21 Nov 2026: unique hooks + 60 fps mandatory
- `engine/hooks.py`: 10 hook openers (neg_flash, pixel_assemble, strip_slam, red_wipe, zoom_punch, rgb_converge,
  halftone_iris, slice_glitch, letterbox_open, shutter_blinds) + `pick_hook()`; rotation log `references/hook_log.md`.
- 60 fps HD is mandatory for every reel; the 60 fps template takes `HOOK=<name>`.
- Skill split into `references/*.md` (one per topic) by `tools/build_skill_refs.py`; SKILL.md stays the source.
- `tools/hook_preview.py` + `samples/hooks_preview_60fps.mp4`.

## v5 — 21 Nov 2026: audit + automation
- Gap audit vs 2026 Instagram research, AI auto-edit tools and the reference reels: `docs/AUDIT_2026-11-21.md`.
- `tools/script_gen.py`: transcript (EN words or KN phrase table) → edit script: hook, headlines, captions, chest row,
  cutaway spots, jump-cut devices, SFX, music bed, IG caption draft, retention/timing checks; `--interactive`.
- `engine/captions.py` (karaoke + chip, SRT, glossary, overlap guards), `engine/kannada_text.py` (Kanglish, conjunct-safe),
  `engine/ref_devices.py` (slate, news stack, face grid, badge, prompt card), hook `face_punch`.
- `tools/qc_audit.py`: one-command delivery audit → `qc_report.md`.
- SKILL v5: retention & algorithm rules, originality rule, exact AI-label rule, caption styles, reference devices.

## v6 — 21 Nov 2026: face-clear rule + Instagram rulebook + skill score
- Face-clear rule: no text, component or effect layer on his face. `engine/face_guard.py` (`protect_face`,
  `FaceZone.check`), wired into the 60 fps template. Day 4 re-rendered with effects passing behind the face.
- `references/instagram_reels_guidelines.md` (+ `docs/INSTAGRAM_REELS_GUIDELINES.md`): specs, length, safe zone,
  recommendation eligibility, text coverage, originality, music, 5-hashtag cap, AI / paid labels, privacy, posting checklist.
- SKILL v6: contradictions fixed (transition FX vs safe zone; AI A-roll vs no-AI rule), new Instagram rules.
- `docs/SKILL_SCORECARD.md`: skill scored 8.0/10 (v3 was 5.9/10) with what 10/10 needs.
