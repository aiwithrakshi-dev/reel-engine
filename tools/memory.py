#!/usr/bin/env python3
"""Reel memory: what every LLM/agent reads before editing, so each run starts smarter than the last.

  memory/content_log.json   every delivered reel (date, brand, language, template, hook, title, headlines, Drive links, QC)
  memory/lessons.md         hand-kept corrections from Rakshith (never auto-deleted)
  memory/CONTEXT.md         generated digest = rules + recent reels + blocked hooks + template rotation + lessons

  python3 tools/memory.py context                   # rebuild CONTEXT.md (agents read this FIRST)
  python3 tools/memory.py suggest --energy high     # template + hook to use next (not in the last 5)
  python3 tools/memory.py log pkg/manifest.json     # add a delivered reel (drive_publish.py does this for you)
  python3 tools/memory.py lesson "text"             # add a lesson
"""
import os, sys, json, argparse, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); MEM = os.path.join(ROOT, 'memory')
sys.path.insert(0, os.path.join(ROOT, 'engine'))
LOG, LESSONS, CTX = (os.path.join(MEM, f) for f in ('content_log.json', 'lessons.md', 'CONTEXT.md'))


def load():
    try: return json.load(open(LOG))
    except Exception: return {'reels': []}


def save(d): os.makedirs(MEM, exist_ok=True); json.dump(d, open(LOG, 'w'), indent=1, ensure_ascii=False)


def log_reel(man):
    if isinstance(man, str): man = json.load(open(man))
    d = load(); key = (man.get('date'), man.get('title'))
    d['reels'] = [r for r in d['reels'] if (r.get('date'), r.get('title')) != key]
    d['reels'].insert(0, {k: man.get(k) for k in ('date', 'title', 'brand', 'lang', 'template', 'hook', 'duration', 'drive', 'qc', 'notes', 'headlines')})
    d['reels'].sort(key=lambda r: r.get('date') or '', reverse=True); save(d)


def recent_hooks(n=5): return [r.get('hook') for r in load()['reels'][:n] if r.get('hook')]


def suggest(energy='high', recent=None):
    from hooks import HOOKS
    from templates import TEMPLATES
    reels = load()['reels']; blocked = set(recent_hooks(5)) if recent is None else set(recent)
    hooks = [h for h, v in HOOKS.items() if h not in blocked and (v[2] == energy or energy == 'any')] or [h for h in HOOKS if h not in blocked]
    used_t = [r.get('template') for r in reels[:6]]
    temps = sorted((t for t in TEMPLATES if TEMPLATES[t]['energy'] in (energy, 'medium') or energy == 'any'), key=lambda t: (used_t.count(t), t))
    return dict(templates=temps[:3], hooks=hooks[:4], blocked_hooks=sorted(blocked))


def write_context():
    from templates import TEMPLATES
    reels = load()['reels']; s = suggest('any')
    L = ['# Reel engine memory (generated — read this before every edit)', '',
         f'Updated {datetime.datetime.now():%Y-%m-%d %H:%M}. Source: memory/content_log.json + memory/lessons.md. Rebuild: `python3 tools/memory.py context`.', '',
         '## Non-negotiables', '- 1080x1920, **60 fps**, H.264 High + AAC 48 kHz, -14 LUFS, true peak <= -1 dBTP.',
         '- Instagram safe zone x 65-960, y 270-1250 for anything readable. 4-line caption + exactly 5 lowercase hashtags.',
         '- **Face-clear**: no text / component / effect layer on his face (engine/face_guard.py). Whole-frame transitions <= 0.2 s only.',
         '- Text follows speech. English video -> English headline + captions; Kannada video -> Kanglish headline + English captions.',
         '- No AI generation by the editor. Fact-check every on-screen claim on the official source.',
         '- Unique hook every reel: never one from the 5 most recent reels below.', '',
         '## Templates', '| /temp | name | best for | energy |', '|---|---|---|---|']
    L += [f"| /temp-{n} | {t['name']} | {t['best_for']} | {t['energy']} |" for n, t in TEMPLATES.items()]
    try:
        di = json.load(open(os.path.join(MEM, 'drive_index.json')))
        L += ['', '## Google Drive', f"- Social Media root: {di['social_media_root']['url']} (id `{di['social_media_root']['id']}`)",
              f"- Months: {', '.join(f'{k} `{v}`' for k, v in di['months'].items())}", f"- Days: {', '.join(f'{k} `{v}`' for k, v in di['days'].items())}",
              '- Layout: Social Media / YYYY-MM Month / Day DD - YYYY-MM-DD / <reel title> / video, thumbnail, Caption (Doc), Timeline (Doc)',
              f"- Asset library (use FIRST, before the Magnific connector): {di.get('asset_library', {}).get('url', 'not built yet')} — {di.get('asset_library', {}).get('contents_2026_11_21', '')}"]
    except Exception: pass
    L += ['', '## Recent reels (newest first)', '| date | title | brand | template | hook | Drive |', '|---|---|---|---|---|---|']
    for r in reels[:15]:
        link = (r.get('drive') or {}).get('folder') or ''
        L.append(f"| {r.get('date')} | {r.get('title')} | {r.get('brand') or ''} | {r.get('template') or ''} | `{r.get('hook')}` | {link} |")
    L += ['', '## Next reel', f"- Blocked hooks (last 5): {', '.join(f'`{h}`' for h in s['blocked_hooks']) or 'none'}",
          f"- Least-used templates lately: {', '.join(f'/temp-{t}' for t in s['templates'])}",
          f"- Free hooks: {', '.join(f'`{h}`' for h in s['hooks'])} (run `tools/memory.py suggest --energy high|medium|calm`)", '',
          '## Lessons (from Rakshith — keep applying)']
    L += open(LESSONS).read().strip().splitlines() if os.path.exists(LESSONS) else ['- (none yet)']
    os.makedirs(MEM, exist_ok=True); open(CTX, 'w').write('\n'.join(L) + '\n'); return CTX


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['context', 'suggest', 'log', 'lesson']); ap.add_argument('arg', nargs='?')
    ap.add_argument('--energy', default='high'); a = ap.parse_args()
    if a.cmd == 'context': print(write_context())
    elif a.cmd == 'suggest': print(json.dumps(suggest(a.energy), indent=1))
    elif a.cmd == 'log': log_reel(a.arg); print(write_context())
    else:
        with open(LESSONS, 'a') as f: f.write(f'- {datetime.date.today()}: {a.arg}\n')
        print(write_context())
