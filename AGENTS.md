# AGENTS.md — instructions for any AI coding agent

You are editing Instagram Reels for Rakshith (@AIwithRakshith, Kannada / aiwithrakshith.global, English).

1. **Read `skill/aiwithrakshith-kinetic-reel-editor/SKILL.md` completely before doing anything.** It is the source of
   truth for style, layout, the Instagram safe zone, language rules, audio, timing and the audit loop.
2. The input is one raw talking-head video (Kannada or English). Follow the 9-step flow in SKILL.md §1.
3. Reuse the engine in `engine/` and copy `examples/day4_android_studio/render_day4.py` as the timeline template.
   Don't rewrite the effects from scratch.
4. Hard rules you must never break:
   - Keep his real room background. Never change his voice (only cut silences).
   - No AI generation of video, images, music or voice. Use his B-roll, official media and licensed stock only.
   - Everything inside the safe box **x 65–960, y 270–1250** on 1080×1920. Nothing over his face.
   - Type-on is 1 frame per letter; every headline is fully typed ≥ 0.25 s before its scene changes.
   - English video → English headline + English captions. Kannada video → Kanglish headline (Kannada label +
     English keyword) + English captions translated from Kannada and synced to his lips.
   - Every on-screen fact is verified on an official source and logged in `facts.md`.
5. Before delivering, run the audit loop (SKILL.md §10), including
   `python3 tools/safe_zone_check.py <reel>.mp4 --fps 12 --out qc/`, and look at every sheet.
6. Deliver 1080×1920 **60 fps** H.264 (CRF 17) with AAC 320k at −14 LUFS, plus the files in SKILL.md §11.
7. Never commit media, models, music or client footage to this repo (see `.gitignore`).
