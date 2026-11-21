#!/usr/bin/env python3
"""Build and sync the private Magnific/Freepik asset library (icons, vectors, photos, PSD mockups, templates, videos).

  export MAGNIFIC_API_KEY=...            # your Magnific/Freepik API key (never commit it)
  python3 tools/magnific_library.py build  --plan assets/plan.json --max 95     # licensed downloads, resumable
  python3 tools/magnific_library.py upload                                       # ZIP per theme -> Drive Editing Pack/Magnific Asset Library
  python3 tools/magnific_library.py pull                                         # new machine: Drive library -> work/assets
  python3 tools/magnific_library.py index                                        # rebuild work/assets/asset_index.csv

Rules baked in (do not remove):
- Files come ONLY from the official download endpoints (/v1/icons/{id}/download, /v1/resources/{id}/download,
  /v1/videos/{id}/download) = licensed, watermark-free originals. Preview/thumbnail URLs are never saved.
- AI-generated stock is skipped by default (--allow-ai to include). His reels use no AI generation by the editor.
- The account has a download cap (~100 per window on the Plus plan, seen 21 Nov 2026). --max stops before it;
  a 429 / limit response stops cleanly and the next run resumes from work/assets/manifest.csv.
- Licence: the library stays private (his Drive). Never add the files to the GitHub repo or share the folder
  publicly — Freepik forbids redistributing resources as a downloadable collection.
"""
import os, sys, csv, json, time, glob, zipfile, argparse, subprocess, urllib.parse, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.path.join(ROOT, 'engine'))
from paths import WORK
LIB = os.environ.get('REEL_ASSETS') or os.path.join(WORK, 'assets')
API = os.environ.get('MAGNIFIC_API_BASE', 'https://api.magnific.com')
MANIFEST = os.path.join(LIB, 'manifest.csv'); INDEX = os.path.join(LIB, 'asset_index.csv')
FIELDS = ['id', 'type', 'theme', 'file', 'style', 'licence', 'title', 'source']
DRIVE_LIB_NAME = 'Magnific Asset Library'


class LimitReached(Exception): pass


def api(path, params=None, key=None):
    url = f'{API}{path}' + ('?' + urllib.parse.urlencode(params, doseq=True) if params else '')
    req = urllib.request.Request(url, headers={'x-magnific-api-key': key, 'x-freepik-api-key': key, 'Accept-Language': 'en-US'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'ignore')[:300]
        if e.code == 429 or 'limit' in body.lower(): raise LimitReached(f'{e.code}: {body}')
        if e.code == 403: return {'_skip': body}
        raise


def done_ids():
    if not os.path.exists(MANIFEST): return set()
    return {(r['type'], r['id']) for r in csv.DictReader(open(MANIFEST))}


def record(row):
    new = not os.path.exists(MANIFEST); os.makedirs(LIB, exist_ok=True)
    with open(MANIFEST, 'a', newline='') as f:
        w = csv.DictWriter(f, FIELDS); new and w.writeheader(); w.writerow(row)


def fetch(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as r, open(dest, 'wb') as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)


def search(kind, term, page, key, extra):
    if kind == 'icon': return api('/v1/icons', dict(term=term, page=page, per_page=50, **extra), key)
    if kind == 'video': return api('/v1/videos', dict(term=term, page=page, limit=50, **extra), key)
    return api('/v1/resources', dict(term=term, page=page, limit=50, **{f'filters[content_type][{kind}]': 1}, **extra), key)


def is_ai(item):
    return bool(item.get('ai_generated') or item.get('is_ai_generated') or (item.get('meta') or {}).get('is_ai_generated'))


def build(a):
    key = os.environ.get('MAGNIFIC_API_KEY') or os.environ.get('FREEPIK_API_KEY')
    if not key: sys.exit('set MAGNIFIC_API_KEY (Magnific/Freepik API key) first')
    plan = json.load(open(a.plan)); have = done_ids(); n = 0
    try:
        for job in plan['jobs']:
            kind, theme, term, want = job['type'], job['theme'], job['query'], job['count']
            rows = list(csv.DictReader(open(MANIFEST))) if os.path.exists(MANIFEST) else []
            got = sum(1 for r in rows if r['type'] == kind and r['theme'] == theme)
            page = 1
            while got < want and n < a.max:
                res = search(kind, term, page, key, job.get('params', {})); items = res.get('data') or []
                if not items: break
                for it in items:
                    if got >= want or n >= a.max: break
                    iid = str(it.get('id'))
                    if (kind, iid) in have or (is_ai(it) and not a.allow_ai): continue
                    if kind == 'icon':
                        d = api(f'/v1/icons/{iid}/download', dict(format='svg'), key)
                    elif kind == 'video':
                        d = api(f'/v1/videos/{iid}/download', None, key)
                    else:
                        d = api(f'/v1/resources/{iid}/download', dict(image_size=job.get('image_size', 'original')) if kind == 'photo' else None, key)
                    if '_skip' in d: continue
                    data = d.get('data') or {}; url = data.get('url'); fn = data.get('filename') or f'{iid}'
                    if not url: continue
                    dest = os.path.join(LIB, kind + 's', theme, f'{theme}_{iid}_{os.path.basename(fn)}'.replace(' ', '-'))
                    fetch(url, dest); have.add((kind, iid)); got += 1; n += 1
                    if kind == 'icon' and dest.endswith('.svg'): png512(dest)
                    record(dict(id=iid, type=kind, theme=theme, file=os.path.relpath(dest, LIB), style=job.get('style', ''),
                                licence='Magnific/Freepik subscriber licence (premium)' if it.get('premium') or (it.get('licenses') or [{}])[0].get('type') == 'premium' else 'Magnific/Freepik subscriber licence',
                                title=(it.get('title') or it.get('name') or '')[:120], source=f'magnific:{kind}:{iid}'))
                    print(f'{n:4d} {kind:6s} {theme:14s} {os.path.basename(dest)}', flush=True)
                    time.sleep(a.sleep)
                page += 1
    except LimitReached as e:
        print(f'\nDownload limit reached ({e}). Saved {n} this run. Re-run later - it resumes from {MANIFEST}.')
    index(); print(f'downloaded {n} this run; library has {sum(1 for _ in open(MANIFEST)) - 1 if os.path.exists(MANIFEST) else 0} files')


def png512(svg):
    out = svg.replace('/icons/', '/icons_png512/')[:-4] + '.png'; os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        import cairosvg; cairosvg.svg2png(url=svg, write_to=out, output_width=512, output_height=512)
    except Exception:
        subprocess.run(['rsvg-convert', '-w', '512', '-h', '512', '-o', out, svg], check=False)


def index():
    rows = list(csv.DictReader(open(MANIFEST))) if os.path.exists(MANIFEST) else []
    with open(INDEX, 'w', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); [w.writerow(r) for r in rows]
    return INDEX


def zips(max_mb=25):
    """ZIP per <type>/<theme>, split so each ZIP stays under max_mb (Drive API has no small limit; the Claude
    connector does: use --max-mb 3 when uploading through it)."""
    out = os.path.join(LIB, '_zips'); os.makedirs(out, exist_ok=True); made = []
    for tdir in sorted(glob.glob(os.path.join(LIB, '*s', '*'))):
        if '_zips' in tdir or not os.path.isdir(tdir): continue
        typ, theme = tdir.split(os.sep)[-2], tdir.split(os.sep)[-1]; files = sorted(glob.glob(os.path.join(tdir, '*')))
        png_dir = tdir.replace('/icons/', '/icons_png512/'); files += sorted(glob.glob(os.path.join(png_dir, '*'))) if typ == 'icons' else []
        part, size, z = 1, 0, None
        for p in files:
            s = os.path.getsize(p)
            if z is None or size + s > max_mb * 1e6:
                if z: z.close()
                zp = os.path.join(out, f'{typ}_{theme}_{part:02d}.zip'); z = zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED); made.append(zp); part += 1; size = 0
            z.write(p, os.path.join(theme, 'png512' if 'png512' in p else os.path.splitext(p)[1][1:], os.path.basename(p))); size += s
        if z: z.close()
    return made


def upload(a):
    sys.path.insert(0, os.path.dirname(__file__)); import drive_publish as dp
    svc = dp.service(); di = json.load(open(os.path.join(ROOT, 'memory', 'drive_index.json')))
    root = di.get('asset_library', {}).get('id')
    if not root:
        ep = dp.find(svc, 'Editing Pack', 'root', dp.FOLDER) or {'id': 'root'}; root = dp.folder(svc, DRIVE_LIB_NAME, ep['id'])['id']
    for zp in zips(a.max_mb):
        typ = os.path.basename(zp).split('_')[0].capitalize(); fo = dp.folder(svc, typ, root)
        r = dp.upload(svc, zp, os.path.basename(zp), fo['id'], 'application/zip'); print('up', r['name'])
    r = dp.upload(svc, index(), 'Asset Index', root, 'text/csv', as_doc=False); print('index', r.get('webViewLink'))


def pull(a):
    """Download the Drive library (ZIPs) into work/assets and unpack — run on any new machine before rendering."""
    sys.path.insert(0, os.path.dirname(__file__)); import drive_publish as dp
    from googleapiclient.http import MediaIoBaseDownload
    import io
    svc = dp.service(); di = json.load(open(os.path.join(ROOT, 'memory', 'drive_index.json'))); root = di['asset_library']['id']
    def walk(fid):
        for f in svc.files().list(q=f"'{fid}' in parents and trashed=false", fields='files(id,name,mimeType)').execute().get('files', []):
            if f['mimeType'] == dp.FOLDER: yield from walk(f['id'])
            else: yield f
    for f in walk(root):
        if not f['name'].endswith(('.zip', '.jpg', '.png', '.mp4')): continue
        dest = os.path.join(LIB, '_drive', f['name']); os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest): continue
        req = svc.files().get_media(fileId=f['id']); fh = io.FileIO(dest, 'wb'); dl = MediaIoBaseDownload(fh, req)
        while not dl.next_chunk()[1]: pass
        if dest.endswith('.zip'):
            typ = f['name'].split('_')[0]; zipfile.ZipFile(dest).extractall(os.path.join(LIB, typ if typ.endswith('s') else typ + 's'))
        print('pulled', f['name'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['build', 'upload', 'pull', 'index'])
    ap.add_argument('--plan', default=os.path.join(ROOT, 'assets', 'plan.json')); ap.add_argument('--max', type=int, default=95)
    ap.add_argument('--sleep', type=float, default=0.5); ap.add_argument('--allow-ai', action='store_true'); ap.add_argument('--max-mb', type=float, default=25)
    a = ap.parse_args()
    {'build': build, 'upload': upload, 'pull': pull, 'index': lambda a: print(index())}[a.cmd](a)
