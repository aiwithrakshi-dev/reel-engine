<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 9f. /temp-1 job-driven style + batch workflow (`engine/template_t1.py`, Nov 2026)

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
- **Moving B-roll first (v2, 25 Nov 2026)** — Rakshith rejected cutaways built mostly from still images. Target 30–45 %
  of the runtime as B-roll, mostly video:
  1. official product video: `tools/fetch_media.py <url> <dir> --videos` also finds MP4/WebM referenced in scripts/JSON
     (Next.js, CMS payloads); official GIF demos → convert to MP4 (`ffmpeg -vf fps=30,format=yuv420p`);
  2. Magnific stock video (`stock_search content_type=video` → `stock_download type=video max_bytes`), cut to ≤ 12 s;
  3. stills only for the exact screen the voice names (pricing table, settings page) — they get a Ken Burns move.
  Scene keys: `fill: true` = full-bleed 1080×1920 cover-fit with `fx`/`fy` focus (best for stock footage and vertical
  official clips; dark top/bottom gradients keep the title pill and caption readable); default = red-bordered card
  (best for UI screen recordings); `clips: [{image, in, dur, title, credit, fill, crop, fx, fy}]` = several shots
  inside one scene with 3-frame zoom-kick quick cuts (+ a tick SFX); `in` = start offset into the clip.
  Never show faces in B-roll (use `in`/`crop`/`fx` to stay on hands, screens and product).
- **Audio audit** (`tools/audio_audit.py`, run by `batch_audit.py`): rebuilds the mix with voice / music / SFX stems
  and checks voice (no clipping, no clicks at silence-cut joins, steady level), music (≥ 18 dB under the voice while
  talking — default bed −29 dB ≈ 20 dB under —, never swelling in pauses, still audible), SFX (no hit louder than the
  voice, hits audible, never within 4 LU of a word — SFX are sidechain-ducked under the voice, `sfx_db` default −15)
  and the final mix (−14 LUFS ±1, ≤ −1 dBTP, LRA ≤ 9, no jump-scare opening, no dead air). Any FAIL → re-mix/re-edit.
  The bed and SFX are auto-levelled against each reel's own voice (`music_under` −15.5 LU before ducking ≈ 21–22 dB
  after; SFX scaled with the voice) and library SFX tails are cut (impact 0.75 s, whoosh 0.6 s, pop 0.28 s, tick
  0.2 s) so they never sit under the next words. Audio-only fixes: `tools/remix_audio.py <reel_dir>` (no re-render).
  WER compares like with like (digits ↔ number words, "1x", "+", "$").
- **Face scan**: `tools/broll_face_scan.py <reel_dirs>` before rendering; look at every flagged window (Haar flags
  server racks and mics too) and move `in`/`crop` off any real face — official demo videos often show avatars.
- **Text match**: captions, labels, big words and card titles must say the same thing the same way — numbers as
  digits everywhere ("4 minutes", "9 references", "5–15-second"), product names in their official spelling and case
  (n8n, Realtime, Settings → Migration Report), the comment keyword in CAPS ("Comment PROMPT"), no stray capitals
  from ASR ("Character drift", not "Character Drift"). Print every job's caption text before rendering and fix it with
  `word_fix`.
