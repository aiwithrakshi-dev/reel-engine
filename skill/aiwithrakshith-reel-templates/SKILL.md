---
name: aiwithrakshith-reel-templates
description: "Edit Rakshith's talking-head video into a 60 fps Instagram Reel in one of 16 templates (/temp-1 … /temp-16), face-clear and safe-grid aligned, then deliver thumbnail, 4K 60 fps video, SEO caption, DM reply and a watermarked DM document, filed in Drive Social Media/month/day."
---

# AI with Rakshith — Reel Templates (/temp-1 … /temp-16)

Router skill. Rakshith types `/temp-N` (+ a video, or "same video as before") and gets a finished 60 fps reel in that
template's style, plus a Drive day folder with the video, thumbnail, caption Doc and timeline Doc.
The engine is the GitHub repo **rakshithgowdams/reel-engine** (private). The house style rules
(/temp-1) are in the sibling skill **aiwithrakshith-kinetic-reel-editor** — they apply to every template.

## 0. Before anything: load memory
1. Clone/pull the repo; run `./setup.sh --no-model` (fonts, pip, doctor). `python3 tools/doctor.py` must print READY.
2. Read `memory/CONTEXT.md` (recent reels, blocked hooks, template rotation, Drive folder IDs, lessons). Never repeat a
   hook from the last 5 reels. If Rakshith corrects something, add it: `python3 tools/memory.py lesson "<his words>"`.

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
| `/temp-8` | Warm Cinematic | t-8 | expert explainers, insights | `rgb_converge` |
| `/temp-9` | Peach Premium | t-9 | "3 ways / tips" lists | `pixel_assemble` |
| `/temp-10` | Card Stage | t-10 | app / AI-tool reviews | `strip_slam` |
| `/temp-11` | Green Terminal | t-11 | money / numbers, dev tools | `slice_glitch` |
| `/temp-12` | Cream Editorial | t-12 | "free / unlimited" reveals | `shutter_blinds` |
| `/temp-13` | Kanglish Tech Split | t-13 | **Kannada / Kanglish** tool news | `zoom_punch` |
| `/temp-14` | Glass Dock | t-14 | "N free AI tools" roundups | `halftone_iris` |
| `/temp-15` | Clean White Split | t-15 | cost comparisons, tool tours | `red_wipe` |
| `/temp-16` | Lime Polaroid | sezz0283 | agency / founder intros, results | `letterbox_open` |

Full specs: `templates/temp-N/TEMPLATE.md` (generated from `engine/templates.py`, the single source of truth).
Styles 2–7 live in `engine/template_render.py`, 8–16 in `engine/template_styles_b.py`. Template-specific job keys:
`banner` (4), `flash` (7), `hook_until` (2), `tiles` (9), `brand` (10), `stamp` on a headline (11), `stat` scene (11),
`dock` (14), `rows`/`total`/`result` table scene (15), `polaroid`/`name`/`badge`/`items` scene (16). Always pass `glossary`.
If the default hook is blocked by memory, pick another from `python3 tools/memory.py suggest --energy <energy>`.
No `/temp-N` given → suggest one from the topic + `memory.py suggest`, say which, and go.

## 1b. Assets (after the template is chosen)
Two sources. **Use the Drive library first — it is the recommended default.**

| | A. Drive library (recommended) | B. Magnific connector (live, logged in) |
|---|---|---|
| What | `Editing Pack › Magnific Asset Library` — licensed, watermark-free originals already downloaded (icons SVG + PNG 512, vectors, photos, PSD mockups, videos) + the "Asset Index" sheet | `stock_search` + `stock_download` during the edit |
| Limits | none — no download cap, works on any machine (`python3 tools/magnific_library.py pull`) | every file counts against the account download cap (~100 per window on Plus); the edit stalls when it hits |
| Consistency | curated themes/styles that match the 16 templates | styles vary per search |
| Use when | always first | only for an item the library lacks — then add it to the library |

- **Job references:** `icon:<theme>/<n>` (dock, tiles, chips), `vector:<theme>/<n>` or `photo:<theme>/<n>` as a scene `image`.
  `engine/assets.py` resolves them from `work/assets`; outline icons take `tint` (white on dark templates).
- **Defaults per template:** outline icons tinted white on dark looks (1, 11, 13); lineal-colour icons on tiles/docks
  (9, 14, 16); light flat vectors for white/peach pages (2, 9, 10, 15); dark tech backgrounds for 11, 12, 13.
- **Watermark rule:** use only files from the official download path (`stock_download` / API download endpoints).
  Never use preview or thumbnail URLs, screenshots of previews, or anything with a watermark — and never remove,
  crop or cover a watermark. No AI-generated stock unless Rakshith asks.
- **Licence:** the library stays private in his Drive. Never commit the files to GitHub (the repo is MIT-licensed)
  and never share the folder publicly — Freepik forbids redistributing resources as a downloadable collection.
- **Not in Magnific stock:** music (use his Drive music beds), SFX (engine synth), fonts (OFL fonts from `setup.sh`).
- **Growing the library:** `MAGNIFIC_API_KEY=… python3 tools/magnific_library.py build --plan assets/plan.json --max 95`
  then `… upload`. It stops cleanly at the download cap and resumes next run (plan targets ~2,240 files).
  Inside Claude without a key: `stock_download` one file per call, stop when the tool reports the limit.

## 2. Alignment rules (every template, enforced by the renderer)
- **Canvas** 1080×1920, 60 fps. **Safe box** x 65–960, y 270–1250 for every readable element; centre line x 512.
- **Bands:** HEAD y 280–430 (labels/headlines above the cap) · FACE cap→chin (nothing, ever) · CAPTION chin+24 → 1245.
- **Face-clear:** `FaceZone.from_head(cap_top, chin, x0, x1)` + 24 px margin. `Reel.check()` stops the render if any
  text/card/chip box touches it. Only whole-frame transitions ≤ 0.2 s may pass over the face. A guard error is a layout
  bug: resize/move the element (size it for its PEAK pop scale), never disable the check.
- **Character:** A-roll moved down `dy` (60 px for his room framing) so cap ≥ 505 and chin ≤ 1100. Split layouts scale him
  (`fit`: 7 = 0.92, 12/13 = 0.8, 14 = 0.56, 15 = 0.58) or crop him into a card (8 PiP, 10 card/dome, 11 facecam,
  16 polaroid); each layout passes its own face zone to the guard. Never crop his face; hands may leave the frame.
- **Every text layer goes through `self.check()`** — `tools/lint_guard.py` (run by `doctor.py`) fails otherwise.
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
   each headline, a transition). Also run every 3rd frame through the guard before the full render.
6. **Render** — `python3 engine/template_render.py job.json --full reel.mp4` (2 parallel halves + mix + mux).
7. **QC** — `python3 tools/qc_audit.py reel.mp4 --hook <hook> --out qc_report.md` must PASS (60 fps, codecs,
   −14 LUFS ±1, ≤ −1 dBTP, hook unique). Then `tools/safe_zone_check.py` sheet for a visual pass.
8. **Package** — `python3 tools/reel_package.py --video reel.mp4 --job job.json --post post.json --title "<Reel title>"
   --qc qc_report.md --brand <brand> --out pkg/` → the **five final outputs for every template**: Instagram thumbnail
   (+ 3:4 grid crop), **4K 60 fps** video (2160×3840) + the 1080p 60 fps file, **short SEO caption** (2–4 lines, keyword in
   line 1 ≤ 125 chars, comment-keyword CTA, 3–5 lowercase hashtags ending #aiwithrakshith) with alt text + pinned comment,
   **DM reply** text, and the **DM document** the CTA promises (.docx + .pdf, full explanation, sourced numbers,
   "AI with Rakshith" watermark on every page) — plus caption.html and timeline.html (with the QC table). Format of
   post.json: `examples/day24_gemini4/post.json`; rules in the kinetic skill §12. English for .global, Kannada-English
   mix for @AIwithRakshith.
9. **Drive** — `Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / <Reel title> /`
   - Local machine: `python3 tools/drive_publish.py pkg/` (OAuth once; finds-or-creates folders, Docs conversion).
   - Inside Claude (Google Drive connector): folder IDs are cached in `memory/drive_index.json`; otherwise search each
     folder by exact title + parent first, create it only if missing (`create_file`, contentMimeType
     `application/vnd.google-apps.folder`); upload video/thumbnail with `base64Content = sha256:<hex>:<abs path>`;
     upload caption.html / timeline.html with a file reference (or `textContent`) and contentMimeType `text/html` so
     they become **Google Docs** — never .txt.
   - Connector limits: ~3.1 MB of file per call → thumbnails and Docs fit; the 60 fps video does not. Upload images with
     `disableConversionToGoogleType: true` (otherwise they turn into empty Docs). Send calls one at a time (parallel
     calls hit "Resource has been exhausted"; wait ~20 s and retry). For the video: run `drive_publish.py` on his
     machine, or ask him — never silently upload a downscaled copy instead.
10. **Memory** — `python3 tools/memory.py log pkg/manifest.json` (drive_publish does it) → rebuilds `memory/CONTEXT.md`;
    commit `memory/` to the repo so every device and every LLM starts with it. Mirror CONTEXT.md to Drive
    (`drive_publish.py --sync-memory` or the connector) as the "Reel Engine — Memory" Doc in Social Media.
11. **Deliver** — send the 4K + 1080p videos, thumbnail, caption (with alt text + pinned comment), DM reply and DM document;
    upload the DM .pdf/.docx unconverted and the caption + DM text as a Google Doc; give the Drive folder link; one line per QC result.

## 4. Don'ts
- Don't put anything on his face, don't remove his room background, don't speed/pitch his voice.
- Don't reuse a hook from the last 5 reels; don't reuse the same music bed two reels in a row.
- Don't save captions/timelines as .txt in Drive; don't create a second "Social Media" or month folder.
- Don't burn the Instagram caption into the video; don't exceed 5 hashtags; don't promise a DM resource you haven't made.
- Don't use watermarked previews or remove a watermark; don't commit library files to GitHub.
- Don't ship ASR spellings: pass the reel's verified `glossary` in every job (fix_words also merges hyphen splits,
  e.g. Juni → Junie, Anti -Gravity → Antigravity).