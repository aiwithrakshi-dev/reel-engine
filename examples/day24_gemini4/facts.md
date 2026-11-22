# Facts — Day 24 "There is no Gemini 4 Pro" (checked 22 Nov 2026)

| On-screen claim | Status | Source |
|---|---|---|
| No model called "Gemini 4 Pro" | Correct. "Gemini 4 Pro" was a leak/rumour name in Sept 2026; Google shipped Gemini 4 as Argon (30 Sep), Carbon (28 Oct) and Hydrogen (12 Nov) | Google DeepMind model cards (Argon, Carbon, Hydrogen); CometAPI explainer on the Sept "Gemini 4 Pro" leaks |
| Argon API: $2 → $4 per 1M input from Dec 1 | Correct. $2 / $10 per 1M input/output to 30 Nov; $4 / $20 from 1 Dec; cached input $0.10 → $0.20 | Gemini API pricing page (via computingforgeeks, buildmvpfast, Let's Data Science); Vertex AI pricing page |
| Carbon has the same prices | Correct. Carbon launched at the same $2/$10 intro price, $4/$20 after 30 Nov | 9to5Google; Google Japan blog (Carbon launch) |
| Argon: API + Gemini app, since Oct 13 | Correct. GA 13 Oct on the paid Gemini API; AI Pro and Ultra in the Gemini app | The New Stack (13 Oct); Let's Data Science |
| Carbon: "Google's strongest", scores higher | Correct. Google calls it its strongest model; leads Google's benchmark table | Google developers blog (Carbon); SecurityWeek |
| Carbon: cyber teams first · Oct 28 | Correct. Announced 28 Oct, Fairwind Program cyber defenders first | SecurityWeek; Neoteo |
| Carbon: open since Nov 10 (paid API + AI Ultra) | Correct. GA to paying developers/enterprises, and AI Ultra in the Gemini app, AI Mode, Antigravity | Android Authority; Let's Data Science; 9to5Google |
| + Hydrogen · fast model · Nov 12 | Correct. Third Gemini 4 model, adapted from Carbon, for fast everyday/agentic work | Google DeepMind Hydrogen model card; SiliconANGLE |
| Batch API = half price | Correct. Batch $1 / $5 vs standard $2 / $10 | computingforgeeks (from the Gemini API pricing page) |
| Cached input −95% | Correct. 95% implicit-cache discount on eligible hits | CometAPI; Vertex AI pricing |

## Voice vs screen (noted in the QC report)
- Voice: "Gemini 4 has two real models, Argon and Carbon." Screen adds "+ Hydrogen · fast model · Nov 12" (Hydrogen shipped 12 Nov).
- Voice: "only some cybersecurity teams can use [Carbon]." That was true 28 Oct–9 Nov. Screen shows "at launch, only CYBER TEAMS" + "cyber teams first · Oct 28" + "open since Nov 10".
- Voice: "doubles in price next week." Screen shows the exact date: "from Dec 1".
- Spelling: Argon, Carbon, Hydrogen, Gemini 4 (Whisper wrote "Gemini for" once → captions show "Gemini 4").
