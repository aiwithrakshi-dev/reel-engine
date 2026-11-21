<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 0. Non-negotiables

1. **Never remove his background.** His real room (wood-slat wall, portrait, bookshelf, gold unicorn, pink lamp,
   red/black chair) stays behind him: darkened 20 %, desaturated 20 %, Gaussian σ 3 (~6 px). He is matted only so
   big type can sit *between* the room and him. Studio/plain background only if he asks for that one video.
2. **Never alter his voice**: no dub, re-voice, speed or pitch change. Only remove silences (pauses → ~0.22 s).
3. **No AI generation of any kind** — no video/image/music/voice generation (Magnific, Higgsfield, HeyGen, etc.).
   B-roll = his own B-roll, real verified web media, and Magnific **stock** only (prefer `ai_generated: excluded`).
4. **Everything inside the Instagram safe zone** (§3). No text, caption, card, pill, icon, screen window, glitch
   block, streak or ring may sit outside it. Verify with an overlay on every audit (`tools/safe_zone_check.py`).
5. **Nothing overlaps his face.** Text follows his speech; every animation finishes before the scene changes.
6. On-screen claims must be factually exact even when the voice is loose (voice "15 reference images" → screen
   "15 REFERENCES"). Every number/name verified on official sources (§5).
7. Only devices from the library (§9). No zoom-blur, cube spins, light leaks, film burn, emoji, robots.
   Motion is snappy and stepped (overshoot pops), never floaty/linear.
8. Music never louder than the voice; every graphic has a sound; hard button ending (no fade-out).
9. Respect Instagram's Terms, Community Guidelines, Music Guidelines and privacy (§4).
10. **Every reel opens with a unique hook** (§9b): never a hook used in the last 5 reels; log it in `hook_log.md`.
11. **Every reel is delivered at 1080×1920, 60 fps HD** (§9c). Never deliver 30 fps; never frame-double a 30 fps render.
