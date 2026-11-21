---
name: aiwithrakshith-kinetic-reel-editor
description: Edit a raw Kannada or English talking-head video into a 60 fps @AIwithRakshith / aiwithrakshith.global Reel: research, verified B-roll, Instagram safe zone, synced Kanglish headlines and English captions.
---

# AI with Rakshith — Kinetic-Type Reel Editor (v3)

Rakshith uploads ONE raw talking-head video (Kannada or English). The editor does everything else: understands it,
researches the topic, pulls verified B-roll, edits it in his kinetic-type house style (giant red 3D words typing on
**behind his head**, pixel-block glitches, neon squiggle streaks, halftone ring bursts, red-framed cards, screen
cutaways, topic-matched music and an SFX on every visual event) inside the Instagram safe zone, syncs every word of
on-screen text and captions to his dialogue, audits every frame in a loop and delivers a **1080×1920, 60 fps HD** Reel.

Approved builds: Kling 4.0 Kannada reel and Day 4 "Claude & Codex in Android Studio" English reel (Nov 2026).
Engine code: this repository (`engine/`, `examples/`) — also mirrored in the claude.ai Project
**"aiwithrakshith.kannada"** under `reel-engine/`. Restore it, don't rewrite it.

---

## 0. Non-negotiables
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

---

## 1. The flow (show it as the plan, then execute)
1. **Upload** raw video (Kannada or English) — plus his own B-roll if he has one.
2. **Understand** — detect language, transcribe, translate, word timings, topic summary (§6).
3. **Research + fact-check** the topic on the open web, official/verified sources only (§5).
4. **Gather** B-roll (official media, screenshots, demo clips) + Magnific stock (vectors, photos, illustrations,
   templates, PSDs, mockups, videos, icons, 3D models, fonts) + topic-matched music + SFX (§7).
5. **Plan** the EDL: every keyword, caption chunk, cutaway, device and SFX on its spoken word; layout per §8.
6. **Build** headlines, captions, graphics, cutaways, audio.
7. **Preview**: render ~15 key frames with the safe-zone overlay, LOOK at them, fix, then full render.
8. **Audit loop** (§10) on every frame — fix and re-render the affected range until 100 % clean.
9. **Deliver** 60 fps HD MP4 + cover + SRT + post text + sources + QC report (§11).
If Rakshith is around, send the preview frames before the full render; if not, decide and note it in the report.

---

## 2. Brands & language rules
| | AI with Rakshith (@AIwithRakshith) | aiwithrakshith.global |
|---|---|---|
| Raw voice | Kannada / Kanglish | English |
| Headline (small label + big keyword) | **Kanglish**: label in Kannada script, big keyword in English as he says it (e.g. label `Codex ಈಗ` + big `ANDROID STUDIO`) | English |
| Captions (bottom of safe zone) | **English translation**, phrase-synced to his lips | English, word-synced |
| Handle pill / CTA | `@aiwithrakshith` | `@aiwithrakshith.global` (confirm exact handle) |
| Post caption | Kannada-English mix + Kannada hashtags (#KannadaAI …) | English, global hashtags |
- Headline is never a full sentence; tech/product names always in English spelling (Kling, Codex, Claude, Junie).
- Captions are wanted on every reel (replaces the old "no subtitles" rule) — short, one line, synced (§8).
- Kannada font: **Noto Sans Kannada** (OFL)
  `raw.githubusercontent.com/google/fonts/main/ofl/notosanskannada/NotoSansKannada%5Bwdth%2Cwght%5D.ttf`,
  rendered with `ImageFont.Layout.RAQM` (Pillow with raqm). No italic → apply a 10° shear for the brand look.
  Never type Kannada per character (breaks conjuncts): reveal per **grapheme cluster** (`regex` `\X`) or per word.

---

## 3. Instagram Reels safe zone guide (1080×1920)
**Safe box (hard limit for every element): x 65–960, y 270–1250.**
| Edge | Keep clear | What Instagram overlays there |
|---|---|---|
| Top | 270 px (14 %) | status bar, "Reels" title, camera icon |
| Bottom | 670 px (35 %) | profile name, follow button, caption text, audio ticker |
| Left | 65 px (6 %) | screen edge / rounded corners |
| Right | 120 px (+ ~230 px wide rail on the lower 40 %) | like, comment, share, save, more, audio thumbnail |
- Source: Meta's Reels ad margins (top 14 %, bottom 35 %, sides 6 %). Organic Reels have no published spec, so use
  the stricter ad numbers; re-check periodically (the UI changes).
- Full-bleed backgrounds/B-roll fill may extend outside the box; anything readable or meaningful may not.
- Profile-grid crop is a 3:4 centre crop (1080×1440, y 240–1680): the cover headline + face must read inside it.
- QC overlay: draw the box (green) on every preview/audit sheet; any element pixel outside it = fail.

---

## 4. Instagram terms, guidelines & privacy checklist
- **Music**: only tracks we hold a licence for (Drive `Background music` — confirm its generator/plan allows
  commercial Instagram use; stock audio only if its licence covers social/commercial). Never commercial
  songs. Offer a no-music version if he prefers Instagram's in-app licensed audio.
- **Third-party media**: official product screenshots/demos used editorially (news/review); no watermarked stock,
  no ripped TV/film/sports clips, no other creators' videos. Credit sources in the post caption.
- **Trademarks/logos**: editorial reference only; never imply sponsorship. If the post is paid → remind him to
  turn on the Paid Partnership label.
- **AI content**: his AI-generated footage/avatar → remind him to turn on the "AI info" label.
- **Privacy**: no private individuals' faces, names, phone numbers, emails, addresses, plates or chats from the web;
  blur them in screenshots (incl. usernames in demos unless public brand accounts).
- **Truthfulness**: no misleading claims, fake numbers, fake UI, or clickbait the video doesn't deliver.
- Comment-to-DM CTAs are fine; no giveaways without rules; stay within Community Guidelines.

---

## 5. Research & verification
- Web search first (standard → extended if thin); scrape full pages; official blogs/docs/press first.
- Every on-screen fact (name, number, version, date, stable/beta, price, limit) needs the official source + ideally
  one reputable outlet → `facts.md`. Confirm it is current as of today.
- If the voice is slightly wrong, the screen shows the correct wording; note it in the report.

---

## 6. Understanding the raw video
- Detect language (Whisper large-v3, `language=None`, first 12 s). Load audio via librosa (faster-whisper's av path breaks).
- English: `faster-whisper large-v3` word timestamps.
- Kannada: transcribe `language='kn'` + `task='translate'`; the editor **reviews and corrects** the English by meaning
  (Whisper Kannada is unreliable) and builds a phrase table: Kannada phrase ↔ English caption ↔ start/end.
- Word onsets: snap to librosa onsets (−0.08/+0.18 s); verify keywords on spectrograms (plosive bursts, 's' HF onset).
- Silence map: `silencedetect=noise=-35dB:d=0.15`; cut pauses ≥ 0.35 s; islands padded and snapped **outward** to
  whole source frames (never trim inside a word); 20 ms crossfades (`cut_vo.py`). Cut video segment by segment and
  concat (a 10+-trim filter graph OOMs).
- Artifact scan at 10 fps: AI cap crown colour flips / white logo growth (`cap_logo_fix.py` recolours the crown each
  frame; `cap_patch.py` pastes a clean crown), finger warps, garbled AI text → fix or hide under a device/cutaway.
- Matte: `matte.py` (RVM resnet50 ONNX, ~0.35 s/frame) on the tightened timeline + the ~1 s tail for the end hold;
  `subject.py`/`chair_mask.py` when the chair must be in front; 1 px choke, drop specks.

---

## 7. B-roll, assets, music, SFX
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

**SFX** (synthesised in `engine/audio.py`, or licensed stock), one per visual event: impact+glitch open, per-letter
ticks −28 dB, blip on type-on start, zap on neon streak, whoosh+boom on rings, swish on smear/marker, riser+whoosh
into cutaways, impact on cutaway slams/exits, pop on every card/pill/icon, final hit. B-roll native audio only where
it proves something (e.g. stereo → auto-pan L→R).

**Mix**: VO high-pass 80 Hz, de-ess, 3:1 comp; music −14 dB pre-duck + sidechain (thr 0.04, ratio 5, att 15, rel 260)
so dialogue stays on top and the bed breathes smoothly; master −14 LUFS, limiter ceiling −2.9 dBTP before AAC
→ ≤ −1 dBTP on the final MP4.

---

## 8. Frame layout (responsive, measured per video)
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
   FX (blocks, streaks, rings) → whole-frame devices → grain 3.5.

**Captions**: Inter Tight Bold Italic 44 px, white, 3 px dark stroke + soft shadow, one line, ≤ 5 words / ≤ 30 chars,
centred in the safe box; the word being spoken gets a red `#E3121B` highlight (karaoke). English: word-synced to
Whisper word times. Kannada: English phrase chunks timed to the Kannada phrase spans (start on the first syllable,
end ≤ 0.15 s after the last), never ahead of his lips. Never cover the face; drop a chunk that just repeats the
headline word being typed in the same 0.3 s.

---

## 9. Device library & timing (`engine/fx.py`; frame counts are 30-fps units → at 60 fps use `n * FPS // 30`)
| Device | Frames (30 fps units) | Use |
|---|---|---|
| Negative flash open | 3 (inverted blur ×0.55 + cyan→red blocks), then scale-in 92→100 % over 3 | frame 0 |
| Big word type-on | **1 letter per frame**; newest letter 1.22× ghost → 1.06× → lock; each part starts on its own spoken word | every keyword |
| Label scatter-in | words stagger 2, snap home in 2-frame steps | small labels |
| Pixel blocks | 2–5 each, 18–42 px on a 6 px grid, reds/pinks | on the letter being revealed / dissolves |
| Neon squiggle streak | 6 (white core + #FF1A2A glow) | hides a jump cut |
| Halftone ring (dots / lines) | 5, op 0.6–0.75 (+3-fr radial blur) | hides a jump cut / reset |
| Vertical smear | 3 | hides a jump cut |
| Red light swoosh | 7 | into a cutaway |
| Cutaway entry / exit | RGB ghost 3 / magenta 1 + negative 2 (or negative 2) | screen & B-roll cutaways |
| Card / pill pop | 4 (0→62→108→100 %) | chest row, cards |
| Marker highlight | red→cyan→green, 2 per word | label emphasis |
| Hold + pixel flicker, hard cut | last 0.8 s | ending |
Budget per ~40 s: ≈ 3 streaks, 6 rings, 1 smear, 2 swooshes, 4 negative flashes. Every jump cut hidden by one.
- A new visual event every 0.3–0.5 s on a spoken word; ~75 % talking head, ~25 % cutaways.
- **Every headline fully typed ≥ 0.25 s before its scene changes** — if speech is too dense, move the cut later or
  shorten the word. `word_on()` writes `<out>.tlog.json` (start / fully typed / on-screen-until).
- End: VO end + 0.28 s final hit; reel ends VO end + 0.82 s, hard cut.

**60 fps render**: `FPS = 60` in fx/render; the 25 fps A-roll is frame-held, graphics animate at 60. Render in two
parallel halves, stream frames (7 GB RAM), grain 3.5. Encode `libx264 High, -r 60, CRF 17, -maxrate 35M
-bufsize 70M, -preset veryfast, AAC 320k 48 kHz, +faststart`.

**Setup**: clone this repo (or restore `reel-engine/*` from the Project); fonts Inter Tight (OFL, google/fonts
`ofl/intertight`) + Noto Sans Kannada; RVM
`github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx`;
`pip install -r requirements.txt`.

---

## 10. Audit loop (repeat until zero failures)
1. Contact sheet at **≥ 12 fps** with the green safe-zone box.
2. Join sheet: 5 frames either side of every jump cut, splice and cutaway edge.
3. tlog audit: every headline's hold ≥ 0.25 s.
4. Caption audit: every chunk vs word/phrase times; none early, none over the face, none outside the box.
5. Facts & spelling vs `facts.md` (Kling not Cling, Junie not Juni).
6. Overlap scan: nothing over the face, nothing outside the safe box, labels never touch big words.
7. Matte edges at 100 %; cap artifacts invisible; no readable garbled AI text; room present on every talking frame.
8. Audio: −14 LUFS ±1, ≤ −1 dBTP on the final MP4, VO on top, music smooth (no abrupt jumps except designed
   drop-outs), every graphic has its SFX.
9. Frame 1 = negative flash + hit; ending = hard button.
Any failure → fix the timeline, re-render only the affected range, splice, re-run the whole audit.

---

## 11. Deliverables
`final_reel_60fps.mp4` (1080×1920, 60 fps) · `cover.png` (reads in the 3:4 grid crop) · `captions.srt` (English) ·
`instagram_post.txt` (caption, hashtags, Story line, source credits, label reminders) · `facts.md` · `credits.csv`
(every B-roll/stock/music/SFX item + licence) · `qc_report.md` (deviations, fixes, audit results) · QC sheets
(contact, join, safe-zone) · `vo_tight.wav` · optional no-music version. Save new layout learnings into `docs/`.

---

## 12. Lessons learned (don't repeat)
- STUDIO (plain background) was rejected — keep his room. Dark-red labels vanish on wood → white labels.
- Fixed layout let text touch his cap and left a huge label→word gap → responsive `stack()` measured from the head.
- Side tiles beside the head looked messy and clipped text → one auto-width row centred on the chest.
- 2 frames/letter was too slow for his speech and CODEX was cut mid-typing → 1 frame/letter + completion audit.
- Whisper Kannada timestamps drift up to 0.3 s; always verify keyword onsets.
- RVM drops the chair → static chair mask from the red piping (wood removal must exclude red, hue < 8).
- Grain makes x264 explode → grain 3.5 + VBV cap. Never load whole videos into RAM.
- YouTube downloads are bot-blocked → use official blog/doc media.
- AI cap artifacts (colour flips, white logo growth) appear in most of his AI talking heads → always scan and fix.
- Rings at full opacity cover his face → op ≤ 0.75.
