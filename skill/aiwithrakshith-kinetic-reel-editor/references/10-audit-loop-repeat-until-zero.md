<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 10. Audit loop (repeat until zero failures)

1. Contact sheet at **≥ 12 fps** with the green safe-zone box.
2. Join sheet: 5 frames either side of every jump cut, splice and cutaway edge.
3. tlog audit: every headline's hold ≥ 0.25 s.
4. Caption audit: every chunk vs word/phrase times; none early, none over the face, none outside the box.
5. Facts & spelling vs `facts.md` (Kling not Cling, Junie not Juni).
6. Overlap scan: nothing over the face, nothing outside the safe box, labels never touch big words.
7. Matte edges at 100 %; cap artifacts invisible; no readable garbled AI text; room present on every talking frame.
8. Audio: −14 LUFS ±1, ≤ −1 dBTP on the final MP4, VO on top, music smooth (no abrupt jumps except designed
   drop-outs), every graphic has its SFX.
9. Frame 1 = the chosen hook + its SFX hit; ending = hard button.
10. Hook not used in the last 5 reels (`hook_log.md`); ffprobe shows `60/1` and ≈ 60 frames per second of runtime.
Any failure → fix the timeline, re-render only the affected range, splice, re-run the whole audit.
