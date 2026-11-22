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
| News / launch / hype / tool drop | 95–110 BPM soft dark pulse, low in the mix (e.g. Pressure_Line); energy from visuals + SFX |
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

**Mix (dialogue first, Rakshith 22 Nov 2026)**: his voice must be clean enough for Instagram's auto-translate / dubbing to
recognise every word. VO high-pass 80 Hz, de-ess, 3:1 comp; music a **slow, soft bed ~20 dB under the voice** (−17 dB pre-gain,
high-pass 60 Hz, low-pass 9 kHz, −6 dB at 1.8 kHz and −4 dB at 3.5 kHz) + gentle sidechain (thr 0.02, ratio 6, att 20, rel 450);
SFX bus −11 dB (~6 dB under the voice). Check: Whisper on the FINAL mix must transcribe the same words as the clean VO (0 % WER)
and the music measured in the mix must sit ≥ 18 dB under the voice. Pick calmer 85–105 BPM beds even for news reels;
energy comes from the visuals and SFX, not a loud bed. Earlier reels used music −14 dB pre-duck (too loud — retired).
so dialogue stays on top and the bed breathes smoothly; master −14 LUFS, limiter ceiling −2.9 dBTP before AAC
→ ≤ −1 dBTP on the final MP4 (re-measure after the final mux).
