<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 0. Non-negotiables

1. **Never remove his background.** His real room (wood-slat wall, portrait, bookshelf, gold unicorn, pink lamp,
   red/black chair) stays behind him: darkened 20 %, desaturated 20 %, Gaussian σ 3 (~6 px). He is matted only so
   big type can sit *between* the room and him. Studio/plain background only if he asks for that one video.
2. **Never alter his voice**: no dub, re-voice, speed or pitch change. Only remove silences (pauses → ~0.22 s).
3. **No AI generation of any kind by the editor** — no video/image/music/voice generation (Magnific, Higgsfield,
   HeyGen, etc.). B-roll = his own B-roll, real verified web media, and Magnific **stock** only (prefer
   `ai_generated: excluded`). (If HIS A-roll is an AI talking head he made, it is used as delivered and the reel
   gets the AI info label, §4.)
4. **Everything readable or persistent inside the Instagram safe zone** (§3): text, captions, cards, pills, icons,
   badges, screen windows, chest row. Transition FX (neon streak, halftone ring, swoosh, smear, flashes) may cross the
   margins for ≤ 0.2 s. Verify with `tools/safe_zone_check.py` on every audit.
5. **FACE-CLEAR: no layer of any kind on his face.** No text layer (headline, label, caption, pill text), no
   component layer (card, tile, pill, badge, sticker, icon, window, prompt card) and no edit/effect layer (neon
   streak, ring, swoosh, pixel block, marker, bloom, PiP) may touch the face zone. The zone is an oval over the
   measured head (min cap-top → max chin, ear to ear) + 24 px. Enforced in code: `engine/face_guard.py`
   (`protect_face()` after every FX pass, so effects pass behind his face; `FaceZone.check()` fails the render on any
   text/component box in the zone). Only whole-frame transitions ≤ 0.2 s (hook, negative flash, ghost, smear) may
   cover it, because they are a cut, not a layer. Text follows his speech; every animation finishes before the
   scene changes.
6. On-screen claims must be factually exact even when the voice is loose (voice "15 reference images" → screen
   "15 REFERENCES"). Every number/name verified on official sources (§5).
7. Only devices from the library (§9). No zoom-blur, cube spins, light leaks, film burn, emoji, robots.
   Motion is snappy and stepped (overshoot pops), never floaty/linear.
8. Music never louder than the voice; every graphic has a sound; hard button ending (no fade-out).
9. Respect Instagram's Terms, Community Guidelines, Music Guidelines and privacy (§4).
10. **Every reel opens with a unique hook** (§9b): never a hook used in the last 5 reels; log it in `hook_log.md`.
11. **Every reel is delivered at 1080×1920, 60 fps HD** (§9c). Never deliver 30 fps; never frame-double a 30 fps render.
