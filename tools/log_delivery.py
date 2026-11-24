#!/usr/bin/env python3
"""Log a delivered template reel: hook_log.md row (newest first) + memory/content_log.json + rebuilt CONTEXT.md.

  python3 tools/log_delivery.py <reel_dir> [--date YYYY-MM-DD] [--energy high] [--notes "..."]

Reads <reel_dir>/job.json (title, template, hook, duration, music, headlines). Run it right after the audit passes,
so the next reel's qc_audit sees this hook as used.
"""
import sys, os, json, argparse, datetime, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import memory

ap = argparse.ArgumentParser(); ap.add_argument('reel_dir'); ap.add_argument('--date', default=datetime.date.today().isoformat())
ap.add_argument('--energy', default='high'); ap.add_argument('--notes', default=''); ap.add_argument('--brand', default='aiwithrakshith.global')
a = ap.parse_args()
job = json.load(open(os.path.join(a.reel_dir, 'job.json')))
music = os.path.splitext(os.path.basename(job.get('music', '')))[0]
title = job.get('title') or os.path.basename(os.path.abspath(a.reel_dir))
row = (f"| {a.date} | {title} (/temp-{job['template']}) | {a.brand} / English | {a.energy} | `{job['hook']}` | "
       f"music {music}, ~20 dB under the voice{('; ' + a.notes) if a.notes else ''} |\n")
p = os.path.join(HERE, '..', 'skill', 'aiwithrakshith-kinetic-reel-editor', 'references', 'hook_log.md')
lines = open(p).read().splitlines(keepends=True)
i = next(k for k, l in enumerate(lines) if l.startswith('|---')) + 1
if row not in lines: lines.insert(i, row)
open(p, 'w').write(''.join(lines))
memory.log_reel(dict(date=a.date, title=title, brand=a.brand, lang='en', template=job['template'], hook=job['hook'],
                     duration=job['duration'], notes=(f'music {music}. ' + a.notes).strip(),
                     headlines=[h['big'] for h in job.get('headlines', [])]))
subprocess.run([sys.executable, os.path.join(HERE, 'memory.py'), 'context'], check=False, capture_output=True)
print('logged', title, job['hook'])
