# Graphics library for the kinetic-type reel (1080x1920 @ 30 fps).
# All layers are float32 RGBA (straight alpha, 0..1); the canvas is float32 RGB 0..255.
import numpy as np, cv2, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from paths import font_path as _fp
FONT_IT = _fp('InterTight-Italic%5Bwght%5D.ttf')
FONT_UP = _fp('InterTight%5Bwght%5D.ttf')

RED = (0xE3, 0x12, 0x1B); RED_MID = (0xAA, 0, 0); RED_DK = (0x5A, 0x02, 0x04); RED_BOT = (0x7A, 0x03, 0x06)
PINK1 = (0xF0, 0x6A, 0x72); PINK2 = (0xF7, 0xB9, 0xBE); LABEL = (0x8A, 0x0A, 0x0A); WHITE = (255, 255, 255)
NEON = (0xFF, 0x1A, 0x2A)
BLOCK_COLS = [RED, PINK1, PINK2, RED_MID, (0xFF, 0x3B, 0x45)]

_fc = {}
def font(weight, size, italic=True):
    k = (weight, size, italic)
    if k not in _fc:
        f = ImageFont.truetype(FONT_IT if italic else FONT_UP, size)
        f.set_variation_by_axes([weight]); _fc[k] = f
    return _fc[k]

def to_layer(pil_rgba):
    return np.asarray(pil_rgba, dtype=np.float32) / 255.0

# ------------------------------------------------------------------ compositing
def over(canvas, lay, x, y, op=1.0):
    """alpha-over an RGBA float layer (0..1) at integer x,y onto canvas (float 0..255)."""
    if lay is None or op <= 0: return
    h, w = lay.shape[:2]; x = int(round(x)); y = int(round(y))
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    l = lay[y0 - y:y1 - y, x0 - x:x1 - x]
    a = l[..., 3:4] * op
    c = canvas[y0:y1, x0:x1]
    c *= (1 - a); c += l[..., :3] * 255.0 * a

def add(canvas, lay, x=0, y=0, op=1.0):
    """additive (light) blend of RGBA layer, colour * alpha."""
    h, w = lay.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    l = lay[y0 - y:y1 - y, x0 - x:x1 - x]
    canvas[y0:y1, x0:x1] += l[..., :3] * l[..., 3:4] * 255.0 * op

def scale_layer(lay, s):
    if abs(s - 1) < 1e-3: return lay
    h, w = lay.shape[:2]; nw, nh = max(1, int(w * s)), max(1, int(h * s))
    return cv2.resize(lay, (nw, nh), interpolation=cv2.INTER_LINEAR)

def rotate_layer(lay, deg):
    if abs(deg) < 0.01: return lay
    h, w = lay.shape[:2]; d = int(math.hypot(w, h)) + 4
    pad = np.zeros((d, d, 4), np.float32); ox, oy = (d - w) // 2, (d - h) // 2; pad[oy:oy + h, ox:ox + w] = lay
    M = cv2.getRotationMatrix2D((d / 2, d / 2), deg, 1.0)
    return cv2.warpAffine(pad, M, (d, d), flags=cv2.INTER_LINEAR)

def over_c(canvas, lay, cx, cy, op=1.0, s=1.0, rot=0.0):
    """place a layer by its centre with scale and rotation."""
    l = rotate_layer(scale_layer(lay, s), rot)
    over(canvas, l, cx - l.shape[1] / 2, cy - l.shape[0] / 2, op)

# ------------------------------------------------------------------ big 3D italic type
class BigWord:
    """Per-letter sprites of the heavy red italic word with gradient, extrude, bevel and shadow."""
    def __init__(self, text, cap, maxw=900, weight=900, track=-0.04, front=False):
        size = int(cap / 0.727)
        f = font(weight, size)
        width = f.getlength(text) + track * size * (len(text) - 1) + 0.14 * size * text.count(' ')
        if width > maxw: size = int(size * maxw / width); f = font(weight, size)
        self.size = size; self.text = text
        ext = max(4, int(W * 0.012 * size / 300)); self.ext = ext
        asc, desc = f.getmetrics(); pad = int(size * 0.35) + ext + 24
        self.letters = []; x = 0.0
        for i, ch in enumerate(text):
            adv = f.getlength(text[:i + 1]) - f.getlength(text[:i]) + track * size + (0.14 * size if ch == ' ' else 0)
            if ch != ' ':
                self.letters.append(self._sprite(ch, f, asc, desc, pad, x))
            x += adv
        self.width = x - track * size; self.asc = asc; self.pad = pad
        self.cap = int(size * 0.727)

    def _sprite(self, ch, f, asc, desc, pad, x):
        bw = int(f.getlength(ch) + 2 * pad + self.size * 0.3); bh = asc + desc + 2 * pad
        m = Image.new('L', (bw, bh), 0); ImageDraw.Draw(m).text((pad, pad), ch, font=f, fill=255)
        M = np.asarray(m, np.float32) / 255
        ys, xs = np.nonzero(M > 0.02)
        if len(ys) == 0: return None
        top, bot = ys.min(), ys.max()
        # vertical gradient fill
        g = np.clip((np.arange(bh) - top) / max(1, bot - top), 0, 1)[:, None]
        fill = np.zeros((bh, bw, 3), np.float32)
        for c in range(3): fill[..., c] = (RED[c] * (1 - g) + RED_BOT[c] * g) / 255
        # extrude: stack shifted masks down-right
        ext = np.zeros_like(M)
        for k in range(1, self.ext + 1):
            sh = np.zeros_like(M); dx, dy = int(round(k * 0.55)), k
            sh[dy:, dx:] = M[:bh - dy, :bw - dx]; ext = np.maximum(ext, sh)
        # bevel highlight (top edge) and inner dark edge
        up = np.zeros_like(M); up[:-2, :] = M[2:, :]
        hl = np.clip(M - up, 0, 1) * 0.55
        shadow = np.clip(cv2.GaussianBlur(np.maximum(M, ext), (0, 0), 12) * 0.55, 0, 0.55)
        sh2 = np.zeros_like(shadow); sh2[10:, 8:] = shadow[:-10, :-8]
        out = np.zeros((bh, bw, 4), np.float32)
        # shadow
        out[..., 3] = sh2
        # extrude colour
        a = ext; out[..., :3] = out[..., :3] * (1 - a[..., None]) + np.array(RED_DK, np.float32) / 255 * a[..., None]
        out[..., 3] = a + out[..., 3] * (1 - a)
        # face
        a = M; out[..., :3] = out[..., :3] * (1 - a[..., None]) + fill * a[..., None]
        out[..., 3] = a + out[..., 3] * (1 - a)
        out[..., :3] = np.clip(out[..., :3] + hl[..., None] * np.array([1.0, 0.55, 0.55]), 0, 1)
        return dict(img=out, x=x - pad, ch=ch)

    def draw(self, canvas, cx, base, start_f, f, step=2, op=1.0, gone=None, s=1.0, starts=None):
        """type-on: letter i appears at start_f + step*i. Newest letter ghosted, scaled, blurred.
        base = baseline y; cx = centre x. gone: set of letter indices removed (dissolve)."""
        x0 = cx - self.width * s / 2; top = base - self.asc * s - self.pad * s
        for i, L in enumerate(self.letters):
            if L is None: continue
            a = f - (starts[i] if starts else start_f + step * i)
            if a < 0: continue
            if gone and i in gone: continue
            img = L['img']
            if a == 0: sc, o, bl = 1.22, 0.4, 3
            elif a == 1: sc, o, bl = 1.06, 0.78, 1
            else: sc, o, bl = 1.0, 1.0, 0
            if s != 1.0: img = scale_layer(img, s)
            if bl: img = cv2.GaussianBlur(img, (0, 0), bl)
            if sc != 1.0:
                h, w = img.shape[:2]; im2 = scale_layer(img, sc)
                over(canvas, im2, x0 + L['x'] * s - (im2.shape[1] - w) / 2, top - (im2.shape[0] - h) / 2, o * op)
            else:
                over(canvas, img, x0 + L['x'] * s, top, o * op)

    def letter_boxes(self, cx, base, s=1.0):
        x0 = cx - self.width * s / 2; out = []
        for L in self.letters:
            if L is None: out.append(None); continue
            w = L['img'].shape[1] * s
            out.append((x0 + (L['x'] + self.pad) * s, base - self.cap * s, x0 + L['x'] * s + w - self.pad * s, base))
        return out

    def n(self): return len(self.letters)

# ------------------------------------------------------------------ small italic label
class Label:
    def __init__(self, text, size=60, color=WHITE, weight=400, shadow=True):
        self.words = []; f = font(weight, size); x = 0
        for wd in text.split(' '):
            w = int(f.getlength(wd)) + 16; h = int(size * 1.45)
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            if shadow:
                d.text((5, 6), wd, font=f, fill=(0, 0, 0, 110))
                im = im.filter(ImageFilter.GaussianBlur(3)); d = ImageDraw.Draw(im)
            d.text((4, 2), wd, font=f, fill=color + (255,))
            self.words.append(dict(img=to_layer(im), x=x, w=w)); x += f.getlength(wd + ' ')
        self.width = x - f.getlength(' '); self.h = int(size * 1.45); self.size = size

    def draw(self, canvas, x, y, start_f, f, op=1.0, seed=1, center=False, word_step=2):
        """scatter-in: each word starts offset and faint, snaps home in 2-frame steps."""
        if f < start_f: return
        rnd = random.Random(seed); x0 = x - self.width / 2 if center else x
        for k, wd in enumerate(self.words):
            a = f - start_f - k * word_step
            ox, oy = rnd.uniform(-70, 70), rnd.uniform(-40, 40)
            if a < 0: continue
            st = min(1.0, (a // 2) / 3)  # stepped: 0, .33, .66, 1
            e = 1 - (1 - st) ** 2
            over(canvas, wd['img'], x0 + wd['x'] + ox * (1 - e), y + oy * (1 - e), op * (0.35 + 0.65 * e))

    def word_boxes(self, x, y, center=False):
        x0 = x - self.width / 2 if center else x
        return [(x0 + wd['x'], y, x0 + wd['x'] + wd['w'] - 12, y + self.h) for wd in self.words]

# ------------------------------------------------------------------ pills, cards, icons
_pc = {}
def pill(text, size=40, bg=RED, fg=WHITE):
    k = (text, size, bg)
    if k in _pc: return _pc[k]
    f = font(560, size); tw = f.getlength(text); h = int(size * 1.55); w = int(tw + size * 1.3)
    im = Image.new('RGBA', (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), radius=h // 2, fill=(0, 0, 0, 60))
    im = im.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w + 8, h + 8), radius=h // 2, fill=bg + (255,))
    d.text((8 + (w - tw) / 2, 8 + h * 0.12), text, font=f, fill=fg + (255,))
    _pc[k] = to_layer(im); return _pc[k]

def card(img_bgr, w, h, stroke=6, radius=32, col=RED, shadow=True):
    """rounded photo card with red stroke. img_bgr: numpy RGB uint8 (cover-fit)."""
    ih, iw = img_bgr.shape[:2]; s = max(w / iw, h / ih)
    r = cv2.resize(img_bgr, (int(iw * s + 1), int(ih * s + 1)), interpolation=cv2.INTER_AREA)
    oy, ox = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2; r = r[oy:oy + h, ox:ox + w]
    P = 24; out = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    m = np.zeros((h + 2 * P, w + 2 * P), np.uint8)
    cv2.rectangle(m, (P, P), (P + w - 1, P + h - 1), 255, -1)
    m = Image.new('L', (w + 2 * P, h + 2 * P), 0); ImageDraw.Draw(m).rounded_rectangle((P, P, P + w - 1, P + h - 1), radius=radius, fill=255)
    M = np.asarray(m, np.float32) / 255
    if shadow:
        sh = cv2.GaussianBlur(M, (0, 0), 10); shs = np.zeros_like(sh); shs[8:, 4:] = sh[:-8, :-4]
        out[..., 3] = shs * 0.28
    inner = Image.new('L', (w + 2 * P, h + 2 * P), 0)
    ImageDraw.Draw(inner).rounded_rectangle((P + stroke, P + stroke, P + w - 1 - stroke, P + h - 1 - stroke), radius=max(4, radius - stroke), fill=255)
    I = np.asarray(inner, np.float32) / 255
    photo = np.zeros((h + 2 * P, w + 2 * P, 3), np.float32); photo[P:P + h, P:P + w] = r / 255  # expects RGB
    colr = np.array(col, np.float32) / 255
    rgb = photo * I[..., None] + colr * (1 - I[..., None])
    a = M
    out[..., :3] = out[..., :3] * (1 - a[..., None]) + rgb * a[..., None]
    out[..., 3] = a + out[..., 3] * (1 - a)
    return out

def pop_scale(a):
    """overshoot pop 0 -> 108 -> 100 % in 4 frames"""
    return [0.0, 0.62, 1.08, 1.0][a] if a < 4 else 1.0

_ic = {}
def icon(kind, size=150):
    """procedural glossy red 3D-style icon badge (clapper, play, bookmark, speaker_l/r, check, doc)."""
    k = (kind, size)
    if k in _ic: return _ic[k]
    S = size * 2; P = 30
    im = Image.new('RGBA', (S + 2 * P, S + 2 * P), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # shadow
    d.rounded_rectangle((P + 10, P + 24, P + S + 10, P + S + 24), radius=S // 4, fill=(60, 0, 0, 120))
    im = im.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(im)
    # extrude
    d.rounded_rectangle((P + 6, P + 16, P + S + 6, P + S + 16), radius=S // 4, fill=RED_DK + (255,))
    # face gradient
    face = Image.new('RGBA', (S, S)); fd = ImageDraw.Draw(face)
    for yy in range(S):
        t = yy / S; c = tuple(int(RED[i] * (1 - t) + RED_MID[i] * t + 30 * (1 - t) * (i == 0)) for i in range(3))
        fd.line((0, yy, S, yy), fill=c + (255,))
    mk = Image.new('L', (S, S), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, S - 1, S - 1), radius=S // 4, fill=255)
    im.paste(face, (P, P), mk); d = ImageDraw.Draw(im)
    # gloss
    gl = Image.new('L', (S, S), 0); ImageDraw.Draw(gl).ellipse((-S * 0.2, -S * 0.75, S * 1.2, S * 0.42), fill=70)
    gl = Image.composite(gl, Image.new('L', (S, S), 0), mk)
    im.paste(Image.new('RGBA', (S, S), (255, 255, 255, 255)), (P, P), gl)
    cx, cy = P + S / 2, P + S / 2; u = S / 10; wc = (255, 255, 255, 255)
    if kind == 'play':
        d.polygon([(cx - 1.6 * u, cy - 2.4 * u), (cx - 1.6 * u, cy + 2.4 * u), (cx + 2.6 * u, cy)], fill=wc)
    elif kind == 'clapper':
        d.rounded_rectangle((cx - 3.2 * u, cy - 0.6 * u, cx + 3.2 * u, cy + 3 * u), radius=u * 0.5, fill=wc)
        d.polygon([(cx - 3.3 * u, cy - 1.2 * u), (cx + 3.0 * u, cy - 2.9 * u), (cx + 3.3 * u, cy - 1.8 * u), (cx - 3.0 * u, cy - 0.2 * u)], fill=wc)
        for k2 in range(3):
            x = cx - 2.2 * u + k2 * 1.9 * u
            d.polygon([(x, cy - 0.6 * u), (x + 0.9 * u, cy - 0.6 * u), (x + 0.3 * u, cy + 0.6 * u), (x - 0.6 * u, cy + 0.6 * u)], fill=RED + (255,))
    elif kind == 'bookmark':
        d.polygon([(cx - 2.2 * u, cy - 3 * u), (cx + 2.2 * u, cy - 3 * u), (cx + 2.2 * u, cy + 3.2 * u), (cx, cy + 1.6 * u), (cx - 2.2 * u, cy + 3.2 * u)], fill=wc)
    elif kind in ('speaker_l', 'speaker_r'):
        d.rectangle((cx - 3 * u, cy - 1.1 * u, cx - 1.6 * u, cy + 1.1 * u), fill=wc)
        d.polygon([(cx - 1.6 * u, cy - 1.1 * u), (cx + 0.6 * u, cy - 3 * u), (cx + 0.6 * u, cy + 3 * u), (cx - 1.6 * u, cy + 1.1 * u)], fill=wc)
        for r in (1.8, 3.0):
            d.arc((cx + 0.6 * u - r * u, cy - r * u, cx + 0.6 * u + r * u, cy + r * u), -45, 45, fill=wc, width=int(u * 0.55))
        f = font(800, int(u * 2.4))
        d.text((P + S - 3.0 * u, P + S - 3.3 * u), 'L' if kind == 'speaker_l' else 'R', font=f, fill=wc)
    elif kind == 'check':
        d.line([(cx - 2.4 * u, cy + 0.2 * u), (cx - 0.6 * u, cy + 2.2 * u), (cx + 2.8 * u, cy - 2.2 * u)], fill=wc, width=int(u * 1.3), joint='curve')
    elif kind == 'doc':
        d.rounded_rectangle((cx - 2.3 * u, cy - 3 * u, cx + 2.3 * u, cy + 3 * u), radius=u * 0.6, fill=wc)
        for k2 in range(4): d.line((cx - 1.4 * u, cy - 1.6 * u + k2 * 1.2 * u, cx + 1.4 * u, cy - 1.6 * u + k2 * 1.2 * u), fill=RED + (255,), width=int(u * 0.45))
    im = im.resize(((S + 2 * P) // 2, (S + 2 * P) // 2), Image.LANCZOS)
    _ic[k] = to_layer(im); return _ic[k]

# ------------------------------------------------------------------ pixel blocks
def make_blocks(seed, t0, t1, boxes_fn, n_per_frame=(1, 3), size=(18, 42)):
    """precompute pixel-block glitch events between frames t0..t1.
    boxes_fn(frame) -> (x0,y0,x1,y1) area the blocks attach to (or None)."""
    rnd = random.Random(seed); ev = []
    for fr in range(t0, t1):
        b = boxes_fn(fr)
        if b is None: continue
        for _ in range(rnd.randint(*n_per_frame)):
            s = rnd.choice([18, 24, 30, 36, 42]) if size == (18, 42) else rnd.randint(*size)
            x = rnd.uniform(b[0] - 60, b[2] + 40); y = rnd.uniform(b[1] - 50, b[3] + 20)
            cl = rnd.randint(1, 4)  # cluster of adjacent squares
            col = rnd.choice(BLOCK_COLS); life = rnd.randint(2, 5)
            for c in range(cl):
                ev.append((fr, life, x + rnd.choice([-1, 0, 1]) * s * c, y + rnd.choice([-1, 0, 1]) * s * (c > 1), s, col, rnd.uniform(0.75, 1)))
    return ev

def draw_blocks(canvas, ev, f, op=1.0):
    for (fr, life, x, y, s, col, o) in ev:
        if fr <= f < fr + life:
            x0, y0 = int(x // 6 * 6), int(y // 6 * 6)
            x1, y1 = min(W, x0 + s), min(H, y0 + s); x0, y0 = max(0, x0), max(0, y0)
            if x1 > x0 and y1 > y0:
                a = o * op; canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + np.array(col, np.float32) * a

# ------------------------------------------------------------------ neon squiggle streak
def neon_streak(canvas, j, n=6, cx=540, amp=95, phase=0.0, vertical=True, yc=960, tail=900):
    """j = frame index within the device (0..n-1). Ribbon snakes bottom->top (or left->right)."""
    if j < 0 or j >= n: return
    lay = np.zeros((H // 2, W // 2), np.float32); core = np.zeros((H, W), np.uint8)
    prog = (j + 1) / n
    if vertical:
        head = 1980 - 2300 * prog; ys = np.arange(int(head), int(head + tail), 6)
        ys = ys[(ys > -50) & (ys < H + 50)]
        if len(ys) < 2: return
        xs = cx + amp * np.sin(ys / 135.0 + phase) + 35 * np.sin(ys / 47.0 + phase * 2)
        pts = np.stack([xs, ys], 1)
    else:
        head = -200 + 1500 * prog; xs = np.arange(int(head - tail), int(head), 6)
        ys = yc + amp * np.sin(xs / 120.0 + phase) + 25 * np.sin(xs / 41.0)
        pts = np.stack([xs, ys], 1)
    p2 = (pts / 2).astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(lay, [p2], False, 1.0, 16, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lay, (0, 0), 7) * 2.6 + cv2.GaussianBlur(lay, (0, 0), 26) * 2.0
    glow = cv2.resize(np.clip(glow, 0, 1.4), (W, H))
    cv2.polylines(core, [pts.astype(np.int32).reshape(-1, 1, 2)], False, 255, 8, cv2.LINE_AA)
    coref = cv2.GaussianBlur(core.astype(np.float32) / 255, (0, 0), 1.2)
    # taper alpha towards tail
    g3 = np.clip(glow, 0, 1)[..., None]
    canvas[:] = canvas * (1 - g3 * 0.85) + np.array(NEON, np.float32) * g3 * 0.85 + glow[..., None] * 40
    canvas[:] = canvas * (1 - coref[..., None]) + 255 * coref[..., None]

# ------------------------------------------------------------------ halftone ring burst
_yy, _xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
def halftone_ring(canvas, j, cx, cy, n=5, r0=60, r1=900, band=230, mode='dots', op=0.72, ry_scale=1.0):
    if j < 0 or j >= n: return
    e = 1 - (1 - (j + 1) / n) ** 2
    r = r0 + (r1 - r0) * e
    X, Y = _xx * 2, _yy * 2
    d = np.sqrt((X - cx) ** 2 + ((Y - cy) / ry_scale) ** 2)
    k = np.clip(1 - np.abs(d - r) / band, 0, 1)  # 1 at ring centre
    if mode == 'dots':
        sp = 16.0; gx = (X % sp) - sp / 2; gy = (Y % sp) - sp / 2; dd = np.sqrt(gx * gx + gy * gy)
        a = (dd < k * sp * 0.55).astype(np.float32)
    else:  # horizontal halftone lines
        sp = 12.0; gy = np.abs((Y % sp) - sp / 2); a = (gy < k * sp * 0.45).astype(np.float32)
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_NEAREST) * (1.0 - 0.6 * j / n) * op
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    col = (np.array(RED, np.float32) * 0.8 + np.array(PINK1, np.float32) * 0.2)
    canvas[:] = canvas * (1 - a[..., None]) + col * a[..., None]

def radial_blur(canvas, cx, cy, amt=0.05, steps=4):
    acc = canvas.copy();
    for i in range(1, steps + 1):
        s = 1 + amt * i / steps
        M = np.float32([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]])
        acc += cv2.warpAffine(canvas, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    canvas[:] = acc / (steps + 1)

# ------------------------------------------------------------------ whole-frame devices
def vertical_smear(canvas, j):
    L = [70, 140, 60][j]
    k = np.zeros((L, 1), np.float32); k[:] = 1 / L
    b = cv2.filter2D(canvas, -1, k)
    out = b.copy(); sh = [10, 18, 8][j]
    out[sh:, :, 0] = b[:-sh, :, 0]; out[:-sh, :, 2] = b[sh:, :, 2]   # RGB: R down, B up (chromatic split)
    out[..., 0] = np.clip(out[..., 0] * 1.08 + 12, 0, 255)  # red glow
    canvas[:] = out

def negative(canvas, blur=10, tint=(1.0, 1.0, 1.0)):
    inv = 255 - canvas
    inv = cv2.GaussianBlur(inv, (0, 0), blur)
    inv *= np.array(tint, np.float32)
    canvas[:] = np.clip(inv * 0.92, 0, 255)

def magenta_ghost(canvas):
    b = cv2.GaussianBlur(canvas, (0, 0), 14)
    g2 = np.zeros_like(b); g2[:, 26:] = b[:, :-26]
    m = 0.6 * b + 0.4 * g2
    m = m * np.array([1.0, 0.62, 0.88], np.float32) + np.array([55, 40, 62], np.float32)  # RGB pink/lavender ghost
    canvas[:] = np.clip(m, 0, 255)

def rgb_ghost(canvas, j, n=3):
    if j >= n: return
    s = int([22, 12, 5][j])
    out = canvas.copy(); out[:, s:, 0] = canvas[:, :-s, 0]; out[:, :-s, 2] = canvas[:, s:, 2]
    canvas[:] = out

def swoosh(canvas, j, n=7, yc=1180, ang=-8):
    """red light streak travelling left->right across mid frame, white bloom growing."""
    if j < 0 or j >= n: return
    lay = np.zeros((H // 2, W // 2), np.float32)
    head = -100 + (W + 300) * (j + 1) / n
    x0 = head - 520
    p1 = (int(x0 / 2), int((yc + math.tan(math.radians(ang)) * (x0 - 540)) / 2))
    p2 = (int(head / 2), int((yc + math.tan(math.radians(ang)) * (head - 540)) / 2))
    cv2.line(lay, p1, p2, 1.0, 7, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lay, (0, 0), 6) * 1.8 + cv2.GaussianBlur(lay, (0, 0), 24) * 1.5
    glow = cv2.resize(np.clip(glow, 0, 1.5), (W, H))
    canvas += glow[..., None] * np.array(NEON, np.float32) * 0.9
    core = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 1.0), (W, H))
    canvas[:] = canvas * (1 - core[..., None] * 0.9) + 255 * core[..., None] * 0.9
    bloom = (j / (n - 1)) ** 2 * 0.55
    canvas[:] = canvas * (1 - bloom) + 255 * bloom

def grain(canvas, f, amt=5.0, _cache={}):
    if 'g' not in _cache:
        rng = np.random.default_rng(7); _cache['g'] = [rng.normal(0, 1, (H, W, 1)).astype(np.float32) for _ in range(6)]
    canvas += _cache['g'][f % 6] * amt
