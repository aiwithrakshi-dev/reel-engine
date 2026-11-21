# Hook animation library: the first 0.2–0.3 s opener of every reel, in the house style.
# Every reel uses a DIFFERENT hook from its recent predecessors (see skill references/05-hooks.md and
# references/hook_log.md). All hooks are written for 60 fps: g = frame index at 60 fps from the start of the reel.
#
#   from hooks import apply_hook, HOOKS, pick_hook
#   apply_hook('pixel_assemble', canvas, g, face=(540, 700))   # canvas: float32 H x W x 3 (0..255), composited frame
#
# Stepped hooks hold each state for 2 frames (the snappy 30-fps grammar); "smooth" hooks use every 60-fps frame.
import math, random
import numpy as np, cv2

W, H = 1080, 1920
RED = (0xE3, 0x12, 0x1B); PINK1 = (0xF0, 0x6A, 0x72); PINK2 = (0xF7, 0xB9, 0xBE); CYAN = (0x29, 0xE0, 0xE6)
NEON = (0xFF, 0x1A, 0x2A); BLOCKS = [RED, PINK1, PINK2, (0xAA, 0, 0), (0xFF, 0x3B, 0x45)]


def _blocks(c, rnd, n, x0, x1, y0, y1, sizes=(18, 24, 30, 36, 42), cols=BLOCKS):
    for _ in range(n):
        s = rnd.choice(sizes); x = int(rnd.uniform(x0, x1) // 6 * 6); y = int(rnd.uniform(y0, y1) // 6 * 6)
        c[y:y + s, x:x + s] = np.array(rnd.choice(cols), np.float32)


def _scale(c, s, cx=540, cy=960, blur=0):
    M = np.float32([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]])
    out = cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.GaussianBlur(out, (0, 0), blur) if blur else out


# ------------------------------------------------------------------ 1. negative flash + scale-in (original opener)
def neg_flash(c, g, face=(540, 760)):
    k = g // 2
    if k < 3:
        inv = cv2.GaussianBlur(255 - c, (0, 0), 9) * 0.92 * 0.55; c[:] = inv
        rnd = random.Random(k); col = CYAN if k < 2 else RED
        for _ in range(2):
            x, y = rnd.uniform(420, 640), rnd.uniform(600, 900); c[int(y):int(y) + 48, int(x):int(x) + 48] = np.array(col, np.float32)
    elif k < 6:
        j = k - 3; c[:] = _scale(c, [0.92, 0.96, 0.99][j], blur=[12, 6, 2][j])


# ------------------------------------------------------------------ 2. pixel assemble: giant red mosaic resolves
def pixel_assemble(c, g, face=(540, 760)):
    k = g // 2; sizes = [144, 96, 64, 40, 24, 12]
    if k >= len(sizes): return
    s = sizes[k]; small = cv2.resize(c, (max(1, W // s), max(1, H // s)), interpolation=cv2.INTER_AREA)
    mos = cv2.resize(small, (W, H), interpolation=cv2.INTER_NEAREST)
    tint = np.array(RED, np.float32); a = [0.55, 0.4, 0.25, 0.12, 0.05, 0][k]
    c[:] = mos * (1 - a) + tint * a
    _blocks(c, random.Random(10 + k), [10, 8, 6, 4, 3, 2][k], 120, 900, 320, 1200)


# ------------------------------------------------------------------ 3. strip slam: 5 horizontal strips slam in from alternate sides
def strip_slam(c, g, face=(540, 760)):
    k = g // 2; n = 5; ease = [1.0, 0.55, 0.18, -0.04, 0.0]
    if k >= n - 1 + len(ease): return
    src = c.copy(); c[:] = 0; hh = H // n
    for i in range(n):
        j = k - i
        e = ease[min(max(j, 0), len(ease) - 1)] if j >= 0 else 1.0
        dx = int(e * W * (1 if i % 2 == 0 else -1))
        y0, y1 = i * hh, (i + 1) * hh if i < n - 1 else H
        seg = src[y0:y1]
        if abs(dx) < W:
            if dx >= 0: c[y0:y1, dx:] = seg[:, :W - dx]
            else: c[y0:y1, :W + dx] = seg[:, -dx:]
        if 0 <= j < 3:   # red leading edge on the moving strip
            ex = dx if dx >= 0 else W + dx
            c[y0:y1, max(0, ex - 6):min(W, ex + 6)] = np.array(RED, np.float32)


# ------------------------------------------------------------------ 4. red wipe: diagonal red band reveals the frame
def red_wipe(c, g, face=(540, 760)):
    n = 16
    if g >= n: return
    p = (g + 1) / n; head = -400 + (W + 900) * (1 - (1 - p) ** 2)
    yy, xx = np.mgrid[0:H:4, 0:W:4]; d = (xx + (yy - 960) * 0.35) - head
    d = cv2.resize(d.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    reveal = np.clip(-d / 40, 0, 1)[..., None]; band = np.clip(1 - np.abs(d + 70) / 70, 0, 1)[..., None]
    core = np.clip(1 - np.abs(d + 70) / 10, 0, 1)[..., None]
    c[:] = c * reveal
    c[:] = c * (1 - band) + np.array(RED, np.float32) * band
    c[:] = c * (1 - core) + 255 * core


# ------------------------------------------------------------------ 5. zoom punch: smooth 135 % -> 98 % -> 100 % with RGB split
def zoom_punch(c, g, face=(540, 760)):
    n = 14
    if g >= n: return
    t = g / (n - 1); s = 1.0 + 0.35 * (1 - t) ** 3 - 0.02 * math.sin(math.pi * min(1, t * 1.4)) * (t < 0.72)
    cx, cy = face; src = c.copy(); acc = np.zeros_like(c)
    for i in range(3):   # zoom blur
        acc += _scale(src, s + 0.04 * (1 - t) * i, cx, cy)
    out = acc / 3; sh = int(26 * (1 - t))
    if sh > 0:
        r = out.copy(); r[:, sh:, 0] = out[:, :-sh, 0]; r[:, :-sh, 2] = out[:, sh:, 2]; out = r
    c[:] = out
    if g < 2: c[:] = c * 0.5 + 255 * 0.5


# ------------------------------------------------------------------ 6. RGB converge: channels fly in from offsets and lock
def rgb_converge(c, g, face=(540, 760)):
    k = g // 2; d = [90, 60, 34, 16, 6, 0]
    if k >= len(d): return
    s = d[k]; out = np.zeros_like(c)
    if s:
        out[:, s:, 0] = c[:, :-s, 0]; out[:, :, 1] = c[:, :, 1]; out[:, :-s, 2] = c[:, s:, 2]
        out[s // 2:, :, 1] = c[:-(s // 2) or None, :, 1] if s > 1 else c[:, :, 1]
    else: out = c.copy()
    lines = (np.arange(H) % 6 < 2).astype(np.float32)[:, None, None] * [0.35, 0.25, 0.15, 0.08, 0.03, 0][k]
    c[:] = out * (1 - lines)


# ------------------------------------------------------------------ 7. halftone iris: frame opens from his face through a red dot ring
def halftone_iris(c, g, face=(540, 760)):
    n = 16
    if g >= n: return
    cx, cy = face; p = (g + 1) / n; r = 40 + 1500 * (1 - (1 - p) ** 2.2)
    yy, xx = np.mgrid[0:H:2, 0:W:2].astype(np.float32); d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    inside = np.clip((r - d) / 6, 0, 1)
    sp = 18.0; gx = (xx % sp) - sp / 2; gy = (yy % sp) - sp / 2; dd = np.sqrt(gx * gx + gy * gy)
    ring = np.clip(1 - np.abs(d - r - 60) / 90, 0, 1); dots = (dd < ring * sp * 0.55).astype(np.float32)
    inside = cv2.resize(inside, (W, H))[..., None]; dots = cv2.resize(dots, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    c[:] = c * inside
    c[:] = c * (1 - dots) + np.array(RED, np.float32) * dots


# ------------------------------------------------------------------ 8. slice glitch: displaced horizontal slices settle
def slice_glitch(c, g, face=(540, 760)):
    k = g // 2; amp = [260, 180, 120, 70, 30, 10, 0]
    if k >= len(amp): return
    rnd = random.Random(77 + k); src = c.copy(); y = 0
    while y < H:
        h = rnd.choice([24, 36, 60, 90, 140]); dx = int(rnd.uniform(-1, 1) * amp[k])
        if rnd.random() < 0.45: dx = 0
        row = np.roll(src[y:y + h], dx, axis=1)
        if amp[k] and rnd.random() < 0.18:
            row = row * 0.6 + np.array(rnd.choice([CYAN, RED]), np.float32) * 0.4
        c[y:y + h] = row; y += h
    if k < 3:
        for _ in range(3):
            yb = int(rnd.uniform(300, 1200)); c[yb:yb + 4] = 255


# ------------------------------------------------------------------ 9. letterbox open: black bars part from the centre line
def letterbox_open(c, g, face=(540, 760)):
    k = g // 2; e = [0.0, 0.08, 0.25, 0.5, 0.75, 0.92, 1.0]
    if k >= len(e): return
    cy = face[1]; half = int(e[k] * 1100); top = max(0, cy - half); bot = min(H, cy + half)
    c[:top] = 0; c[bot:] = 0
    for y in (top, bot):
        c[max(0, y - 3):min(H, y + 3)] = np.array(RED, np.float32)
    if k < 2: c[max(0, cy - 2):cy + 2] = 255


# ------------------------------------------------------------------ 10. shutter blinds: 12 vertical blinds snap open, staggered
def shutter_blinds(c, g, face=(540, 760)):
    k = g // 2; n = 12; e = [0.0, 0.3, 0.7, 1.06, 1.0]
    if k >= n // 2 + len(e): return
    src = c.copy(); c[:] = np.array((14, 6, 8), np.float32); bw = W // n
    for i in range(n):
        j = k - abs(i - n // 2) // 1 // 2
        ee = e[min(max(j, 0), len(e) - 1)] if j >= 0 else 0.0
        w = int(bw * min(ee, 1.0)); x0 = i * bw + (bw - w) // 2
        if w > 0: c[:, x0:x0 + w] = src[:, x0:x0 + w]
        if 0 <= j < 3: c[:, i * bw:i * bw + 3] = np.array(RED, np.float32)


# name: (function, frames at 60 fps, energy, paired SFX)
HOOKS = {
    'neg_flash':      (neg_flash,      12, 'high',   'impact + glitch burst'),
    'pixel_assemble': (pixel_assemble, 12, 'high',   'digital crunch + impact'),
    'strip_slam':     (strip_slam,     18, 'high',   '5 fast slams + sub hit'),
    'red_wipe':       (red_wipe,       16, 'medium', 'whoosh + impact'),
    'zoom_punch':     (zoom_punch,     14, 'high',   'reverse whoosh into punch'),
    'rgb_converge':   (rgb_converge,   12, 'medium', 'glitch zap + soft hit'),
    'halftone_iris':  (halftone_iris,  16, 'calm',   'riser tail + boom'),
    'slice_glitch':   (slice_glitch,   14, 'high',   'data glitch + impact'),
    'letterbox_open': (letterbox_open, 14, 'calm',   'cinematic hit + sub'),
    'shutter_blinds': (shutter_blinds, 18, 'medium', 'shutter clicks + pop'),
}


def apply_hook(name, canvas, g, face=(540, 760)):
    """Apply hook `name` to the composited 60-fps frame g (in place). No-op after the hook's frames."""
    fn, n, _, _ = HOOKS[name]
    if 0 <= g < n: fn(canvas, g, face=face)


def pick_hook(energy, recent, seed=0):
    """Choose a hook matching the topic energy that is NOT in `recent` (names of the last 5 reels' hooks)."""
    order = {'high': ['high', 'medium'], 'medium': ['medium', 'high', 'calm'], 'calm': ['calm', 'medium']}[energy]
    for e in order:
        pool = [k for k, v in HOOKS.items() if v[2] == e and k not in recent]
        if pool: return random.Random(seed).choice(sorted(pool))
    return random.Random(seed).choice(sorted(k for k in HOOKS if k not in recent[-1:]))
