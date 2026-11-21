# Day 4 — "Claude & Codex inside Android Studio" (aiwithrakshith.global, English VO)
# Kinetic-type grammar, ORIGINAL room background, everything inside the Instagram Reels safe zone:
#   x 65 .. 960 (right 120 px kept clear for the like/comment/share rail), y 270 .. 1250 (top 14 %, bottom 35 %)
# 60 fps build: every effect keeps its 30-fps timing; continuous motion (rings, streaks, swooshes,
#   screen push-ins, grain) gets true in-between frames. Logic frame f is in 30-fps units, SUB = 0 or 0.5.
# usage: python3 render_d4_60.py <f60_0> <f60_1> <f0> <f1> <out.mp4>   |   python3 render_d4.py 0 0 <png_dir> f1,f2,...
import sys, json, math, random, subprocess, os, glob
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from fx import *
from islands import snapped
from subject_d4 import combined_alpha
from PIL import Image as PImage
import fx as _fx
SUB = 0.0
def _cont(fn):
    def g(canvas, j, *a, **k):
        n = k.get('n', fn.__defaults__[0] if fn is not _fx.halftone_ring else 5)
        if 0 <= j < n - 1: j = j + SUB          # half-step between two 30-fps device frames
        return fn(canvas, j, *a, **k)
    return g
neon_streak = _cont(_fx.neon_streak); halftone_ring = _cont(_fx.halftone_ring); swoosh = _cont(_fx.swoosh)
D = '/home/claude/d4/'
WK = json.load(open(D + 'words_final.json'))
def wt(k): return WK[k]
def F(t): return int(round(t * FPS))
J = [s[2] for s in snapped()][1:]          # 10 jump cuts
VO_END = snapped()[-1][3]; END_T = round(VO_END + 0.82, 2); NF = F(END_T); HIT_T = VO_END + 0.28
DY = 60                                    # subject shift: cap top >= 505, chin <= ~1100 (face inside the safe zone)
SX0, SX1, SY0, SY1 = 65, 960, 270, 1250    # safe zone
CX = (SX0 + SX1) // 2                      # 512 : centre of the safe zone
MAXW = SX1 - SX0 - 30                      # big words <= 865 px wide

# ---------------------------------------------------------------- assets
GD = np.load(D + 'assets/gif_dropdown.npy', mmap_mode='r'); GC = np.load(D + 'assets/gif_caps.npy', mmap_mode='r')
CC = sorted(glob.glob(D + 'web/ccdemo/*.png'))
_imc = {}
def img(path):
    if path not in _imc: _imc[path] = np.asarray(PImage.open(path).convert('RGB'))
    return _imc[path]
def cc(t):  # cc_demo at t seconds (12.6 s, 105 frames)
    return img(CC[min(len(CC) - 1, max(0, int(t * 105 / 12.6)))])
REG = D + 'web/agent_registry.png'; SEL = D + 'web/agent_selector.png'; RAB = D + 'web/Rabbit2_Strapi_27563aeaf4_1BAzRM.webp'

# ---------------------------------------------------------------- subject + room
class Subject:
    def __init__(self, f0):
        self.v = cv2.VideoCapture(D + 'aroll_patched30.mp4'); self.a = cv2.VideoCapture(D + 'alpha_r50.mkv')
        self.n = 1176; self.pos = -1
        if 0 < f0 < self.n:
            self.v.set(cv2.CAP_PROP_POS_FRAMES, f0); self.a.set(cv2.CAP_PROP_POS_FRAMES, f0); self.pos = f0 - 1
        self.tail = None; self.cache = None
    def get(self, f):
        if f < self.n:
            while self.pos < f:
                _, fr = self.v.read(); _, al = self.a.read(); self.pos += 1; self.cache = (fr, al)
        else:
            if self.tail is None:
                vt = cv2.VideoCapture(D + 'aroll_tail_fixed.mp4'); at = cv2.VideoCapture(D + 'alpha_tail.mkv'); self.tail = []
                while True:
                    ok, fr = vt.read(); ok2, al = at.read()
                    if not ok or not ok2: break
                    self.tail.append((fr, al))
            k = f - self.n; n = len(self.tail); per = 2 * n - 2
            k = k % per; k = k if k < n else per - k            # boomerang the 0.3 s tail for the end hold
            self.cache = self.tail[k]
        fr, al = self.cache
        a = combined_alpha(fr, al[..., 0])
        rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32)
        g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * 0.97; rgb = 255 * (0.5 + (rgb / 255 - 0.5) * 1.04)
        lay = np.zeros((H, W, 4), np.float32)
        lay[DY:, :, :3] = np.clip(rgb[:H - DY], 0, 255) / 255; lay[DY:, :, 3] = a[:H - DY]
        self.room = room_bg(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32))
        return lay

def room_bg(src):   # ORIGINAL mode: his real room, darkened + desaturated 20 %, ~6 px blur
    out = np.empty((H, W, 3), np.float32); out[DY:] = src[:H - DY]
    ext = cv2.resize(src[0:70], (W, DY + 60), interpolation=cv2.INTER_LINEAR)
    out[:DY] = ext[:DY]; k = np.linspace(1, 0, 60)[:, None, None]; out[DY:DY + 60] = ext[DY:] * k + out[DY:DY + 60] * (1 - k)
    g = out.mean(2, keepdims=True); out = g + (out - g) * 0.8; out *= 0.8
    return cv2.GaussianBlur(out, (0, 0), 3)

# ---------------------------------------------------------------- helpers (from the approved engine)
class A: cache = {}
def bw(key, text, cap, **kw):
    kw.setdefault('maxw', MAXW)
    if key not in A.cache: A.cache[key] = BigWord(text, cap, **kw)
    return A.cache[key]
def lb(key, text, **kw):
    if key not in A.cache: A.cache[key] = Label(text, **kw)
    return A.cache[key]
def cd(key, im, w, h, **kw):
    if key not in A.cache: A.cache[key] = card(im, w, h, **kw)
    return A.cache[key]
def blocks_for_word(key, word, cx, base, f0, step=1, extra=6, seed=0):
    k = 'blk_' + key
    if k in A.cache: return A.cache[k]
    boxes = word.letter_boxes(cx, base)
    def bf(fr):
        i = (fr - f0) // step
        if i < 0 or i >= len(boxes) + extra // step: return None
        b = boxes[min(i, len(boxes) - 1)]
        return (max(SX0, b[0]), max(SY0, b[1]), min(SX1, b[2]), b[3])
    A.cache[k] = make_blocks(hash(key) % 9999 + seed, f0, f0 + step * len(boxes) + extra, bf); return A.cache[k]
def dissolve_blocks(key, word, cx, base, f0, seed=3):
    k = 'dis_' + key
    if k in A.cache: return A.cache[k]
    boxes = [b for b in word.letter_boxes(cx, base) if b]; rnd = random.Random(seed); ev = []
    for fr in range(f0, f0 + 6):
        for b in rnd.sample(boxes, min(len(boxes), 4)):
            for _ in range(3):
                ev.append((fr, rnd.randint(2, 4), rnd.uniform(b[0], b[2]), rnd.uniform(b[1], b[3]), rnd.choice([18, 24, 30, 36]), rnd.choice(BLOCK_COLS), 0.9))
    A.cache[k] = ev; return ev
def gone_set(word, f, f0, seed=5):
    if f < f0: return None
    n = word.n(); order = list(range(n)); random.Random(seed).shuffle(order)
    return set(order[:min(n, int((f - f0 + 1) * n / 4))])
def marker(canvas, label, x, y, f0, f, center=False):
    cols = [RED, (0x29, 0xD3, 0xE6), (0x3B, 0xD1, 0x4A)]
    for n, b in enumerate(label.word_boxes(x, y, center=center)):
        a = f - (f0 + 2 * n)
        if 0 <= a < 3:
            w = (b[2] - b[0]) * min(1, (a + 1) / 2); y0 = int(b[1] + label.h * 0.18); y1 = int(b[1] + label.h * 0.82)
            canvas[y0:y1, int(b[0]):int(b[0] + w)] = np.array(cols[n % 3], np.float32)
TLOG = {}
def word_on(c, key, text, cap, base, t, f, cx=CX, starts=None, gone_at=None, step=1):
    w = bw(key, text, cap); f0 = F(t)
    fin = (max(starts) if starts else f0 + step * (w.n() - 1)) + 2
    e = TLOG.setdefault(key, {'text': text, 'start': f0, 'full': fin, 'last': f, 'gone': gone_at}); e['last'] = max(e['last'], f)
    w.draw(c, cx, base, f0, f, starts=starts, gone=gone_set(w, f, gone_at) if gone_at else None, step=step)
    draw_blocks(c, blocks_for_word(key, w, cx, base, f0, step=step), f)
    if gone_at: draw_blocks(c, dissolve_blocks(key, w, cx, base, gone_at), f)
    return w
def strike_x(c, cx, cy, w, h, f, f0):
    """red pixel ✕ stamped over a word (2-frame overshoot)."""
    if f < f0: return
    s = 1.2 if f == f0 else 1.0
    for k, u in enumerate(np.linspace(-1, 1, 11)):
        for sg in (1, -1):
            px = cx + u * w / 2 * s; py = cy + sg * u * h / 2 * s; x0, y0 = int(px // 6 * 6), int(py // 6 * 6)
            c[y0:y0 + 18, x0:x0 + 18] = np.array(RED if k % 3 else PINK1, np.float32)
_tc = {}
def tile(text, w=250, h=78, size=34):
    """dark glass name tile with red stroke (agent names, checklist items)."""
    k = (text, w, h, size)
    if k in _tc: return _tc[k]
    from PIL import ImageDraw, ImageFilter
    im = PImage.new('RGBA', (w + 24, h + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 16, w + 14, h + 16), radius=20, fill=(0, 0, 0, 90)); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 12, h + 12), radius=20, fill=(22, 18, 22, 235), outline=RED + (255,), width=4)
    f_ = font(700, size, True); tw = f_.getlength(text)
    d.text((12 + (w - tw) / 2, 12 + (h - size * 1.2) / 2), text, font=f_, fill=(255, 255, 255, 255))
    _tc[k] = to_layer(im); return _tc[k]

# ---------------------------------------------------------------- screen cutaway (landscape footage inside the safe zone)
WIN = (75, 560, 875, 650)     # x, y, w, h  -> 75..950 x 560..1210
def fit_box(b, aspect):
    x0, y0, x1, y1 = b; w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if w / h > aspect: h = w / aspect
    else: w = h * aspect
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
def screen_cut(c, src, box0, box1, zf, f, win=WIN, notch=True):
    """full-frame blurred backdrop of the same footage + sharp window; stepped push from box0 to box1 at frame zf."""
    ih, iw = src.shape[:2]; s = max(W / iw, H / ih)
    bg = cv2.resize(src, (int(iw * s) + 1, int(ih * s) + 1), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    oy, ox = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
    c[:] = cv2.GaussianBlur(bg[oy:oy + H, ox:ox + W], (0, 0), 22) * 0.42
    x, y, w, h = win; asp = w / h
    b0, b1 = fit_box(box0, asp), fit_box(box1, asp)
    e = 0.0 if f < zf else float(np.interp(f - zf + SUB, [0, 1, 2, 3], [0.35, 0.75, 0.95, 1.0]))
    b = [b0[i] + (b1[i] - b0[i]) * e for i in range(4)]
    M = np.float32([[w / (b[2] - b[0]), 0, -b[0] * w / (b[2] - b[0])], [0, h / (b[3] - b[1]), -b[1] * h / (b[3] - b[1])]])
    view = cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_AREA if e < 0.5 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(18, 18, 20)).astype(np.float32)
    m = np.zeros((h + 40, w + 40), np.uint8); cv2.rectangle(m, (20 + 26, 20), (20 + w - 26, 20 + h), 255, -1); cv2.rectangle(m, (20, 20 + 26), (20 + w, 20 + h - 26), 255, -1)
    for px, py in [(46, 46), (20 + w - 26, 46), (46, 20 + h - 26), (20 + w - 26, 20 + h - 26)]: cv2.circle(m, (px, py), 26, 255, -1, cv2.LINE_AA)
    Mf = m.astype(np.float32) / 255
    sh = cv2.GaussianBlur(Mf, (0, 0), 16); reg = c[y - 20 + 14:y + h + 20 + 14, x - 20:x + w + 20]
    reg *= (1 - 0.55 * sh[:reg.shape[0], :reg.shape[1], None])
    reg = c[y - 20:y + h + 20, x - 20:x + w + 20]; vm = Mf[..., None]
    pad = np.zeros_like(reg); pad[20:20 + h, 20:20 + w] = view
    reg[:] = reg * (1 - vm) + pad * vm
    edge = np.zeros_like(Mf); cv2.drawContours(edge, cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], -1, 1.0, 6, cv2.LINE_AA)
    reg[:] = reg * (1 - edge[..., None]) + np.array(RED, np.float32) * edge[..., None]
    if notch: c[y - 4:y + 16, x + w // 2 - 70:x + w // 2 + 70] = np.array(RED, np.float32)

# ---------------------------------------------------------------- the edit
# Layout v2 (Rakshith's notes, 21 Nov): nothing touches the face, label sits tight on the big word, and
# secondary components go in ONE centred row on the chest.
#   face (reel coords): cap top >= 505 (min over all frames), chin <= ~1100, x ~330..750
#   headline: built upward from BASE (big-word baseline, 24 px above the highest cap) -> label glued 20 px above
#   chest row: centred on the body (x 528), y 1180, inside the safe zone (<= 1250)
HX = 524                 # headline centre (body centre, kept inside the safe zone)
BASE = 445 + DY - 26     # 479 : big-word baseline above the head
CHEST_X, CHEST_Y = 528, 1180
LGAP, WGAP = 20, 14      # label-baseline -> word-cap gap ; word-baseline -> next item gap

def _lab_metrics(size, weight=400):
    fo = font(weight, size); asc, desc = fo.getmetrics(); return asc, desc
def stack_h(items):
    h = 0
    for k, it in enumerate(items):
        if it[0] == 'L': asc, desc = _lab_metrics(it[3]); h += (asc + 2) + (LGAP if k + 1 < len(items) else desc)
        else: w = bw(it[1], it[2], it[3]); h += w.cap + (w.ext + WGAP if k + 1 < len(items) else w.ext)
    return h
def stack(c, f, items, top=None, base=None, cx=HX, align_left=True):
    """items: ('L', key, text, size, t) small label | ('W', key, text, cap, t, starts, gone_at, step) big word.
    Either top (y of the first glyph) or base (baseline of the LAST big word) anchors the block."""
    if top is None:   # responsive: shrink the big word until the whole block fits under the safe-zone top
        for _ in range(6):
            tot = stack_h(items) - (lambda it: (bw(it[1], it[2], it[3]).ext) if it[0] == 'W' else 0)(items[-1])
            exc = 276 - (base - tot)
            if exc <= 0: break
            items = [(it[0], it[1] + '_fit', it[2], max(60, int(bw(it[1], it[2], it[3]).cap - exc - 2)), *it[4:]) if it[0] == 'W' else it for it in items]
    words = [bw(it[1], it[2], it[3]) for it in items if it[0] == 'W']
    left = cx - max(w.width for w in words) / 2 if words else cx
    if top is None:
        tot = 0; last = None
        for k, it in enumerate(items):
            if it[0] == 'L': asc, desc = _lab_metrics(it[3]); tot += asc + 2 + LGAP
            else:
                w = bw(it[1], it[2], it[3]); tot += w.cap; last = w
                if k + 1 < len(items): tot += w.ext + WGAP
        top = base - tot
    y = top; boxes = []
    for k, it in enumerate(items):
        if it[0] == 'L':
            _, key, text, size, t = it[:5]; asc, desc = _lab_metrics(size)
            L = lb(key, text, size=size)
            lx = left + 8 if align_left else cx - L.width / 2
            L.draw(c, lx, y - 2, F(t), f, seed=hash(key) % 97)
            boxes.append(('L', L, lx, y - 2)); y += asc + 2 + LGAP
        else:
            _, key, text, cap, t, starts, gone_at, step = (list(it) + [None, None, 1])[:8]
            w = bw(key, text, cap); b = y + w.cap
            word_on(c, key, text, cap, b, t, f, cx=cx, starts=starts, gone_at=gone_at, step=step or 1)
            boxes.append(('W', w, cx, b)); y = b + w.ext + WGAP
    return boxes

def struck(lay):
    """copy of a pill layer with a blocky red pixel ✕ across it."""
    o = lay.copy(); h, w = o.shape[:2]
    for k, u in enumerate(np.linspace(0.12, 0.88, 9)):
        for sg in (0, 1):
            x = int(u * w); y = int((u if sg == 0 else 1 - u) * h * 0.8 + h * 0.1)
            col = np.array(RED if k % 3 else PINK1, np.float32) / 255
            o[max(0, y - 8):y + 8, max(0, x - 8):x + 8, :3] = col; o[max(0, y - 8):y + 8, max(0, x - 8):x + 8, 3] = 1
    return o
_lc = {}
def L_(key, fn):
    if key not in _lc: _lc[key] = fn()
    return _lc[key]
def ctile(text, size=28, check=False, dark=True):
    """auto-width glass tile (optionally with a red check badge)."""
    k = ('ct', text, size, check)
    if k in _lc: return _lc[k]
    from PIL import ImageDraw, ImageFilter
    fo = font(700, size, True); tw = int(fo.getlength(text)); h = int(size * 2.1); pl = 22 + (int(h * 0.62) + 10 if check else 0)
    w = tw + pl + 26
    im = PImage.new('RGBA', (w + 24, h + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 16, w + 14, h + 16), radius=h // 2 - 4, fill=(0, 0, 0, 90)); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 12, h + 12), radius=h // 2 - 4, fill=(22, 18, 22, 238), outline=RED + (255,), width=4)
    if check:
        s = int(h * 0.62); x0 = 12 + 14; y0 = 12 + (h - s) // 2
        d.rounded_rectangle((x0, y0, x0 + s, y0 + s), radius=8, fill=RED + (255,))
        d.line([(x0 + s * 0.22, y0 + s * 0.52), (x0 + s * 0.42, y0 + s * 0.72), (x0 + s * 0.8, y0 + s * 0.3)], fill=(255, 255, 255, 255), width=max(3, s // 8), joint='curve')
    d.text((12 + pl, 12 + (h - size * 1.25) / 2), text, font=fo, fill=(255, 255, 255, 255))
    _lc[k] = to_layer(im); return _lc[k]
def chest_row(c, f, items, y=CHEST_Y, gap=6):
    """items: (layer, t_start[, swap_layer, t_swap]) — final layout centred on the chest; each pops on its word."""
    ws = [it[0].shape[1] for it in items]; tot = sum(ws) + gap * (len(items) - 1); x = CHEST_X - tot / 2
    for it, w in zip(items, ws):
        lay, t0 = it[0], it[1]
        if len(it) > 2 and f >= F(it[3]): lay = it[2]
        a = f - F(t0)
        if a >= 0: over_c(c, lay, x + w / 2, y, s=pop_scale(a))
        x += w + gap

TXT = 290
def render_frame(f, subj):
    t = f / FPS; c = BG0.copy(); behind = []; front = []; fxl = []; post = []; cut = False
    w = wt

    # ===== 0. HOOK 0 -> C1 : google just let | CLAUDE + CODEX ; chest: [Claude Agent][Codex]
    C1a = 2.15
    if t < C1a:
        st = [F(w('claude')) + i for i in range(6)] + [F(w('codex')) + i for i in range(6)]
        behind.append(lambda: stack(c, f, [('L', 'l_g', 'google just let', 52, w('google') + 0.03),
                                          ('W', 'w_cc', 'CLAUDE + CODEX', 150, w('claude'), st)], base=BASE))
        front.append(lambda: chest_row(c, f, [(ctile('Claude Agent', 30), w('claude') + 0.07), (ctile('Codex', 30), w('codex') + 0.07)]))
        fxl.append(lambda: swoosh(c, f - (F(C1a) - 7), n=7, yc=1000))

    # ===== C1 (1.93 -> J0): inside ANDROID STUDIO -> they can TEST their own code
    if F(C1a) <= f < F(J[0]):
        cut = True; tb = F(w('test')) - 1
        if f < tb:
            k = min(len(GD) - 1, int((t - C1a) * 30) + 10)
            screen_cut(c, np.asarray(GD[k]), (0, 0, 976, 752), (640, 100, 976, 318), F(w('studio')) + 2, f)
        else:
            k = min(len(GC) - 1, int((t - w('test')) * 30) + 45)
            screen_cut(c, np.asarray(GC[k]), (0, 40, 976, 700), (0, 225, 720, 400), tb + 6, f)
        def _cw():
            if f < tb:
                st = [F(w('android')) + i for i in range(7)] + [F(w('studio')) + i for i in range(6)]
                stack(c, f, [('L', 'l_in', 'inside', 52, C1a + 0.03), ('W', 'w_as', 'ANDROID STUDIO', 150, w('android'), st)], top=278)
            else:
                bx = stack(c, f, [('L', 'l_they', 'they can', 52, w('test') - 0.03), ('W', 'w_test', 'TEST', 170, w('test'))], top=278, cx=380)
                _, wd, cx_, b = bx[1]
                lb('l_own', 'their own code', size=52).draw(c, cx_ + wd.width / 2 + 30, b - 64, F(w('their')), f, seed=4)
            j = f - F(C1a); halftone_ring(c, j, CX, 880, r0=80, r1=900, op=0.6)
            neon_streak(c, j, n=4, vertical=False, yc=900, amp=60, tail=1000)
        fxl.append(_cw)
        if f - F(C1a) < 3: post.append(('rgb', f - F(C1a)))
        if 0 <= f - tb < 2: post.append(('rgb', f - tb))

    # ===== 1. J0 -> C2 : bring your own | AGENT  ->  now in the | STABLE ; chest: [Rabbit 2 art][Android Studio Rabbit 2][beta ✕]
    C2a = J[1]
    if F(J[0]) <= f < F(C2a):
        def _b():
            if f < F(w('stable')):
                stack(c, f, [('L', 'l_byo', 'bring your own', 52, w('bring')), ('W', 'w_agent1', 'AGENT', 200, w('agent'), None, F(w('stable')) - 4)], base=BASE)
            else:
                stack(c, f, [('L', 'l_now', 'now in the', 52, w('now')), ('W', 'w_stable', 'STABLE', 200, w('stable'))], base=BASE)
        behind.append(_b)
        def _fr():
            rb = img(RAB); art = cd('rabbit_s', rb[0:2001, 2000:4001], 96, 96, radius=20, stroke=4)
            beta = pill('beta', size=34, bg=(70, 70, 76))
            chest_row(c, f, [(art, w('release')), (pill('Android Studio Rabbit 2', size=34), w('release') + 0.1),
                             (beta, w('not'), L_('beta_x', lambda: struck(beta)), w('beta'))])
        front.append(_fr)
        fxl.append(lambda: swoosh(c, f - (F(C2a) - 7), n=7, yc=1000))

    # ===== C2 (J1 -> 12.10): pick from more than | 40+ AGENTS (agent registry)
    C2b = 12.10
    if F(C2a) <= f < F(C2b):
        cut = True
        screen_cut(c, img(REG), (40, 30, 1075, 750), (370, 205, 650, 495), F(w('40')) + 2, f)
        def _cw():
            st = [F(w('40')) + i for i in range(3)] + [F(w('agents')) + i for i in range(6)]
            stack(c, f, [('L', 'l_pick', 'pick from more than', 52, C2a + 0.03), ('W', 'w_40ag', '40+ AGENTS', 170, w('40'), st)], top=278)
            halftone_ring(c, f - F(C2a), CX, 880, r0=80, r1=900, op=0.6)
        fxl.append(_cw)
        if f - F(C2a) < 3: post.append(('rgb', f - F(C2a)))

    # ===== 2. 12.10 -> J2 : your pick | ANY AGENT ; chest: 4 agent tiles
    if F(C2b) <= f < F(J[2]) + 2:
        behind.append(lambda: stack(c, f, [('L', 'l_your', 'your pick', 52, C2b + 0.07),
                                          ('W', 'w_any', 'ANY AGENT', 170, w('claude2') - 0.1, None, F(J[2]) - 2)], base=BASE))
        def _fr():
            if f < F(J[2]):
                chest_row(c, f, [(ctile('Claude Agent', 28), w('claude2')), (ctile('Codex', 28), w('codex2')),
                                 (ctile('Junie', 28), w('juni')), (ctile('Antigravity', 28), w('anti'))])
        front.append(_fr)

    # ===== 3. J2 -> J3 : the big | DIFFERENCE?
    if F(J[2]) - 2 <= f < F(J[3]):
        def _b():
            if f >= F(J[2]): stack(c, f, [('L', 'l_big', 'the big', 52, w('big')), ('W', 'w_diff', 'DIFFERENCE?', 160, w('difference'))], base=BASE)
        behind.append(_b)
        fxl.append(lambda: neon_streak(c, f - (F(J[2]) - 2), n=6, cx=HX + 20, phase=0.4))

    # ===== 4. J3 -> C3 : the agent sees your | PROJECT -> BUILD SETUP -> COMPOSE PREVIEWS ; chest: 3 check tiles
    C3a = J[5]
    if F(J[3]) <= f < F(C3a):
        def _b():
            if f < F(J[4]): it = ('W', 'w_proj', 'PROJECT', 190, w('project'), None, F(J[4]) - 2)
            elif f < F(w('composed')) - 1: it = ('W', 'w_bs', 'BUILD SETUP', 160, w('build'), None, F(w('composed')) - 4)
            else: it = ('W', 'w_cp', 'COMPOSE PREVIEWS', 150, w('composed'))
            stack(c, f, [('L', 'l_sees', 'the agent sees your', 52, w('agent3')), it], base=BASE)
        behind.append(_b)
        front.append(lambda: chest_row(c, f, [(ctile('whole project', 26, True), w('project') + 0.07), (ctile('build setup', 26, True), w('build') + 0.07),
                                             (ctile('compose previews', 26, True), w('composed') + 0.07)]))
        def _fx():
            halftone_ring(c, f - F(J[3]), CX, 900, r0=300, r1=900, band=150, mode='lines', ry_scale=1.5, op=0.7)
            swoosh(c, f - (F(C3a) - 7), n=7, yc=1000)
        fxl.append(_fx)
        if 0 <= f - F(J[3]) < 3: post.append(('radial', f - F(J[3])))
    if F(J[4]) - 1 <= f < F(J[4]) + 2: post.append(('smear', f - (F(J[4]) - 1)))

    # ===== C3 (J5 -> J6): it can | RUN THE APP | on the emulator -> and | CHECKS ITS / OWN WORK
    if F(C3a) <= f < F(J[6]):
        cut = True; ck = F(w('check'))
        if f < ck: screen_cut(c, cc(2.0 + (t - C3a) * 1.1), (0, 0, 1280, 802), (520, 0, 1280, 470), F(w('emulator')), f)
        else: screen_cut(c, cc(11.4 + (t - w('check')) * 0.4), (0, 330, 780, 540), (40, 340, 760, 530), ck + 30, f)
        def _cw():
            if f < ck:
                stack(c, f, [('L', 'l_itcan', 'it can', 52, C3a + 0.03), ('W', 'w_run', 'RUN THE APP', 110, w('run'), None, None, 1),
                             ('L', 'l_emu', 'on the emulator', 52, w('emulator'))], top=278)
            else:
                stack(c, f, [('W', 'w_chk', 'CHECKS ITS', 100, w('check'), None, None, 1), ('W', 'w_work', 'OWN WORK', 100, w('own3'), None, None, 1)], top=300)
            if f - F(C3a) < 3: rgb_ghost(c, f - F(C3a))
        fxl.append(_cw)
        if 0 <= f - ck < 2: post.append(('rgb', f - ck))

    # ===== 5. J6 -> C4 : sign in with | YOUR PLAN ; chest: [the one you already pay for]
    C4a = J[7]
    if F(J[6]) <= f < F(C4a):
        behind.append(lambda: stack(c, f, [('L', 'l_sign', 'sign in with', 52, w('sign')), ('W', 'w_plan', 'YOUR PLAN', 170, w('plan') - 0.2)], base=BASE))
        front.append(lambda: chest_row(c, f, [(pill('the one you already pay for', size=34), w('already'))]))

    # ===== C4 (J7 -> J8): settings › tools › ai › | AGENTS (registry tree)
    if F(C4a) <= f < F(J[8]):
        cut = True
        screen_cut(c, img(REG), (40, 30, 1075, 750), (50, 60, 560, 445), F(w('tools')), f)
        def _cw():
            for i, (txt, k, x) in enumerate([('settings ›', 'settings', 95), ('tools ›', 'tools', 390), ('ai ›', 'ai', 600)]):
                L = lb('p%d' % i, txt, size=60, weight=500); L.draw(c, x, 278, F(w(k)), f, seed=40 + i)
                marker(c, L, x, 278, F(w(k)) - 1, f)
            word_on(c, 'w_agents2', 'AGENTS', 170, 528, w('agents2'), f, cx=HX)
            if f >= F(w('agents2')):
                x0, y0, ww, hh = WIN; bx0, by0, bx1, by1 = fit_box((50, 60, 560, 445), ww / hh)
                sx = ww / (bx1 - bx0); sy = hh / (by1 - by0)
                rx0 = int(x0 + (55 - bx0) * sx); ry0 = int(y0 + (412 - by0) * sy); rx1 = int(x0 + (355 - bx0) * sx); ry1 = int(y0 + (440 - by0) * sy)
                if (f - F(w('agents2'))) % 8 < 6: cv2.rectangle(c, (max(rx0, x0 + 6), ry0), (min(rx1, x0 + ww - 6), ry1), RED, 6, cv2.LINE_AA)
            halftone_ring(c, f - F(C4a), CX, 880, r0=80, r1=900, op=0.6)
        fxl.append(_cw)
        if f - F(C4a) < 3: post.append(('rgb', f - F(C4a)))

    # ===== 6. J8 -> J9 : for | FREELANCERS -> client apps in | DAYS ; chest: 3 app cards + [weeks ✕]
    if F(J[8]) <= f < F(J[9]):
        def _b():
            if f < F(w('days')):
                stack(c, f, [('L', 'l_for', 'for', 52, w('for2')), ('W', 'w_free', 'FREELANCERS', 160, w('freelancers'), None, F(w('days')) - 4)], base=BASE)
            else:
                stack(c, f, [('L', 'l_cin', 'client apps in', 52, w('client')), ('W', 'w_days', 'DAYS', 200, w('days'))], base=BASE)
        behind.append(_b)
        def _fr():
            apps = [(535, 30, 830, 325), (873, 25, 1258, 230), (873, 405, 1258, 610)]
            items = []
            for i, bx in enumerate(apps):
                src = np.ascontiguousarray(cc(4.8)[bx[1]:bx[3], bx[0]:bx[2]])
                items.append((cd('app2_%d' % i, src, 170, 110, radius=16, stroke=4), w('client') + 0.1 * i))
            wk = pill('weeks', size=34, bg=(70, 70, 76))
            items.append((wk, w('weeks'), L_('weeks_x', lambda: struck(wk)), w('weeks') + 0.12))
            chest_row(c, f, items)
        front.append(_fr)

    # ===== 7. J9 -> end : comment | BUILD (+ handle pill on the label row) ; chest: [comment card][5 app prompts][doc][setup guide]
    if F(J[9]) - 2 <= f:
        def _b():
            if f < F(J[9]): return
            bx = stack(c, f, [('L', 'l_comm', 'comment', 56, w('comment')), ('W', 'w_build', 'BUILD', 200, w('build2'))], base=BASE)
            _, L, lx, ly = bx[0]; _, wd, cx_, b = bx[1]
            marker(c, L, lx, ly, F(w('comment')) - 1, f)
            a = f - F(w('send'))
            if a >= 0:
                p = pill('@aiwithrakshith.global', size=30)
                over(c, p, min(lx + L.width + 22, 962 - p.shape[1]), ly + 4 + (0 if a > 2 else (2 - a) * 10))
        behind.append(_b)
        def _fr():
            if f < F(J[9]): return
            cc_ = A.cache.get('comment_card')
            if cc_ is None:
                from PIL import ImageDraw, ImageFilter
                im = PImage.new('RGBA', (270, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                d.rounded_rectangle((8, 10, 262, 92), radius=22, fill=(0, 0, 0, 70)); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
                d.rounded_rectangle((4, 4, 258, 86), radius=22, fill=(255, 255, 255, 255), outline=RED + (255,), width=4)
                d.ellipse((14, 21, 58, 65), fill=RED + (255,)); d.text((27, 26), 'A', font=font(800, 28, False), fill=(255, 255, 255, 255))
                d.text((70, 14), 'your_comment', font=font(600, 17, False), fill=(40, 40, 40, 255))
                d.text((70, 36), 'BUILD', font=font(900, 34, False), fill=RED + (255,))
                d.text((214, 30), '♥', font=font(700, 28, False), fill=RED + (255,))
                cc_ = to_layer(im); A.cache['comment_card'] = cc_
            chest_row(c, f, [(cc_, w('comment') + 0.13), (pill('5 app prompts', size=30), w('5')),
                             (icon('doc', 64), w('guide')), (pill('setup guide', size=30), w('guide') + 0.07)])
            if f >= F(VO_END):
                rnd = random.Random(f // 3)
                for _ in range(2): draw_blocks(c, [(f, 1, rnd.uniform(110, 940), rnd.uniform(1135, 1225), rnd.choice([18, 24]), rnd.choice(BLOCK_COLS), 0.8)], f)
        front.append(_fr)
        fxl.append(lambda: neon_streak(c, f - (F(J[9]) - 2), n=6, cx=HX + 20, phase=2.6))

    # ---------------------------------------------------------------- composite
    if not cut:
        sl = subj.get(f); c[:] = subj.room
        for d_ in behind: d_()
        over(c, sl, 0, 0)
        for d_ in front: d_()
    for d_ in fxl: d_()
    for kind, j in post:
        if kind == 'smear' and 0 <= j < 3: vertical_smear(c, j)
        if kind == 'radial' and 0 <= j < 3: radial_blur(c, CX, 900, amt=[0.06, 0.04, 0.02][j])
        if kind == 'rgb': rgb_ghost(c, j)
    if f < 3:                                     # negative flash open
        negative(c, blur=9); c *= 0.55; rnd = random.Random(f); colb = (0x29, 0xE0, 0xE6) if f < 2 else RED
        for _ in range(2):
            x, y = rnd.uniform(420, 640), rnd.uniform(600, 900); c[int(y):int(y) + 48, int(x):int(x) + 48] = np.array(colb, np.float32)
    elif f < 6:                                   # scale-in
        j = f - 3; s = [0.92, 0.96, 0.99][j]; bl = [12, 6, 2][j]
        M = np.float32([[s, 0, 540 * (1 - s)], [0, s, 960 * (1 - s)]])
        c[:] = cv2.GaussianBlur(cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REPLICATE), (0, 0), bl)
    for jt in (J[0], J[6]):                       # cutaway exits on a jump cut: magenta ghost 1 fr -> negative 2 fr
        j = f - F(jt)
        if j == 0: magenta_ghost(c)
        elif j in (1, 2):
            negative(c, blur=8 - 3 * j); c *= [0.55, 0.7][j - 1]
            if j == 1: c[640:680, 300:340] = np.array((0x29, 0xE0, 0xE6), np.float32)
    for jt in (C2b, J[8]):                        # other exits: negative flash 2 fr
        j = f - F(jt)
        if 0 <= j < 2: negative(c, blur=9 - 4 * j); c *= 0.6
    grain(c, 2 * f + int(SUB * 2), amt=3.5)
    return np.clip(c, 0, 255).astype(np.uint8)
BG0 = np.zeros((H, W, 3), np.float32)

if __name__ == '__main__':
    g0, g1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; g1 = min(g1, 2 * NF)
    if out.endswith('.mp4'):
        subj = Subject(g0 // 2)
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '60', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for g in range(g0, g1):
            SUB = (g % 2) * 0.5
            ff.stdin.write(render_frame(g // 2, subj).tobytes())
            if g % 120 == 0: print('frame', g, flush=True)
        ff.stdin.close(); ff.wait()
        json.dump(TLOG, open(out + '.tlog.json', 'w'))
    else:
        os.makedirs(out, exist_ok=True)
        for g in [int(x) for x in sys.argv[4].split(',')]:
            SUB = (g % 2) * 0.5
            subj = Subject(max(0, g // 2)); im = render_frame(g // 2, subj); cv2.imwrite(f'{out}/g{g:04d}.png', im[..., ::-1])
