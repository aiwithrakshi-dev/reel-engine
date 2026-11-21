"""Asset resolver: templates ask for 'icon:ai/3' or assets.icon('money', 2) and get a clean RGBA layer from the private
library (work/assets, synced from Drive by tools/magnific_library.py pull). Never reads preview/thumbnail URLs.

  from assets import icon, image, pick
  icon('ai', 0, size=96)                       # first AI icon, 96 px RGBA
  icon('social', 3, size=84, tint='#FFFFFF')   # outline icon recoloured white for dark templates
  pick('icon:money/2')                         # job-file reference
  image('vectors/tech-bg', 0)                  # RGB background (numpy float)
"""
import os, csv, glob, functools
import numpy as np
from PIL import Image
from paths import WORK
LIB = os.environ.get('REEL_ASSETS') or os.path.join(WORK, 'assets')


@functools.lru_cache(None)
def rows():
    p = os.path.join(LIB, 'asset_index.csv')
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def files(kind, theme):
    r = [x for x in rows() if x['type'] == kind and x['theme'] == theme]
    if r: return [os.path.join(LIB, x['file']) for x in r]
    return sorted(glob.glob(os.path.join(LIB, kind + 's', theme, '*')))


def _hex(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


@functools.lru_cache(512)
def icon(theme, n=0, size=128, tint=None):
    fs = files('icon', theme)
    if not fs: raise FileNotFoundError(f'no icons for theme "{theme}" in {LIB} - run tools/magnific_library.py pull')
    src = fs[n % len(fs)]; png = src.replace(os.sep + 'icons' + os.sep, os.sep + 'icons_png512' + os.sep)[:-4] + '.png'
    if src.endswith('.svg') and not os.path.exists(png):
        os.makedirs(os.path.dirname(png), exist_ok=True)
        try:
            import cairosvg; cairosvg.svg2png(url=src, write_to=png, output_width=512, output_height=512)
        except Exception:
            os.system(f'rsvg-convert -w 512 -h 512 -o "{png}" "{src}"')
    im = Image.open(png if src.endswith('.svg') else src).convert('RGBA').resize((size, size), Image.LANCZOS)
    a = np.asarray(im).copy()
    if tint: a[..., :3] = _hex(tint)
    return a


def image(kind_theme, n=0):
    kind, theme = kind_theme.split('/', 1); kind = kind.rstrip('s')
    fs = [f for f in files(kind, theme) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not fs: raise FileNotFoundError(f'no {kind_theme} images in {LIB}')
    return np.asarray(Image.open(fs[n % len(fs)]).convert('RGB')).astype(np.float32)


def pick(ref, size=96, tint=None):
    """'icon:ai/3' -> RGBA icon; 'vector:tech-bg/0' / 'photo:studio-desk/2' -> file path."""
    kind, rest = ref.split(':', 1); theme, _, n = rest.partition('/'); n = int(n or 0)
    if kind == 'icon': return icon(theme, n, size, tint)
    fs = files(kind, theme); return fs[n % len(fs)]


def available():
    out = {}
    for r in rows(): out.setdefault(r['type'], {}).setdefault(r['theme'], 0); out[r['type']][r['theme']] += 1
    return out
