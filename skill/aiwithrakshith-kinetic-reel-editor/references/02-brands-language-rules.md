<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 2. Brands & language rules

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
