---
name: aiwithrakshith-kinetic-reel-editor
description: Edit a raw Kannada or English talking-head video into a 60 fps @AIwithRakshith / aiwithrakshith.global Reel with a unique hook, verified B-roll, Instagram safe zone, Kanglish headlines and English captions.
---

# AI with Rakshith — Kinetic-Type Reel Editor (v6)

Rakshith uploads ONE raw talking-head video (Kannada or English). The editor does everything else: understands it,
researches the topic, pulls verified B-roll, edits it in his kinetic-type house style (giant red 3D words typing on
**behind his head**, pixel-block glitches, neon squiggle streaks, halftone ring bursts, red-framed cards, screen
cutaways, topic-matched music and an SFX on every visual event) inside the Instagram safe zone, syncs every word of
on-screen text and captions to his dialogue, opens with a **unique hook animation**, audits every frame in a loop and
delivers a **1080×1920, 60 fps HD** Reel. Every reel, no exceptions.

Detailed reference files (one topic each, generated from this file) live next to it in `references/`; the hook
rotation log is `references/hook_log.md`; the full Instagram & Reels rulebook is
`references/instagram_reels_guidelines.md`.

Approved builds: Kling 4.0 Kannada reel and Day 4 "Claude & Codex in Android Studio" English reel (Nov 2026).
Engine code: this repository (`engine/`, `examples/`) — also mirrored in the claude.ai Project
**"aiwithrakshith.kannada"** under `reel-engine/`. Restore it, don't rewrite it.

---

> **Templates:** this skill is the house style = `/temp-1`. For `/temp-2` … `/temp-7` (six other styles) use the
> `aiwithrakshith-reel-templates` skill; every rule below (face-clear, safe zone, 60 fps, unique hook) still applies.
> Read `memory/CONTEXT.md` in the repo before every edit, and deliver to Drive `Social Media/YYYY-MM Month/Day DD - date/`.

## 0. Non-negotiables
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

---

## 1. The flow (show it as the plan, then execute)
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
- Instagram post caption: short and SEO-friendly — 2–4 lines, main keyword in line 1 (≤ 125 chars), CTA with the comment
  keyword last, 3–5 lowercase hashtags ending with `#aiwithrakshith` (full rules in §12).
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
- **Text coverage:** Instagram recommends fewer Reels that are mostly covered by text. Big type, labels and captions
  stay under ~35 % of the frame area on talking-head shots; cutaways show one headline, never paragraphs.
- Full Instagram & Reels rulebook (specs, length, recommendations, originality, music, hashtags, labels, privacy,
  posting checklist): `references/instagram_reels_guidelines.md`.

---

## 4. Instagram terms, guidelines & privacy checklist
- **Music**: only tracks we hold a licence for (Drive `Background music` — confirm its generator/plan allows
  commercial Instagram use; stock audio only if its licence covers social/commercial). Never commercial
  songs. Offer a no-music version if he prefers Instagram's in-app licensed audio.
- **Third-party media**: official product screenshots/demos used editorially (news/review); no watermarked stock,
  no ripped TV/film/sports clips, no other creators' videos. Credit sources in the post caption.
- **Trademarks/logos**: editorial reference only; never imply sponsorship. If the post is paid → remind him to
  turn on the Paid Partnership label.
- **AI content**: Meta requires the AI label for photorealistic video or realistic-sounding audio that was digitally
  created or altered (penalties possible). His AI-generated talking head / avatar or AI voice → the "AI info" label
  is REQUIRED on that reel; list it in `instagram_post.txt` and the QC report.
- **Originality** (Instagram, Apr 2026): low-effort reposts lose recommendations. Third-party media only inside our
  framed windows with a push-in, our headline and his commentary; never a full-screen repost or a re-upload of
  someone's clip. Original A-roll is always the backbone.
- **Privacy**: no private individuals' faces, names, phone numbers, emails, addresses, plates or chats from the web;
  blur them in screenshots (incl. usernames in demos unless public brand accounts).
- **Truthfulness**: no misleading claims, fake numbers, fake UI, or clickbait the video doesn't deliver.
- **Hashtags: maximum 5** (Instagram-enforced since Dec 2025; caption + comments count together). Specific tags
  only, never `#reels` / `#explore`.
- **Recommendation eligibility:** never muted, blurry/low-res, bordered, or carrying another app's watermark; no
  contest/giveaway framing (comment-keyword DM offers only); no unproven health or money claims.
- Comment-to-DM CTAs are fine; stay within Community Guidelines.

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

---

## 9. Device library & timing (`engine/fx.py`; frame counts are 30-fps units → at 60 fps use `n * FPS // 30`)

| Device | Frames (30 fps units) | Use |
|---|---|---|
| Hook opener | 6–9 (12–18 at 60 fps) — one of the 11 hooks in §9b, never repeated within 5 reels | frame 0 |
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

## 9b. Hook library — a unique opener for every reel (`engine/hooks.py`)
The first 0.2–0.3 s decides the scroll-stop, so no two recent reels may open the same way.

| Hook | Frames @60 | Energy | Look | SFX |
|---|---|---|---|---|
| `neg_flash` | 12 | high | negative frame + cyan→red blocks, scale-in 92→100 % | impact + glitch burst |
| `pixel_assemble` | 12 | high | giant red mosaic (144→12 px) resolves into the frame | digital crunch + impact |
| `strip_slam` | 18 | high | 5 horizontal strips slam in from alternate sides, red edges | 5 fast slams + sub hit |
| `red_wipe` | 16 | medium | diagonal red light band sweeps and reveals the frame | whoosh + impact |
| `zoom_punch` | 14 | high | white pop, 135 % → 98 % → 100 % zoom-blur punch with RGB split | reverse whoosh into punch |
| `rgb_converge` | 12 | medium | R/G/B channels fly in from 90 px offsets and lock, scanlines fade | glitch zap + soft hit |
| `halftone_iris` | 16 | calm | iris opens from his face through a red halftone dot ring | riser tail + boom |
| `slice_glitch` | 14 | high | horizontal slices displaced, cyan/red tints, settle in 7 steps | data glitch + impact |
| `letterbox_open` | 14 | calm | black bars part from the face line, red edge lines | cinematic hit + sub |
| `shutter_blinds` | 18 | medium | 12 vertical blinds snap open from the centre outwards | shutter clicks + pop |
| `face_punch` | 14 | high | extreme close-up on his eyes snaps back (2.6× → 1×), red frame flash | bass drop + shutter snap |

Rules:
- Read `references/hook_log.md` first. Never use a hook from the last 5 reels; never the same energy hook 3 times in a row.
  The log lives in the private GitHub repo `rakshithgowdams/reel-engine` (skill/…/references/hook_log.md).
  As of 21 Nov 2026 the Kling 4.0 and Day 4 reels both used `neg_flash`, so it is blocked for the next reels.
- Match energy to the topic (news/launch → high, tutorial → medium, story → calm); `pick_hook(energy, recent)` does it.
- The first headline still types on its first spoken word; the hook only frames the opening.
- Set it with `HOOK=<name>` when rendering; pair the SFX from the table; add the row to `hook_log.md` on delivery
  (and push it to the repo).
- Preview all hooks on the new reel's own frames with `tools/hook_preview.py` when choosing.
- New hooks may be added to `engine/hooks.py` (same style: red/pink/cyan palette, stepped or punchy, ≤ 0.3 s, inside the
  frame logic, no AI generation); add them to this table and the log.

## 9e. Reference-reel devices (`engine/ref_devices.py`)
From the "ChatGPT GIF update" reference (Nov 2026), house palette, inside the safe zone:

| Device | Use |
|---|---|
| `slate` | dark blue-grey full-frame background for UI / card scenes (instead of a blurred room) |
| `news_stack` | 2–3 headline cards from official sources popping 3 frames apart, red NEW sticker on the first |
| `face_grid` | grid of his own frames/photos popping 2 frames apart ("SAME FACE", "EVERY POST") |
| `badge` | one big red word with white rim and overshoot pop ("FREE", "NEW", "STABLE"): headline zone, never on the face |
| `prompt_card` | dark-blue prompt bubble typing 2 chars/frame, the @mention inside a red chip |
| `face_punch` hook | extreme close-up on his eyes snapping back with a red frame flash (§9b) |

## 9f. /temp-1 job-driven style + batch workflow (`engine/template_t1.py`, Nov 2026)
`template_render.py` now renders /temp-1 from a `job.json` like the other templates (`class Reel(StylesB, StyleT1)`), so a
whole folder of raw videos can be edited unattended. Look: room background kept, 3D white/red one-line captions in one
size just under the chin, label pill + giant red 3D keyword in the HEAD band, cutaways as a red-bordered card on a dark
red-glow backdrop.
- **New transition `negswoosh`** (template 1 default, 12 frames): a diagonal red light swoosh wipes across; frames at
  p 0.42–0.58 show the blurred negative of the frame. Whole-frame, ≤ 0.2 s, so it may pass over the face.
- **New overlays**: `_t1_halftone` (dot band confined to the HEAD band, first 14 frames of a headline), `_t1_glint`
  (light sweep across the red letters after typing), `_t1_blocks` (pixel blocks for 10 frames on the keyword), red
  edge glow (vignette ring, opacity 0.33, never on the face), grain 3.
- **Punch-in jump-cut hiding**: every jump cut toggles a 1.06× scale about the face centre (`job['punch']`,
  `punch_scale`), with a swoosh SFX. Caption band and face zone are sized for the punched frame.
- **Auto-fit**: `_fit_pill` shrinks label/title pills until their PEAK pop width ≤ 780 px; big words 84–150 px cap,
  ≤ 760 px wide; caption centre = face-zone bottom + half caption height (clamped ≤ 1248).
- **Cutaway scene** keys: `t0, t1, image` (image or video; video plays at its own fps), `title`, `credit`, optional
  `crop` [x0, y0, x1, y1] fractions. Card ≤ 800×680 at cy 755; never crop away words the title relies on.
- **SFX from files**: `job['sfx'] = {impact, pop, whoosh, tick, swoosh}` paths (Magnific SFX), else synthesised.
  Template 1 adds a tick on each label and a swoosh on each punch.
- **Batch tools**:
  1. `tools/prep_reel.py raw.mp4 asr.json out/` — speech islands → `aroll_tight.mp4` (source fps), `vo.wav`,
     `words.json`, face measured with the OpenCV Haar cascade in `models/` (not in git; download
     `haarcascade_frontalface_default.xml` from opencv/opencv `data/haarcascades`).
  2. `plan.json` — hook, music, `sfx`, `word_fix` (index → text; "" deletes, use it to merge "3"+".0" → "3.0"),
     `headlines` [{label, big, label_t, big_t}], `scenes`.
  3. `tools/make_job.py <reel_dir> plan.json` — builds `job.json` (dy, face zone, punch cuts, typing steps; fails if a
     big word lands < 0.3 s before the next headline).
  4. Test sheet (edge frames ±7 around every scene through the guard + a sample sheet) → look at it.
  5. Render queue: one reel at a time (2 CPUs), then `tools/batch_audit.py <reel_dir>` — captions.srt, qc_audit
     (--hook --srt), Whisper WER of the final mix vs the words (≤ 0.08), 3 fps safe-box/face-zone sheets and a joins
     sheet. QC FIX → fix the plan or engine, delete reel.mp4, re-queue.
  6. `tools/log_delivery.py <reel_dir>` right after a pass, in delivery order, so the next audit sees the hook as used.
  7. `tools/fetch_media.py <url> <dir>` pulls og:image and page media from an official product page (+ sources.csv);
     run with `< /dev/null` inside shell loops.
- B-roll in batches: official product media (credited "Source: <site>") + Magnific stock (credited "Magnific stock").
  No faces in B-roll unless it is the product UI itself; skip or crop any person's face.
- **Text match**: captions, labels, big words and card titles must say the same thing the same way — numbers as
  digits everywhere ("4 minutes", "9 references", "5–15-second"), product names in their official spelling and case
  (n8n, Realtime, Settings → Migration Report), the comment keyword in CAPS ("Comment PROMPT"), no stray capitals
  from ASR ("Character drift", not "Character Drift"). Print every job's caption text before rendering and fix it with
  `word_fix`.

## 9c. 60 fps render (mandatory for every reel)
- Template: `examples/day4_android_studio/render_day4_60.py`. Frame numbers are 60 fps frames `g`; the timeline logic runs
  in 30-fps units (`f = g // 2`, `SUB = 0 / 0.5`), so every device keeps its approved timing while continuous motion —
  halftone rings, neon streaks, swooshes, screen push-ins, grain — gets real in-between frames. The hook runs per 60 fps frame.
- Usage: `HOOK=<name> python3 render.py <g0> <g1> part.mp4` (two parallel halves), test frames
  `python3 render.py 0 0 test_dir g1,g2,...`.
- Encode `libx264 High, -r 60, CRF 17, -maxrate 35M -bufsize 70M, -preset veryfast, AAC 320k 48 kHz, +faststart`;
  verify `r_frame_rate=60/1` and the frame count (≈ 60 × duration) with ffprobe.
- The A-roll stays at its native cadence (25 fps, frame-held); never motion-interpolate his face.
- Re-measure audio after muxing: true peak must be ≤ −1 dBTP (lower the mix 0.5 dB if needed).

**Setup**: clone this repo (or restore `reel-engine/*` from the Project); fonts Inter Tight (OFL, google/fonts
`ofl/intertight`) + Noto Sans Kannada; RVM
`github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx`;
`pip install -r requirements.txt`.

---

## 9d. Retention & algorithm rules (2026 research)
- Watch time, sends per reach and likes per reach are the top ranking signals. Edit for completion and rewatch.
- The hook is visible AND readable in the first second: hook animation + the first label on screen by ≤ 1.0 s.
- Something changes on screen at least every 3 s (our 0.3–0.5 s events usually exceed it; script_gen flags gaps).
- One idea per reel; cut every pause and filler; target 15–60 s (90 s max unless the topic needs it; 3 min ceiling
  for recommendations).
- Loop: the last line or final frame pays off the first, so the replay feels seamless.
- Caption (post): line 4 is the CTA. Use the comment keyword when there's a DM offer, otherwise "save / send this to…"
  (sends drive non-follower reach).
- Unsure between two hooks → post one as a Trial Reel (non-followers first) and keep the winner's hook in the log.

## 10. Audit loop (repeat until zero failures)
1. Contact sheet at **≥ 12 fps** with the green safe-zone box.
2. Join sheet: 5 frames either side of every jump cut, splice and cutaway edge.
3. tlog audit: every headline's hold ≥ 0.25 s.
4. Caption audit: every chunk vs word/phrase times; none early, none over the face, none outside the box.
5. Facts & spelling vs `facts.md` (Kling not Cling, Junie not Juni).
6. Face-clear scan: on every contact-sheet frame, no text, component or effect layer touches the face oval
   (`protect_face` in the render + `FaceZone.check` on every text/component box); nothing outside the safe box;
   labels never touch big words.
7. Matte edges at 100 %; cap artifacts invisible; no readable garbled AI text; room present on every talking frame.
8. Audio: −14 LUFS ±1, ≤ −1 dBTP on the final MP4, VO on top, music smooth (no abrupt jumps except designed
   drop-outs), every graphic has its SFX.
9. Frame 1 = the chosen hook + its SFX hit; ending = hard button.
10. Hook not used in the last 5 reels (`hook_log.md`); ffprobe shows `60/1` and ≈ 60 frames per second of runtime.
11. `python3 tools/qc_audit.py final.mp4 --tlog *.tlog.json --hook <name> --new-reel --srt captions.srt --cover cover.png
    --sheets qc/` passes; attach its `qc_report.md`.
Any failure → fix the timeline, re-render only the affected range, splice, re-run the whole audit.

---

## 11. Deliverables
**Always the five final outputs in §12** (thumbnail, 4K 60 fps video, SEO caption, DM reply, watermarked DM document), plus: `final_reel_60fps.mp4` (1080×1920, 60 fps, hook named in the QC report and logged) · `cover.png` (reads in the 3:4
grid crop) · `contact.png` (safe-zone contact sheet) · `captions.srt` (English) · `instagram_post.txt` (short SEO caption,
3–5 lowercase tags, Story line, source credits, label reminders) · `facts.md` · `credits.csv`
(every B-roll/stock/music/SFX item + licence) · `qc_report.md` (deviations, fixes, audit results) · QC sheets
(contact, join, safe-zone) · `vo_tight.wav` · optional no-music version. Save new layout learnings into `docs/`.

---

## 12. Final outputs — every reel, every template (Rakshith, 22 Nov 2026)
Write `post.json` (example: `examples/day24_gemini4/post.json`) and run
`python3 tools/reel_package.py --video reel.mp4 --job job.json --post post.json --title "<title>" --qc qc_report.md --out pkg/`
(or `tools/reel_outputs.py` for a reel built outside the template engine). The reel is not finished until all five exist:
1. **Instagram thumbnail** — `*_thumbnail.jpg` 1080×1920 + `*_thumbnail_grid.jpg` (3:4 profile-grid crop); headline + face read in both.
2. **4K 60 fps video** — `*_4k_60fps.mp4` 2160×3840, 60/1, H.264 High 5.2, AAC 320k (Lanczos master from the 1080p render;
   the A-roll is 1080p, so say "4K master", not "native 4K") + the 1080p 60 fps file.
3. **Instagram caption — short and SEO-friendly**: 2–4 short lines; line 1 ≤ 125 chars (shows before "more") and holds the
   main search keyword (tool/model name + topic); line 2 the one key fact; last line the CTA with the comment keyword
   ("Comment MODEL and I'll DM you …"); then 3–5 lowercase hashtags ending `#aiwithrakshith`. Also write the **alt text**
   (Advanced settings → Accessibility; keywords in a natural sentence) and a **pinned comment** repeating the CTA.
   English for .global; Kannada-English mix for @AIwithRakshith. `caption_checks()` must PASS.
4. **Instagram DM reply** — `dm_message.txt`: thanks + `{link}` to the DM document + one action to take + follow line.
5. **DM document** — the checklist/guide the CTA promises, as `.docx` + `.pdf` (`tools/dm_doc.js`): complete explanation,
   every number verified and sourced (same standard as `facts.md`), date checked, "AI with Rakshith" watermark on every
   page, brand header, page-numbered footer. Upload the PDF + .docx to the reel's Drive folder unconverted (conversion to
   Google Docs drops the watermark); Rakshith shares the PDF as "Anyone with the link" and pastes that link into the DM reply.
The caption + alt text + pinned comment + DM reply also go to Drive as one Google Doc ("— Instagram Caption + DM").

## 13. Lessons learned (don't repeat)
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
