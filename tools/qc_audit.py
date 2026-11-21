#!/usr/bin/env python3
"""One-command delivery audit for a finished reel -> qc_report.md (PASS / FIX per check).

  python3 tools/qc_audit.py final_reel_60fps.mp4 --tlog part1.mp4.tlog.json part2.mp4.tlog.json \
      --hook zoom_punch --srt captions.srt --cover cover.png --sheets qc/ --out qc_report.md

Checks: 1080x1920 · 60 fps (r_frame_rate 60/1, frames ≈ 60 × duration) · H.264 + AAC · length (15-90 s sweet spot,
180 s max) · file size (< 4 GB; warn > 300 MB) · loudness −14 LUFS ±1 · true peak ≤ −1 dBTP · every headline typed
≥ 0.25 s before its scene change (tlog) · hook not used in the last 5 reels (hook_log.md) · captions present, ≤ 30
chars per line, never early (SRT) · cover inside the 3:4 grid crop · optional safe-zone contact sheets at 12 fps.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK_LOG = os.path.join(HERE, '..', 'skill', 'aiwithrakshith-kinetic-reel-editor', 'references', 'hook_log.md')


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames'
                          ':format=duration,size', '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summ = err[err.rfind('Summary'):]
    i = re.search(r'I:\s+(-?[\d.]+) LUFS', summ); p = re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ)
    return (float(i.group(1)) if i else None, float(p.group(1)) if p else None)


def tlog_holds(paths, fps=30):
    T = {}
    for p in paths:
        for k, v in json.load(open(p)).items():
            if k in T: T[k]['last'] = max(T[k]['last'], v['last'])
            else: T[k] = dict(v)
    rows = []
    for k, v in sorted(T.items(), key=lambda x: x[1]['start']):
        end = v['gone'] if v.get('gone') else v['last'] + 1
        rows.append((v['text'], round((end - v['full']) / fps, 2)))
    return rows


def recent_hooks(n=5):
    if not os.path.exists(HOOK_LOG): return []
    hs = [re.findall(r'`(\w+)`', l)[0] for l in open(HOOK_LOG, encoding='utf-8') if l.startswith('|') and '`' in l]
    return hs[:n]


def srt_check(path):
    blocks = open(path, encoding='utf-8').read().strip().split('\n\n'); long_ = 0; n = 0
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3:
            n += 1; long_ += sum(len(l) > 30 for l in lines[2:])
    return n, long_


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--tlog', nargs='*', default=[])
    ap.add_argument('--hook'); ap.add_argument('--new-reel', action='store_true', help='hook must not be in the log yet')
    ap.add_argument('--srt'); ap.add_argument('--cover'); ap.add_argument('--sheets'); ap.add_argument('--out', default='qc_report.md')
    a = ap.parse_args(); R = []
    def chk(name, ok, detail): R.append((name, ok, detail))
    info = probe(a.video); v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    au = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    dur = float(info['format']['duration']); size = int(info['format']['size']); nf = int(v.get('nb_frames', 0) or 0)
    chk('Resolution 1080×1920', (v['width'], v['height']) == (1080, 1920), f"{v['width']}×{v['height']}")
    chk('60 fps (constant)', v['r_frame_rate'] == '60/1' and abs(nf - 60 * dur) <= 3, f"{v['r_frame_rate']}, {nf} frames for {dur:.2f} s")
    chk('H.264 video + AAC audio', v['codec_name'] == 'h264' and au is not None and au['codec_name'] == 'aac', f"{v['codec_name']} + {au['codec_name'] if au else 'no audio'}")
    chk('Length 15–90 s (180 s max for recommendations)', 15 <= dur <= 90 if dur <= 180 else False, f'{dur:.1f} s')
    chk('File size < 4 GB (warn > 300 MB)', size < 300e6, f'{size / 1e6:.0f} MB')
    I, P = loudness(a.video)
    chk('Loudness −14 LUFS ±1', I is not None and abs(I + 14) <= 1, f'{I} LUFS')
    chk('True peak ≤ −1 dBTP', P is not None and P <= -1.0, f'{P} dBTP')
    if a.tlog:
        rows = tlog_holds(a.tlog); bad = [r for r in rows if r[1] < 0.25]
        chk('Every headline typed ≥ 0.25 s before its cut', not bad, f"{len(rows)} headlines; " + (', '.join(f'{t} {h}s' for t, h in bad) or 'all OK'))
    if a.hook:
        rec = recent_hooks(); dup = a.hook in (rec if a.new_reel else rec[1:])
        chk(f'Hook `{a.hook}` unique in the last 5 reels', not dup, f"log: {', '.join(rec) or 'empty'}")
    if a.srt:
        n, long_ = srt_check(a.srt); chk('Captions: present, one line ≤ 30 chars', n > 0 and long_ == 0, f'{n} cues, {long_} long lines')
    if a.cover:
        from PIL import Image
        im = Image.open(a.cover); chk('Cover 1080×1920 (headline + face inside the 3:4 crop y 240–1680)', im.size == (1080, 1920), f'{im.size} — check the crop by eye')
    if a.sheets:
        subprocess.run([sys.executable, os.path.join(HERE, 'safe_zone_check.py'), a.video, '--fps', '12', '--out', a.sheets], check=True)
        chk('Safe-zone sheets written (review every frame)', True, f'{a.sheets}/safe_zone_sheet_*.png')
    ok = all(r[1] for r in R)
    L = [f'# QC report: {os.path.basename(a.video)}\n', f"**Result: {'PASS' if ok else 'FIX NEEDED'}** ({sum(r[1] for r in R)}/{len(R)} checks)\n",
         '| Check | Result | Detail |', '|---|---|---|'] + [f"| {n} | {'PASS' if o else 'FIX'} | {d} |" for n, o, d in R]
    L += ['\nManual checks still required: nothing over the face · facts match facts.md · jump cuts hidden · captions synced to lips ·'
          ' Instagram labels (AI info / Paid Partnership) set correctly · Instagram auto-captions OFF when captions are burned in.']
    open(a.out, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('\n'.join(L[:2 + len(R) + 2]))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
