---
name: aiwithrakshith-reel-templates
description: Edit Rakshith's talking-head video into a 60 fps Instagram Reel in one of 7 templates chosen with /temp-1 … /temp-7, with face-clear safe-grid alignment, then file video, thumbnail, caption and timeline Google Docs into Drive Social Media/month/day.
---

# AI with Rakshith — Reel Templates (/temp-1 … /temp-7)

Router skill. Rakshith types `/temp-N` (+ a video, or "same video as before") and gets a finished 60 fps reel in that
template's style, plus a Drive day folder with the video, thumbnail, caption Doc and timeline Doc.
The engine is the GitHub repo **rakshithgowdams/aiwithrakshith-reel-engine** (private). The house style rules
(/temp-1) are in the sibling skill **aiwithrakshith-kinetic-reel-editor** — they apply to every template.

## 0. Before anything: load memory
1. Clone/pull the repo; run `./setup.sh --no-model` (fonts, pip, doctor). `python3 tools/doctor.py` must print READY.
2. Read `memory/CONTEXT.md` (recent reels, blocked hooks, template rotation, lessons). Never repeat a hook from the
   last 5 reels. If Rakshith corrects something, add it: `python3 tools/memory.py lesson "<his words>"`.

## 1. Templates
| command | name | reference | use it for | hook default |
|---|---|---|---|---|
| `/temp-1` | Red Kinetic (house) | his Kling 4.0 + Day 4 reels | AI tool launches, news, hype | any unused, red |
| `/temp-2` | Minimal Cinematic | @tahacreate | calm tutorials, design/process | `letterbox_open` |
| `/temp-3` | Editorial Script | @ahmadjamilofficial1 | mindset, creativity, stories | `face_punch` |
| `/temp-4` | Listicle Chapters | @weblyfe | "N tips/steps/tools", summaries | `shutter_blinds` |
| `/temp-5` | Bold Yellow Creator | @artzenmedia | creator tips, app walkthroughs | `zoom_punch` |
| `/temp-6` | Orange Explainer | @hammadkhalid8 | business, money, frameworks | `strip_slam` |
| `/temp-7` | SaaS Split-Screen | @marcel_grauu | product / SaaS demos | `halftone_iris` |
Full specs: `templates/temp-N/TEMPLATE.md` (generated from `engine/templates.py`, the single source of truth).
If the default hook is blocked by memory, pick another from `python3 tools/memory.py suggest --energy <energy>`.
No `/temp-N` given → suggest one from the topic + `memory.py suggest`, say which, and go.

## 2. Alignment rules (every template, enforced by the renderer)
- **Canvas** 1080×1920, 60 fps. **Safe box** x 65–960, y 270–1250 for every readable element; centre line x 512.
- **Bands:** HEAD y 280–430 (labels/headlines above the cap) · FACE cap→chin (nothing, ever) · CAPTION chin+40 → 1245.
- **Face-clear:** `FaceZone.from_head(cap_top, chin, x0, x1)` + 24 px margin. `Reel.check()` stops the render if any
  text/card/chip box touches it. Only whole-frame transitions ≤ 0.2 s may pass over the face.
- **Character:** A-roll moved down `dy` (60 px for his room framing) so cap ≥ 505 and chin ≤ 1100; /temp-7 scales him
  to 0.92 in the lower panel. Never crop his face; hands may leave the frame.
- **Text:** max 30 chars per caption line, auto-shrink to 860 px wide; captions appear on the word's start frame,
  never early; one keyword per beat; English video → English, Kannada video → Kanglish headline + English captions.
- **Pace:** an event every 0.3–0.6 s; scene length per template (/temp-3 fastest ~1.7 s, /temp-4 chapters ~8 s);
  every scene change and pop gets an SFX; music ducked under the voice.
- **Images/components:** rounded cards with soft shadow, centred on x 540, inside the safe box; screenshots only from
  official sources; no garbled AI text; no AI generation by the editor.

## 3. Pipeline
1. **Intake** — video, brand (AI with Rakshith = Kannada; aiwithrakshith.global = English), topic, CTA, facts to verify.
2. **Prep** (house engine): silence islands → tight A-roll at 30 fps + `vo_proc.wav`; word timings (`words_reel.json`,
   reel time) with faster-whisper; verify keyword onsets. Measure the face: cap_top / chin / x0 / x1 after `dy`.
3. **Plan** — `python3 tools/script_gen.py --words … --lang en|kn --brand … --energy …` → headlines, captions, cutaways.
4. **Job** — write `job.json` (format in `templates/README.md`; example `examples/templates_demo/make_jobs.py`):
   template, aroll, dy, duration, face, words, headlines, scenes (t0/t1 + title/sub/image/items/quote/kicker), hook,
   vo, music (different bed per template), banner (/temp-4), flash (/temp-7), hook_until (/temp-2).
   /temp-1 uses `examples/day4_android_studio/render_day4_60.py` with `HOOK=<name>`.
5. **Test frames** — `python3 engine/template_render.py job.json 0 0 test/ 6,180,…` and LOOK at them (hook, each scene,
   each headline, a transition). Fix before the full render.
6. **Render** — `python3 engine/template_render.py job.json --full reel.mp4` (2 parallel halves + mix + mux).
7. **QC** — `python3 tools/qc_audit.py reel.mp4 --hook <hook> --out qc_report.md` must PASS (60 fps, codecs,
   −14 LUFS ±1, ≤ −1 dBTP, hook unique). Then `tools/safe_zone_check.py` sheet for a visual pass.
8. **Package** — `python3 tools/reel_package.py --video reel.mp4 --job job.json --title "<Reel title>" --caption caption.txt
   --qc qc_report.md --brand <brand> --out pkg/` → video, thumbnail (+ 3:4 grid crop), caption.html, timeline.html.
   Caption: 4 lines + exactly 5 lowercase hashtags; English for .global, Kannada-English mix for @AIwithRakshith.
9. **Drive** — `Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / <Reel title> /`
   - Local machine: `python3 tools/drive_publish.py pkg/` (OAuth once; finds-or-creates folders, Docs conversion).
   - Inside Claude (Google Drive connector): search each folder by exact title + parent first, create it only if
     missing (`create_file`, contentMimeType `application/vnd.google-apps.folder`); upload video/thumbnail with
     `base64Content = sha256:<hex>:<abs path>`; upload caption.html / timeline.html (QC table is inside the timeline) with
     `textContent` and contentMimeType `text/html` (or `text/plain`) so they become **Google Docs** — never .txt.
   - Connector limits: ~3.1 MB of file per call → thumbnails and Docs fit; the 60 fps video does not. Upload images with
     `disableConversionToGoogleType: true` (otherwise they turn into empty Docs). Send calls one at a time (parallel
     calls hit "Resource has been exhausted"; wait ~20 s and retry). For the video: run `drive_publish.py` on his
     machine, or ask him — never silently upload a downscaled copy instead.
10. **Memory** — `python3 tools/memory.py log pkg/manifest.json` (drive_publish does it) → rebuilds `memory/CONTEXT.md`;
    commit `memory/` to the repo so every device and every LLM starts with it. Mirror CONTEXT.md to Drive
    (`drive_publish.py --sync-memory` or the connector) as "Reel Engine — Memory".
11. **Deliver** — send the video + thumbnail, give the Drive folder link and the caption; one line per QC result.

## 4. Don'ts
- Don't put anything on his face, don't remove his room background, don't speed/pitch his voice.
- Don't reuse a hook from the last 5 reels; don't reuse the same music bed two reels in a row.
- Don't save captions/timelines as .txt in Drive; don't create a second "Social Media" or month folder.
- Don't burn the Instagram caption into the video; don't exceed 5 hashtags.
