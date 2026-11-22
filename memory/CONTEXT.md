# Reel engine memory (generated — read this before every edit)

Updated 2026-11-22 07:16. Source: memory/content_log.json + memory/lessons.md. Rebuild: `python3 tools/memory.py context`.

## Non-negotiables
- 1080x1920, **60 fps**, H.264 High + AAC 48 kHz, -14 LUFS, true peak <= -1 dBTP.
- Instagram safe zone x 65-960, y 270-1250 for anything readable. 4-line caption + exactly 5 lowercase hashtags.
- **Face-clear**: no text / component / effect layer on his face (engine/face_guard.py). Whole-frame transitions <= 0.2 s only.
- Text follows speech. English video -> English headline + captions; Kannada video -> Kanglish headline + English captions.
- No AI generation by the editor. Fact-check every on-screen claim on the official source.
- Unique hook every reel: never one from the 5 most recent reels below.

## Templates
| /temp | name | best for | energy |
|---|---|---|---|
| /temp-1 | Red Kinetic (house style) | AI tool launches, news drops, hype explainers | high |
| /temp-2 | Minimal Cinematic | calm tutorials, design/process explainers, "how to" talks | calm |
| /temp-3 | Editorial Script | mindset, creativity, storytelling, motivational takes | medium |
| /temp-4 | Listicle Chapters | "N tips/steps/tools" lists, book or course summaries | medium |
| /temp-5 | Bold Yellow Creator | creator tips, tool walkthroughs, Canva/app tutorials | high |
| /temp-6 | Orange Explainer | business, money, book lessons, frameworks | high |
| /temp-7 | SaaS Split-Screen | product demos, SaaS / app features, before-after workflows | medium |
| /temp-8 | Warm Cinematic | expert explainers, "most people never see this" insights, calm authority | medium |
| /temp-9 | Peach Premium | "3 ways / 3 tips" lists, creative-tool tips, premium tutorials | medium |
| /temp-10 | Card Stage | app / AI-tool reviews, "this tool just ..." launches, SaaS features | high |
| /temp-11 | Green Terminal | money / numbers stories, dev & AI-agent tools, "I built X" breakdowns | high |
| /temp-12 | Cream Editorial | "free / unlimited" reveals, dev-tool deep dives, documentary tone | medium |
| /temp-13 | Kanglish Tech Split | KANNADA / Kanglish tool news, app walkthroughs, "free alternative" reels | high |
| /temp-14 | Glass Dock | "N free AI tools" roundups, app recommendations, creator tool stacks | high |
| /temp-15 | Clean White Split | cost comparisons, "replace N subscriptions", tool tours | medium |
| /temp-16 | Lime Polaroid | agency / founder intros, client results, case studies, service offers | medium |

## Google Drive
- Social Media root: https://drive.google.com/drive/folders/1JBIU5uDtb8-5eDNs4hDbtGomyTqXzTmt (id `1JBIU5uDtb8-5eDNs4hDbtGomyTqXzTmt`)
- Months: 2026-11 November `1jjPyisRuBOBlO1WUWUo41KETIct3Lw7G`
- Days: 2026-11-21 `1FP4073opUPgKV2jep81VwPWFeUDnZX3H`, 2026-11-22 `1fGd3_QsMjWXREu18j51KieSfUR4JWQ8T`
- Layout: Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / <reel title> / video, thumbnail, Caption (Doc), Timeline (Doc)
- Asset library (use FIRST, before the Magnific connector): https://drive.google.com/drive/folders/1w8JfNSj9YE5CduUC8q6NzJ2uqe-FMMXK — 98 icons (ai 26, code 18, app 18, money 18 lineal-color; social 18 outline) + 2 vectors (tech-bg, dev-scenes)

## Recent reels (newest first)
| date | title | brand | template | hook | Drive |
|---|---|---|---|---|---|
| 2026-11-22 | Day 24 — There is no Gemini 4 Pro (price doubles Dec 1) | aiwithrakshith.global | 1 | `strip_slam` |  |
| 2026-11-21 | Day 4 — Claude & Codex inside Android Studio (BYOA) | aiwithrakshith.global | 1 | `neg_flash` |  |
| 2026-11-19 | Kling 4.0 — 10 prompts / keyframe method | @AIwithRakshith | 1 | `neg_flash` |  |

## Next reel
- Blocked hooks (last 5): `neg_flash`, `strip_slam`
- Least-used templates lately: /temp-2, /temp-3, /temp-4
- Free hooks: `pixel_assemble`, `red_wipe`, `zoom_punch`, `rgb_converge` (run `tools/memory.py suggest --energy high|medium|calm`)

## Lessons (from Rakshith — keep applying)
- Keep his real room as the background; never matte him onto a studio/plain background unless asked for that one video.
- Never translate, re-voice, speed up or pitch-shift his voice; only tighten pauses.
- Labels on the room must be white with a soft shadow (dark red vanishes on the wood wall).
- Streaks, swooshes and rings must never cross his face (Day 4 v3 broke this at 15.8 s / 21.6 s / 35.4 s → face_guard added).
- Every reel at 60 fps HD; every reel a different hook; captions never appear before the word is spoken.
- On-screen numbers must match the official source exactly, even when the voice is loose ("15 REFERENCES", not "15 images").
- Grain makes x264 explode: grain amount 3.5 and VBV cap (maxrate 25-35M).
- Kannada Whisper word times drift up to 0.3 s: verify keyword onsets on the waveform.
- Deliver into Drive: Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / <reel> with caption + timeline as Google Docs.
- 2026-11-21: Drive connector inside Claude carries max ~3.1 MB per file: thumbnails + Docs go through it, the 60 fps videos go up with tools/drive_publish.py (local OAuth) or by hand. Images need disableConversionToGoogleType=true or they become empty Docs.
- 2026-11-21: Alignment guard: size every popped/scaled element for its PEAK scale (e.g. maxw 720 for a 1.18x pop); two-line captions under the chin need 30-34 px + 62 px with a 68 px step.
- 2026-11-21: Always pass the reel glossary in template jobs: raw ASR showed 'Juni' and 'Anti -Gravity' in captions until fix_words() merged hyphen splits and applied the glossary.
- 2026-11-21: Magnific stock downloads did not use credits on the Plus plan, but the account hit a stock download cap after ~100 files (21 Nov 2026) and the tool says not to retry in that conversation. Build the 1,000-3,000 library in ~95-file runs with tools/magnific_library.py (API key) or across days.
- 2026-11-21: Assets: Drive library first (Editing Pack / Magnific Asset Library), Magnific connector only for missing items. Only official download files — never preview URLs or anything watermarked. Library stays private: never in GitHub.
- 2026-11-22: Day 24: fx.py inserts engine/ at sys.path[0], so a reel's own islands.py gets shadowed by engine/islands.py (Day 4 cuts!). Name per-reel modules uniquely (islands_d24.py) and print J before rendering.
- 2026-11-22: Script facts can go stale between recording and editing (Day 24: Carbon opened to all paid devs Nov 10, Hydrogen shipped Nov 12). Keep his voice, correct on screen, and tell him before the render.
- 2026-11-22: Streaks/rings/swooshes must be clipped to the safe zone with a feathered mask (render_d24_60.py SAFE_OUT) and rings kept to r1 ~520-560 so the clip isn't visible.
- 2026-11-22: Music was too loud on Day 24 and Instagram's auto-translate could not hear the dialogue. Rakshith wants slow, soft background music: bed ~20 dB under the voice, vocal-band EQ dip, SFX ~6 dB under; verify with Whisper on the final mix (0 % WER vs the clean voice).
- 2026-11-22: Every reel must end with five outputs: Instagram thumbnail, 4K 60 fps video, short SEO caption (keyword first, comment-keyword CTA, 3-5 hashtags) with alt text + pinned comment, DM reply text, and a DM document (.docx + .pdf) with the full explanation and an 'AI with Rakshith' watermark (tools/reel_package.py --post).
