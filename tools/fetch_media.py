#!/usr/bin/env python3
"""Download official media (og:image + large content images / mp4 / gif / webp) from a product page or blog post.

  python3 tools/fetch_media.py <url> <out_dir> [--max 12] [--minw 700]

B-roll priority 2 (SKILL.md §7): the product's own blog / docs / press page. Files are saved as-is (no previews, no
watermark removal); a sources.csv records file -> page URL so the reel can credit the source on screen.
Writes a contact sheet out_dir/sheet.jpg so you can pick the right shot by looking.
"""
import sys, os, re, csv, argparse, html, urllib.parse, subprocess
import numpy as np, cv2

ap = argparse.ArgumentParser(); ap.add_argument('url'); ap.add_argument('out'); ap.add_argument('--max', type=int, default=12)
ap.add_argument('--minw', type=int, default=700); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'

def get(url, path):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '-A', UA, '-o', path, '-w', '%{http_code}', url], capture_output=True, text=True)
    return r.stdout.strip() == '200' and os.path.exists(path) and os.path.getsize(path) > 2000

page = os.path.join(a.out, '_page.html')
if not get(a.url, page): sys.exit(f'could not fetch {a.url}')
src = open(page, encoding='utf-8', errors='ignore').read()
cands = []
for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)(?::src)?["\'][^>]*content=["\']([^"\']+)', src, re.I): cands.append(m.group(1))
for m in re.finditer(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\'](?:og:image|twitter:image)', src, re.I): cands.append(m.group(1))
for m in re.finditer(r'(?:src|data-src|poster)=["\']([^"\']+\.(?:png|jpe?g|webp|gif|mp4|webm)(?:\?[^"\']*)?)["\']', src, re.I): cands.append(m.group(1))
for m in re.finditer(r'srcset=["\']([^"\']+)["\']', src, re.I):
    parts = [p.strip().split(' ')[0] for p in m.group(1).split(',') if p.strip()]
    if parts: cands.append(parts[-1])                       # largest rendition
seen = set(); urls = []
for c in cands:
    u = urllib.parse.urljoin(a.url, html.unescape(c))
    k = re.sub(r'\?.*$', '', u)
    if k in seen or any(x in k.lower() for x in ('logo', 'favicon', 'icon', 'avatar', 'sprite', 'pixel', 'badge')): continue
    seen.add(k); urls.append(u)

rows = []; thumbs = []
for i, u in enumerate(urls):
    if len(rows) >= a.max: break
    ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower() or '.jpg'
    if ext not in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.mp4', '.webm'): ext = '.jpg'
    p = os.path.join(a.out, f'm{i:02d}{ext}')
    if not get(u, p): continue
    if ext in ('.mp4', '.webm', '.gif'):
        cap = cv2.VideoCapture(p); n = cap.get(cv2.CAP_PROP_FRAME_COUNT); cap.set(cv2.CAP_PROP_POS_FRAMES, int(n // 3)); ok, im = cap.read()
    else:
        if ext == '.webp' or ext == '.gif':
            q = p + '.png'; subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-frames:v', '1', q]); im = cv2.imread(q)
        else: im = cv2.imread(p)
        ok = im is not None
    if not ok or im is None or im.shape[1] < a.minw: os.remove(p); continue
    rows.append((os.path.basename(p), u, a.url, im.shape[1], im.shape[0]))
    t = cv2.resize(im, (360, int(360 * im.shape[0] / im.shape[1])))[:300]
    t = cv2.copyMakeBorder(t, 0, 300 - t.shape[0], 0, 0, cv2.BORDER_CONSTANT); cv2.putText(t, os.path.basename(p), (8, 28), 0, 0.8, (0, 255, 255), 2)
    thumbs.append(t)
with open(os.path.join(a.out, 'sources.csv'), 'a', newline='') as f: csv.writer(f).writerows(rows)
if thumbs:
    while len(thumbs) % 3: thumbs.append(np.zeros_like(thumbs[0]))
    sheet = np.vstack([np.hstack(thumbs[i:i + 3]) for i in range(0, len(thumbs), 3)]); cv2.imwrite(os.path.join(a.out, 'sheet.jpg'), sheet)
print(len(rows), 'files ->', a.out)
for r in rows: print(r[0], r[3], 'x', r[4], r[1][:110])
