#!/usr/bin/env python3
"""Fails if a text layer is composited without going through the alignment guard (self.check) on the same or next line.
Decorative layers that are intentionally unchecked must carry the comment  # guard: decorative"""
import re, sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bad = []
for fn in ('engine/template_render.py', 'engine/template_styles_b.py'):
    lines = open(os.path.join(ROOT, fn)).read().splitlines()
    for i, l in enumerate(lines):
        if re.search(r'comp\(c, (T\.)?text\(|comp\(c, lay,|comp\(c, cut,|comp\(c, lab,|comp\(c, squeeze\(', l) and 'guard: decorative' not in l and not l.lstrip().startswith('def '):
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if 'check(' not in l and 'check(' not in nxt: bad.append(f'{fn}:{i + 1}: {l.strip()[:110]}')
print('\n'.join(bad) or 'guard lint: every text layer is checked'); sys.exit(1 if bad else 0)
