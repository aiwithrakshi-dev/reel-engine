<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 7. B-roll, assets, music, SFX

**B-roll priority**: (1) his own B-roll → (2) official media from the product's blog/docs/press kit (demo GIFs,
animated WebP, MP4s, screenshots — download directly; YouTube is bot-blocked in the workspace) → (3) Magnific stock
video/photos (`stock_search` + `stock_download`, `ai_generated: excluded`, licence via `stock_get`) for context →
(4) Magnific stock icons / 3D / mockups / PSD / templates / fonts for graphics. Screenshots go in the red-framed
safe-zone window with a stepped 4-frame push-in on the exact UI element being named, over a blurred backdrop.
Own B-roll: scene-detect (`scdet`), cache to .npy, stills 3 frames after each cut; shot shorter than its slot →
cut to another shot on the beat, never freeze.

**Music** — a *different, topic-matched* track every video (log used tracks; don't repeat back-to-back):

| Topic energy | Bed |
|---|---|
| News / launch / hype / tool drop | 120–135 BPM dark trap / bass-house, deep 808 (e.g. Black_Asphalt) |
| Tutorial / how-to / calm explainer | 85–105 BPM lo-fi / soft electronic |
| Story / emotional / film | 70–95 BPM cinematic pulse, pads |
| Business / money / freelancing | 100–118 BPM upbeat house / corporate groove |

Analyse BPM/key/sub with librosa; re-sequence on bar lines; cuts inside cutaways on beats; drop-out 0.17 s before
every cutaway entry/exit, slam back on the cut, downbeat on the slam; end on the final hit. If Magnific has no stock
audio, use the Drive `Background music` folder in the edit package
https://drive.google.com/drive/folders/1tWaeU9u8_vI3wiVATkvfLKEln9Vo8PBP (its SFX folders are YouTube re-uploads → don't use).

**SFX** (synthesised in `engine/audio.py`, or licensed stock), one per visual event: the hook's paired hit (§9b),
per-letter ticks −28 dB, blip on type-on start, zap on neon streak, whoosh+boom on rings, swish on smear/marker,
riser+whoosh into cutaways, impact on cutaway slams/exits, pop on every card/pill/icon, final hit. B-roll native
audio only where it proves something (e.g. stereo → auto-pan L→R).

**Mix**: VO high-pass 80 Hz, de-ess, 3:1 comp; music −14 dB pre-duck + sidechain (thr 0.04, ratio 5, att 15, rel 260)
so dialogue stays on top and the bed breathes smoothly; master −14 LUFS, limiter ceiling −2.9 dBTP before AAC
→ ≤ −1 dBTP on the final MP4 (re-measure after the final mux).
