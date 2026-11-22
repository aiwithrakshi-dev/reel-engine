# Day 24 — "There is no Gemini 4 Pro" (aiwithrakshith.global, English VO) — /temp-1 house style, 60 fps
# Built from examples/day4_android_studio/render_day4_60.py (helpers kept), new timeline + captions + face checks.
# Safe zone x 65..960, y 270..1250. Logic frame f in 30-fps units, SUB = 0 / 0.5 for 60 fps in-betweens.
# usage: HOOK=strip_slam python3 render_d24_60.py <g0> <g1> <out.mp4> | python3 render_d24_60.py 0 0 <png_dir> g1,g2,...
import sys, json, math, random, subprocess, os
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = '/home/claude/reel-engine/engine'
sys.path.insert(0, HERE); sys.path.insert(1, ENG)
from fx import *
import fx as _fx
from islands_d24 import snapped
from PIL import Image as PImage, ImageDraw, ImageFilter
from hooks import apply_hook, HOOKS
from face_guard import FaceZone, protect_face
from captions import chunk_words, CaptionTrack, write_srt, apply_glossary
from ref_devices import slate
import ref_devices as _rd

HOOK = os.environ.get('HOOK', 'strip_slam')    # neg_flash blocked (hook_log): strip_slam = high energy, unused
assert HOOK in HOOKS
D = '/home/claude/d24/'
DY = 40                                        # cap top >= 505, chin <= ~1070 in reel coords
CAP_TOP, CHIN, HX0, HX1 = 465 + DY, 1030 + DY, 350, 730
FACE_ZONE = FaceZone.from_head(cap_top=CAP_TOP, chin=CHIN, x0=HX0, x1=HX1)
FACE = (540, (CAP_TOP + CHIN) // 2)
SUB = 0.0
def _cont(fn):
    def g(canvas, j, *a, **k):
        n = k.get('n', fn.__defaults__[0] if fn is not _fx.halftone_ring else 5)
        if 0 <= j < n - 1: j = j + SUB
        return fn(canvas, j, *a, **k)
    return g
neon_streak = _cont(_fx.neon_streak); halftone_ring = _cont(_fx.halftone_ring); swoosh = _cont(_fx.swoosh)

def F(t): return int(round(t * FPS))
J = [s[2] for s in snapped()][1:]              # 9 jump cuts
VO_END = snapped()[-1][3]; END_T = round(VO_END + 0.82, 2); NF = F(END_T); HIT_T = VO_END + 0.28
SX0, SX1, SY0, SY1 = 65, 960, 270, 1250
CX = (SX0 + SX1) // 2; MAXW = SX1 - SX0 - 30

# ---------------------------------------------------------------- words (reel seconds, onset-verified)
WL = json.load(open(D + 'words_final_list.json'))
_n = {}; WK = {}
for w_, s_, e_ in WL:
    k = ''.join(ch for ch in w_.lower() if ch.isalnum()); i = _n.get(k, 0); _n[k] = i + 1
    WK[k + (str(i) if i else '')] = s_
WK['on1'] = 26.85
def w(k): return WK[k]

# ---------------------------------------------------------------- subject + room
from subject_d24 import combined_alpha
class Subject:
    def __init__(self, f0):
        self.v = cv2.VideoCapture(D + 'aroll_tight30.mp4'); self.a = cv2.VideoCapture(D + 'alpha_r50.mkv')
        self.n = 1102; self.pos = -1
        if 0 < f0 < self.n:
            self.v.set(cv2.CAP_PROP_POS_FRAMES, f0); self.a.set(cv2.CAP_PROP_POS_FRAMES, f0); self.pos = f0 - 1
        self.tail = None; self.cache = None
    def get(self, f):
        if f < self.n:
            while self.pos < f:
                _, fr = self.v.read(); _, al = self.a.read(); self.pos += 1; self.cache = (fr, al)
        else:
            if self.tail is None:
                vt = cv2.VideoCapture(D + 'aroll_tail30.mp4'); at = cv2.VideoCapture(D + 'alpha_tail.mkv'); self.tail = []
                while True:
                    ok, fr = vt.read(); ok2, al = at.read()
                    if not ok or not ok2: break
                    self.tail.append((fr, al))
            k = f - self.n; n = len(self.tail); per = 2 * n - 2
            k = k % per; k = k if k < n else per - k            # boomerang the tail for the end hold
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

# ---------------------------------------------------------------- helpers (approved engine)
class A: cache = {}
TH = [True]                                     # talking-head frame? (face checks apply)
def bw(key, text, cap, **kw):
    kw.setdefault('maxw', MAXW)
    if key not in A.cache: A.cache[key] = BigWord(text, cap, **kw)
    return A.cache[key]
def lb(key, text, **kw):
    if key not in A.cache: A.cache[key] = Label(text, **kw)
    return A.cache[key]
def chk(box, what):
    if TH[0]:
        FACE_ZONE.check(box, what, CUR_T[0])
    x0, y0, x1, y1 = box
    if x0 < SX0 - 2 or x1 > SX1 + 2 or y0 < SY0 - 2 or y1 > SY1 + 2:
        raise ValueError(f'{what} {tuple(int(v) for v in box)} outside the safe zone at {CUR_T[0]:.2f}s')
CUR_T = [0.0]
SAFE_OUT = np.ones((H, W), np.float32); SAFE_OUT[SY0 + 30:SY1 - 30, SX0 + 30:SX1 - 30] = 0
SAFE_OUT = np.clip(cv2.GaussianBlur(SAFE_OUT, (0, 0), 14) * 1.0, 0, 1)[..., None]; SAFE_OUT[:SY0] = 1; SAFE_OUT[SY1:] = 1; SAFE_OUT[:, :SX0] = 1; SAFE_OUT[:, SX1:] = 1
def blocks_for_word(key, word, cx, base, f0, step=1, extra=6, seed=0):
    k = 'blk_' + key
    if k in A.cache: return A.cache[k]
    boxes = word.letter_boxes(cx, base)
    def bf(fr):
        i = (fr - f0) // step
        if i < 0 or i >= len(boxes) + extra // step: return None
        b = boxes[min(i, len(boxes) - 1)]
        return (max(SX0, b[0]), max(SY0, b[1]), min(SX1 - 42, b[2]), b[3])
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
TLOG = {}
def word_on(c, key, text, cap, base, t, f, cx=CX, starts=None, gone_at=None, step=1):
    wd = bw(key, text, cap); f0 = F(t)
    fin = (max(starts) if starts else f0 + step * (wd.n() - 1)) + 2
    e = TLOG.setdefault(key, {'text': text, 'start': f0, 'full': fin, 'last': f, 'gone': gone_at}); e['last'] = max(e['last'], f)
    if f >= f0: chk((cx - wd.width / 2, base - wd.cap, cx + wd.width / 2, base + wd.ext), f'big word {text!r}')
    wd.draw(c, cx, base, f0, f, starts=starts, gone=gone_set(wd, f, gone_at) if gone_at else None, step=step)
    draw_blocks(c, blocks_for_word(key, wd, cx, base, f0, step=step), f)
    if gone_at: draw_blocks(c, dissolve_blocks(key, wd, cx, base, gone_at), f)
    return wd
def strike_x(c, cx, cy, ww, hh, f, f0):
    """red pixel ✕ stamped over a word (2-frame overshoot)."""
    if f < f0: return
    n = int(ww / 26) + 1; shown = min(n, (f - f0 + 1) * (n // 4 + 1))              # pixel strike-through, drawn left -> right in 4 frames
    rnd = random.Random(11)
    for k in range(shown):
        u = -1 + 2 * k / (n - 1); px = cx + u * ww / 2; py = cy + rnd.uniform(-6, 6) - u * hh * 0.08
        x0, y0 = int(px // 6 * 6), int(py // 6 * 6)
        c[y0 - 8:y0 + 22, x0 + 3:x0 + 33] = np.array((40, 4, 6), np.float32)          # dark drop
        c[y0 - 12:y0 + 18, x0:x0 + 30] = np.array((255, 255, 255) if k % 4 else PINK2, np.float32)

HX = 526
BASE = CAP_TOP - 34                             # 481: big-word baseline (+extrude) clears the face zone
CHEST_X, CHEST_Y = 528, 1126
LGAP, WGAP = 20, 14
def _lab_metrics(size, weight=400):
    fo = font(weight, size); return fo.getmetrics()
def stack_h(items):
    h = 0
    for k, it in enumerate(items):
        if it[0] == 'L': asc, desc = _lab_metrics(it[3]); h += (asc + 2) + (LGAP if k + 1 < len(items) else desc)
        else: wd = bw(it[1], it[2], it[3]); h += wd.cap + (wd.ext + WGAP if k + 1 < len(items) else wd.ext)
    return h
def stack(c, f, items, top=None, base=None, cx=HX, align_left=True):
    if top is None:
        for _ in range(6):
            tot = stack_h(items) - (lambda it: (bw(it[1], it[2], it[3]).ext) if it[0] == 'W' else 0)(items[-1])
            exc = 278 - (base - tot)
            if exc <= 0: break
            items = [(it[0], it[1] + '_fit', it[2], max(60, int(bw(it[1], it[2], it[3]).cap - exc - 2)), *it[4:]) if it[0] == 'W' else it for it in items]
    words = [bw(it[1], it[2], it[3]) for it in items if it[0] == 'W']
    left = cx - max(wd.width for wd in words) / 2 if words else cx
    if top is None:
        tot = 0
        for k, it in enumerate(items):
            if it[0] == 'L': asc, desc = _lab_metrics(it[3]); tot += asc + 2 + LGAP
            else:
                wd = bw(it[1], it[2], it[3]); tot += wd.cap
                if k + 1 < len(items): tot += wd.ext + WGAP
        top = base - tot
    y = top; boxes = []
    for k, it in enumerate(items):
        if it[0] == 'L':
            _, key, text, size, t = it[:5]; asc, desc = _lab_metrics(size)
            L = lb(key, text, size=size)
            lx = left + 8 if align_left else cx - L.width / 2
            if f >= F(t): chk((lx, y - 2, lx + L.width, y - 2 + L.h), f'label {text!r}')
            L.draw(c, lx, y - 2, F(t), f, seed=hash(key) % 97)
            boxes.append(('L', L, lx, y - 2)); y += asc + 2 + LGAP
        else:
            _, key, text, cap, t, starts, gone_at, step = (list(it) + [None, None, 1])[:8]
            wd = bw(key, text, cap); b = y + wd.cap
            word_on(c, key, text, cap, b, t, f, cx=cx, starts=starts, gone_at=gone_at, step=step or 1)
            boxes.append(('W', wd, cx, b)); y = b + wd.ext + WGAP
    return boxes
_lc = {}
def L_(key, fn):
    if key not in _lc: _lc[key] = fn()
    return _lc[key]
def ctile(text, size=24, check=False, cross=False):
    """auto-width dark glass tile with red stroke (optional red check badge)."""
    k = ('ct', text, size, check, cross)
    if k in _lc: return _lc[k]
    fo = font(700, size, True); tw = int(fo.getlength(text)); h = int(size * 2.1); pl = 22 + (int(h * 0.62) + 10 if check else 0)
    ww = tw + pl + 26
    im = PImage.new('RGBA', (ww + 24, h + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 16, ww + 14, h + 16), radius=h // 2 - 4, fill=(0, 0, 0, 90)); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, ww + 12, h + 12), radius=h // 2 - 4, fill=(22, 18, 22, 238), outline=RED + (255,), width=4)
    if check:
        s = int(h * 0.62); x0 = 12 + 14; y0 = 12 + (h - s) // 2
        d.rounded_rectangle((x0, y0, x0 + s, y0 + s), radius=8, fill=RED + (255,))
        d.line([(x0 + s * 0.22, y0 + s * 0.52), (x0 + s * 0.42, y0 + s * 0.72), (x0 + s * 0.8, y0 + s * 0.3)], fill=(255, 255, 255, 255), width=max(3, s // 8), joint='curve')
    d.text((12 + pl, 12 + (h - size * 1.25) / 2), text, font=fo, fill=(255, 255, 255, 255))
    _lc[k] = to_layer(im); return _lc[k]
def chest_row(c, f, items, y=CHEST_Y, gap=6):
    """items: (layer, t_start) — one row centred on the chest; each pops on its word."""
    ws = [it[0].shape[1] for it in items]; tot = sum(ws) + gap * (len(items) - 1); x = CHEST_X - tot / 2
    for it, ww in zip(items, ws):
        lay, t0 = it[0], it[1]; a = f - F(t0)
        if a >= 0:
            hh = lay.shape[0]; chk((x + 12, y - hh / 2 + 12, x + ww - 12, y + hh / 2 - 12), 'chest tile')
            over_c(c, lay, x + ww / 2, y, s=pop_scale(a))
        x += ww + gap
CHEST_BOX = (65, CHEST_Y - 28, 960, CHEST_Y + 28)

# ---------------------------------------------------------------- slate graphics (our own, from verified facts)
def rgba_icon(name, size):
    k = ('ic', name, size)
    if k not in _lc:
        im = PImage.open(D + 'assets/' + name + '.png').convert('RGBA').resize((size, size), PImage.LANCZOS); _lc[k] = im
    return _lc[k]
def panel(wd, hh, radius=26, fill=(246, 246, 248, 255), stroke=None):
    im = PImage.new('RGBA', (wd + 48, hh + 48), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((28, 34, wd + 28, hh + 34), radius, fill=(0, 0, 0, 130)); im = im.filter(ImageFilter.GaussianBlur(10)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((24, 24, wd + 24, hh + 24), radius, fill=fill, outline=stroke, width=6 if stroke else 0)
    return im, d
def model_card(name, icon_name, lines, tag, hot=False):
    k = ('mc', name)
    if k in _lc: return _lc[k]
    im, d = panel(400, 420, stroke=RED + (255,) if hot else None)
    ic = rgba_icon(icon_name, 150); im.alpha_composite(ic, (24 + 125, 50))
    d.text((24 + 200, 222), 'GEMINI 4', font=font(800, 24, False), fill=(120, 120, 128, 255), anchor='mm')
    d.text((24 + 200, 268), name, font=font(900, 64, True), fill=RED + (255,) if hot else (20, 20, 24, 255), anchor='mm')
    y = 318
    for ln in lines:
        d.text((24 + 200, y), ln, font=font(600, 25, False), fill=(40, 40, 46, 255), anchor='mm'); y += 34
    tw = font(800, 22, False).getlength(tag) + 34
    d.rounded_rectangle((24 + 200 - tw / 2, 400, 24 + 200 + tw / 2, 436), 18, fill=RED + (255,))
    d.text((24 + 200, 418), tag, font=font(800, 22, False), fill=(255, 255, 255, 255), anchor='mm')
    _lc[k] = to_layer(im); return _lc[k]
def leak_chart():
    k = ('leak',)
    if k in _lc: return _lc[k]
    im, d = panel(820, 460, fill=(30, 34, 42, 255))
    d.text((64, 64), '“GEMINI 4 PRO” BENCHMARKS', font=font(800, 34, False), fill=(235, 235, 240, 255))
    d.text((64, 108), 'screenshot going round online', font=font(500, 26, True), fill=(150, 154, 165, 255))
    rnd = random.Random(7)
    for i in range(5):
        y = 170 + i * 58; L = rnd.uniform(0.45, 0.95)
        d.text((64, y + 6), '???', font=font(700, 26, False), fill=(130, 134, 145, 255))
        d.rounded_rectangle((150, y, 150 + int(600 * L), y + 38), 10, fill=(92, 98, 112, 255))
    _lc[k] = to_layer(im); return _lc[k]
def stamp(text):
    k = ('stamp', text)
    if k in _lc: return _lc[k]
    fo = font(900, 64, False); tw = int(fo.getlength(text)); ww, hh = tw + 70, 110
    im = PImage.new('RGBA', (ww + 40, hh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((24, 28, ww + 20, hh + 24), 18, fill=(0, 0, 0, 120)); im = im.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, ww + 20, hh + 20), 18, fill=RED + (255,), outline=(255, 255, 255, 255), width=6)
    d.text((20 + ww / 2, 20 + hh / 2), text, font=fo, fill=(255, 255, 255, 255), anchor='mm')
    im = im.rotate(-8, expand=True, resample=PImage.BICUBIC)
    _lc[k] = to_layer(im); return _lc[k]
PRICE_ROWS = [('Input', '$2', '$4'), ('Output', '$10', '$20'), ('Cached input', '$0.10', '$0.20')]
def price_table(stage):
    """stage: rows shown (0..3); new column shown if stage >= 4."""
    k = ('price', stage)
    if k in _lc: return _lc[k]
    im, d = panel(840, 470)
    ic = rgba_icon('price', 84); im.alpha_composite(ic, (24 + 730, 44))
    d.text((64, 58), 'GEMINI 4 ARGON · API', font=font(850, 34, False), fill=(20, 20, 24, 255))
    d.text((64, 102), 'per 1M tokens', font=font(500, 26, True), fill=(110, 110, 118, 255))
    d.text((470, 170), 'TO NOV 30', font=font(800, 24, False), fill=(110, 110, 118, 255), anchor='mm')
    if stage >= 4: d.text((720, 170), 'FROM DEC 1', font=font(850, 24, False), fill=RED + (255,), anchor='mm')
    for i, (lab, a, b) in enumerate(PRICE_ROWS):
        if stage < i + 1: break
        y = 230 + i * 78
        d.line((64, y - 30, 840, y - 30), fill=(225, 225, 230, 255), width=2)
        d.text((64, y), lab, font=font(700, 32, False), fill=(30, 30, 36, 255), anchor='lm')
        d.text((470, y), a, font=font(800, 40, False), fill=(30, 30, 36, 255), anchor='mm')
        if stage >= 4:
            d.rounded_rectangle((640, y - 30, 800, y + 30), 14, fill=RED + (255,))
            d.text((720, y), b, font=font(900, 40, False), fill=(255, 255, 255, 255), anchor='mm')
    d.text((64, 470), 'Carbon has the same prices · source: Google Gemini API pricing', font=font(500, 22, True), fill=(120, 120, 128, 255))
    _lc[k] = to_layer(im); return _lc[k]
def place(c, lay, cx, cy, f, f0, what):
    a = f - f0
    if a < 0: return
    hh, ww = lay.shape[:2]; chk((cx - ww / 2 + 20, cy - hh / 2 + 20, cx + ww / 2 - 20, cy + hh / 2 - 20), what)
    over_c(c, lay, cx, cy, s=pop_scale(a))

# ---------------------------------------------------------------- captions (karaoke, word-synced, English)
CW = [list(x) for x in WL]
for i, x in enumerate(CW):
    if x[0] == 'for' and i > 0 and CW[i - 1][0].lower() == 'gemini': x[0] = '4'
    if x[0].lower() == 'model' and i > 0 and CW[i - 1][0].lower() == 'comment': x[0] = 'MODEL'
    if x[0] == 'Pro,' and i < 8: pass
def _merge(ws, seq):
    out = []; i = 0; n = len(seq)
    while i < len(ws):
        if [x[0].strip(',.!').lower() for x in ws[i:i + n]] == [q.lower() for q in seq]:
            out.append([' '.join(x[0] for x in ws[i:i + n]), ws[i][1], ws[i + n - 1][2]]); i += n
        else: out.append(ws[i]); i += 1
    return out
for seq in (['Gemini', '4', 'Pro'], ['Gemini', '4'], ['December', '1st'], ['cost', 'saving'], ['batch', 'jobs'], ['set', 'up']):
    CW = _merge(CW, seq)
CHUNKS = apply_glossary(chunk_words([(a, b, c_) for a, b, c_ in CW]), {'cost saving': 'cost-saving'})
from captions import FUNC as _FUNC
def _tidy(chunks):
    """captions never end on and/the/a...: move a trailing function word to the next line; start a line at 'comment';
    hold the last line until the VO ends."""
    out = [dict(c, words=list(c['words'])) for c in chunks]
    for i, c in enumerate(out):
        for j, wd in enumerate(c['words']):
            if j > 0 and wd[0].lower() == 'comment':
                out.insert(i + 1, {'words': c['words'][j:]}); c['words'] = c['words'][:j]; break
    for i in range(len(out) - 1):
        c, n_ = out[i], out[i + 1]
        while len(c['words']) > 1 and c['words'][-1][0].strip(',.').lower() in _FUNC and len(n_['words']) < 5:
            n_['words'].insert(0, c['words'].pop())
    k = 1
    while k < len(out):                                   # a one-word line shorter than 0.4 s joins the line before it
        if len(out[k]['words']) == 1 and k + 1 < len(out) and out[k + 1]['words'][0][1] - out[k]['words'][0][1] < 0.4:
            if len(' '.join(x[0] for x in out[k - 1]['words'] + out[k]['words'])) <= 30: out[k - 1]['words'] += out[k]['words']
            else: out[k + 1]['words'] = out[k]['words'] + out[k + 1]['words']
            del out[k]
        else: k += 1
    for c in out:
        c['start'] = c['words'][0][1]; c['text'] = ' '.join(x[0] for x in c['words'])
    for a_, b_ in zip(out, out[1:]): a_['end'] = b_['start']
    out[-1]['end'] = VO_END - 0.1
    return out
CHUNKS = _tidy(CHUNKS)
CAPS = CaptionTrack(CHUNKS, mode='karaoke', y_bottom=1250, cx=CX, face_box=FACE_ZONE.box, avoid=[(65, CHEST_Y - 28, 960, CHEST_Y + 16)])

# ---------------------------------------------------------------- the edit
C1a, C1b = J[1], J[3]           # cutaway 1: the Gemini 4 models            5.72 -> 9.88
C2a, C3a, C3b = J[6], J[7], w('so')   # cutaway 2: leaked "4 Pro" chart 19.32 -> 24.40 ; cutaway 3: price card -> 28.22
def render_frame(f, subj):
    t = f / FPS; CUR_T[0] = t
    c = np.zeros((H, W, 3), np.float32); behind = []; front = []; fxl = []; post = []; cut = False

    # ===== S0 0 -> J0 : there is no | GEMINI 4 PRO (✕) ; chest: [just a leaked name]
    if f < F(J[0]):
        st = [F(w('gemini')) + i for i in range(6)] + [F(w('4'))] + [F(w('pro')) + i for i in range(3)]
        def _b():
            bx = stack(c, f, [('L', 'l_no', 'there is no', 52, 0.16), ('W', 'w_g4p', 'GEMINI 4 PRO', 140, w('gemini'), st)], base=BASE)
            _, wd, cx_, b = bx[1]; strike_x(c, cx_, b - wd.cap / 2, wd.width * 0.92, wd.cap * 1.1, f, F(w('pro')) + 6)
        behind.append(_b)
        front.append(lambda: chest_row(c, f, [(ctile('only a leaked name', 28), w('pro') + 0.25)]))
        fxl.append(lambda: neon_streak(c, f - (F(J[0]) - 2), n=6, cx=HX + 20, phase=0.4))

    # ===== S1 J0 -> C1a : the one you can use | DOUBLES ; chest: [$2 → $4 per 1M input] [Dec 1]
    if F(J[0]) <= f < F(C1a):
        behind.append(lambda: stack(c, f, [('L', 'l_one', 'the one you can use', 52, w('the')), ('W', 'w_dbl', 'DOUBLES', 190, w('doubles'))], base=BASE))
        front.append(lambda: chest_row(c, f, [(ctile('API: $2 → $4 per 1M input', 26), w('price')), (ctile('from Dec 1', 26, True), w('next'))]))
        fxl.append(lambda: swoosh(c, f - (F(C1a) - 7), n=7, yc=1000))

    # ===== C1 (J1 -> J3): Gemini 4 | REAL MODELS -> the real ones | ARGON + CARBON ; model cards + Hydrogen chip
    if F(C1a) <= f < F(C1b):
        cut = True; slate(c, seed=f % 7)
        def _cw():
            if f < F(w('argon')):
                st = [F(w('real')) + i for i in range(4)] + [F(w('models')) + i for i in range(6)]
                stack(c, f, [('L', 'l_g4h', 'Gemini 4 has', 52, C1a + 0.05), ('W', 'w_real', 'REAL MODELS', 150, w('real'), st, F(w('argon')) - 4)], top=290)
            else:
                st = [F(w('argon')) + i for i in range(5)] + [F(w('and1')) + 1] + [F(w('carbon')) + i for i in range(6)]
                stack(c, f, [('L', 'l_real', 'the real names', 52, w('argon')), ('W', 'w_ac', 'ARGON + CARBON', 130, w('argon'), st)], top=290)
            if f < F(w('argon')): _rd.badge(c, 'GEMINI 4', f, F(w('41')), cx=CX, cy=800, size=110)
            place(c, model_card('Argon', 'argon', ['API + Gemini app', 'since Oct 13'], 'USE IT TODAY'), 290, 790, f, F(w('argon')), 'argon card')
            place(c, model_card('Carbon', 'carbon', ["Google's strongest", 'API + AI Ultra · Nov 10'], 'SCORES HIGHER', hot=True), 735, 790, f, F(w('carbon')), 'carbon card')
            place(c, ctile('+ Hydrogen · fast model · Nov 12', 24), CX, 1060, f, F(w('carbon')) + 9, 'hydrogen chip')
            halftone_ring(c, f - F(C1a), CX, 820, r0=80, r1=520, op=0.6)
        fxl.append(_cw)
        if f - F(C1a) < 3: post.append(('rgb', f - F(C1a)))

    # ===== S2 C1b -> J4 : use it today | ARGON ; chest: [✓ Gemini app] [✓ API]
    if F(C1b) <= f < F(J[4]):
        behind.append(lambda: stack(c, f, [('L', 'l_today', 'use it today', 52, w('use1')), ('W', 'w_argon', 'ARGON', 210, w('argon1'))], base=BASE))
        front.append(lambda: chest_row(c, f, [(ctile('Gemini app', 28, True), w('app')), (ctile('API', 28, True), w('api'))]))
        fxl.append(lambda: neon_streak(c, f - (F(J[4]) - 2), n=6, cx=HX + 20, phase=1.7))

    # ===== S3a J4 -> J5 : scores higher on Google's tests | CARBON ; chest: [Google's own benchmarks]
    if F(J[4]) <= f < F(J[5]):
        behind.append(lambda: stack(c, f, [('L', 'l_scores', 'scores higher on Google\'s tests', 48, w('scores')), ('W', 'w_carbon', 'CARBON', 200, w('carbon1'))], base=BASE))
        front.append(lambda: chest_row(c, f, [(ctile("Google's own benchmarks", 28), w('googles'))]))

    # ===== S3b J5 -> C2a : at launch, only | CYBER TEAMS ; chest: [cyber teams first · Oct 28] [✓ open since Nov 10]
    if F(J[5]) <= f < F(C2a):
        st = [F(w('cybersecurity')) + i for i in range(5)] + [F(w('teams')) + i for i in range(5)]
        behind.append(lambda: stack(c, f, [('L', 'l_launch', 'at launch, only', 52, w('only')), ('W', 'w_cyber', 'CYBER TEAMS', 160, w('cybersecurity'), st)], base=BASE))
        front.append(lambda: chest_row(c, f, [(ctile('cyber teams first · Oct 28', 26), w('teams')), (ctile('open since Nov 10', 26, True), w('can2'))]))
        def _fx():
            halftone_ring(c, f - F(J[5]), CX, 880, r0=200, r1=560, band=130, mode='lines', ry_scale=1.5, op=0.7)
        fxl.append(_fx)
        if 0 <= f - F(J[5]) < 3: post.append(('radial', f - F(J[5])))
    if F(C2a) - 1 <= f < F(C2a) + 2: post.append(('smear', f - (F(C2a) - 1)))

    # ===== C2 (J6 -> J7): if a video shows | GEMINI 4 PRO -> that name | DOESN'T EXIST ; leaked chart + stamp
    if F(C2a) <= f < F(C3a):
        cut = True; slate(c, seed=3 + f % 7)
        def _cw():
            if f < F(w('that')):
                st = [F(w('gemini2')) + i for i in range(6)] + [F(w('42'))] + [F(w('pro1')) + i for i in range(3)]
                stack(c, f, [('L', 'l_vid', 'if a video shows', 52, w('if')), ('W', 'w_g4p2', 'GEMINI 4 PRO', 140, w('gemini2'), st, F(w('that')) - 4)], top=290)
            else:
                st = [F(w('doesnt')) + i for i in range(7)] + [F(w('exist')) + i for i in range(5)]
                stack(c, f, [('L', 'l_name', 'that name', 52, w('that')), ('W', 'w_dne', "DOESN'T EXIST", 120, w('doesnt'), st)], top=290)
            place(c, leak_chart(), CX, 820, f, F(w('video')), 'leak chart')
            place(c, stamp('NOT A REAL MODEL'), CX, 830, f, F(w('name')), 'stamp')
            halftone_ring(c, f - F(C2a), CX, 820, r0=80, r1=520, op=0.6)
        fxl.append(_cw)
        if f - F(C2a) < 3: post.append(('rgb', f - F(C2a)))

    # ===== C3 (J7 -> 'so'): reports say Argon's API | PRICE DOUBLES -> from | DEC 1 ; price card
    if F(C3a) <= f < F(C3b):
        cut = True; slate(c, seed=11 + f % 7)
        def _cw():
            if f < F(w('december')):
                st = [F(w('price1')) + i for i in range(5)] + [F(w('doubles1')) + i for i in range(7)]
                stack(c, f, [('L', 'l_rep', 'Argon API', 52, w('reports')), ('W', 'w_pd', 'PRICE DOUBLES', 130, w('price1'), st, F(w('december')) - 3)], top=290)
            else:
                st = [F(w('december')) + i for i in range(3)] + [F(w('1st'))]
                stack(c, f, [('L', 'l_from', 'from', 52, w('december')), ('W', 'w_dec', 'DEC 1', 200, w('december'), st)], top=290)
            stg = 0 if f < F(w('reports')) else 0.5
            for i, k in enumerate(('argons', 'api1', 'price1')):
                if f >= F(w(k)): stg = i + 1
            if f >= F(w('doubles1')): stg = 4
            if f >= F(w('reports')):
                a = f - F(w('reports')); lay = price_table(stg); hh, ww = lay.shape[:2]
                chk((CX - ww / 2 + 20, 830 - hh / 2 + 20, CX + ww / 2 - 20, 830 + hh / 2 - 20), 'price card')
                over_c(c, lay, CX, 830, s=pop_scale(a) if a < 4 else (1.03 if 0 <= f - F(w('doubles1')) < 2 else 1.0))
            halftone_ring(c, f - F(C3a), CX, 830, r0=200, r1=560, band=130, mode='lines', ry_scale=1.5, op=0.6)
        fxl.append(_cw)
        if f - F(C3a) < 3: post.append(('rgb', f - F(C3a)))

    # ===== S4 'so' -> 'comment' : this week, run your | BATCH JOBS -> or set up | CACHING ; chest tiles
    if F(C3b) <= f < F(w('comment')):
        def _b():
            if f < F(w('set')):
                st = [F(w('batch')) + i for i in range(5)] + [F(w('jobs')) + i for i in range(4)]
                stack(c, f, [('L', 'l_run', 'this week, run your', 52, w('so') + 0.05), ('W', 'w_batch', 'BATCH JOBS', 170, w('batch'), st, F(w('set')) - 4)], base=BASE)
            else:
                stack(c, f, [('L', 'l_set', 'or set up', 52, w('set')), ('W', 'w_cache', 'CACHING', 190, w('caching'))], base=BASE)
        behind.append(_b)
        front.append(lambda: chest_row(c, f, [(ctile('Batch API = half price', 26), w('jobs')), (ctile('cached input: −95%', 26, True), w('caching'))]))

    # ===== S5 'comment' -> end : comment | MODEL + handle pill ; chest: [comment card] [Gemini 4 cost-saving checklist]
    if F(w('comment')) <= f:
        def _b():
            bx = stack(c, f, [('L', 'l_comm', 'comment', 56, w('comment')), ('W', 'w_model', 'MODEL', 210, w('model'))], base=BASE)
            _, L, lx, ly = bx[0]
            a = f - F(w('send'))
            if a >= 0:
                p = pill('@aiwithrakshith.global', size=30); px = min(lx + L.width + 22, SX1 - p.shape[1])
                chk((px, ly + 4, px + p.shape[1], ly + 4 + p.shape[0]), 'handle pill')
                over(c, p, px, ly + 4 + (0 if a > 2 else (2 - a) * 10))
        behind.append(_b)
        def _fr():
            cc_ = A.cache.get('comment_card')
            if cc_ is None:
                im = PImage.new('RGBA', (270, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                d.rounded_rectangle((8, 10, 262, 92), radius=22, fill=(0, 0, 0, 70)); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
                d.rounded_rectangle((4, 4, 258, 86), radius=22, fill=(255, 255, 255, 255), outline=RED + (255,), width=4)
                d.ellipse((14, 21, 58, 65), fill=RED + (255,)); d.text((27, 26), 'A', font=font(800, 28, False), fill=(255, 255, 255, 255))
                d.text((70, 14), 'your_comment', font=font(600, 17, False), fill=(40, 40, 40, 255))
                d.text((70, 36), 'MODEL', font=font(900, 34, False), fill=RED + (255,))
                d.text((214, 30), '♥', font=font(700, 28, False), fill=RED + (255,))
                cc_ = to_layer(im); A.cache['comment_card'] = cc_
            chest_row(c, f, [(cc_, w('model') + 0.1), (ctile('Gemini 4 cost-saving checklist', 26), w('gemini3'))])
            if f >= F(VO_END):
                rnd = random.Random(f // 3)
                for _ in range(2): draw_blocks(c, [(f, 1, rnd.uniform(110, 900), rnd.uniform(1100, 1150), rnd.choice([18, 24]), rnd.choice(BLOCK_COLS), 0.8)], f)
        front.append(_fr)
    if F(J[8]) - 2 <= f < F(J[8]) + 6: fxl.append(lambda: neon_streak(c, f - (F(J[8]) - 2), n=6, cx=HX + 20, phase=2.6))
    if F(J[4]) - 2 <= f < F(J[4]) + 6 and not (F(C1b) <= f < F(J[4])): fxl.append(lambda: neon_streak(c, f - (F(J[4]) - 2), n=6, cx=HX + 20, phase=1.7))
    if F(J[0]) <= f < F(J[0]) + 6: fxl.append(lambda: neon_streak(c, f - (F(J[0]) - 2), n=6, cx=HX + 20, phase=0.4))

    # ---------------------------------------------------------------- composite
    TH[0] = not cut
    if not cut:
        sl = subj.get(f); c[:] = subj.room
        for d_ in behind: d_()
        over(c, sl, 0, 0)
        for d_ in front: d_()
    CAPS.draw(c, t)
    pre = c.copy()
    for d_ in fxl: d_()
    if not cut: protect_face(c, pre, FACE_ZONE)
    m_ = SAFE_OUT                                                              # streaks / rings / swooshes stay inside the safe zone
    c[:] = c * (1 - m_) + pre * m_
    for kind, j in post:
        if kind == 'smear' and 0 <= j < 3: vertical_smear(c, j)
        if kind == 'radial' and 0 <= j < 3: radial_blur(c, CX, 880, amt=[0.06, 0.04, 0.02][j])
        if kind == 'rgb': rgb_ghost(c, j)
    apply_hook(HOOK, c, 2 * f + int(SUB * 2), face=FACE)
    j = f - F(C1b)                                   # cutaway 1 exit on a jump cut: magenta ghost 1 fr -> negative 2 fr
    if j == 0: magenta_ghost(c)
    elif j in (1, 2):
        negative(c, blur=8 - 3 * j); c *= [0.55, 0.7][j - 1]
        if j == 1: c[640:680, 300:340] = np.array((0x29, 0xE0, 0xE6), np.float32)
    for jt in (C3a, C3b):                             # slate -> slate and cutaway 3 exit: negative flash 2 fr
        j = f - F(jt)
        if 0 <= j < 2: negative(c, blur=9 - 4 * j); c *= 0.6
    grain(c, 2 * f + int(SUB * 2), amt=3.5)
    return np.clip(c, 0, 255).astype(np.uint8)

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
        json.dump(TLOG, open(out + '.tlog.json', 'w')); json.dump(CAPS.boxes[:1], open(out + '.caps.json', 'w'))
    else:
        os.makedirs(out, exist_ok=True)
        for g in [int(x) for x in sys.argv[4].split(',')]:
            SUB = (g % 2) * 0.5
            subj = Subject(max(0, g // 2)); im = render_frame(g // 2, subj)
            ov = im.copy(); cv2.rectangle(ov, (SX0, SY0), (SX1, SY1), (0, 255, 0), 2)
            cv2.imwrite(f'{out}/g{g:04d}.png', ov[..., ::-1])
