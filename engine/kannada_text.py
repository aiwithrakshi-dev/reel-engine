# Kannada / Kanglish text for headlines and labels (Noto Sans Kannada + Inter Tight, RAQM shaping).
#
# - Mixed strings ("Codex ಈಗ", "Android Studio ಒಳಗೆ") are split into script runs: Kannada runs use Noto Sans Kannada,
#   Latin runs use Inter Tight, so English product names keep the brand font.
# - Reveal per grapheme cluster (never per code point) so conjuncts like ಕ್ಷ / ಸ್ಟ never break mid-type.
# - 10° shear gives the italic brand look (Noto Sans Kannada has no italic).
#
#   from kannada_text import render_text, clusters, reveal
#   lay = render_text('Codex ಈಗ', size=52, color=(255,255,255))     # RGBA float32 layer (0..1)
#   for n in range(len(clusters(s)) + 1): part = reveal(s, n)        # type-on, one cluster per frame
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
try:
    import regex
except ImportError:  # pip install regex
    regex = None

_HERE = os.path.dirname(os.path.abspath(__file__))
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import FONT_DIRS
KN = re.compile(r'[ಀ-೿‌‍]')
RAQM = ImageFont.Layout.RAQM if features.check('raqm') else ImageFont.Layout.BASIC


def _find(name):
    for d in FONT_DIRS:
        if d and os.path.exists(os.path.join(d, name)): return os.path.join(d, name)
    raise FileNotFoundError(f'{name} not found; put NotoSansKannada[wdth,wght].ttf and InterTight in work/fonts')


_fc = {}
def _font(kind, size, weight):
    k = (kind, size, weight)
    if k not in _fc:
        name = 'NotoSansKannada%5Bwdth,wght%5D.ttf' if kind == 'kn' else 'InterTight-Italic%5Bwght%5D.ttf'
        f = ImageFont.truetype(_find(name), size, layout_engine=RAQM)
        try: f.set_variation_by_axes([weight, 100] if kind == 'kn' else [weight])   # Noto axes: Weight, Width
        except Exception: pass
        _fc[k] = f
    return _fc[k]


def clusters(text):
    """Grapheme clusters for type-on. Unicode's extended clusters split Kannada conjuncts at the virama (ಕ್ + ಷೇ),
    so a cluster ending in virama (U+0CCD) is joined with the next one (unless a ZWNJ follows)."""
    if regex is not None:
        base = regex.findall(r'\X', text); out = []
        for c in base:
            if out and out[-1].endswith('\u0CCD') and not c.startswith('\u200C') and KN.match(c[0]): out[-1] += c
            else: out.append(c)
        return out
    out = []                                          # fallback: attach combining marks / virama to the previous base
    for ch in text:
        if out and (0x0CBC <= ord(ch) <= 0x0CD6 or ch in '‌‍' or (out[-1].endswith('್'))): out[-1] += ch
        else: out.append(ch)
    return out


def reveal(text, n):
    return ''.join(clusters(text)[:n])


def runs(text):
    """Split into (script, chunk) runs: 'kn' for Kannada, 'lat' for everything else (spaces join the previous run)."""
    out = []
    for ch in text:
        s = 'kn' if KN.match(ch) else ('sp' if ch.isspace() else 'lat')
        if s == 'sp' and out: out[-1][1] += ch; continue
        if out and out[-1][0] == s: out[-1][1] += ch
        else: out.append([s if s != 'sp' else 'lat', ch])
    return [(a, b) for a, b in out]


def render_text(text, size=52, color=(255, 255, 255), weight=500, shear=10, shadow=True, stroke=0, stroke_color=(10, 8, 10)):
    """Render a Kannada / English / mixed string to an RGBA float layer (0..1), baseline-aligned, sheared."""
    parts = runs(text)
    fonts = [_font(k, int(size * (1.0 if k == 'lat' else 1.02)), weight + (100 if k == 'kn' else 0)) for k, _ in parts]
    asc = max(f.getmetrics()[0] for f in fonts); desc = max(f.getmetrics()[1] for f in fonts)
    widths = [f.getlength(t) for f, (_, t) in zip(fonts, parts)]
    pad = int(size * 0.5) + stroke; w = int(sum(widths)) + 2 * pad; h = asc + desc + 2 * pad
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    def draw(img, dx, dy, fill, sw=0):
        d = ImageDraw.Draw(img); x = pad
        for f, (_, t), wd in zip(fonts, parts, widths):
            d.text((x + dx, pad + asc + dy), t, font=f, fill=fill, anchor='ls', stroke_width=sw, stroke_fill=stroke_color + (255,)); x += wd
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); draw(sh, 2, 4, (0, 0, 0, 160)); im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(3)))
    draw(im, 0, 0, tuple(color) + (255,), stroke)
    if shear:
        k = np.tan(np.radians(shear)); ow = int(w + h * k)   # top leans right, baseline row stays put
        im = im.transform((ow, h), Image.AFFINE, (1, k, -k * h, 0, 1, 0), resample=Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255


def has_kannada(text):
    return bool(KN.search(text))
