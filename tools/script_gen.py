#!/usr/bin/env python3
"""Editing-script generator: raw transcript -> a complete, editable edit plan in the house style.

It drafts what an editor decides by hand: hook, every headline (small label + big keyword on its spoken word),
caption chunks, chest-row items, cutaway suggestions, an effect on every jump cut, SFX cues, music bed, retention and
timing checks, and a 4-line Instagram caption with 5 lowercase tags. The plan is a DRAFT: review it (or run with
--interactive to accept/edit each headline in the terminal; an LLM can edit edl.json directly), then build render.py.

English:  python3 tools/script_gen.py --words words.json --islands islands.py --brand global --out plan/
Kannada:  python3 tools/script_gen.py --phrases phrases.json --lang kn --brand kannada --out plan/
  words.json   : [[word, start, end], ...]  (Whisper word timestamps, SOURCE seconds)
  phrases.json : [[kannada_text, english_text, start, end], ...]  (reviewed translation, SOURCE seconds)
  islands      : islands.py with ISL = [(a, b), ...] or a JSON list; maps source -> reel time and gives the jump cuts
  --glossary   : JSON {"Juni": "Junie", ...} verified spellings from facts.md
Outputs: edl.json, edl.csv, plan.md, captions.srt, instagram_caption_draft.txt
"""
import argparse, csv, json, math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
from captions import chunk_words, phrases_to_chunks, apply_glossary, write_srt
from hooks import HOOKS, pick_hook

FPS30 = 30
STOP = set('a an the and or but so to of in on at for with from by is are was were be been it its it\'s this that these those '
           'i you he she we they me my your our their his her them us just let can will would could should do does did '
           'has have had not no yes than then there here what which who whom when where why how all any some more most '
           'very really also now new own one two ill im ive youre dont doesnt isnt its thats lets weve theyre whats heres theres'.split())
POWER = {'free': 3, 'new': 2, 'stable': 3, 'beta': 2, 'launch': 3, 'launched': 3, 'released': 3, 'release': 2, 'days': 2,
         'weeks': 1, 'agent': 2, 'agents': 2, 'prompt': 2, 'prompts': 2, 'build': 2, 'plan': 2, 'test': 2, 'difference': 2,
         'project': 2, 'setup': 2, 'freelancers': 2, 'secret': 2, 'mistake': 2, 'stop': 2, 'hack': 2, 'save': 2,
         'every': 1, 'same': 1, 'fix': 2, 'fast': 2, 'faster': 2, 'cheap': 2, 'money': 2, 'clients': 2, 'workflow': 2}
UI_WORDS = {'settings', 'emulator', 'app', 'screen', 'menu', 'dashboard', 'inside', 'demo', 'registry', 'tools', 'tab',
            'button', 'editor', 'studio', 'code', 'terminal', 'website', 'page', 'upload', 'preview', 'previews'}
LAUNCH = {'just', 'new', 'now', 'stable', 'launched', 'released', 'release', 'announced', 'dropped', 'update', 'finally'}
HOWTO = {'how', 'step', 'steps', 'first', 'second', 'then', 'click', 'open', 'go', 'select', 'tutorial'}
STORY = {'story', 'remember', 'when', 'felt', 'life', 'journey', 'once', 'dream'}
MUSIC = {'high': '120-135 BPM dark trap / bass-house, deep 808', 'medium': '85-105 BPM lo-fi / soft electronic',
         'calm': '70-95 BPM cinematic pulse, pads', 'business': '100-118 BPM upbeat house / groove'}
DEVICES = ['neon_streak', 'halftone_ring', 'vertical_smear', 'halftone_ring_lines']
DEVICE_SFX = {'neon_streak': 'zap', 'halftone_ring': 'whoosh + boom', 'vertical_smear': 'swish', 'halftone_ring_lines': 'whoosh + boom',
              'cutaway': 'riser + whoosh in, impact on slam'}


# ------------------------------------------------------------------ inputs
def load_islands(path):
    if not path: return None
    if path.endswith('.json'): isl = json.load(open(path))
    else:
        ns = {}; exec(compile(open(path).read(), path, 'exec'), ns); isl = ns['ISL']
    out, t = [], 0.0
    for a, b in isl:
        a2 = math.floor(a / 0.04 + 1e-6) * 0.04; b2 = math.ceil(b / 0.04 - 1e-6) * 0.04
        out.append((a2, b2, t, t + (b2 - a2))); t += b2 - a2
    return out


def to_reel(ts, isl):
    if isl is None: return ts
    for a, b, r0, r1 in isl:
        if a - 1e-6 <= ts <= b + 1e-6: return r0 + (ts - a)
    return None


def clean(w): return re.sub(r'[^\w+%$₹.-]', '', w).strip('.')


# ------------------------------------------------------------------ analysis
def sentences(words, isl_cuts, phrase_mode=False):
    """Split reel-time words into sentences on punctuation, long pauses or jump cuts."""
    out, cur = [], []
    cuts = sorted(isl_cuts)
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        end = re.search(r'[.!?]$', w[0]) or nxt is None or (nxt[1] - w[2] > 0.45)
        if phrase_mode:                          # Kannada: one sentence per spoken phrase
            if end: out.append(cur); cur = []
            continue
        if not end and nxt is not None and len(cur) >= 2:           # a jump cut between the middles of w and nxt
            lo_, hi_ = (w[1] + w[2]) / 2, (nxt[1] + nxt[2]) / 2
            if any(lo_ < c <= hi_ for c in cuts): end = True
        if not end and re.search(r'[,;:]$', w[0]) and len(cur) >= 4 and nxt is not None and not clean(nxt[0])[:1].isupper(): end = True
        if end and nxt is not None and clean(w[0]).lower() == 'comment': end = False      # keep 'comment X' together
        if not end and nxt is not None and len(cur) >= 6 and clean(nxt[0]).lower() in ('and', 'but', 'so', 'because', 'for'): end = True
        if not end and len(cur) >= 12 and clean(w[0]).lower() != 'comment': end = True
        if end: out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def score_token(tok, idx):
    t = clean(tok); lo = t.lower()
    if not t or lo in STOP: return -9
    s = 0.0
    if re.search(r'\d', t): s += 3.5
    if t[:1].isupper() and idx > 0: s += 3
    if re.match(r'^[A-Z][a-z]+[A-Z]', t) or (t.isupper() and len(t) > 1): s += 2
    s += POWER.get(lo, 0)
    s += 0.6 if 4 <= len(t) <= 12 else (-1 if len(t) > 14 else 0)
    if lo in UI_WORDS: s += 0.5
    return s


def pick_keyword(sent, used=()):
    toks = [w[0] for w in sent]; best = None
    for i, tok in enumerate(toks):
        sc = score_token(tok, i)
        if clean(tok).upper() in used: sc -= 2.5                  # don't repeat the same big word
        if sc <= 0: continue
        j = i                                    # grow proper-noun / number+noun phrases ("Android Studio", "40 agents")
        while j + 1 < len(toks) and (clean(toks[j + 1])[:1].isupper() and clean(toks[i])[:1].isupper()
                                     or re.search(r'\d', clean(toks[i])) and j == i
                                     or j == i and POWER.get(clean(toks[i]).lower()) and POWER.get(clean(toks[j + 1]).lower())) \
                and not re.search(r'[.,!?]$', toks[j]):
            j += 1
        phrase = ' '.join(clean(t) for t in toks[i:j + 1])
        if len(phrase) > 16: j, phrase = i, clean(toks[i])
        sc += 0.8 * (j - i)
        if best is None or sc > best[0]: best = (sc, i, j, phrase)
    return best


def label_for(sent, i, j):
    toks = [re.sub(r"[^\w'+%$₹-]", '', w[0]).lower() for w in sent]
    before = [t for t in toks[max(0, i - 4):i] if t]
    lab = ' '.join(before[-4:])
    if len(lab) < 3:
        lab = ' '.join(t for t in toks[j + 1:j + 4] if t)
    return lab[:28]


def chest_items(sent):
    toks = [w[0] for w in sent]; txt = ' '.join(toks); items = []
    groups, cur = [], []                          # consecutive capitalised tokens = one name ("Claude Agent")
    for w in sent:
        t = clean(w[0])
        if t[:1].isupper() and t.lower() not in STOP: cur.append((t, w[1]))
        if not (t[:1].isupper() and t.lower() not in STOP) or re.search(r'[,.;]$', w[0]):
            if cur: groups.append((' '.join(x[0] for x in cur), cur[0][1])); cur = []
    if cur: groups.append((' '.join(x[0] for x in cur), cur[0][1]))
    if len(groups) >= 3 and txt.count(',') >= 2: items += [('tile', n, t) for n, t in groups][:4]
    m = re.search(r'\bnot (?:a |an |the )?(\w+)', txt, re.I)
    if m:
        w = next((x for x in sent if clean(x[0]).lower() == m.group(1).lower()), sent[-1]); items.append(('struck_pill', m.group(1), w[1]))
    m = re.search(r'\bcomment\s+"?(\w+)"?', txt, re.I)
    if m:
        w = next((x for x in sent if clean(x[0]).lower() == 'comment'), sent[0]); items.append(('cta_card', m.group(1).upper(), w[1]))
    return items


def detect_energy(words):
    lo = [clean(w[0]).lower() for w in words[:40]]
    if sum(t in LAUNCH for t in lo) >= 2: return 'high'
    if sum(t in HOWTO for t in lo) >= 2: return 'medium'
    if sum(t in STORY for t in lo) >= 2: return 'calm'
    return 'medium'


def recent_hooks(log_path, n=5):
    if not log_path or not os.path.exists(log_path): return []
    hooks = []
    for line in open(log_path, encoding='utf-8'):
        if line.startswith('|') and '`' in line:
            m = re.findall(r'`(\w+)`', line)
            if m and m[0] in HOOKS: hooks.append(m[0])
    return hooks[:n]


# ------------------------------------------------------------------ plan
def build_plan(words, isl, a):
    cuts = [r0 for (_, _, r0, _) in isl[1:]] if isl else []
    end_t = words[-1][2] + 0.82
    energy = a.energy if a.energy != 'auto' else detect_energy(words)
    recent = recent_hooks(a.hook_log)
    hook = a.hook or pick_hook(energy, recent, seed=len(words))
    sents = sentences(words, cuts, phrase_mode=(a.lang == 'kn'))
    heads, chest, cutaways, events, used = [], [], [], [], set()
    for k, s in enumerate(sents):
        items = chest_items(s)
        tiles = [x for x in items if x[0] == 'tile']
        if len(tiles) >= 3 and heads:             # a list of names: tiles on the chest, big word = "ANY <category>"
            cat = re.sub(r'^\d+\+?\s*', '', heads[-1]['big']).rstrip('S?') or 'ONE'
            label, big, i, j, sc = 'your pick', f'ANY {cat}', 0, 0, 5.0
        else:
            kw = pick_keyword(s, used)
            if not kw: continue
            sc, i, j, phrase = kw
            label, big = label_for(s, i, j), phrase.upper() + ('?' if s[-1][0].endswith('?') and j == len(s) - 1 else '')
        used.add(big); used.update(big.split())
        heads.append({'id': f'h{k + 1}', 'label': label, 'big': big, 'label_t': round(s[0][1], 2),
                      'big_t': round(s[i][1], 2), 'sentence': ' '.join(w[0] for w in s), 'score': round(sc, 1)})
        for typ, txt, t in items: chest.append({'type': typ, 'text': txt, 't': round(t, 2), 'head': f'h{k + 1}'})
        lo = {clean(w[0]).lower() for w in s}
        if lo & UI_WORDS or (k == 0 and energy == 'high'):
            cutaways.append({'t0': round(s[0][1], 2), 't1': round(s[-1][2], 2), 'head': f'h{k + 1}',
                             'suggest': f'screen cutaway: official screenshot/demo showing "{phrase}" (push-in on it)'})
    merged = []                                   # merge overlapping cutaway suggestions
    for c in cutaways:
        if merged and c['t0'] <= merged[-1]['t1'] + 0.3: merged[-1]['t1'] = c['t1']; merged[-1]['suggest'] += ' + ' + c['suggest'].split(': ', 1)[1]
        else: merged.append(c)
    cutaways = merged[:max(1, int(len(heads) * 0.3))]   # ~25 % of runtime
    # timing: typed-by and the next scene change
    for n, h in enumerate(heads):
        letters = len(re.sub(r'\W', '', h['big']))
        h['typed_t'] = round(h['big_t'] + (letters - 1) / FPS30 + 2 / FPS30, 2)
        nxt = heads[n + 1]['label_t'] if n + 1 < len(heads) else end_t
        nxt_cut = min([c['t0'] for c in cutaways if c['t0'] > h['big_t']] + [nxt])
        h['scene_change_t'] = round(nxt_cut, 2); h['hold'] = round(nxt_cut - h['typed_t'], 2)
        h['ok'] = h['hold'] >= 0.25
        if not h['ok']: h['fix'] = 'shorten the big word or move the next cut later (needs hold >= 0.25 s)'
    devices = []
    for n, c in enumerate(cuts):
        inside = any(cw['t0'] - 0.1 <= c <= cw['t1'] + 0.1 for cw in cutaways)
        dev = 'cutaway' if inside else DEVICES[n % len(DEVICES)]
        devices.append({'t': round(c, 2), 'device': dev, 'sfx': DEVICE_SFX[dev]})
    for h in heads: events += [h['label_t'], h['big_t']]
    events += [c['t'] for c in chest] + [d['t'] for d in devices] + [c['t0'] for c in cutaways] + [0.0]
    events = sorted(set(round(e, 2) for e in events if e is not None))
    gaps = [(round(b - a2, 2), a2) for a2, b in zip(events, events[1:] + [end_t])]
    worst = max(gaps) if gaps else (0, 0)
    first_text = heads[0]['big_t'] if heads else None
    if not any(c['type'] == 'cta_card' for c in chest):          # CTA anywhere in the transcript ("comment BUILD")
        for n, w in enumerate(words[:-1]):
            if clean(w[0]).lower() == 'comment':
                chest.append({'type': 'cta_card', 'text': clean(words[n + 1][0]).upper(), 't': round(w[1], 2), 'head': 'cta'}); break
    cta = next((c for c in chest if c['type'] == 'cta_card'), None)
    checks = [
        ('Hook text on screen in the first 1.0 s', first_text is not None and heads[0]['label_t'] <= 1.0, f"first label {heads[0]['label_t'] if heads else '-'} s, big word {first_text} s"),
        ('Something changes on screen at least every 3 s', worst[0] <= 3.0, f'longest still stretch {worst[0]} s at {worst[1]} s'),
        ('Every headline typed >= 0.25 s before its scene changes', all(h['ok'] for h in heads), f"{sum(not h['ok'] for h in heads)} too tight"),
        ('Length in the 15-90 s sweet spot (3 min max)', 15 <= end_t <= 90, f'{end_t:.1f} s'),
        ('CTA in the last 25 %', bool(cta and cta['t'] >= end_t * 0.75), f"{cta['text'] if cta else 'none'}"),
        (f'Hook `{hook}` not used in the last 5 reels', hook not in recent, f'recent: {", ".join(recent) or "none"}'),
    ]
    return {'brand': a.brand, 'lang': a.lang, 'energy': energy, 'hook': hook, 'hook_sfx': HOOKS[hook][3],
            'music': MUSIC['business' if a.business else energy], 'end_t': round(end_t, 2), 'headlines': heads,
            'chest_row': chest, 'cutaways': cutaways, 'jump_cut_devices': devices, 'checks': checks,
            'loop_tip': 'End on a line that pays off the first line so the replay feels seamless (rewatches count).'}


def ig_caption(plan, words):
    heads = plan['headlines']; sents = [h['sentence'] for h in heads]
    def tidy(x): x = x.strip().rstrip(' ,;'); return (x[0].upper() + x[1:] + ('' if x[-1:] in '.!?' else '.')) if x else x
    line1 = tidy(' '.join(sents[:2])).rstrip('.') + (' 🤯' if plan['energy'] == 'high' else '')
    rest = sents[2:-2] or sents[1:]
    line2 = tidy(' '.join(rest[:2])); line3 = tidy(max(rest[2:] or [''], key=len))
    cta = next((c for c in plan['chest_row'] if c['type'] == 'cta_card'), None)
    line4 = (f'Comment "{cta["text"]}" and I\'ll send it to you 👇' if cta else 'Save this and send it to someone who needs it 👇') + ' · Sources: <official source> · not sponsored'
    from collections import Counter
    names = Counter()                              # product / proper names first, then big words
    for h in heads:
        for m in re.finditer(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)', h['sentence']):
            if m.start() > 0: names[m.group(1).lower().replace(' ', '')] += 1      # skip sentence-initial capitals
    kws = [n for n, _ in names.most_common() if n not in {'google', 'the', 'it', 'you', 'pick', 'bring'}]
    kws += [re.sub(r'[^a-z0-9]', '', h['big'].lower()) for h in heads]
    kws = [k for k in dict.fromkeys(kws) if k and not k.isdigit() and len(k) > 2]
    tags = ['#' + t for t in (kws + ['aitools', 'ai'])[:4]] + ['#aiwithrakshith']
    return '\n'.join([line1, line2, line3, line4, '', ' '.join(dict.fromkeys(tags))]) + '\n\n(DRAFT: tighten each line, verify facts, keep 4 lines + 5 lowercase tags.)\n'


def write_outputs(plan, chunks, words, out):
    os.makedirs(out, exist_ok=True)
    json.dump(plan, open(os.path.join(out, 'edl.json'), 'w'), indent=1, ensure_ascii=False)
    with open(os.path.join(out, 'edl.csv'), 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f); wr.writerow(['t', 'type', 'text', 'detail'])
        wr.writerow([0.0, 'hook', plan['hook'], plan['hook_sfx']])
        rows = []
        for h in plan['headlines']:
            rows += [(h['label_t'], 'label', h['label'], h['id']), (h['big_t'], 'big_word', h['big'], f"typed {h['typed_t']} s, hold {h['hold']} s" + ('' if h['ok'] else ' TOO TIGHT'))]
        rows += [(c['t'], c['type'], c['text'], c['head']) for c in plan['chest_row']]
        rows += [(c['t0'], 'cutaway', f"{c['t0']}-{c['t1']} s", c['suggest']) for c in plan['cutaways']]
        rows += [(d['t'], 'jump_cut', d['device'], d['sfx']) for d in plan['jump_cut_devices']]
        rows += [(round(c['start'], 2), 'caption', c['text'], f"until {c['end']:.2f}") for c in chunks]
        for r in sorted(rows, key=lambda r: (r[0], r[1])): wr.writerow(r)
    write_srt(chunks, os.path.join(out, 'captions.srt'))
    open(os.path.join(out, 'instagram_caption_draft.txt'), 'w', encoding='utf-8').write(ig_caption(plan, words))
    L = [f"# Edit plan ({plan['brand']}, {plan['lang']}) · {plan['end_t']} s · energy **{plan['energy']}**\n",
         f"- **Hook:** `{plan['hook']}` (SFX: {plan['hook_sfx']})", f"- **Music bed:** {plan['music']} (new track, log it)",
         f"- **Loop:** {plan['loop_tip']}\n", '## Checks\n', '| Check | Result | Detail |', '|---|---|---|']
    L += [f"| {c} | {'PASS' if ok else 'FIX'} | {d} |" for c, ok, d in plan['checks']]
    L += ['\n## Headlines (label + big word on its spoken word)\n', '| # | Label at | Label | Big at | BIG WORD | Typed | Hold | Sentence |', '|---|---|---|---|---|---|---|---|']
    L += [f"| {h['id']} | {h['label_t']} | {h['label']} | {h['big_t']} | **{h['big']}** | {h['typed_t']} | {h['hold']}{'' if h['ok'] else ' ⚠'} | {h['sentence']} |" for h in plan['headlines']]
    L += ['\n## Chest row\n'] + [f"- {c['t']} s · {c['type']} · {c['text']}" for c in plan['chest_row']] or ['- none']
    L += ['\n## Cutaways (~25 % of runtime)\n'] + [f"- {c['t0']}-{c['t1']} s · {c['suggest']}" for c in plan['cutaways']]
    L += ['\n## Jump cuts\n'] + [f"- {d['t']} s · {d['device']} · SFX {d['sfx']}" for d in plan['jump_cut_devices']]
    L += ['\n## Captions\n', f'{len(chunks)} chunks → `captions.srt` (burned in; turn OFF Instagram auto-captions so they don\'t double up).']
    open(os.path.join(out, 'plan.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')


def interactive(plan):
    print('\nReview headlines: Enter = keep · type NEW BIG WORD · "label | BIG" to change both · "-" to drop')
    keep = []
    for h in plan['headlines']:
        ans = input(f"[{h['big_t']:>5}s] {h['label']!r} / {h['big']!r}  ({h['sentence']})\n> ").strip()
        if ans == '-': continue
        if '|' in ans: h['label'], h['big'] = [x.strip() for x in ans.split('|', 1)]; h['big'] = h['big'].upper()
        elif ans: h['big'] = ans.upper()
        keep.append(h)
    plan['headlines'] = keep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--words'); ap.add_argument('--phrases'); ap.add_argument('--islands')
    ap.add_argument('--lang', default='en', choices=['en', 'kn']); ap.add_argument('--brand', default='global', choices=['global', 'kannada'])
    ap.add_argument('--energy', default='auto', choices=['auto', 'high', 'medium', 'calm']); ap.add_argument('--business', action='store_true')
    ap.add_argument('--hook'); ap.add_argument('--hook-log', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skill',
                    'aiwithrakshith-kinetic-reel-editor', 'references', 'hook_log.md'))
    ap.add_argument('--glossary'); ap.add_argument('--caption-style', default='karaoke', choices=['karaoke', 'chip'])
    ap.add_argument('--interactive', action='store_true'); ap.add_argument('--out', default='plan')
    a = ap.parse_args()
    isl = load_islands(a.islands); gl = json.load(open(a.glossary)) if a.glossary else {}
    if a.lang == 'kn':
        ph = json.load(open(a.phrases)); ph = [(kn, en, to_reel(s, isl), to_reel(e, isl) or to_reel(s, isl) + 0.3) for kn, en, s, e in ph if to_reel(s, isl) is not None]
        chunks, words = [], []
        for p_ in ph:                                             # one sentence per Kannada phrase
            cs = phrases_to_chunks([p_]); chunks += cs
            ws = [w for c in cs for w in c['words']]
            if ws: ws[-1] = (ws[-1][0].rstrip('.,') + '.', ws[-1][1], ws[-1][2])
            words += ws
    else:
        src = json.load(open(a.words))
        words = [(w, to_reel(s, isl), to_reel(e, isl) or to_reel(s, isl) + 0.2) for w, s, e in src if to_reel(s, isl) is not None]
        chunks = chunk_words(words)
    if gl:
        apply_glossary(chunks, gl)
        words = [w for c in chunks for w in c['words']]
    for c in chunks: c['style'] = a.caption_style
    plan = build_plan(words, isl, a)
    if a.lang == 'kn':                            # Kanglish: Kannada label from the spoken phrase + English big word
        for h in plan['headlines']:
            ph_ = next((p for p in ph if p[2] - 0.05 <= h['big_t'] <= p[3] + 0.05), None)
            if ph_:
                toks = ph_[0].split()
                latin = [(t, i, i) for i, t in enumerate(toks) if re.match(r'^[A-Za-z0-9+.-]{2,}$', t)]
                if latin:                                     # the English term he says, multi-word names kept
                    kw = pick_keyword([(t, 0, 0) for t, _, _ in [('x', 0, 0)] + latin])
                    if kw:
                        h['big'] = kw[3].upper(); first = latin[kw[1] - 1][1]
                        before = [t for t in toks[:first] if re.search('[\u0C80-\u0CFF]', t)]
                        h['label'] = ' '.join(before[-3:]) or h['label']
                if not latin or not h['label'] or not re.search('[\u0C80-\u0CFF]', h['label']):
                    h['label'] = ' '.join([t for t in toks if re.search('[\u0C80-\u0CFF]', t)][:3]) or h['label']
                h['kannada_phrase'] = ph_[0]
    if a.interactive: interactive(plan)
    write_outputs(plan, chunks, words, a.out)
    bad = [c for c, ok, _ in plan['checks'] if not ok]
    print(f"plan written to {a.out}/ · {len(plan['headlines'])} headlines · hook {plan['hook']} · {len(chunks)} caption chunks"
          + (f" · FIX: {'; '.join(bad)}" if bad else ' · all checks pass'))


if __name__ == '__main__':
    main()
