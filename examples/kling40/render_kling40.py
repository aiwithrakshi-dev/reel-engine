# Timeline + renderer for final_reel_kn.mp4 (video only; audio mixed separately).
# usage: python3 render.py <start_frame> <end_frame> <out.mp4|png_dir> [png]
import sys, json, math, random, subprocess, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from fx import *
from islands import snapped

WK = json.load(open('/home/claude/work/words_final.json'))
def wt(k): return WK[k]
def F(t): return int(round(t * FPS))
JOINS = [s[2] for s in snapped()][1:]
VO_END = snapped()[-1][3]
END_T = round(VO_END + 0.82, 2); NF = F(END_T)
HIT_T = VO_END + 0.28
DY = 230  # subject vertical offset (STUDIO mode), cap top ~ y 738
HEAD = (540, 900)  # head centre in reel frame

# ---------------------------------------------------------------- sources
BR = np.load('/home/claude/work/broll_frames.npy', mmap_mode='r')
def broll(t):  # t = BROLL seconds -> RGB uint8 720x1280
    i = min(len(BR) - 1, max(0, int(t * 24 + 1e-6))); return np.ascontiguousarray(BR[i][..., ::-1])
SHOT = {1: 0.0, 2: 2.125, 3: 4.25, 4: 6.333, 5: 8.458, 6: 10.542, 7: 13.542, 8: 15.833, 9: 17.917, 10: 20.083, 11: 22.042, 12: 24.125, 13: 26.292, 14: 28.167}
SHOT_END = {k: (SHOT.get(k + 1, 30.04)) for k in SHOT}
def still(shot, off=3 / 24):
    return broll(1.6 if shot == 1 else SHOT[shot] + off)
KF10 = [1, 2, 3, 5, 6, 7, 9, 11, 12, 13]  # the "10 keyframes" set (Part B §4)

class Subject:
    def __init__(self, f0):
        sys.path.insert(0, '/home/claude/work/scripts'); from subject import combined_alpha
        self.ca = combined_alpha
        self.v = cv2.VideoCapture('/home/claude/work/aroll_patched30.mp4'); self.a = cv2.VideoCapture('/home/claude/work/alpha_r50.mkv')
        self.vt = cv2.VideoCapture('/home/claude/work/aroll_tail30.mp4'); self.at = cv2.VideoCapture('/home/claude/work/alpha_tail.mkv')
        self.n = 1214; self.pos = -1; self.tpos = 0
        if f0 > 0 and f0 < self.n:
            self.v.set(cv2.CAP_PROP_POS_FRAMES, f0); self.a.set(cv2.CAP_PROP_POS_FRAMES, f0); self.pos = f0 - 1
        self.cache = None
    def get(self, f):
        if f < self.n:
            while self.pos < f:
                _, fr = self.v.read(); _, al = self.a.read(); self.pos += 1; self.cache = (fr, al)
        else:
            if not hasattr(self, 'tail'):
                self.tail = []
                while True:
                    ok, fr = self.vt.read(); ok2, al = self.at.read()
                    if not ok or not ok2: break
                    self.tail.append((fr, al))
            self.cache = self.tail[min(len(self.tail) - 1, f - self.n + 1)]
        fr, al = self.cache
        a = self.ca(fr, al[..., 0])
        rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32)
        # light natural grade: gentle S-curve, -5 % sat
        g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * 0.95
        rgb = 255 * (0.5 + (rgb / 255 - 0.5) * 1.05)
        lay = np.zeros((H, W, 4), np.float32)
        lay[DY:, :, :3] = np.clip(rgb[:H - DY], 0, 255) / 255; lay[DY:, :, 3] = a[:H - DY]
        self.room = room_bg(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32))
        return lay

# studio background plate
def studio_bg():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([0xE0, 0xDD, 0xE7], np.float32); mid = np.array([0xE5, 0xE2, 0xE6], np.float32); flo = np.array([0xE8, 0xE0, 0xE5], np.float32)
    c = np.where(y[..., None] < 0.55, top + (mid - top) * (y[..., None] / 0.55), mid + (flo - mid) * ((y[..., None] - 0.55) / 0.45))
    bg = np.repeat(c, W, axis=1).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 950) / 1100) ** 2)
    bg += (np.clip(1 - r, 0, 1) * 6)[..., None]; bg -= (np.clip(r - 0.9, 0, 1) * 14)[..., None]
    return bg
BG = studio_bg()
MODE = 'ORIGINAL'   # keep the room: darkened + desaturated 20 %, blurred ~6 px; type stays behind via the matte
def room_bg(src):
    out = np.empty((H, W, 3), np.float32)
    out[DY:] = src[:H - DY]
    ext = cv2.resize(src[0:70], (W, DY + 60), interpolation=cv2.INTER_LINEAR)   # wall slats are vertical: stretch the top rows
    out[:DY] = ext[:DY]
    k = np.linspace(1, 0, 60)[:, None, None]; out[DY:DY + 60] = ext[DY:] * k + out[DY:DY + 60] * (1 - k)
    g = out.mean(2, keepdims=True); out = g + (out - g) * 0.8
    out *= 0.8
    return cv2.GaussianBlur(out, (0, 0), 3)

# ---------------------------------------------------------------- assets (built lazily)
class A: pass
A.cache = {}
def bw(key, text, cap, **kw):
    if key not in A.cache: A.cache[key] = BigWord(text, cap, **kw)
    return A.cache[key]
def lb(key, text, **kw):
    if key not in A.cache: A.cache[key] = Label(text, **kw)
    return A.cache[key]
def cd(key, img, w, h, **kw):
    if key not in A.cache: A.cache[key] = card(img, w, h, **kw)
    return A.cache[key]

def blocks_for_word(key, word, cx, base, f0, step=2, extra=6, seed=0, bias=None):
    """pixel blocks attached to the newest letter while typing (always on text being revealed)."""
    k = 'blk_' + key
    if k in A.cache: return A.cache[k]
    boxes = word.letter_boxes(cx, base)
    def bf(fr):
        i = (fr - f0) // step
        if i < 0 or i >= len(boxes) + extra // step: return None
        b = boxes[min(i, len(boxes) - 1)]
        if bias: b = (b[0], b[1] + bias, b[2], b[3] + bias)
        return b
    A.cache[k] = make_blocks(hash(key) % 9999 + seed, f0, f0 + step * len(boxes) + extra, bf)
    return A.cache[k]

def dissolve_blocks(key, word, cx, base, f0, seed=3):
    k = 'dis_' + key
    if k in A.cache: return A.cache[k]
    boxes = [b for b in word.letter_boxes(cx, base) if b]
    rnd = random.Random(seed); ev = []
    for fr in range(f0, f0 + 6):
        for b in rnd.sample(boxes, min(len(boxes), 4)):
            for _ in range(3):
                s = rnd.choice([18, 24, 30, 36]); ev.append((fr, rnd.randint(2, 4), rnd.uniform(b[0], b[2]), rnd.uniform(b[1], b[3]), s, rnd.choice(BLOCK_COLS), 0.9))
    A.cache[k] = ev; return ev

def gone_set(word, f, f0, seed=5):
    """letters removed progressively during a dissolve starting at f0 (4 frames)."""
    if f < f0: return None
    n = word.n(); order = list(range(n)); random.Random(seed).shuffle(order)
    k = min(n, int((f - f0 + 1) * n / 4)); return set(order[:k])

def marker(canvas, label, x, y, f0, f, words_idx=None):
    """highlighter bars swipe across label words red->cyan->green, 2 frames each, then vanish."""
    cols = [RED, (0x29, 0xD3, 0xE6), (0x3B, 0xD1, 0x4A)]
    boxes = label.word_boxes(x, y)
    idx = words_idx if words_idx is not None else range(len(boxes))
    for n, i in enumerate(idx):
        a = f - (f0 + 2 * n)
        if 0 <= a < 3:
            b = boxes[i]; c = cols[n % 3]; w = (b[2] - b[0]) * min(1, (a + 1) / 2)
            y0 = int(b[1] + label.h * 0.18); y1 = int(b[1] + label.h * 0.82)
            canvas[y0:y1, int(b[0]):int(b[0] + w)] = np.array(c, np.float32)

def phone_frame(canvas, x0=200, y0=290, w=680, h=1150, r=80):
    """frosted-glass phone frame (thin red outline, red notch pill)."""
    reg = canvas[y0:y0 + h, x0:x0 + w]
    fro = cv2.GaussianBlur(reg, (0, 0), 7) * 0.86 + 255 * 0.14
    m = np.zeros((h, w), np.uint8); cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in [(r, r), (w - r, r), (r, h - r), (w - r, h - r)]: cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    M = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1)[..., None]
    reg[:] = reg * (1 - M) + fro * M
    edge = np.zeros((h, w), np.float32)
    cnt = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    cv2.drawContours(edge, cnt, -1, 1.0, 4, cv2.LINE_AA)
    e = edge[..., None] * 0.85; reg[:] = reg * (1 - e) + np.array(RED, np.float32) * e
    reg[28:52, w // 2 - 70:w // 2 + 70] = np.array(RED, np.float32)  # notch pill

def card_live_rgb(t_b):
    return broll(t_b)

# ---------------------------------------------------------------- the edit (event layer per frame)
def render_frame(f, subj):
    t = f / FPS
    canvas = BG.copy()
    post = []  # whole-frame post devices
    fx_layer = []  # callables drawn after subject (front/fx)
    behind = []; front = []
    cutaway = None
    J = JOINS

    # ---------------- segment timing helpers
    def seg(a, b): return F(a) <= f < F(b)

    # ======== 1. 0 -> J0 : "not a single CUT ✕"
    if f < F(J[0]):
        L = lb('l_not', 'not a single'); W1 = bw('w_cut', 'CUT', 300)
        cut_f = F(wt('ಕಟ್ಇಲ್ಲ')); diss = F(J[0]) - 2
        def _b(c=canvas):
            L.draw(c, 150, 400, F(wt('ಒಂದೇ')) + 3, f, seed=11)
            W1.draw(c, 540, 760, cut_f, f, gone=gone_set(W1, f, diss))
            draw_blocks(c, blocks_for_word('cut', W1, 540, 760, cut_f), f)
            xf = F(wt('ಇಲ್ಲ1'))
            if xf <= f < diss + 2:  # pixel ✕ stamp
                s = 1.25 if f == xf else 1.0; xs = np.linspace(-1, 1, 15)
                for k, u in enumerate(xs):
                    for sgn in (1, -1):
                        px = 540 + u * 230 * s; py = 640 + sgn * u * 150 * s
                        x0, y0 = int(px // 6 * 6), int(py // 6 * 6)
                        c[y0:y0 + 30, x0:x0 + 30] = np.array(RED if k % 3 else PINK1, np.float32)
            draw_blocks(c, dissolve_blocks('cut', W1, 540, 760, diss), f)
        behind.append(_b)

    # ======== 2. J0 -> J1 : "no EDITING" (neon streak hides join + cap flip)
    if F(J[0]) - 4 <= f < F(J[1]):
        W2 = bw('w_edit', 'EDITING', 260); L = lb('l_no', 'no')
        ef = F(wt('ಎಡಿಟಿಂಗ್')); lf = F(wt('ಕೂಡಇಲ್ಲ'))
        diss = F(J[1]) - 1
        def _b(c=canvas):
            if f >= F(J[0]):
                W2.draw(c, 540, 755, ef, f, gone=gone_set(W2, f, diss))
                L.draw(c, 120, 440, lf, f, seed=12)
                draw_blocks(c, blocks_for_word('edit', W2, 540, 755, ef, bias=60), f)
        behind.append(_b)
        # pixel blocks on the cap while the AI cap flip is being repaired (attached to EDITING reveal)
        def _fx(c=canvas):
            if F(J[0]) <= f < F(J[0]) + 11:
                rnd = random.Random(f)
                for _ in range(4):
                    s = rnd.choice([24, 30, 36]); x = rnd.uniform(400, 680); y = rnd.uniform(735, 830)
                    draw_blocks(c, [(f, 1, x, y, s, rnd.choice(BLOCK_COLS), 0.9)], f)
            neon_streak(c, f - (F(J[0]) - 2), n=6, cx=560, phase=0.3)
        fx_layer.append(_fx)

    # ======== 3. J1 -> J2 : "this whole scene" + card (BROLL live) + ONE TAKE + pills
    if F(J[1]) <= f < F(J[2]):
        L = lb('l_scene', 'this whole scene'); W3 = bw('w_take', 'ONE TAKE', 150, maxw=860)
        cf = F(J[1]) + 9; of = F(wt('ಒಂದೇ2')); tf = F(wt('ಟೇಕಲ್ಲಿ'))
        def _b(c=canvas):
            L.draw(c, 110, 160, F(wt('ಇಡೀಸೀನ್')), f, seed=13)
            # ONE types on ಒಂದೇ, TAKE on ಟೇಕಲ್ಲಿ
            st = [of + 2 * i for i in range(3)] + [tf + 2 * i for i in range(4)]
            W3.draw(c, 540, 400, of, f, starts=st)
            draw_blocks(c, blocks_for_word('take1', W3, 540, 400, of), f); draw_blocks(c, blocks_for_word('take2', W3, 540, 400, tf - 6, seed=4), f)
            # card behind head, live BROLL from shot 1
            a = f - cf
            if a >= 0:
                s = pop_scale(a); live = card(card_live_rgb(min(29.9, (f - cf) / FPS)), 330, 400)
                over_c(c, live, 540, 625, s=s)
                if a < 5: draw_blocks(c, make_blocks(31, cf, cf + 5, lambda fr: (380, 380, 700, 800)), f)
                # pills
                for (txt, wkey, side) in [('made with ai', 'AI', -1), ('1 generation', 'ಮಾಡಿದೀನಿ', 1)]:
                    pf = F(wt(wkey)); pa = f - pf
                    if pa >= 0:
                        p = pill(txt); slide = [0.35, 0.75, 1.0][pa] if pa < 3 else 1.0
                        px = 540 + side * (165 + p.shape[1] / 2 * slide) - p.shape[1] / 2 + (0 if side > 0 else 0)
                        px = (540 + 165 - 40 + (p.shape[1] * (slide - 1))) if side > 0 else (540 - 165 + 40 - p.shape[1] * slide)
                        over(c, p, px, 440, op=min(1, 0.4 + pa * 0.3))
        behind.append(_b)
        def _fx(c=canvas):
            j = f - F(J[1]); halftone_ring(c, j, 540, 880, r0=60, r1=820)
        fx_layer.append(_fx)
        if f - F(J[1]) < 3: post.append(('radial', f - F(J[1])))

    # ======== 4. J2 -> J3 : SAVE this (front) + bookmark icon; vertical smear on join
    if F(J[2]) <= f < F(J[3]):
        W4 = bw('w_save', 'SAVE', 230); L = lb('l_this', 'this', size=58, color=WHITE, weight=400, shadow=True)
        sf = F(wt('ಸೇವ್'))
        def _fr(c=canvas):
            W4.draw(c, 540, 1360, sf, f)
            if f >= sf + 6: L.draw(c, 540, 1365, sf + 6, f, center=True, seed=14)
            draw_blocks(c, blocks_for_word('save', W4, 540, 1360, sf), f)
            a = f - sf
            if a >= 0: over_c(c, icon('bookmark', 150), 905, 1010 + 6 * math.sin(f / 6), s=pop_scale(a))
        front.append(_fr)
    if F(J[2]) - 1 <= f < F(J[2]) + 2: post.append(('smear', f - (F(J[2]) - 1)))

    # ======== 5. J3 -> J4 : KEYFRAME / METHOD + stacked cards + swoosh into cutaway
    if F(J[3]) <= f < F(J[4]):
        L1 = lb('l_how', 'how I use'); L2 = lb('l_watch', 'watch')
        W5a = bw('w_kf', 'KEYFRAME', 190, maxw=900); W5b = bw('w_meth', 'METHOD', 190, maxw=900)
        f1 = F(wt('ಕೀಫ್ರೇಮ್ಸ್')); f2 = F(wt('ಬಳಸ್ತೀನಿ'))
        def _b(c=canvas):
            L1.draw(c, 95, 190, F(wt('ನಾನು2')), f, seed=15)
            L2.draw(c, 830, 190, F(wt('ತೋರಿಸ್ತೀನಿ')), f, seed=16)
            W5a.draw(c, 540, 470, f1, f); W5b.draw(c, 540, 690, f2, f)
            draw_blocks(c, blocks_for_word('kf', W5a, 540, 470, f1), f); draw_blocks(c, blocks_for_word('meth', W5b, 540, 690, f2), f)
        behind.append(_b)
        sc0 = f1 + 4
        def _fr(c=canvas):
            items = [('stk2', still(2), 230, 300, 175, 1235, -9), ('stk5', still(5), 230, 300, 255, 1300, 4), ('stk7', still(7), 210, 370, 345, 1245, 8)]
            for k, (key, img, w, h, x, y, rot) in enumerate(items):
                a = f - (sc0 + 4 * k)
                if a < 0: continue
                cdl = cd(key, img, w, h, radius=26 if key != 'stk7' else 40, stroke=6 if key != 'stk7' else 10, col=RED if key != 'stk7' else (25, 25, 28))
                e = min(1, (a + 1) / 4); e = 1 - (1 - e) ** 3
                over_c(c, cdl, x - 160 * (1 - e), y + 420 * (1 - e), rot=rot)
        front.append(_fr)
        def _fx(c=canvas):
            j = f - F(J[3]); halftone_ring(c, j, 540, 1250, r0=330, r1=900, band=150, mode='lines', ry_scale=1.5, op=0.75)
            swoosh(c, f - (F(J[4]) - 7), n=7, yc=1150)
        fx_layer.append(_fx)

    # ======== 6. CUTAWAY 1 J4 -> J5 : Kling 4.0 / in one go / 30 SECONDS / max per video
    if F(J[4]) <= f < F(J[5]):
        c0 = J[4]; bar = 4 * 0.4636
        c1 = c0 + bar; c2 = c0 + 10 * 0.4636   # hard cuts on the beat
        if t < c1: img = broll(SHOT[1] + (t - c0))
        elif t < c2: img = broll(SHOT[6] + (t - c1))
        else: img = broll(SHOT[7] + 0.1 + (t - c2))
        cutaway = cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        canvas[:] = cutaway
        def _cw(c=canvas):
            phone_frame(c)
            la = lb('cw_kling', 'Kling 4.0', size=62, color=WHITE, weight=500, shadow=True)
            lb2 = lb('cw_go', 'in one go', size=56, color=WHITE, weight=300, shadow=True)
            lb3 = lb('cw_max', 'max per video', size=50, color=WHITE, weight=300, shadow=True)
            w30 = bw('cw_30', '30', 250); wsec = bw('cw_sec', 'SECONDS', 118, maxw=600)
            la.draw(c, 540, 420, F(wt('ಕ್ಲಿಂಗ್')), f, center=True, seed=21)
            lb2.draw(c, 540, 520, F(wt('ಒಂದೇ3')), f, center=True, seed=22)
            w30.draw(c, 540, 900, F(wt('30')), f); wsec.draw(c, 540, 1060, F(wt('ಸೆಕೆಂಡ್')), f)
            draw_blocks(c, blocks_for_word('cw30', w30, 540, 900, F(wt('30'))), f)
            draw_blocks(c, blocks_for_word('cwsec', wsec, 540, 1060, F(wt('ಸೆಕೆಂಡ್'))), f)
            lb3.draw(c, 540, 1110, F(wt('ವಿಡಿಯೋ')), f, center=True, seed=23)
            for kind, x, y, f0, ph in [('clapper', 150, 1240, F(c0) + 4, 0), ('play', 920, 330, F(c0) + 8, 2)]:
                a = f - f0
                if a >= 0: over_c(c, icon(kind, 170), x, y + 8 * math.sin(f / 7 + ph), s=pop_scale(a), rot=-8 if kind == 'clapper' else 10)
            j = f - F(c0); halftone_ring(c, j, 540, 960, r0=80, r1=1000)
            neon_streak(c, j, n=4, vertical=False, yc=980, amp=70, tail=1100)
        fx_layer.append(_cw)
        if f - F(J[4]) < 3: post.append(('rgb', f - F(J[4])))

    # ======== 7. J5 -> J6 : up to 10 KEYFRAMES + fan of 10 keyframe cards
    if F(J[5]) <= f < F(J[6]) + 6:
        L = lb('l_upto', 'up to'); W7 = bw('w_10kf', '10 KEYFRAMES', 122, maxw=900)
        f1 = F(wt('ಹತ್ತು')); f2 = F(wt('ಕೀಫ್ರೇಮ್ಸ್2')); diss = F(J[6]) - 2
        st7 = [f1, f1 + 2] + [f2 + 2 * i for i in range(10)]
        fan0 = st7[-1] + 4
        def _b(c=canvas):
            if f < F(J[6]) + 2:
                L.draw(c, 100, 180, F(J[5]) + 3, f, seed=17)
                W7.draw(c, 540, 752, f1, f, starts=st7, gone=gone_set(W7, f, diss))
                draw_blocks(c, blocks_for_word('10kf', W7, 540, 752, f1), f); draw_blocks(c, blocks_for_word('10kf2', W7, 540, 752, f2 - 4, seed=2), f)
                draw_blocks(c, dissolve_blocks('10kf', W7, 540, 752, diss), f)
            for k in range(10):
                a = f - (fan0 + 2 * k)
                if a < 0 or f >= diss + 2 + (k % 3): continue
                ang = math.radians(158 - k * 136 / 9); R = 450
                x = 540 + R * math.cos(ang); y = 760 - R * math.sin(ang) * 0.86
                cl = cd('fan%d' % k, still(KF10[k]), 110, 146, radius=14, stroke=4)
                over_c(c, cl, x, y, s=pop_scale(a), rot=(k - 4.5) * -6)
        behind.append(_b)

    # ======== 8a. J6 -> 8b : STORY + "what happens next" marker
    s8b = F(wt('ಒಂದೊಂದು')) - 2
    if F(J[6]) <= f < F(J[7]):
        W8 = bw('w_story', 'STORY', 270); L = lb('l_next', 'what happens next', size=50)
        sf = F(wt('ಕಥೆಯಲ್ಲಿ'))
        W8b = bw('w_bbb', 'BEAT BY BEAT', 118, maxw=900)
        def _b(c=canvas):
            if f < s8b + 4:
                W8.draw(c, 540, 755, sf, f, gone=gone_set(W8, f, s8b))
                draw_blocks(c, blocks_for_word('story', W8, 540, 755, sf), f); draw_blocks(c, dissolve_blocks('story', W8, 540, 755, s8b), f)
                lf = F(wt('ಮುಂದೆ')) - 1
                if f >= lf + 1 and f < s8b: L.draw(c, 130, 395, lf + 1, f, seed=18, word_step=2)
                marker(c, L, 130, 395, lf, f)
            if f >= s8b:
                f1 = F(wt('ಒಂದೊಂದು')); f2 = F(wt('ಕೀಫ್ರೇಮಲ್ಲಿ'))
                st8 = [f1 + 2 * i for i in range(7)] + [f2 + 2 * i for i in range(4)]
                W8b.draw(c, 540, 752, f1, f, starts=st8)
                draw_blocks(c, blocks_for_word('bbb', W8b, 540, 752, f1), f); draw_blocks(c, blocks_for_word('bbb2', W8b, 540, 752, f2 - 12, seed=3), f)
                for k, (shot, wk, x) in enumerate([(1, 'ಒಂದೊಂದು', 230), (5, None, 540), (8, 'ಕೀಫ್ರೇಮಲ್ಲಿ', 850)]):
                    pf = F(wt('ಒಂದೊಂದು')) + 11 * k
                    a = f - pf
                    if a < 0: continue
                    over_c(c, cd('beat%d' % k, still(shot), 250, 310, radius=26), x, 400, s=pop_scale(a), rot=[-5, 2, 6][k])
                    p = pill('beat %d' % (k + 1), size=30)
                    if a >= 2: over(c, p, x - p.shape[1] / 2, 530)
        behind.append(_b)
        def _fx(c=canvas): neon_streak(c, f - (F(J[6]) - 2), n=6, cx=520, phase=1.7)
        fx_layer.append(_fx)
    # (the streak into 8a also clears the fan cards)

    # ======== 9. J7 -> J8 : ACTOR / PROPS cards, SAME ✓, 15 REFERENCES + cluster
    if F(J[7]) <= f < F(J[8]):
        r9c = F(wt('ಹದಿನೈದು')) - 2
        L = lb('l_through', 'through the whole scene')
        def _b(c=canvas):
            if f < r9c:
                L.draw(c, 540, 175, F(wt('ಸೀನ್')), f, seed=19, center=True)
                for (key, shot, x, rot, f0, ptxt, pk) in [('actor', 7, 300, -6, F(wt('ನಟನ')), 'actor look', 'ಲುಕ್'), ('props', 9, 780, 6, F(wt('ಪ್ರಾಪ್ಸ್')), 'props', 'ಪ್ರಾಪ್ಸ್')]:
                    a = f - f0
                    if a < 0: continue
                    over_c(c, cd('c9' + key, still(shot, 0.5), 330, 430, radius=30), x, 520, s=pop_scale(a), rot=rot)
                    if a < 5: draw_blocks(c, make_blocks(hash(key) % 99, f0, f0 + 5, lambda fr, x=x: (x - 180, 300, x + 180, 760)), f)
                    pa = f - F(wt(pk)) - (2 if key == 'props' else 0)
                    if pa >= 0:
                        p = pill(ptxt); over(c, p, x - p.shape[1] / 2 + (1 - min(1, (pa + 1) / 3)) * 40, 285)
            else:
                Lu = lb('l_upto15', 'up to'); W15 = bw('w_15', '15', 280); WR = bw('w_refs', 'REFERENCES', 150, maxw=900)
                f1 = F(wt('ಹದಿನೈದು')); f2 = F(wt('ರೆಫರೆನ್ಸ್'))
                Lu.draw(c, 120, 168, r9c + 2, f, seed=20)
                W15.draw(c, 360, 500, f1, f); WR.draw(c, 540, 690, f2, f, step=2)
                draw_blocks(c, blocks_for_word('15', W15, 360, 500, f1), f); draw_blocks(c, blocks_for_word('refs', WR, 540, 690, f2), f)
                cf = F(wt('ಇಮೇಜಸ್'))
                for k, (shot, x, y, rot) in enumerate([(5, 700, 330, -8), (7, 830, 300, 4), (9, 950, 350, 10)]):
                    a = f - (cf + 3 * k)
                    if a >= 0: over_c(c, cd('ref%d' % k, still(shot, 0.4), 150, 200, radius=18, stroke=5), x, y, s=pop_scale(a), rot=rot)
                a = f - cf - 9
                if a >= 0:
                    p = pill('refs', size=30); over(c, p, 640, 205)
        behind.append(_b)
        def _fr(c=canvas):
            sf = F(wt('ಒಂದೇ4'))
            if sf <= f < r9c:
                W9 = bw('w_same', 'SAME', 230); W9.draw(c, 540, 1360, sf, f)
                draw_blocks(c, blocks_for_word('same', W9, 540, 1360, sf), f)
                a = f - F(wt('ರೀತಿ'))
                if a >= 0: over_c(c, icon('check', 120), 880, 1180, s=pop_scale(a), rot=8)
        front.append(_fr)
        def _fx(c=canvas):
            halftone_ring(c, f - F(J[7]), 540, 880, r0=60, r1=820)
            halftone_ring(c, f - r9c, 540, 880, r0=60, r1=900)
        fx_layer.append(_fx)
        for d0 in (F(J[7]), r9c):
            if 0 <= f - d0 < 3: post.append(('radial', f - d0))

    # ======== 10. CUTAWAY 2 J8 -> J9 : STEREO SOUND (shot 12, native audio panned)
    if F(J[8]) <= f < F(J[9]):
        tb = min(SHOT[12] + (t - J[8]), SHOT_END[12] - 0.05)
        canvas[:] = cv2.resize(broll(tb), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        pan = json.load(open('/home/claude/work/pan_env.json'))
        def _cw(c=canvas):
            phone_frame(c)
            lp = lb('cw_plus', 'plus', size=58, color=WHITE, weight=300, shadow=True)
            lp.draw(c, 540, 450, F(wt('ಜೊತೆಗೆ')), f, center=True, seed=24)
            ws = bw('cw_st', 'STEREO', 160, maxw=600); wso = bw('cw_so', 'SOUND', 160, maxw=600)
            ws.draw(c, 540, 760, F(wt('ಸ್ಟೀರಿಯೋ')), f); wso.draw(c, 540, 960, F(wt('ಸೌಂಡ್')), f)
            draw_blocks(c, blocks_for_word('st', ws, 540, 760, F(wt('ಸ್ಟೀರಿಯೋ'))), f)
            i = min(len(pan['L']) - 1, f - F(J[8]))
            for side, x, k in [('speaker_l', 330, 'L'), ('speaker_r', 750, 'R')]:
                a = f - F(J[8]) - 3
                if a >= 0: over_c(c, icon(side, 160), x, 1210, s=pop_scale(a) * (1 + 0.16 * pan[k][i]))
            rgb_j = f - F(J[8])
        fx_layer.append(_cw)
        if f - F(J[8]) < 3: post.append(('rgb', f - F(J[8])))

    # ======== 11. J9 -> J10 : the ones I used / MY KEYFRAMES / 2x5 grid deal
    if F(J[9]) <= f < F(J[10]):
        L = lb('l_ones', 'the ones I used'); WM = bw('w_my', 'MY KEYFRAMES', 130, maxw=900)
        g0 = F(wt('ಇವು')); mf = F(wt('ಕೀಫ್ರೇಮ್ಸ್3')) - 2
        def _b(c=canvas):
            L.draw(c, 540, 160, F(wt('ಇವು')) + 1, f, center=True, seed=25)
            WM.draw(c, 540, 755, mf, f, step=1)
            draw_blocks(c, blocks_for_word('my', WM, 540, 755, mf, step=1), f)
            for k in range(10):
                a = f - (g0 + 2 * k)
                if a < 0: continue
                r_, col = divmod(k, 5); x = 150 + col * 195; y = 345 + r_ * 200
                over_c(c, cd('grid%d' % k, still(KF10[k]), 160, 180, radius=16, stroke=5), x, y + (1 - min(1, a / 3)) * -60, s=pop_scale(a), rot=[-3, 2, -2, 3, -1][col])
                if a >= 2:
                    p = pill('%02d' % (k + 1), size=26); over(c, p, x - 70, y - 105)
        behind.append(_b)

    # ======== 12. CUTAWAY 3 J10 -> J11 : final take montage 2 -> 11 -> 13
    if F(J[10]) - 7 <= f < F(J[10]):
        def _fx(c=canvas): swoosh(c, f - (F(J[10]) - 7), n=7, yc=1150)
        fx_layer.append(_fx)
    if F(J[10]) <= f < F(J[11]):
        seg_d = (J[11] - J[10]) / 3; k = min(2, int((t - J[10]) / seg_d)); shot = [2, 11, 13][k]
        tb = SHOT[shot] + 0.15 + (t - J[10] - k * seg_d)
        canvas[:] = cv2.resize(broll(tb), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        def _cw(c=canvas):
            fr = np.zeros((H, W), np.uint8); cv2.rectangle(fr, (40, 120), (W - 40, H - 330), 255, 7, cv2.LINE_AA)
            frm = cv2.GaussianBlur(fr.astype(np.float32) / 255, (0, 0), 0.8)[..., None]
            c[:] = c * (1 - frm) + np.array(RED, np.float32) * frm
            a = f - F(wt('final'))
            if a >= 0:
                p = pill('final take · 1 generation', size=40); over(c, p, 540 - p.shape[1] / 2 + (0 if a > 2 else (2 - a) * 20), 1480)
        fx_layer.append(_cw)
        if f - F(J[10]) < 3: post.append(('rgb', f - F(J[10])))

    # ======== 13. J11 -> J12 : want all 10 PROMPTS ?
    if F(J[11]) <= f < F(J[12]):
        L = lb('l_want', 'want all'); W13a = bw('w_10p', '10', 240); W13b = bw('w_pr', 'PROMPTS', 190, maxw=820); Wq = bw('w_q', '?', 190)
        f1 = F(wt('ಹತ್ತು2')); f2 = F(wt('ಪ್ರಾಂಪ್ಟ್')); fq = max(F(wt('ಬೇಕಾ')), f2 + 14)
        diss = F(J[12]) - 2
        def _b(c=canvas):
            L.draw(c, 300, 170, f1, f, seed=26)
            W13a.draw(c, 540, 470, f1, f, gone=gone_set(W13a, f, diss)); W13b.draw(c, 510, 690, f2, f, gone=gone_set(W13b, f, diss))
            a = f - fq
            if a >= 0 and f < diss + 2: over_c(c, Wq.letters[0]['img'], 510 + W13b.width / 2 + 40, 610, s=pop_scale(a) * 1.0)
            draw_blocks(c, blocks_for_word('10p', W13a, 540, 470, f1), f); draw_blocks(c, blocks_for_word('pr', W13b, 510, 690, f2), f)
            draw_blocks(c, dissolve_blocks('pr', W13b, 510, 690, diss), f)
        behind.append(_b)

    # ======== 14. J12 -> J13 : PROMPT + "comment" marker
    if F(J[12]) <= f:
        WP = bw('w_prompt', 'PROMPT', 250, maxw=900); L = lb('l_comment', 'comment', size=50)
        pf = F(wt('ಪ್ರಾಂಪ್ಟ್2')); mf = F(wt('ಕಮೆಂಟ್'))
        def _b(c=canvas):
            WP.draw(c, 540, 755, pf, f)
            draw_blocks(c, blocks_for_word('prompt', WP, 540, 755, pf), f)
            if f >= mf + 1 and f < F(J[13]): L.draw(c, 140, 425, mf + 1, f, seed=27)
            if f < F(J[13]): marker(c, L, 140, 425, mf, f)
            # ======== 15/16 CTA card cluster
            if f >= F(J[13]):
                cc = A.cache.get('comment_card')
                if cc is None:
                    from PIL import Image, ImageDraw
                    im = Image.new('RGBA', (600, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle((10, 14, 590, 184), radius=34, fill=(0, 0, 0, 50)); im = im.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle((6, 6, 584, 176), radius=34, fill=(255, 255, 255, 255), outline=RED + (255,), width=5)
                    d.ellipse((34, 46, 114, 126), fill=RED + (255,)); d.text((58, 58), 'A', font=font(800, 46, False), fill=(255, 255, 255, 255))
                    d.text((140, 40), 'your_comment', font=font(600, 30, False), fill=(40, 40, 40, 255))
                    d.text((140, 82), 'PROMPT', font=font(900, 56, False), fill=RED + (255,))
                    d.text((470, 66), '♥', font=font(700, 52, False), fill=RED + (255,))
                    cc = to_layer(im); A.cache['comment_card'] = cc
                cf = F(J[13]) + 3; a = f - cf
                if a >= 0: over_c(c, cc, 400, 330, s=pop_scale(a), rot=-4)
                df = F(wt('ಹತ್ತನ್ನೂ')); a = f - df
                if a >= 0:
                    over_c(c, icon('doc', 210), 860, 360 + 5 * math.sin(f / 6), s=pop_scale(a), rot=8)
                    if a >= 2: p = pill('all 10 keyframe prompts', size=32); over(c, p, 1000 - p.shape[1], 500)
                hf = F(wt('ಕಳಿಸ್ತೀನಿ')); a = f - hf
                if a >= 0: p = pill('@aiwithrakshith', size=46); over_c(c, p, 400, 480, s=pop_scale(a))
                if f >= F(VO_END):  # hold: tiny pixel flicker on the cards
                    rnd = random.Random(f // 3)
                    for _ in range(2):
                        draw_blocks(c, [(f, 1, rnd.uniform(120, 1000), rnd.uniform(220, 560), rnd.choice([18, 24]), rnd.choice(BLOCK_COLS), 0.8)], f)
        behind.append(_b)
        def _fx(c=canvas):
            neon_streak(c, f - (F(J[12]) - 2), n=6, cx=560, phase=2.6)
            halftone_ring(c, f - F(J[13]), 540, 880, r0=40, r1=520, n=4, band=150, op=0.85)
        fx_layer.append(_fx)

    # ---------------------------------------------------------------- composite
    if cutaway is None and not (F(J[8]) <= f < F(J[9])) and not (F(J[10]) <= f < F(J[11])):
        sl = subj.get(f)
        if MODE == 'ORIGINAL':
            canvas[:] = subj.room
        for d in behind: d()
        if MODE != 'ORIGINAL':
            sh = cv2.GaussianBlur(sl[..., 3], (0, 0), 22); shl = np.zeros_like(sh); shl[18:, 10:] = sh[:-18, :-10]
            canvas *= (1 - 0.16 * shl[..., None])
        over(canvas, sl, 0, 0)
        for d in front: d()
        for d in fx_layer: d()
    else:
        for d in fx_layer: d()

    # ---------------------------------------------------------------- whole-frame devices
    for kind, j in post:
        if kind == 'smear' and 0 <= j < 3: vertical_smear(canvas, j)
        if kind == 'radial' and 0 <= j < 3: radial_blur(canvas, 540, 900, amt=[0.06, 0.04, 0.02][j])
        if kind == 'rgb': rgb_ghost(canvas, j)
    # open: negative flash (frames 0-2) then scale-in 92 -> 100 % with blur (frames 3-5)
    if f < 3:
        negative(canvas, blur=9); canvas *= 0.55
        rnd = random.Random(f); colb = (0x29, 0xE0, 0xE6) if f < 2 else RED
        for _ in range(2):
            x, y = rnd.uniform(560, 760), rnd.uniform(560, 760); canvas[int(y):int(y) + 48, int(x):int(x) + 48] = np.array(colb, np.float32)
    elif f < 6:
        j = f - 3; s = [0.92, 0.96, 0.99][j]; bl = [12, 6, 2][j]
        M = np.float32([[s, 0, 540 * (1 - s)], [0, s, 960 * (1 - s)]])
        canvas[:] = cv2.GaussianBlur(cv2.warpAffine(canvas, M, (W, H), borderMode=cv2.BORDER_REPLICATE), (0, 0), bl)
    # exits from cutaways 1 & 2: 1 frame magenta ghost -> 2 frames negative (measured order)
    for jt in (J[5], J[9]):
        j = f - F(jt)
        if j == 0: magenta_ghost(canvas)
        elif j in (1, 2):
            negative(canvas, blur=8 - 3 * j); canvas *= [0.55, 0.7][j - 1]
            if j == 1:
                rnd = random.Random(f); canvas[int(rnd.uniform(500, 700)):, :][:40, 300:340] = np.array((0x29, 0xE0, 0xE6), np.float32)
    # exit from cutaway 3: negative flash (2 frames)
    j = f - F(J[11])
    if 0 <= j < 2: negative(canvas, blur=9 - 4 * j); canvas *= 0.6
    grain(canvas, f, amt=3.5)
    return np.clip(canvas, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    f0, f1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    f1 = min(f1, NF)
    subj = Subject(f0)
    if out.endswith('.mp4'):
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            ff.stdin.write(render_frame(f, subj).tobytes())
            if f % 60 == 0: print('frame', f, flush=True)
        ff.stdin.close(); ff.wait()
    else:
        os.makedirs(out, exist_ok=True)
        frames = [int(x) for x in sys.argv[4].split(',')]
        for f in frames:
            subj = Subject(max(0, f))
            img = render_frame(f, subj); cv2.imwrite(f'{out}/f{f:04d}.png', img[..., ::-1])
