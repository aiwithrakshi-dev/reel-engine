# Skill audit: aiwithrakshith-kinetic-reel-editor (21 Nov 2026)

**Score: 8.0 / 10 for v6** (up from **5.9 / 10** for v3, the version saved on claude.ai before today).

Scale: 10 = a new editor or any LLM can produce an approved reel from a raw video with no extra instructions, and
every rule is checked automatically. Scores are per category, unweighted.

| # | Category | v3 (saved) | v6 (now) | Evidence for v6 | What 10/10 needs |
|---|---|---|---|---|---|
| 1 | Style fidelity (look, devices, timing) | 9 | **9** | Frame-exact device specs from 2 approved reels; reference-reel devices added | A third approved Kannada reel built entirely on v6 |
| 2 | Instagram compliance (specs, policies) | 7 | **9** | Full rulebook: 5-hashtag cap, originality, required AI label, text coverage, recommendation eligibility | Re-verify every quarter; tie to Meta's own spec page when it publishes organic Reels margins |
| 3 | Face & layout protection | 5 | **9** | Face-clear rule + `face_guard.py` (effects pass behind the face; text/component boxes fail the render); safe-zone sheets | Per-frame face tracking instead of one oval per reel |
| 4 | Hook & retention craft | 6 | **8.5** | 11 hooks with rotation log, first-second text rule, 3 s change rule, loop ending, Trial Reels | Feed Instagram Insights retention curves back into hook/pace choices |
| 5 | Automation (raw video → reel) | 3 | **6.5** | `script_gen` drafts the full edit script; `qc_audit` checks delivery; captions/Kanglish/devices are modules | One command from raw video to render (transcribe → plan → render.py generated from `edl.json` → QC) |
| 6 | Kannada / Kanglish support | 5 | **7** | Kanglish labels, conjunct-safe type-on, phrase-synced English captions, Kannada path in script_gen | Proven on a real Kannada reel; reviewed phrase-table tool |
| 7 | QC & verifiability | 6 | **9** | `qc_audit.py` (fps, codecs, LUFS, true peak, typing holds, hook uniqueness, SRT), 12 fps sheets, tlog | Automatic face/caption overlap and lip-sync detection on the final file |
| 8 | Audio & music | 7 | **7** | Mix spec, ducking, SFX per event, true-peak re-measure | Licensed music source confirmed in writing, music log, topic-matched track picker |
| 9 | Portability (any LLM, setup) | 4 | **7** | GitHub repo, AGENTS.md, CLAUDE.md, universal prompt, per-topic references | Remove hard-coded `/home/claude/...` paths; one `setup.sh`; config file per reel |
| 10 | Clarity & maintainability | 7 | **8** | One source (SKILL.md) + generated references; contradictions fixed | Shorter SKILL.md (core rules only) with details living in the references |
| | **Overall** | **5.9** | **8.0** | | |

## Problems found in the skill and fixed in v6

1. **Contradiction:** rule 4 said no streak or ring may leave the safe zone, but every approved reel uses
   full-frame streaks and rings. Now: readable/persistent elements stay inside; transition FX may cross the margins
   for ≤ 0.2 s.
2. **Contradiction:** "No AI generation of any kind" vs his AI-generated talking heads. Now: the rule applies to
   what the editor adds; his AI A-roll is used as delivered and gets the required AI info label.
3. **Face rule too vague:** "Nothing overlaps his face" had no definition and no check, and Day 4 broke it (neon
   streaks and swooshes crossed his face at 15.8 s, 21.6 s and 35.4 s). Now: an explicit face-clear rule (text,
   component and effect layers), a measured face oval, and code that enforces it.
4. **Missing Instagram rules:** 5-hashtag limit, recommendation eligibility (no watermarks/borders/mostly-text),
   originality policy, exact AI-label requirement, no giveaway framing. All added.
5. **Captions required but no caption code** (fixed in v5), **no edit-script automation** (fixed in v5).

## Open items (why it isn't 10 yet)

- Rendering is still a hand-built `render.py` per reel; `edl.json` doesn't generate it yet.
- Kannada support hasn't been proven on a real Kannada reel since these tools were added.
- Music licence status of the Drive library is unconfirmed.
- Hard-coded workspace paths make the engine awkward to run on another machine.
- The face oval is measured once per reel, not tracked per frame. Fine for a seated talking head, not for walking
  shots.
