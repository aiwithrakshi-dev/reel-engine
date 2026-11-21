
## 11. Instagram safe zone (mandatory from Day 4, Nov 2026 — overrides the old x 80–1000 / y 160–1450 box)
Rakshith asked that ALL text, B-roll windows, cards, pills and animation sit inside the Reels safe zone.
- Safe box on 1080×1920: **x 65–960, y 270–1250** (Meta Reels margins: top 14 %, bottom 35 %, sides 6 %,
  plus 120 px kept clear on the right for the like/comment/share rail). Centre of the box: x 512.
- Talking head: shift **down 120 px** (`DY=120`, not 230) so his face sits inside the box (cap top ≈ y 590, chin ≈ 1220).
- Type zones inside the box: small label y ≈ 280; single big word baseline ≈ 595; two-line 445/590 or 400/545;
  agent/checklist tiles beside the head x ≈ 190 and ≈ 840, y 760–940; CTA pills/cards y 700–880.
- Screen cutaways (landscape screenshots/demos): blurred full-frame backdrop of the same footage + a sharp red-framed
  window at x 75–950, y 560–1210, with a stepped push-in (4 frames) on the keyword; text above the window (y 280–560).
- Verify with a green safe-zone overlay on test frames and on the join sheet before delivering.

## 12. B-roll for news/tool topics (no own B-roll)
Use the tool maker's official material: blog GIFs/animated WebP, demo MP4s and screenshots from the official
blog/docs (e.g. developer.android.com/blog/posts/…). YouTube downloads are bot-blocked in the workspace.
Cache clip ranges as .npy, show them inside the safe-zone window, push in on the exact UI element being named.
Generic AI cap artifact (crown grows a white logo): `cap_logo_fix.py` recolours it to the crown's dark grey every frame.

## 13. Layout v2 — face-clear, tight headline, chest row (Rakshith's notes 21 Nov 2026, supersedes §11 positions)
- Measure the head first: cap-top min over ALL frames (alpha) and chin. Day 4: source cap top ≥ 441, chin ≤ ~1040.
- `DY = 60` → reel cap top ≥ 505, chin ≤ ~1100. NOTHING (text, cards, pills, glitch blocks) may enter the face box.
- Headline = `stack(..., base=BASE)`: built UPWARD from the big-word baseline `BASE = capTopMin + DY - 26` (≈ 479).
  Label sits 20 px above the word's cap (label baseline → cap top), left-aligned to the word's left edge — never a fixed y.
  Responsive: if the block would rise above y 276, the big word auto-shrinks until it fits (`_fit` keys).
- Secondary components (agent tiles, checklist, pills, cards, CTA cards, ✕ pills) go in ONE row centred on the
  chest: `chest_row()` at x 528, y 1180 (below chin, inside the safe zone). Final layout is fixed; each item pops on its word.
- Tiles are auto-width (`ctile`) so text never clips; checklist tiles carry the check badge inside the tile.
- Cutaways: `stack(..., top=278)` above the window (window y 560–1210). Extra pills (e.g. handle) go right of the label.

## 14. Text must follow the speech (Rakshith's notes 21 Nov 2026)
- Type-on speed = **1 frame per letter** (labels: 2-frame word stagger). Each part of a headline starts on its own
  spoken word (e.g. CLAUDE on "Claude", + CODEX on "Codex").
- A headline must be FULLY typed ≥ 0.25 s before its scene changes (cutaway, dissolve, next headline). Never cut away
  mid-animation: if speech is too dense, move the cut later (Day 4: cutaway moved 1.93 → 2.15 s) or shorten the word.
- `word_on()` logs every headline to `<out>.tlog.json` (start / fully typed / on-screen-until); run the audit after
  every render and fix anything with hold < 0.25 s before delivering. Audio per-letter ticks use the same 1-frame step.
