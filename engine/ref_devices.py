# Devices from Rakshith's reference reel ("ChatGPT GIF update", Nov 2026), in the house palette.
# Each returns / draws onto a float32 canvas (H x W x 3, 0..255) and keeps inside the safe zone x 65-960, y 270-1250.
#
#   slate(canvas)                                   dark slate full-frame background (for UI / card scenes)
#   news_stack(canvas, items, f, f0, cx, y0)        stacked news cards popping in, red "NEW" sticker on the first
#   face_grid(canvas, imgs, f, f0, cols, box)       grid of photos popping in one by one (2 frames apart)
#   badge(canvas, text, f, f0, cx, cy)              big red badge ("FREE") with overshoot pop
#   prompt_card(canvas, text, f, f0, box, mention)  dark prompt bubble typing 2 chars/frame, @mention in a red chip
# f / f0 are 30-fps-unit frame numbers (at 60 fps pass f = g // 2) so the steps stay snappy.
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from captions import font

W, H = 1080, 1920
RED = (0xE3, 0x12, 0x1B)
POP = [0.0, 0.62, 1.08, 1.0]


def _paste(canvas, rgba, cx, cy, s=1.0):
    if s <= 0: return
    im = Image.fromarray(rgba) if isinstance(rgba, np.ndarray) else rgba
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255; h, w = a.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2); x1, y1 = x0 + w, y0 + h
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if cx1 <= cx0 or cy1 <= cy0: return
    sub = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; al = sub[..., 3:4]
    canvas[cy0:cy1, cx0:cx1] = canvas[cy0:cy1, cx0:cx1] * (1 - al) + sub[..., :3] * 255 * al


def _pop(f, f0):
    a = f - f0
    return 0.0 if a < 0 else POP[min(a, 3)]


def slate(canvas, seed=0):
    """Dark blue-grey slate (#171B21 → #0E1115 vignette) with fine noise: the reference reel's UI/card background."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 540) / 900) ** 2 + ((yy - 820) / 1300) ** 2)
    base = np.clip(1 - d * 0.6, 0.35, 1)[..., None] * np.array((23, 27, 33), np.float32)
    canvas[:] = base + np.random.default_rng(seed).normal(0, 2.2, (H, W, 1)).astype(np.float32)


def _card(w, h, title, sub, new=False, radius=18):
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((24, 28, w + 24, h + 28), radius, fill=(0, 0, 0, 110)); im = im.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, w + 20, h + 20), radius, fill=(246, 246, 248, 255))
    d.text((44, 38), sub.upper(), font=font(700, 20, False), fill=RED + (255,))
    y = 66
    for line in _wrap(title, font(800, 34, False), w - 48):
        d.text((44, y), line, font=font(800, 34, False), fill=(20, 20, 24, 255)); y += 42
    if new:
        st = Image.new('RGBA', (120, 56), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((4, 4, 116, 52), 10, fill=RED + (255,)); sd.text((18, 10), 'NEW', font=font(900, 32, True), fill=(255, 255, 255, 255))
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC); im.alpha_composite(st, (w - 70, 0))
    return im


def _wrap(text, f, maxw):
    lines, cur = [], ''
    for wd in text.split():
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    return lines + ([cur] if cur else [])


_cache = {}
def news_stack(canvas, items, f, f0, cx=512, y0=420, w=820, step=3, gap=14):
    """items: [(source_label, headline), ...] newest first. Cards pop in `step` frames apart; first gets a NEW sticker."""
    y = y0
    for i, (src, title) in enumerate(items):
        k = ('news', i, src, title, w)
        if k not in _cache: _cache[k] = _card(w, 64 + 42 * len(_wrap(title, font(800, 34, False), w - 48)), title, src, new=(i == 0))
        im = _cache[k]; _paste(canvas, im, cx, y + im.height / 2, _pop(f, f0 + step * i)); y += im.height - 40 + gap


def face_grid(canvas, imgs, f, f0, cols=3, box=(110, 420, 930, 1100), step=2, gap=14, radius=16):
    """imgs: list of RGB uint8 arrays. Cells pop in one by one (reading order)."""
    rows = (len(imgs) + cols - 1) // cols; cw = (box[2] - box[0] - gap * (cols - 1)) / cols; ch = (box[3] - box[1] - gap * (rows - 1)) / rows
    for i, src in enumerate(imgs):
        r, c = divmod(i, cols); k = ('cell', id(src), int(cw), int(ch))
        if k not in _cache:
            h0, w0 = src.shape[:2]; s = max(cw / w0, ch / h0); im = cv2.resize(src, (int(w0 * s) + 1, int(h0 * s) + 1), interpolation=cv2.INTER_AREA)
            oy, ox = (im.shape[0] - int(ch)) // 2, (im.shape[1] - int(cw)) // 2; im = im[oy:oy + int(ch), ox:ox + int(cw)]
            m = Image.new('L', (int(cw), int(ch)), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, int(cw) - 1, int(ch) - 1), radius, fill=255)
            p = Image.fromarray(im).convert('RGBA'); p.putalpha(m); fr = Image.new('RGBA', (int(cw) + 8, int(ch) + 8), (0, 0, 0, 0))
            ImageDraw.Draw(fr).rounded_rectangle((0, 0, int(cw) + 7, int(ch) + 7), radius + 4, fill=(255, 255, 255, 255)); fr.alpha_composite(p, (4, 4))
            _cache[k] = fr
        _paste(canvas, _cache[k], box[0] + c * (cw + gap) + cw / 2, box[1] + r * (ch + gap) + ch / 2, _pop(f, f0 + step * i))


def badge(canvas, text, f, f0, cx=512, cy=760, size=120):
    k = ('badge', text, size)
    if k not in _cache:
        fo = font(900, size, False); tw = int(fo.getlength(text)); w, h = tw + 80, int(size * 1.25)
        im = Image.new('RGBA', (w + 40, h + 44), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((24, 30, w + 24, h + 30), 24, fill=(0, 0, 0, 130)); im = im.filter(ImageFilter.GaussianBlur(9)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((20, 20, w + 20, h + 20), 24, fill=RED + (255,), outline=(255, 255, 255, 255), width=6)
        d.text((60, 20 + (h - size * 1.2) / 2), text, font=fo, fill=(255, 255, 255, 255)); _cache[k] = im
    _paste(canvas, _cache[k], cx, cy, _pop(f, f0))


def prompt_card(canvas, text, f, f0, box=(95, 560, 930, 900), mention='@rakshith', cps=2):
    """Dark-blue prompt bubble; text types `cps` characters per frame; the @mention sits in a red chip."""
    n = max(0, (f - f0) * cps)
    if f < f0: return
    x0, y0, x1, y1 = box; im = Image.new('RGBA', (x1 - x0 + 30, y1 - y0 + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((18, 22, x1 - x0 + 12, y1 - y0 + 16), 26, fill=(0, 0, 0, 120)); im = im.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, x1 - x0, y1 - y0), 26, fill=(29, 58, 138, 250))
    fo = font(500, 30, False); x, y = 36, 34; shown = text[:n]
    for wd in shown.split(' '):
        wl = fo.getlength(wd + ' ')
        if x + wl > x1 - x0 - 30: x, y = 36, y + 42
        if y > y1 - y0 - 50: break
        if wd.startswith(mention[:max(1, len(wd))]) and mention.startswith(wd.rstrip(',.')):
            d.rounded_rectangle((x - 6, y - 2, x + fo.getlength(wd) + 6, y + 38), 8, fill=RED + (255,))
        d.text((x, y), wd, font=fo, fill=(255, 255, 255, 255)); x += wl
    if n < len(text) and (f // 4) % 2 == 0: d.rectangle((x, y + 4, x + 3, y + 36), fill=(255, 255, 255, 255))   # cursor
    _paste(canvas, im, (x0 + x1) / 2, (y0 + y1) / 2)
