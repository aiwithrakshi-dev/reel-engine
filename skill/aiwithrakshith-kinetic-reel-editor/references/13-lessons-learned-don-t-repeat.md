<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 13. Lessons learned (don't repeat)

STUDIO (plain background) was rejected — keep his room. Dark-red labels vanish on wood → white labels.
- Fixed layout let text touch his cap and left a huge label→word gap → responsive `stack()` measured from the head.
- Side tiles beside the head looked messy and clipped text → one auto-width row centred on the chest.
- 2 frames/letter was too slow for his speech and CODEX was cut mid-typing → 1 frame/letter + completion audit.
- Whisper Kannada timestamps drift up to 0.3 s; always verify keyword onsets.
- RVM drops the chair → static chair mask from the red piping (wood removal must exclude red, hue < 8).
- Grain makes x264 explode → grain 3.5 + VBV cap. Never load whole videos into RAM.
- YouTube downloads are bot-blocked → use official blog/doc media.
- AI cap artifacts (colour flips, white logo growth) appear in most of his AI talking heads → always scan and fix.
- Rings at full opacity cover his face → op ≤ 0.75.
- The first two reels both opened with `neg_flash` → hooks now rotate from a 10-hook library with a log.
- Frame-doubling a 30 fps file is not 60 fps → render with the 60 fps template.
- 60 fps muxing raised the true peak to −0.7 dBTP → always re-measure after the final mux.
- The skill required captions but the engine had no caption code → `captions.py` (+ SRT, glossary, overlap guards).
- Day 4's layout put the chest row where a caption line now needs to go → reserve the caption band when planning DY.
- Whisper splits words across jump cuts and drops punctuation late in a take → script_gen splits sentences on cuts,
  conjunctions and length too.
- Batch (Nov 2026): a transition's negative progress made a negative crop index and an 8.9 GB allocation → clamp p to
  [0, 1] and test ±7 frames around every scene edge before a full render.
- Caching the graded base frame per source frame + ultrafast intermediates cut a 40 s reel from ~20 to ~5 min on 2 CPUs.
- Cropping a product card cut the version number off its headline ("Announcing n8n") → check every crop on the test sheet.
- Day 4's neon streaks and swooshes crossed his face (15.8 s, 21.6 s, 35.4 s) → face-clear rule + `face_guard.py`;
  effects now pass behind the face oval.
