<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 12. Lessons learned (don't repeat)

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
