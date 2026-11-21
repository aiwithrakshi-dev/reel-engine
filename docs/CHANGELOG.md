# Changelog

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
