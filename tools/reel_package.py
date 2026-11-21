#!/usr/bin/env python3
"""Build the publish package for one rendered reel: everything that goes into the Drive day folder.

  python3 tools/reel_package.py --video out.mp4 --job job.json --title "Android Studio BYOA" \
      --caption caption.txt [--qc qc_report.md] [--thumb-t 12.6] [--date 2026-11-21] --out pkg/

Writes pkg/:
  <slug>_60fps.mp4          the reel (copied)
  <slug>_thumbnail.jpg      1080x1920 cover frame (+ <slug>_thumbnail_grid.jpg 1080x1440 3:4 profile-grid crop)
  caption.html              Instagram caption (4 lines + 5 lowercase hashtags), uploaded as a Google Doc
  timeline.html             per-second edit timeline: hook, headlines, scenes, captions, SFX, checks; uploaded as a Google Doc
  qc_report.md              copied; its table is also embedded in the timeline Doc
  manifest.json             what drive_publish.py uploads and where
"""
import os, sys, json, re, shutil, argparse, subprocess, datetime, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.path.join(ROOT, 'engine'))
from templates import TEMPLATES

CSS = ('body{font-family:Arial,sans-serif;font-size:11pt;color:#111} h1{font-size:20pt} h2{font-size:14pt;margin-top:18pt}'
       'table{border-collapse:collapse;width:100%} td,th{border:1px solid #bbb;padding:4pt 6pt;vertical-align:top;font-size:10pt}'
       'th{background:#f1f1f1;text-align:left} .k{color:#E3121B;font-weight:bold}')


def slugify(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')[:48]


def fmt(t): return f'{int(t // 60)}:{t % 60:05.2f}'


def thumbnail(video, t, out, grid_out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', video, '-frames:v', '1', '-q:v', '2', out], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', 'crop=1080:1440:0:240', '-q:v', '2', grid_out], check=True)


def caption_html(title, caption, meta):
    lines = [l for l in caption.strip().splitlines()]
    body = ''.join(f'<p>{html.escape(l) if l.strip() else "&nbsp;"}</p>' for l in lines)
    tags = re.findall(r'#\w+', caption)
    checks = [('4-line caption', len([l for l in lines if l.strip() and not l.strip().startswith('#')]) <= 4),
              ('exactly 5 hashtags', len(tags) == 5), ('hashtags lowercase', all(t == t.lower() for t in tags))]
    rows = ''.join(f'<tr><td>{k}</td><td>{"PASS" if v else "CHECK"}</td></tr>' for k, v in checks)
    mrows = ''.join(f'<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>' for k, v in meta.items())
    return (f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><h1>{html.escape(title)} — Instagram caption</h1>'
            f'<h2>Caption (copy-paste)</h2>{body}<h2>Checks</h2><table>{rows}</table><h2>Post details</h2><table>{mrows}</table>'
            '<p>Burned-in text is never part of the caption. AI label: only if the reel contains photorealistic AI video or audio.</p></body></html>')


def timeline_html(title, job, spec, meta, qc=None):
    ev = [(0.0, 'HOOK', f"{job.get('hook')} (accent {spec['palette']['accent']}) + impact SFX")]
    for h in job.get('headlines', []):
        ev.append((h['label_t'], 'LABEL', h['label'])); ev.append((h['big_t'], 'HEADLINE', h['big']))
    for i, s in enumerate(job.get('scenes', [])):
        what = ' · '.join(x for x in (s.get('kicker'), s.get('title'), s.get('sub'), os.path.basename(s['image']) if s.get('image') else None,
                                      'quote card' if s.get('quote') else None, 'tree: ' + ' / '.join(s['items']) if s.get('items') else None) if x)
        ev.append((s['t0'], f'SCENE {i + 1} IN', what)); ev.append((s['t1'], f'SCENE {i + 1} OUT', 'back to talking head'))
    if job.get('banner'): ev.append((job['banner'][0], 'BANNER', f"{job['banner'][2]} / {job['banner'][3]}"))
    for t in job.get('flash', []): ev.append((t, 'FLASH', 'full-colour word flash'))
    ev.sort(key=lambda e: e[0])
    words = job['words'] if isinstance(job['words'], list) else json.load(open(job['words']))
    from template_render import fix_words
    words = fix_words([tuple(w) for w in words], job.get('glossary'))
    words = [w for w in words if w[1] < job['duration']]
    rows = ''.join(f'<tr><td>{fmt(t)}</td><td class="k">{k}</td><td>{html.escape(str(v))}</td></tr>' for t, k, v in ev)
    sec = {}
    for w, s, e in words: sec.setdefault(int(s), []).append(w)
    srows = ''.join(f'<tr><td>{fmt(k)}</td><td>{html.escape(" ".join(v))}</td></tr>' for k, v in sorted(sec.items()))
    rules = ''.join(f'<li>{r}</li>' for r in [
        '1080x1920, 60 fps, H.264 High + AAC 48 kHz, -14 LUFS, true peak <= -1 dBTP',
        'Readable elements inside the safe zone x 65-960, y 270-1250',
        'Face-clear: no text, card or effect layer on the face oval (FaceZone check on every box)',
        'Captions follow speech (never early); one hook not used in the last 5 reels'])
    mrows = ''.join(f'<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>' for k, v in meta.items())
    return (f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><h1>{html.escape(title)} — edit timeline</h1>'
            f'<table>{mrows}</table><h2>Events</h2><table><tr><th>time</th><th>event</th><th>detail</th></tr>{rows}</table>'
            f'<h2>Spoken words by second</h2><table><tr><th>time</th><th>words</th></tr>{srows}</table><h2>Rules applied</h2><ul>{rules}</ul>'
            + (qc_html(qc) if qc else '') + '</body></html>')


def qc_html(md):
    rows = [l.strip().strip('|').split('|') for l in md.splitlines() if l.startswith('|') and '---' not in l][1:]
    res = next((l.replace('*', '') for l in md.splitlines() if 'Result' in l), '')
    return (f'<h2>QC — {html.escape(res)}</h2><table><tr><th>check</th><th>result</th><th>detail</th></tr>'
            + ''.join('<tr>' + ''.join(f'<td>{html.escape(c.strip().strip("`"))}</td>' for c in r) + '</tr>' for r in rows) + '</table>')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--video', required=True); ap.add_argument('--job'); ap.add_argument('--template', type=int)
    ap.add_argument('--title', required=True); ap.add_argument('--caption', required=True); ap.add_argument('--qc')
    ap.add_argument('--thumb-t', type=float); ap.add_argument('--thumb'); ap.add_argument('--date', default=datetime.date.today().isoformat())
    ap.add_argument('--brand', default='global'); ap.add_argument('--out', required=True); a = ap.parse_args()
    job = json.load(open(a.job)) if a.job else dict(template=a.template or 1, headlines=[], scenes=[], words=[], duration=0, hook='?')
    n = int(job['template']); spec = TEMPLATES[n]; os.makedirs(a.out, exist_ok=True); slug = slugify(a.title)
    vid = os.path.join(a.out, f'{slug}_60fps.mp4'); shutil.copy(a.video, vid)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid], capture_output=True, text=True).stdout)
    if not job.get('duration'): job['duration'] = dur
    th, tg = os.path.join(a.out, f'{slug}_thumbnail.jpg'), os.path.join(a.out, f'{slug}_thumbnail_grid.jpg')
    if a.thumb: shutil.copy(a.thumb, th); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', th, '-vf', 'crop=1080:1440:0:240', tg], check=True)
    else:
        t = a.thumb_t if a.thumb_t is not None else (job['headlines'][-1]['big_t'] + 0.6 if job.get('headlines') else dur * 0.4)
        thumbnail(vid, min(t, dur - 0.1), th, tg)
    meta = {'date': a.date, 'brand': a.brand, 'template': f"/temp-{n} {spec['name']}", 'hook': job.get('hook'), 'duration': f'{dur:.2f} s',
            'video': os.path.basename(vid), 'reference style': spec['ref']}
    cap = open(a.caption).read()
    open(os.path.join(a.out, 'caption.html'), 'w').write(caption_html(a.title, cap, meta))
    open(os.path.join(a.out, 'timeline.html'), 'w').write(timeline_html(a.title, job, spec, meta, open(a.qc).read() if a.qc else None))
    files = [dict(path=os.path.basename(vid), kind='video', mime='video/mp4'), dict(path=os.path.basename(th), kind='thumbnail', mime='image/jpeg'),
             dict(path=os.path.basename(tg), kind='thumbnail_grid', mime='image/jpeg'),
             dict(path='caption.html', kind='caption', mime='text/html', doc_title=f'{a.title} — Caption'),
             dict(path='timeline.html', kind='timeline', mime='text/html', doc_title=f'{a.title} — Timeline')]
    if a.qc:
        shutil.copy(a.qc, os.path.join(a.out, 'qc_report.md'))
        pass  # QC table is inside the timeline Doc; qc_report.md stays in the package folder
    d = datetime.date.fromisoformat(a.date)
    man = dict(title=a.title, slug=slug, date=a.date, brand=a.brand, template=n, hook=job.get('hook'), duration=round(dur, 2),
               drive_path=['Social Media', d.strftime('%Y-%m %B'), f'Day {d.day:02d} - {a.date}', a.title], files=files)
    json.dump(man, open(os.path.join(a.out, 'manifest.json'), 'w'), indent=1)
    print('package ->', a.out, '| drive:', ' / '.join(man['drive_path']))


if __name__ == '__main__':
    main()
