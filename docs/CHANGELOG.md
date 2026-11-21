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
