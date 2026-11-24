#!/usr/bin/env python3
"""Build a template job.json from tools/prep_reel.py output + a short plan (batch-friendly).

  python3 tools/make_job.py <reel_dir> plan.json            -> <reel_dir>/job.json

plan.json: {template, hook, music, title, word_fix: {"index": "text"}, glossary,
            headlines: [{label, big, label_t, big_t}], scenes: [{t0, t1, image, title, credit?, in?}], sfx: {...}}
Computes: face zone in reel px (incl. the punch-in growth), dy, punch cut list, headline 'until' + type-on speed
(so every word is typed >= 0.25 s before the next beat), reel duration (VO end + 0.82 s hard ending), end hit.
"""
import sys, os, json, math

rd, planp = sys.argv[1], sys.argv[2]
prep = json.load(open(os.path.join(rd, 'prep.json'))); plan = json.load(open(planp))
words = json.load(open(os.path.join(rd, 'words.json')))
for k, v in plan.get('word_fix', {}).items(): words[int(k)][0] = v
words = [w for w in words if w[0].strip()]
vo_end = max(w[2] for w in words)
dur = round(vo_end + 0.82, 3)
f = prep['face_src']; scale = plan.get('punch_scale', 1.06)
# move him as low as the chin rule allows (chin <= 1100): a taller HEAD band = bigger keywords, cap stays >= 505
dy = int(max(prep['dy'], min(1100 - f['chin'], 220)))
cy = (f['cap_top'] + f['chin']) / 2; grow = math.ceil((scale - 1) * (cy - f['cap_top'])) + 2
growx = math.ceil((scale - 1) * (f['x1'] - f['x0']) / 2) + 2
cuts = [c for c in prep['cuts'] if 0.3 < c < vo_end]
heads = sorted(plan['headlines'], key=lambda h: h['label_t'])
bounds = sorted([h['label_t'] for h in heads] + [s['t0'] for s in plan.get('scenes', [])] + [dur])
for h in heads:
    nxt = min([b for b in bounds if b > h['label_t'] + 1e-3] + [dur]); h['until'] = round(nxt, 3)
    n = len(h['big'].replace(' ', ''))
    room = (nxt - 0.25 - h['big_t']) * 30          # 30-fps frames available to type it
    h['step'] = round(max(0.4, min(1.0, (room - 2) / max(1, n - 1))), 3)
    if h['big_t'] > nxt - 0.3: raise SystemExit(f"headline {h['big']}: big_t {h['big_t']} too close to the next beat {nxt}")
job = dict(template=plan.get('template', 1), hook=plan['hook'], title=plan.get('title', ''),
           aroll=os.path.join(rd, 'aroll_tight.mp4'), src_fps=prep['fps'], duration=dur, dy=dy,
           face=dict(cap_top=f['cap_top'] + dy - grow, chin=f['chin'] + dy + grow, x0=f['x0'] - growx, x1=f['x1'] + growx),
           face_src_c=prep['face_src_c'], punch=cuts, punch_scale=scale,
           words=words, glossary=plan.get('glossary', {}), headlines=heads, scenes=plan.get('scenes', []),
           vo=os.path.join(rd, 'vo.wav'), music=plan['music'], music_db=plan.get('music_db', -27),
           sfx=plan.get('sfx', {}), end_hit=round(vo_end + 0.28, 3), caption_px=plan.get('caption_px', 50))
json.dump(job, open(os.path.join(rd, 'job.json'), 'w'), indent=1)
print('job', rd, 'dur', dur, 'dy', dy, 'cap_top', job['face']['cap_top'], 'chin', job['face']['chin'], 'cuts', len(cuts),
      'heads', len(heads), 'scenes', len(job['scenes']))
