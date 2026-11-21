#!/usr/bin/env python3
"""Split SKILL.md into one reference .md file per section (skill/.../references/), so any LLM or editor can load
just the topic it needs. SKILL.md stays the single source of truth: edit it, then run this script.

  python3 tools/build_skill_refs.py          # (re)write references/*.md
  python3 tools/build_skill_refs.py --check  # exit 1 if references/ is out of date
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SKILL = os.path.join(ROOT, 'skill', 'aiwithrakshith-kinetic-reel-editor')
SRC = os.path.join(SKILL, 'SKILL.md'); OUT = os.path.join(SKILL, 'references')
KEEP = {'hook_log.md'}   # hand-maintained files in references/
NOTE = '<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->\n\n'


def slug(title):
    num = re.match(r'(\d+[a-z]?)\.', title)
    words = re.sub(r"[`().,&—–/:']", ' ', title.split('.', 1)[1] if num else title).lower().split()
    words = [w for w in words if w not in {'the', 'a', 'an', 'and', 'for', 'every', 'per', 'of', 'in', 'is'}][:5]
    n = num.group(1) if num else 'x'
    n = n if not n[-1].isalpha() else n[:-1].zfill(2) + n[-1]
    return f"{n.zfill(2)}-{'-'.join(words)}.md"


def build():
    text = open(SRC, encoding='utf-8').read()
    body = text.split('\n---\n', 1)[1] if text.startswith('---') else text
    parts = re.split(r'(?m)^## ', body)
    files = {}
    for p in parts[1:]:
        title, rest = p.split('\n', 1)
        content = rest.strip().strip('-').strip()
        files[slug(title)] = NOTE + f'# {title.strip()}\n\n{content}\n'
    idx = NOTE + '# Skill references — AI with Rakshith kinetic reel editor\n\nOne file per topic, split from `../SKILL.md`.\n\n'
    idx += '| File | Topic |\n|---|---|\n' + ''.join(f'| [`{k}`]({k}) | {v.splitlines()[2][2:]} |\n' for k, v in sorted(files.items()))
    idx += '| [`hook_log.md`](hook_log.md) | Hooks used per reel (hand-maintained; check before picking a hook) |\n'
    files['README.md'] = idx
    return files


def main():
    files = build(); os.makedirs(OUT, exist_ok=True)
    stale = [f for f in os.listdir(OUT) if f.endswith('.md') and f not in files and f not in KEEP]
    if '--check' in sys.argv:
        bad = stale + [k for k, v in files.items() if not os.path.exists(os.path.join(OUT, k)) or open(os.path.join(OUT, k), encoding='utf-8').read() != v]
        print('references up to date' if not bad else f'out of date: {bad}'); sys.exit(1 if bad else 0)
    for f in stale: os.remove(os.path.join(OUT, f))
    for k, v in files.items(): open(os.path.join(OUT, k), 'w', encoding='utf-8').write(v)
    print(f'wrote {len(files)} files to {OUT}')


if __name__ == '__main__':
    main()
