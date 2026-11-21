<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 3. Instagram Reels safe zone guide (1080×1920)

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
