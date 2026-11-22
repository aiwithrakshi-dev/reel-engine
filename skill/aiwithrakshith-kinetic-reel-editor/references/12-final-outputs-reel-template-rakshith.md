<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 12. Final outputs — every reel, every template (Rakshith, 22 Nov 2026)

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
