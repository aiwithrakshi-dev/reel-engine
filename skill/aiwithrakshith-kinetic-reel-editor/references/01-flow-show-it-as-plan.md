<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 1. The flow (show it as the plan, then execute)

1. **Upload** raw video (Kannada or English) — plus his own B-roll if he has one.
2. **Understand** — detect language, transcribe, translate, word timings, topic summary (§6).
3. **Research + fact-check** the topic on the open web, official/verified sources only (§5).
4. **Gather** B-roll (official media, screenshots, demo clips) + Magnific stock (vectors, photos, illustrations,
   templates, PSDs, mockups, videos, icons, 3D models, fonts) + topic-matched music + SFX (§7).
5. **Plan** the EDL with `tools/script_gen.py` (transcript → hook, headlines, captions, chest row, cutaway spots,
   jump-cut devices, SFX, music, IG caption draft, retention checks), then review it (`--interactive` or edit
   `edl.json`): taste, facts and B-roll choices are the editor's. Layout per §8.
6. **Build** headlines, captions, graphics, cutaways, audio.
7. **Preview**: render ~15 key frames with the safe-zone overlay, LOOK at them, fix, then full render.
8. **Audit loop** (§10) on every frame — `tools/qc_audit.py` + the contact sheets; fix and re-render the affected
   range until 100 % clean.
9. **Deliver** 60 fps HD MP4 + cover + SRT + post text + sources + QC report (§11).
If Rakshith is around, send the preview frames before the full render; if not, decide and note it in the report.
