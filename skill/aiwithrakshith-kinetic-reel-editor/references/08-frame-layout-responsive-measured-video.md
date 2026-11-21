<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 8. Frame layout (responsive, measured per video)

1. **Measure the head** over ALL frames from the matte: min cap-top and max chin (source px).
2. `DY` = shift so the face sits inside the safe box with room above (Day 4: DY 60 → cap ≥ 505, chin ≤ 1100).
   100 % scale. The opened strip at the top is filled by stretching the room's top rows with a 60 px blend.
3. **Headline** (`stack(..., base=BASE)`): built upward from the big-word baseline `BASE = capTopMin + DY − 26`.
   Small label 20 px above the word's cap, left-aligned to the word. If the block would rise above y 276 the big word
   auto-shrinks. Big words ≤ 865 px wide; white labels with soft shadow; big-word shadow 0.55. Never a fixed y.
4. **Bottom band between chin and y 1250** (responsive split):
   - **Chest row** — secondary components (tiles, checklist, pills, cards, ✕ pills, CTA cards) in ONE row centred on
     the body (x ≈ 528), auto-width tiles (`ctile`), height ≤ 64, each pops on its word.
   - **Caption line** below it, ending at y ≤ 1245.
   - Not enough room (< 150 px) → reduce DY (face moves up, headline auto-shrinks) until both fit.
5. Cutaways: headline `stack(..., top=278)`; screen window x 75–950, y 560–1210; caption stays in its band.
6. Composite order: room → big type behind → cards behind head → him (matte) → chest row → captions →
   FX (blocks, streaks, rings) → whole-frame devices → hook → grain 3.5.

**Captions** (`engine/captions.py`; two styles; turn Instagram's auto-captions OFF when captions are burned in):
- `karaoke` (default on talking head): Inter Tight Bold Italic 44 px, white, 3 px dark stroke + soft shadow, one line, ≤ 5 words / ≤ 30 chars,
centred in the safe box; the word being spoken gets a red `#E3121B` highlight (karaoke). English: word-synced to
Whisper word times. Kannada: English phrase chunks timed to the Kannada phrase spans (start on the first syllable,
end ≤ 0.15 s after the last), never ahead of his lips. Never cover the face; drop a chunk that just repeats the
headline word being typed in the same 0.3 s.
- `chip` (reference-reel style, for punch lines over cutaways/slates or fast news reels): 2–4 heavy upright caps
  words, ONE keyword on a red rounded box ("SAVE **THIS**", "JUST **DROPPED**", "**FIX** SINGLE FRAMES"), stepped pop.
- Line breaks keep names and number pairs together ("Android Studio", "40 agents") and never end on "and / the / a".
  Run `apply_glossary` with the verified spellings from `facts.md` (Juni → Junie, Cling → Kling).
- Kannada/Kanglish labels: `engine/kannada_text.py` (script runs, RAQM, conjunct-safe type-on, 10° shear).
- The caption band and the chest row must not touch: `CaptionTrack(..., avoid=[chest_row_box])` raises if they do.
