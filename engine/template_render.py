#!/usr/bin/env python3
"""Template renderer for /temp-1 ... /temp-16 (/temp-1 job-driven style in template_t1.py; the hand-built
house renders, e.g. examples/day4_android_studio/render_day4_60.py, still work for one-off reels).

  python3 engine/template_render.py job.json <g0> <g1> part.mp4        # 60 fps frames g0..g1 (silent video)
  python3 engine/template_render.py job.json 0 0 test_dir g1,g2,...    # test PNGs
  python3 engine/template_render.py job.json --audio out.wav           # VO + template music + SFX mix
  python3 engine/template_render.py job.json --full out.mp4            # everything: video (2 parallel halves) + audio + mux

job.json (see templates/README.md):
  template, aroll (tight A-roll video), duration, face {cap_top, chin, x0, x1} (source px), words (reel-time
  [[w, s, e]]), headlines [{label, big, label_t, big_t, script?}], scenes [{t0, t1, title, sub?, image?, items?,
  kicker?, quote?}], banner [t0, t1, title, sub], flash [t...], hook, vo, music, music_db
Every readable box is checked against the safe zone and the face oval (FaceZone.check) — a violation stops the render.
"""
import os, sys, json, math, random, re, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from templates import TEMPLATES, SAFE
from face_guard import FaceZone
import hooks as HK
from template_styles_b import StylesB
from template_t1 import StyleT1

W, H, FPS = 1080, 1920, 60
from paths import FONT_DIRS
FONT_FILES = {'inter': 'Inter%5Bopsz,wght%5D.ttf', 'intertight': 'InterTight%5Bwght%5D.ttf',
              'intertight-i': 'InterTight-Italic%5Bwght%5D.ttf', 'anton': 'Anton-Regular.ttf',
              'playfair': 'PlayfairDisplay%5Bwght%5D.ttf', 'playfair-i': 'PlayfairDisplay-Italic%5Bwght%5D.ttf',
              'montserrat': 'Montserrat%5Bwght%5D.ttf', 'montserrat-i': 'Montserrat-Italic%5Bwght%5D.ttf',
              'spacemono': 'SpaceMono-Regular.ttf', 'spacemono-b': 'SpaceMono-Bold.ttf'}


# ------------------------------------------------------------------ primitives
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


_fc = {}
def font(spec, size):
    name, _, wt = spec.partition(':'); k = (name, size, wt)
    if k in _fc: return _fc[k]
    path = next((os.path.join(d, FONT_FILES[name]) for d in FONT_DIRS if d and os.path.exists(os.path.join(d, FONT_FILES[name]))), None)
    if path is None: raise FileNotFoundError(f'font {FONT_FILES[name]} missing: run setup.sh (downloads all OFL fonts)')
    f = ImageFont.truetype(path, size)
    if wt:
        try:
            vals = []
            for ax in f.get_variation_axes():
                n = ax['name'].decode() if isinstance(ax['name'], bytes) else str(ax['name'])
                vals.append(max(ax['minimum'], min(ax['maximum'], int(wt))) if 'eight' in n else
                            (max(ax['minimum'], min(ax['maximum'], 32)) if 'ptical' in n else ax['default']))
            f.set_variation_by_axes(vals)
        except Exception: pass
    _fc[k] = f; return f


_tc = {}
def text(s, spec, size, fill='#FFFFFF', stroke=0, stroke_fill='#000000', shadow=None, tracking=0, grad=None,
         glow=None, maxw=None):
    """RGBA uint8 layer of one line. shadow=(dx, dy, blur, alpha); grad=(top_hex, bottom_hex); glow=(hex, radius, gain).
    maxw shrinks the font until the line fits."""
    k = (s, spec, size, fill, stroke, stroke_fill, shadow, tracking, grad, glow, maxw)
    if k in _tc: return _tc[k]
    f = font(spec, size)
    def width(fo): return sum(fo.getlength(ch) for ch in s) + tracking * max(0, len(s) - 1) if tracking else fo.getlength(s)
    while maxw and width(f) > maxw and size > 20: size = int(size * 0.94); f = font(spec, size)
    asc, desc = f.getmetrics(); pad = int(size * 0.45) + stroke + (glow[1] * 2 if glow else 0)
    w = int(width(f)) + 2 * pad; h = asc + desc + 2 * pad
    mask = Image.new('L', (w, h), 0); d = ImageDraw.Draw(mask)
    def draw(dr, fill_, sw=0, sf=None):
        if tracking:
            x = pad
            for ch in s: dr.text((x, pad), ch, font=f, fill=fill_, stroke_width=sw, stroke_fill=sf); x += f.getlength(ch) + tracking
        else: dr.text((pad, pad), s, font=f, fill=fill_, stroke_width=sw, stroke_fill=sf)
    draw(d, 255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if glow:
        gm = mask.filter(ImageFilter.GaussianBlur(glow[1])); ga = np.clip(np.asarray(gm).astype(np.float32) * glow[2], 0, 255).astype(np.uint8)
        gl = Image.new('RGBA', (w, h), rgb(glow[0]) + (0,)); gl.putalpha(Image.fromarray(ga)); out = Image.alpha_composite(out, gl)
    if shadow:
        dx, dy, bl, al = shadow; sh = Image.new('L', (w, h), 0); draw(ImageDraw.Draw(sh), 255, stroke, 255)
        sh = sh.transform((w, h), Image.AFFINE, (1, 0, -dx, 0, 1, -dy)).filter(ImageFilter.GaussianBlur(bl))
        sl = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sl.putalpha(Image.fromarray((np.asarray(sh) * al).astype(np.uint8)))
        out = Image.alpha_composite(out, sl)
    if stroke:
        st = Image.new('L', (w, h), 0); draw(ImageDraw.Draw(st), 255, stroke, 255)
        sl = Image.new('RGBA', (w, h), rgb(stroke_fill) + (0,)); sl.putalpha(st); out = Image.alpha_composite(out, sl)
    if grad:
        a, b = np.array(rgb(grad[0]), np.float32), np.array(rgb(grad[1]), np.float32); yy = np.linspace(0, 1, h)[:, None, None]
        col = (a * (1 - yy) + b * yy) * np.ones((1, w, 1)); fl = Image.fromarray(col.astype(np.uint8)).convert('RGBA')
    else: fl = Image.new('RGBA', (w, h), rgb(fill) + (255,))
    fl.putalpha(mask); out = Image.alpha_composite(out, fl)
    arr = np.asarray(out); _tc[k] = arr; return arr


def comp(c, lay, cx, cy, scale=1.0, alpha=1.0, anchor='c', rot=0.0, blur=0):
    """Composite RGBA uint8 `lay` onto float canvas. anchor: c (centre), l (left-middle), bl (bottom-left), b (bottom-centre).
    Returns the drawn box (x0, y0, x1, y1) of the visible glyph area (padding trimmed)."""
    if alpha <= 0.003 or scale <= 0.01: return None
    im = lay
    if scale != 1.0 or rot:
        p = Image.fromarray(lay)
        if scale != 1.0: p = p.resize((max(1, int(p.width * scale)), max(1, int(p.height * scale))), Image.BICUBIC)
        if rot: p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
        im = np.asarray(p)
    if blur: im = cv2.GaussianBlur(im, (0, 0), blur)
    h, w = im.shape[:2]
    x0 = {'c': cx - w / 2, 'l': cx, 'bl': cx, 'b': cx - w / 2}[anchor]; y0 = {'c': cy - h / 2, 'l': cy - h / 2, 'bl': cy - h, 'b': cy - h}[anchor]
    x0, y0 = int(round(x0)), int(round(y0)); X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0: return None
    sub = im[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0].astype(np.float32); a = sub[..., 3:4] / 255 * alpha
    c[Y0:Y1, X0:X1] = c[Y0:Y1, X0:X1] * (1 - a) + sub[..., :3] * a
    ys, xs = np.where(sub[..., 3] > 40)
    return (X0 + xs.min(), Y0 + ys.min(), X0 + xs.max(), Y0 + ys.max()) if len(xs) else None


def rounded_card(img, w, h, r=28, border=0, border_col='#FFFFFF', shadow=True):
    ih, iw = img.shape[:2]; s = max(w / iw, h / ih); im = cv2.resize(img, (int(iw * s) + 1, int(ih * s) + 1), interpolation=cv2.INTER_AREA)
    oy, ox = (im.shape[0] - h) // 2, (im.shape[1] - w) // 2; im = im[oy:oy + h, ox:ox + w]
    pad = 40; out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad + 6, pad + 16, pad + w + 6, pad + h + 16), r, fill=120)
        sl = Image.new('RGBA', out.size, (0, 0, 0, 0)); sl.putalpha(sh.filter(ImageFilter.GaussianBlur(18))); out = Image.alpha_composite(out, sl)
    if border:
        b = Image.new('RGBA', out.size, (0, 0, 0, 0)); ImageDraw.Draw(b).rounded_rectangle((pad - border, pad - border, pad + w + border, pad + h + border), r + border, fill=rgb(border_col) + (255,))
        out = Image.alpha_composite(out, b)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    p = Image.fromarray(im.astype(np.uint8)).convert('RGBA'); p.putalpha(m); out.alpha_composite(p, (pad, pad))
    return np.asarray(out)


def vgrad(c0, c1, h=H, w=W):
    a, b = np.array(rgb(c0), np.float32), np.array(rgb(c1), np.float32); t = np.linspace(0, 1, h)[:, None, None]
    return (a * (1 - t) + b * t) * np.ones((1, w, 1), np.float32)


def ease_out(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3


def fix_words(words, glossary=None):
    """ASR clean-up before anything is drawn: join hyphen-split tokens ('Anti' + '-Gravity.' -> 'Anti-Gravity.'), then
    apply the reel's verified spellings (glossary dict or path: {'Juni': 'Junie', 'Anti-Gravity': 'Antigravity'})."""
    out = []
    for w, s, e in words:
        if out and w.startswith('-') and len(w) > 1: pw, ps, pe = out.pop(); out.append((pw + w, ps, e)); continue
        out.append((w, s, e))
    if isinstance(glossary, str): glossary = json.load(open(glossary))
    if glossary:
        g = {k.lower().replace(' ', ''): v for k, v in glossary.items()}
        fixed = []
        for w, s, e in out:
            m = re.match(r'^(\W*)(.*?)(\W*)$', w); core = m.group(2)
            fixed.append((m.group(1) + g.get(core.lower(), core) + m.group(3), s, e))
        out = fixed
    return out


# ------------------------------------------------------------------ source + grade
class Source:
    def __init__(self, path, fps=30):
        self.cap = cv2.VideoCapture(path); self.fps = fps; self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)); self.i = -1; self.cur = None
    def at(self, t):
        k = min(self.n - 1, max(0, int(t * self.fps + 1e-6)))
        if k < self.i or k > self.i + 90: self.cap.set(cv2.CAP_PROP_POS_FRAMES, k); self.i = k - 1
        while self.i < k:
            ok, fr = self.cap.read()
            if not ok: break
            self.i += 1; self.cur = fr
        return cv2.cvtColor(self.cur, cv2.COLOR_BGR2RGB).astype(np.float32)


_vig = {}
def grade(img, g):
    out = img * np.array(g.get('gain', (1, 1, 1)), np.float32) + np.array(g.get('lift', (0, 0, 0)), np.float32)
    m = out.mean(2, keepdims=True); out = m + (out - m) * g.get('sat', 1.0)
    out = (out - 128) * g.get('contrast', 1.0) + 128
    v = g.get('vignette', 0)
    if v:
        if v not in _vig:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - 540) / 760) ** 2 + ((yy - 900) / 1150) ** 2)
            _vig[v] = np.clip(1 - v * np.clip(r - 0.35, 0, 1) ** 1.6, 0, 1)[..., None]
        out = out * _vig[v]
    return np.clip(out, 0, 255)


# ------------------------------------------------------------------ audio
def synth(kind, sr=48000):
    t = np.arange(int(sr * {'impact': 0.9, 'whoosh': 0.45, 'pop': 0.09, 'tick': 0.03, 'swell': 0.7}[kind])) / sr; rng = np.random.default_rng(len(t))
    if kind == 'impact': y = np.sin(2 * np.pi * (48 + 40 * np.exp(-t * 8)) * t) * np.exp(-t * 4.5) + rng.normal(0, 1, len(t)) * np.exp(-t * 40) * 0.4
    elif kind == 'whoosh':
        n = rng.normal(0, 1, len(t)); env = np.sin(np.pi * t / t[-1]) ** 2; y = np.convolve(n, np.ones(18) / 18, 'same') * env * 2.2
    elif kind == 'pop': y = np.sin(2 * np.pi * (900 - 4500 * t) * t) * np.exp(-t * 45)
    elif kind == 'tick': y = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 200) * 0.6
    else: y = np.convolve(rng.normal(0, 1, len(t)), np.ones(60) / 60, 'same') * (t / t[-1]) ** 2 * 3
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


_smp = {}
def _sample(path, sr=48000):
    if path not in _smp:
        import soundfile as sf_
        tmp = '/tmp/_sfx_' + os.path.basename(path) + '.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', str(sr), tmp], check=True)
        y, _ = sf_.read(tmp, dtype='float32'); _smp[path] = y / (np.abs(y).max() + 1e-9)
    return _smp[path]


def build_audio(job, spec, out_wav, stems_dir=None):
    sr = 48000; dur = job['duration']; n = int(sr * dur); sfx = np.zeros(n, np.float32)
    lib = job.get('sfx', {})     # e.g. {'impact': '/path/impact.mp3', 'pop': ..., 'whoosh': ...} (Magnific SFX)
    def add(kind, t, gain):
        y = (_sample(lib[kind]) if kind in lib else synth(kind)) * gain; i = int(t * sr); j = min(n, i + len(y))
        if 0 <= i < n: sfx[i:j] += y[:j - i]
    add('impact', 0.0, 0.42)
    for h in job.get('headlines', []):
        if h['big_t'] < dur: add('pop' if spec['energy'] != 'calm' else 'tick', h['big_t'], 0.35)
    for s in job.get('scenes', []):
        if s['t0'] < dur: add('whoosh', max(0, s['t0'] - 0.18), 0.36); add('whoosh', max(0, s['t1'] - 0.18), 0.3)
        acc = s['t0']
        for c in s.get('clips', [])[:-1]:          # quick cuts inside a multi-shot scene
            acc += c['dur']
            if acc < min(dur, s['t1']): add('tick' if 'tick' in lib else 'pop', acc, 0.22)
    for t in job.get('flash', []):
        if t < dur: add('impact', t, 0.4)
    for h in job.get('headlines', []):            # label pop + per-letter ticks are part of the /temp-1 grammar
        if int(job['template']) == 1 and h.get('label') and h['label_t'] < dur: add('tick', h['label_t'], 0.25)
    for t in job.get('punch', []):
        if int(job['template']) == 1 and t < dur: add('swoosh' if 'swoosh' in lib else 'tick', t, 0.12)
    if job.get('end_hit') and job['end_hit'] < dur: add('impact', job['end_hit'], 0.5)   # hard button ending
    sf_path = out_wav + '.sfx.wav'
    import soundfile as sf; sf.write(sf_path, np.stack([sfx, sfx], 1), sr)
    mdb = job.get('music_db', -29)   # dialogue-safe: bed ~20 dB under the voice (22 Nov 2026)
    fc = (f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume={mdb}dB,highpass=f=60,lowpass=f=9000,equalizer=f=1800:t=q:w=1.2:g=-6,equalizer=f=3500:t=q:w=1.2:g=-4,afade=t=out:st={dur - 0.04}:d=0.04[m];"
          f"[0:a]atrim=0:{dur},asetpts=PTS-STARTPTS,asplit=3[v][vk][vk2];[m][vk]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450[md];"
          f"[2:a]volume={job.get('sfx_db', -15)}dB[s0];[s0][vk2]sidechaincompress=threshold=0.03:ratio=4:attack=4:release=220:makeup=1[s];"   # SFX duck under words (audio audit 25 Nov 2026)
          f"[v][md][s]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', job['vo'], '-stream_loop', '-1', '-i', job['music'], '-i', sf_path,
                    '-filter_complex', fc, '-map', '[a]', '-ac', '2', '-t', str(dur), out_wav], check=True)
    if stems_dir:   # pre-loudnorm stems for tools/audio_audit.py (same chain, same relative levels)
        os.makedirs(stems_dir, exist_ok=True)
        fs = fc.split('[v][md][s]amix')[0] + '[v]anull[vo_];[md]anull[mu_];[s]anull[sx_]'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', job['vo'], '-stream_loop', '-1', '-i', job['music'], '-i', sf_path,
                        '-filter_complex', fs, '-map', '[vo_]', '-ac', '2', '-t', str(dur), os.path.join(stems_dir, 'vo.wav'),
                        '-map', '[mu_]', '-ac', '2', '-t', str(dur), os.path.join(stems_dir, 'music.wav'),
                        '-map', '[sx_]', '-ac', '2', '-t', str(dur), os.path.join(stems_dir, 'sfx.wav')], check=True)
    os.remove(sf_path)
    # second pass: measure and correct to -14 LUFS (single-pass loudnorm can land ~1 dB low), keep true peak <= -1.5 dBTP
    import soundfile as sf, pyloudnorm as pyln
    y, sr_ = sf.read(out_wav); L = pyln.Meter(sr_).integrated_loudness(y)
    if abs(L + 14) > 0.3:
        tmp = out_wav + '.fix.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out_wav, '-af', f'volume={-14 - L:.2f}dB,alimiter=limit=0.84:level=false', tmp], check=True)
        os.replace(tmp, out_wav)


# ------------------------------------------------------------------ the template engine
class Reel(StylesB, StyleT1):
    def __init__(self, job):
        self.job = job; self.n = int(job['template']); self.spec = TEMPLATES[self.n]; self.pal = self.spec['palette']
        self.src = Source(job['aroll'], job.get('src_fps', 30)); self.dur = job['duration']
        f = job['face']; self.face = FaceZone.from_head(f['cap_top'], f['chin'], f['x0'], f['x1'])
        self.words = [tuple(w) for w in json.load(open(job['words']))] if isinstance(job['words'], str) else [tuple(w) for w in job['words']]
        self.words = fix_words(self.words, job.get('glossary'))
        self.heads = job.get('headlines', []); self.scenes = job.get('scenes', [])
        self.bigset = {w.lower() for h in self.heads for w in re.findall(r'[\w+]+', h['big'])}
        self.imgs = {}; self.boxes = []
        self.trans = {1: ('negswoosh', 12), 2: ('blur', 10), 3: ('wash', 8), 4: ('whip', 8), 5: ('zoom', 8), 6: ('swoosh', 10), 7: ('scale', 6),
                      8: ('leak', 12), 9: ('blur', 10), 10: ('scale', 8), 11: ('glitch', 6), 12: ('blur', 8), 13: ('bend', 12),
                      14: ('zoom', 8), 15: ('cut', 2), 16: ('scale', 8)}[self.n]
        if self.n == 7: self.face = self._t7_face()

    # --- helpers
    def img(self, p):
        if p not in self.imgs:
            if ':' in p and not os.path.exists(p):   # library reference, e.g. 'vector:tech-bg/0' (engine/assets.py)
                import assets; p2 = assets.pick(p)
            else: p2 = p
            self.imgs[p] = np.asarray(Image.open(p2).convert('RGB'))
        return self.imgs[p]

    def check(self, box, what, t, face=True):
        if box is None: return
        x0, y0, x1, y1 = box
        if x0 < SAFE[0] - 2 or x1 > SAFE[2] + 2 or y0 < SAFE[1] - 2 or y1 > SAFE[3] + 2:
            raise ValueError(f'temp-{self.n}: {what} {box} leaves the safe zone at {t:.2f}s')
        if face is True: self.face.check(box, f'temp-{self.n} {what}', t)
        elif face: face.check(box, f'temp-{self.n} {what}', t)  # layout-specific face zone (split, card, polaroid)

    def head_at(self, t):
        cur = None
        for i, h in enumerate(self.heads):
            if h['label_t'] <= t < h.get('until', 1e9): cur = (i, h)
        return cur

    def scene_at(self, t):
        for i, s in enumerate(self.scenes):
            if s['t0'] <= t < s['t1']: return i, s
        return None

    def word_at(self, t):
        for w in self.words:
            if w[1] <= t < w[2]: return w
        return None

    def chunk_at(self, t, max_words, max_chars):
        if not hasattr(self, '_chunks'):
            from captions import chunk_words
            self._chunks = chunk_words(self.words, max_words=max_words, max_chars=max_chars)
        for c in self._chunks:
            if c['start'] <= t < c['end']: return c
        return None

    def shifted(self, t):
        """A-roll moved down by job['dy'] (same framing as the house render); the opened strip is the room's top rows stretched."""
        src = self.src.at(t); dy = int(self.job.get('dy', 0))
        cuts = self.job.get('punch')
        if cuts:   # hide each jump cut: alternate framing 1.0 / punch_scale about the face centre (face stays put)
            k = sum(1 for x in cuts if x <= t)
            if k % 2:
                s_ = self.job.get('punch_scale', 1.06); fx_, fy_ = self.job['face_src_c']
                M = np.float32([[s_, 0, fx_ * (1 - s_)], [0, s_, fy_ * (1 - s_)]])
                src = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        if not dy: return src
        out = np.empty_like(src); out[dy:] = src[:H - dy]; ext = cv2.resize(src[0:70], (W, dy + 60), interpolation=cv2.INTER_LINEAR)
        out[:dy] = ext[:dy]; k = np.linspace(1, 0, 60)[:, None, None]; out[dy:dy + 60] = ext[dy:] * k + out[dy:dy + 60] * (1 - k)
        return out

    def base(self, t):
        return grade(self.shifted(t), self.spec['grade'])

    # --- state machine + transitions
    def state(self, t):
        if self.n == 4 and self.job.get('banner') and self.job['banner'][0] <= t < self.job['banner'][1]: pass
        sc = self.scene_at(t)
        fl = [x for x in self.job.get('flash', []) if x <= t < x + 0.5]
        if fl and self.n == 7: return ('flash', fl[0])
        if self.n == 2 and t < self.job.get('hook_until', 0): return ('abstract', 0)
        return ('scene', sc[0]) if sc else ('talk', 0)

    def render_state(self, st, t):
        k, i = st
        if k == 'talk': return self.talk(t)
        if k == 'scene': return self.scene(t, self.scenes[i], i)
        if k == 'abstract': return self.abstract(t)
        if k == 'flash': return self.flash(t, i)

    def frame(self, g):
        t = g / FPS; st = self.state(t); kind, n = self.trans; half = n / FPS / 2
        bounds = sorted({0.0} | {s['t0'] for s in self.scenes} | {s['t1'] for s in self.scenes} |
                        set(self.job.get('flash', [])) | {x + 0.5 for x in self.job.get('flash', [])} | ({self.job['hook_until']} if self.n == 2 and self.job.get('hook_until') else set()))
        b = next((x for x in bounds if abs(t - x) < half and x > 0), None)
        if b is None: c = self.render_state(st, t)
        else:
            sa, sb = self.state(b - 1e-3), self.state(b + 1e-3); p = (t - (b - half)) / (2 * half)
            if sa == sb or 'flash' in (sa[0], sb[0]): c = self.render_state(st, t)
            else: c = self.transition(kind, self.render_state(sa, t), self.render_state(sb, t), p)
        HK.RED = rgb(self.pal['accent']); HK.BLOCKS = [HK.RED, (255, 255, 255), tuple(int(v * 0.6) for v in HK.RED)]
        HK.apply_hook(self.job.get('hook', 'zoom_punch'), c, g, face=(int(self.face.cx), int(self.face.cy)))
        return np.clip(c, 0, 255).astype(np.uint8)

    def transition(self, kind, a, b, p):
        p = min(max(p, 0), 1)
        if kind == 'leak':   # warm light-leak flash (t-8)
            base = a * (1 - p) + b * p; k = math.sin(math.pi * p)
            if not hasattr(self, '_leak'):
                yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); g = np.exp(-(((xx - 300) ** 2) / (2 * 520 ** 2) + ((yy - 700) ** 2) / (2 * 900 ** 2)))
                self._leak = g[..., None] * np.array((255, 205, 120), np.float32) + (1 - g[..., None]) * np.array((255, 120, 160), np.float32) * 0.6
            return np.clip(base * (1 - 0.65 * k) + self._leak * k * 0.85 + base * k * 0.3, 0, 255)
        if kind == 'glitch':  # RGB split + slice offsets (t-11)
            src = a if p < 0.5 else b; k = math.sin(math.pi * p); out = src.copy(); rnd = np.random.default_rng(int(p * 97))
            sh = int(28 * k); out[..., 0] = np.roll(src[..., 0], sh, axis=1); out[..., 2] = np.roll(src[..., 2], -sh, axis=1)
            for _ in range(6):
                y0 = int(rnd.integers(0, H - 80)); hgt = int(rnd.integers(20, 80)); out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], int(rnd.integers(-60, 60) * k), axis=1)
            return out
        if kind == 'bend':    # paper-bend page turn (t-13)
            e = ease_out(p); src = np.float32([[0, 0], [W, 0], [W, H], [0, H]]); ins = 260 * (1 - e); dy = 420 * (1 - e)
            dst = np.float32([[ins, dy], [W - ins * 0.4, dy * 0.6], [W, H], [0, H]]); M = cv2.getPerspectiveTransform(src, dst)
            wb = cv2.warpPerspective(b, M, (W, H), borderValue=(0, 0, 0)); m = cv2.warpPerspective(np.ones((H, W), np.float32), M, (W, H))[..., None]
            return a * (1 - m) * (0.6 + 0.4 * (1 - e)) + wb * m
        if kind == 'negswoosh':   # /temp-1: red light swoosh wipe with a 2-frame negative flash at the switch (<= 0.2 s)
            xx = np.arange(W)[None, :] + np.arange(H)[:, None] * 0.35; edge = -700 + (W + 1400) * ease_out(p)
            m = (xx < edge).astype(np.float32)[..., None]; band = np.clip(1 - np.abs(xx - edge) / 150, 0, 1)[..., None]
            out = a * (1 - m) + b * m
            out = out * (1 - band) + (np.array((255, 40, 50), np.float32) * 0.7 + 255 * 0.3 * band) * band
            if 0.42 <= p < 0.58: out = cv2.GaussianBlur(255 - out, (0, 0), 6) * 0.6
            return out
        if kind == 'cut': return b if p >= 0.5 else a
        if kind == 'blur':
            k = math.sin(math.pi * p) * 22 + 0.1; return cv2.GaussianBlur(a, (0, 0), k) * (1 - p) + cv2.GaussianBlur(b, (0, 0), k) * p
        if kind == 'wash':
            base = a if p < 0.5 else b; al = math.sin(math.pi * p) * 0.9
            g = vgrad('#E8132E', '#FFD23F') * np.linspace(1, 0.7, W)[None, :, None] + 0; return base * (1 - al) + g * al
        if kind == 'whip':
            e = ease_out(p); sh = int(W * e); out = np.zeros_like(a)
            out[:, :W - sh] = a[:, sh:]; out[:, W - sh:] = b[:, :sh] if sh else out[:, W - sh:]
            return cv2.blur(out, (int(1 + 90 * math.sin(math.pi * p)), 1))
        if kind == 'zoom':
            src, s = (a, 1 + 0.25 * p) if p < 0.5 else (b, 1.25 - 0.25 * p); M = np.float32([[s, 0, 540 * (1 - s)], [0, s, 960 * (1 - s)]])
            im = cv2.warpAffine(src, M, (W, H), borderMode=cv2.BORDER_REFLECT)
            acc = im.copy()
            for i in range(1, 4):
                s2 = 1 + 0.02 * i * math.sin(math.pi * p); M2 = np.float32([[s2, 0, 540 * (1 - s2)], [0, s2, 960 * (1 - s2)]])
                acc += cv2.warpAffine(im, M2, (W, H), borderMode=cv2.BORDER_REFLECT)
            return acc / 4
        if kind == 'swoosh':
            xx = np.arange(W)[None, :] + np.arange(H)[:, None] * 0.45; edge = -900 + (W + 1800) * ease_out(p)
            m = (xx < edge).astype(np.float32)[..., None]; band = np.clip(1 - np.abs(xx - edge) / 120, 0, 1)[..., None]
            out = a * (1 - m) + b * m; return out * (1 - band) + np.array(rgb('#FFFFFF'), np.float32) * band * 0.9 + out * band * 0.1
        if kind == 'scale':
            s = 1.06 - 0.06 * ease_out(p); M = np.float32([[s, 0, 540 * (1 - s)], [0, s, 960 * (1 - s)]])
            return a * (1 - p) + cv2.warpAffine(b, M, (W, H), borderMode=cv2.BORDER_REFLECT) * p
        return b if p >= 0.5 else a

    # ================================================================ per-template drawing
    def talk(self, t):
        return getattr(self, f't{self.n}_talk')(t)

    def scene(self, t, sc, i):
        return getattr(self, f't{self.n}_scene')(t, sc, i)

    # ---------------------------------------------------------------- temp-2 Minimal Cinematic
    def abstract(self, t):
        fr = self.shifted(t); top = cv2.resize(fr[0:420], (W, H)); c = cv2.GaussianBlur(top, (0, 0), 38)
        m = c.mean(2, keepdims=True); c = m + (c - m) * 0.35; c = c * 0.35 + np.array((236, 242, 242), np.float32) * 0.65
        ch = self.chunk_at(t, 3, 18)
        if ch is None and hasattr(self, '_chunks'):   # hold the last line on the hook page (no empty frames before the cut)
            prev = [x for x in self._chunks if x['start'] <= t]; ch = prev[-1] if prev else None
        if ch: self._t2_words(c, t, ch, cy=900, small=84, big=120, ink='#16211F', check_face=False)
        return c

    def _t2_words(self, c, t, ch, cy, small, big, ink, check_face=True):
        lays = []
        for w, s, e in ch['words']:
            if t < s: break
            key = re.sub(r'\W', '', w).lower() in self.bigset
            lay = text(w.strip(',.'), 'playfair-i:600' if key else 'inter:600', big if key else small, fill=ink,
                       shadow=(0, 3, 6, 0.35) if ink == '#FFFFFF' else None)
            lays.append((lay, s, int((big if key else small) * 0.45)))
        if not lays: return
        gap = 16; ws = [l.shape[1] - 2 * pd for l, _, pd in lays]; tot = sum(ws) + gap * (len(ws) - 1)
        x = 512 - tot / 2
        for (lay, s, pd), wdt in zip(lays, ws):
            a = ease_out((t - s) / 0.12); box = comp(c, lay, x - pd, cy, anchor='l', alpha=a, blur=int((1 - a) * 6))
            self.check(box, 'caption', t, face=check_face); x += wdt + gap

    def t2_talk(self, t):
        c = self.base(t); ch = self.chunk_at(t, 3, 18)
        if ch: self._t2_words(c, t, ch, cy=self.face.box[3] + 70, small=44, big=72, ink='#FFFFFF')
        return c

    def t2_scene(self, t, sc, i):
        c = np.full((H, W, 3), rgb(self.pal['bg']), np.float32); a = t - sc['t0']
        words = sc['title'].split(); y = 690          # block centred in the safe box (title 690 -> branch labels ~1040)
        x_tot = text(sc['title'], 'inter:700', 84, fill=self.pal['ink'], maxw=860)
        box = comp(c, x_tot, 512, y, alpha=ease_out(a / 0.25), blur=int(max(0, 1 - a / 0.25) * 8)); self.check(box, 'title', t, face=False)
        if sc.get('sub'):
            box = comp(c, text(sc['sub'], 'inter:500', 42, fill='#3A3A3A', maxw=860), 512, y + 78, alpha=ease_out((a - 0.3) / 0.25)); self.check(box, 'sub', t, face=False)
        if sc.get('items'):   # tree diagram on the safe-zone centre line (x 512); 2 or 3 branches, labels fit their column
            items = sc['items'][:3]; xs = (252, 772) if len(items) == 2 else (222, 512, 802); colw = 400 if len(items) == 2 else 270
            p = ease_out((a - 0.35) / 0.3); stem_y0, stem_y1 = y + 110, y + 200   # tree builds in ~1.2 s (event every 0.3 s)
            cv2.line(c, (512, stem_y0), (512, int(stem_y0 + (stem_y1 - stem_y0) * p)), (25, 25, 25), 8)
            if p >= 1:
                q = ease_out((a - 0.65) / 0.3); half = int((xs[-1] - 512) * q)
                cv2.line(c, (512 - half, stem_y1), (512 + half, stem_y1), (25, 25, 25), 8)
                if q >= 1:
                    for k, (it, xx) in enumerate(zip(items, xs)):
                        r = ease_out((a - 0.95 - 0.15 * k) / 0.25)
                        cv2.line(c, (xx, stem_y1), (xx, int(stem_y1 + 90 * r)), (25, 25, 25), 8)
                        box = comp(c, text(it, 'inter:600', 50, fill=self.pal['ink'], maxw=colw), xx, stem_y1 + 150, alpha=r); self.check(box, 'item', t, face=False)
        elif sc.get('image'):
            card = rounded_card(self.img(sc['image']), 780, 560, r=30)
            s = 0.94 + 0.06 * ease_out((a - 0.2) / 0.5) + 0.01 * a; box = comp(c, card, 512, 930, scale=s, alpha=ease_out((a - 0.2) / 0.3))
            self.check(box, 'image card', t, face=False)
        return c

    # ---------------------------------------------------------------- temp-3 Editorial Script
    def _t3_headline(self, c, t, idx, h, top_y, check_face=True):
        a = t - h['label_t']; lab = text(h['label'], 'inter:800', 42, shadow=(0, 3, 8, 0.6), maxw=820)
        box = comp(c, lab, 90, top_y, anchor='l', alpha=ease_out(a / 0.12)); self.check(box, 'label', t, check_face)
        if t < h['big_t']: return
        b = t - h['big_t']; script = h.get('script') or (idx % 2 == 1)
        if script:
            lay = text(h['big'].lower(), 'playfair-i:700', 118, fill=self.pal['accent'], shadow=(0, 4, 10, 0.5), maxw=820)
            w = int(lay.shape[1] * ease_out(b / 0.35)); cut = lay.copy(); cut[:, w:, 3] = 0
            box = comp(c, cut, 512, top_y + 82, rot=3); self.check(box, 'script word', t, check_face)
        else:
            lay = text(h['big'], 'intertight:900', 150, shadow=(0, 6, 14, 0.55), maxw=720)  # peak scale 1.18 -> 850 px
            s = 1.18 - 0.18 * ease_out(b / 0.2); box = comp(c, lay, 512, top_y + 92, scale=s, alpha=ease_out(b / 0.08))
            self.check(box, 'big word', t, check_face)
            if h.get('accent'):
                acc = text(h['accent'], 'playfair-i:700', 96, fill=self.pal['accent'], shadow=(0, 3, 8, 0.5))
                w = int(acc.shape[1] * ease_out((b - 0.25) / 0.35)); cut = acc.copy(); cut[:, w:, 3] = 0
                box = comp(c, cut, 660, top_y + 150, rot=6); self.check(box, 'accent word', t, check_face)

    def t3_talk(self, t):
        c = self.base(t); hh = self.head_at(t)
        if hh: self._t3_headline(c, t, hh[0], hh[1], top_y=300)
        w = self.word_at(t)
        if w and re.sub(r'\W', '', w[0]).lower() not in self.bigset:
            box = comp(c, text(w[0].strip(',.'), 'inter:700', 40, shadow=(0, 3, 8, 0.6)), 512, self.face.box[3] + 70); self.check(box, 'caption', t)
        return c

    def t3_scene(self, t, sc, i):
        c = np.full((H, W, 3), rgb(self.pal['bg']), np.float32); a = t - sc['t0']
        if sc.get('image'):
            card = rounded_card(self.img(sc['image']), 660, 760, r=40); s = 1.0 + 0.04 * a / max(0.1, sc['t1'] - sc['t0'])
            comp(c, card, 540, 860, scale=s * (0.96 + 0.04 * ease_out(a / 0.25)))
        hh = self.head_at(t)
        if hh: self._t3_headline(c, t, hh[0], hh[1], top_y=300, check_face=False)
        return c

    # ---------------------------------------------------------------- temp-4 Listicle Chapters
    def t4_talk(self, t):
        c = self.base(t); bn = self.job.get('banner')
        if bn and bn[0] <= t < bn[1] + 0.25: self._t4_banner(c, t, bn)
        ch = self.chunk_at(t, 5, 30)
        if ch:
            f = font('montserrat:700', 36); parts = []; x = 0
            for w, s, e in ch['words']:
                lay = text(w, 'montserrat:700', 36, fill='#111111' if t >= s else '#BDBDBD'); parts.append(lay)
            gw = [p.shape[1] - 2 * int(36 * 0.45) for p in parts]; tot = sum(gw) + 12 * (len(gw) - 1)
            y = min(self.face.box[3] + 105, 1208); pill = np.zeros((70, int(tot) + 44, 4), np.uint8)
            pim = Image.new('RGBA', (pill.shape[1], 70), (0, 0, 0, 0)); ImageDraw.Draw(pim).rounded_rectangle((0, 0, pill.shape[1] - 1, 69), 20, fill=(255, 255, 255, 242))
            box = comp(c, np.asarray(pim), 512, y); self.check(box, 'caption pill', t)
            x = 512 - tot / 2
            for p, wd in zip(parts, gw): comp(c, p, x - int(36 * 0.45), y + 1, anchor='l'); x += wd + 12
        return c

    def _t4_banner(self, c, t, bn):
        a = t - bn[0]; out = max(0, t - bn[1]) / 0.25; dy = int(-420 * (1 - ease_out(a / 0.2)) - 420 * ease_out(out))
        bh = 410; g = vgrad('#7FA693', '#3F5E4F', h=bh)
        rnd = random.Random(7); edge = [bh - 30 + rnd.randint(-14, 14) for _ in range(28)]
        m = np.ones((bh, W), np.float32); xs = np.linspace(0, W, len(edge))
        for x in range(W):
            e = int(np.interp(x, xs, edge)); m[e:, x] = 0
        ys0 = max(0, dy); ys1 = min(H, dy + bh)
        if ys1 > ys0:
            sub = m[ys0 - dy:ys1 - dy, :, None]; c[ys0:ys1] = c[ys0:ys1] * (1 - sub) + g[ys0 - dy:ys1 - dy] * sub
            ti = bn[2][:max(0, int((a - 0.1) * 30))] if out == 0 else ''
            if ti:
                box = comp(c, text(ti, 'playfair:800', 86, maxw=860, shadow=(0, 3, 8, 0.35)), 512, dy + 300); self.check(box, 'banner title', t)
            if a > 0.6 and out == 0:
                box = comp(c, text(bn[3], 'spacemono-b', 28, tracking=6, maxw=860), 512, dy + 370, alpha=ease_out((a - 0.6) / 0.2)); self.check(box, 'banner sub', t)

    def t4_scene(self, t, sc, i):
        top, bot = self.pal['chapters'][i % len(self.pal['chapters'])]; c = vgrad(top, bot); a = t - sc['t0']
        noise = np.random.default_rng(i).normal(0, 3, (H, W, 1)).astype(np.float32); c = c + noise
        box = comp(c, text(sc.get('kicker', f'TIP #{i + 1}'), 'spacemono-b', 34, fill='#EAF2F8', tracking=10), 512, 330, alpha=ease_out(a / 0.2)); self.check(box, 'kicker', t, face=False)
        title = sc['title'].upper(); n = max(0, int((a - 0.25) * 40)); shown = title[:n]
        if shown:
            lines, cur = [], ''
            for wd in shown.split(' '):
                cand = (cur + ' ' + wd).strip()
                if font('playfair:800', 70).getlength(cand) > 860 and cur: lines.append(cur); cur = wd
                else: cur = cand
            lines.append(cur)
            for k, ln in enumerate(lines[:3]):
                box = comp(c, text(ln, 'playfair:800', 70, shadow=(0, 3, 8, 0.3), maxw=880), 512, 420 + k * 80); self.check(box, 'chapter title', t, face=False)
        if sc.get('image'):
            card = rounded_card(self.img(sc['image']), 560, 640, r=20); fl = 8 * math.sin(a * 2.2)
            comp(c, card, 540, 900 + fl, scale=0.9 + 0.1 * ease_out((a - 0.15) / 0.3), alpha=ease_out((a - 0.15) / 0.2))
        return c

    # ---------------------------------------------------------------- temp-5 Bold Yellow Creator
    def t5_talk(self, t):
        c = self.base(t); hh = self.head_at(t)
        if hh:
            i, h = hh; a = t - h['label_t']
            box = comp(c, text(h['label'].upper(), 'anton', 36, fill='#F3EFD6', tracking=2, shadow=(0, 2, 6, 0.6), maxw=820), 512, 288, alpha=ease_out(a / 0.15)); self.check(box, 'label', t)
            if t >= h['big_t']:
                b = t - h['big_t']; big = h['big'].upper(); f = font('anton', 160)
                full = text(big, 'anton', 146, fill=self.pal['accent'], glow=(self.pal['accent'], 10, 0.5), shadow=(0, 6, 12, 0.5), maxw=860)
                k = min(len(big), int(b * 30) + 1); frac = k / len(big)
                cut = full.copy(); cut[:, int(full.shape[1] * frac) + (0 if k < len(big) else 999):, 3] = 0
                box = comp(c, cut, 512, 392, blur=1 if k < len(big) else 0); self.check(box, 'big word', t)
        w = self.word_at(t)
        if w:
            box = comp(c, text(w[0].strip(',.').upper(), 'anton', 62, shadow=(0, 4, 10, 0.65)), 512, self.face.box[3] + 85); self.check(box, 'caption', t)
        return c

    def t5_scene(self, t, sc, i):
        a = t - sc['t0']
        if i % 2 == 0:   # white grid page + screenshot card
            c = np.full((H, W, 3), rgb(self.pal['grid_bg']), np.float32)
            for x in range(0, W, 135): c[:, x:x + 2] = (232, 232, 232)
            for y in range(0, H, 135): c[y:y + 2] = (232, 232, 232)
            if sc.get('image'):
                im = self.img(sc['image']); ih, iw = im.shape[:2]; wcard = 860; hcard = min(980, int(wcard * ih / iw))
                card = rounded_card(im, wcard, hcard, r=18); s = (0.9 + 0.1 * ease_out(a / 0.3)) * (1 + 0.03 * a)
                comp(c, card, 540, 760, scale=s)
        else:            # purple grid + phone + iMessage bubble
            p0, p1 = self.pal['purple']; c = vgrad(p0, p1)
            for k in range(-8, 9):
                x0 = 540 + k * 70; cv2.line(c, (x0, 760), (540 + k * 260, H), (110, 120, 255), 2, cv2.LINE_AA)
            for k in range(12): y = int(760 + (H - 760) * (k / 12) ** 1.6); cv2.line(c, (0, y), (W, y), (110, 120, 255), 2, cv2.LINE_AA)
            c = cv2.GaussianBlur(c, (0, 0), 1.2) * 0.85 + c * 0.15
            if sc.get('image'):
                scr = rounded_card(self.img(sc['image']), 460, 920, r=46, border=16, border_col='#111111')
                comp(c, scr, 560, 870 + 30 * (1 - ease_out(a / 0.4)), rot=-6 + 3 * ease_out(a / 0.6), alpha=ease_out(a / 0.25))
            if a > 0.4 and sc.get('title'):
                msg = sc['title']; f = font('inter:600', 40); tw = int(f.getlength(msg)) + 56
                bim = Image.new('RGBA', (min(tw, 860), 92), (0, 0, 0, 0)); ImageDraw.Draw(bim).rounded_rectangle((0, 0, bim.width - 1, 91), 40, fill=rgb(self.pal['bubble']) + (255,))
                comp(c, np.asarray(bim), 512, 330, scale=[0.6, 1.08, 1.0][min(2, int((a - 0.4) * 30))])
                box = comp(c, text(msg, 'inter:600', 40, maxw=800), 512, 330); self.check(box, 'bubble', t, face=False)
        return c

    # ---------------------------------------------------------------- temp-6 Orange Explainer
    def t6_talk(self, t):
        c = self.base(t); ch = self.chunk_at(t, 5, 30)
        if ch:
            ws = [w for w in ch['words'] if w[1] <= t]
            if ws:
                keyi = max(range(len(ch['words'])), key=lambda k: (re.sub(r'\W', '', ch['words'][k][0]).lower() in self.bigset, len(ch['words'][k][0]), k))
                l1 = [w for k, w in enumerate(ch['words']) if k != keyi and w[1] <= t]; l2 = ch['words'][keyi] if ch['words'][keyi][1] <= t else None
                yb = 1246
                if l2:
                    b = t - l2[1]; lay = text(l2[0].strip(',.').upper(), 'montserrat-i:900', 62, grad=(self.pal['accent'], self.pal['accent2']), stroke=3, stroke_fill='#2A1600', shadow=(0, 5, 10, 0.6), maxw=680)  # peak 1.25
                    box = comp(c, lay, 512, yb, anchor='b', scale=1.12 - 0.12 * ease_out(b / 0.12)); self.check(box, 'gold line', t); yb -= 68
                if l1:
                    lay = text(' '.join(w[0].strip(',.') for w in l1).upper(), 'montserrat-i:900', 30, stroke=2, stroke_fill='#1A1A1A', shadow=(0, 4, 8, 0.6), maxw=860)
                    box = comp(c, lay, 512, yb, anchor='b'); self.check(box, 'white line', t)
        return c

    def t6_scene(self, t, sc, i):
        a = t - sc['t0']; c = np.full((H, W, 3), rgb(self.pal['bg']), np.float32)
        for x in range(0, W, 54): c[:, x:x + 2] = rgb(self.pal['grid'])
        for y in range(0, H, 54): c[y:y + 2] = rgb(self.pal['grid'])
        sw = np.zeros((H, W), np.uint8); off = int(120 * math.sin(a * 1.4))
        cv2.ellipse(sw, (900 + off, 140), (520, 210), -28, 0, 360, 255, 120); cv2.ellipse(sw, (120 - off, 1760), (560, 230), -22, 0, 360, 255, 140)
        m = cv2.GaussianBlur(sw.astype(np.float32) / 255, (0, 0), 3)[..., None] * 0.55; c = c * (1 - m) + 255 * m
        box = comp(c, text(sc['title'], 'playfair:800', 80, shadow=(0, 4, 10, 0.35), maxw=860), 512, 380, alpha=ease_out(a / 0.2)); self.check(box, 'title', t, face=False)
        if sc.get('quote'):
            q = sc['quote']; cw, chh = 820, 300; card = Image.new('RGBA', (cw + 40, chh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
            d.rounded_rectangle((28, 34, cw + 28, chh + 34), 28, fill=(0, 0, 0, 70)); card = card.filter(ImageFilter.GaussianBlur(10)); d = ImageDraw.Draw(card)
            d.rounded_rectangle((20, 20, cw + 20, chh + 20), 28, fill=(255, 255, 255, 255)); d.ellipse((52, 52, 122, 122), fill=rgb(self.pal['bg']) + (255,))
            d.text((140, 56), q['name'], font=font('inter:700', 32), fill=(17, 17, 17, 255)); d.text((140, 96), q['handle'], font=font('inter:500', 26), fill=(130, 130, 130, 255))
            shown = q['text'][:max(0, int((a - 0.4) * 45))]; y = 160
            for ln in shown.split('\n'): d.text((52, y), ln, font=font('inter:600', 34), fill=(17, 17, 17, 255)); y += 46
            box = comp(c, np.asarray(card), 540, 800, scale=0.9 + 0.1 * ease_out(a / 0.25)); self.check(box, 'quote card', t, face=False)
        elif sc.get('image'):
            card = rounded_card(self.img(sc['image']), 760, 600, r=24, border=10)
            comp(c, card, 540, 860, scale=0.9 + 0.1 * ease_out(a / 0.25) + 0.02 * a)
        return c

    # ---------------------------------------------------------------- temp-7 SaaS Split
    def _t7_face(self):
        f = self.job['face']; s = 0.92; self.t7 = dict(s=s, oy=650 - f['cap_top'] * s, ox=540 - 540 * s, y0=610)
        return FaceZone.from_head(650, f['chin'] * s + self.t7['oy'], f['x0'] * s + self.t7['ox'], f['x1'] * s + self.t7['ox'])

    def _lavender(self):
        if not hasattr(self, '_lav'):
            c = np.full((H, W, 3), rgb(self.pal['bg']), np.float32); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            for cx, cy, r in ((200, 420, 420), (900, 560, 380), (540, 1500, 500)):
                g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * 0.55
                c = c * (1 - g) + np.array(rgb(self.pal['blob']), np.float32) * g
            self._lav = c
        return self._lav.copy()

    def _t7_word(self, c, t, cy, check_face=True):
        hh = self.head_at(t); w = self.word_at(t)
        if hh and hh[1]['big_t'] <= t < hh[1]['big_t'] + 0.9:
            s, word = hh[1]['big_t'], hh[1]['big']
        elif w: s, word = w[1], w[0].strip(',.')
        else: return
        b = t - s; sc = [0.85, 1.06, 1.0][min(2, int(b * 30))]
        box = comp(c, text(word, 'intertight:800', 120, fill=self.pal['text'], maxw=800), 512, cy, scale=sc); self.check(box, 'kinetic word', t, check_face)

    def t7_talk(self, t):
        c = self._lavender(); p = self.t7; fr = grade(self.shifted(t), self.spec['grade'])
        sw, sh = int(W * p['s']), int(H * p['s']); fr = cv2.resize(fr, (sw, sh), interpolation=cv2.INTER_AREA)
        y0 = p['y0']; src_y0 = int(y0 - p['oy']); hgt = min(H - y0 - 10, sh - src_y0); x0 = int(p['ox'])
        panel = fr[src_y0:src_y0 + hgt]; m = np.zeros((hgt, sw), np.uint8); cv2.rectangle(m, (0, 0), (sw - 1, hgt - 1), 255, -1)
        mm = Image.new('L', (sw, hgt), 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, sw - 1, hgt + 60), 36, fill=255)
        a = np.asarray(mm).astype(np.float32)[..., None] / 255; c[y0:y0 + hgt, x0:x0 + sw] = c[y0:y0 + hgt, x0:x0 + sw] * (1 - a) + panel * a
        self._t7_word(c, t, 440)
        return c

    def t7_scene(self, t, sc, i):
        a = t - sc['t0']; c = self._lavender()
        if sc.get('image'):
            im = self.img(sc['image']); ih, iw = im.shape[:2]; wcard = 900; hcard = min(700, int(wcard * ih / iw))
            comp(c, rounded_card(im, wcard, hcard, r=26), 540, 760, scale=0.94 + 0.06 * ease_out(a / 0.3))
        if sc.get('title'):
            box = comp(c, text(sc['title'], 'intertight:800', 64, fill='#0B0B22', maxw=860), 512, 330, alpha=ease_out(a / 0.2)); self.check(box, 'title', t, face=False)
        w = self.word_at(t)
        if w:
            lay = text(w[0].strip(',.'), 'intertight:800', 54, fill='#FFFFFF'); pim = Image.new('RGBA', (lay.shape[1] - 10, 86), (0, 0, 0, 0))
            ImageDraw.Draw(pim).rounded_rectangle((0, 0, pim.width - 1, 85), 18, fill=rgb(self.pal['accent']) + (255,))
            comp(c, np.asarray(pim), 512, 1190); box = comp(c, lay, 512, 1190); self.check(box, 'word chip', t, face=False)
        return c

    def flash(self, t, t0):
        c = np.full((H, W, 3), rgb(self.pal['accent']), np.float32); hh = self.head_at(t0 + 0.01)
        word = hh[1]['big'] if hh else 'NOW'; b = t - t0
        box = comp(c, text(word, 'intertight:800', 130, maxw=800), 512, 960, scale=[0.85, 1.06, 1.0][min(2, int(b * 30))]); self.check(box, 'flash word', t, face=False)
        return c


# ------------------------------------------------------------------ CLI
def render_range(job, g0, g1, out):
    r = Reel(job); g1 = min(g1, int(job['duration'] * FPS))
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '10', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)   # intermediate part: the final mux re-encodes
    for g in range(g0, g1):
        ff.stdin.write(r.frame(g).tobytes())
        if g % 120 == 0: print(f'temp-{r.n} frame {g}', flush=True)
    ff.stdin.close(); ff.wait()


def full(job, out):
    n = int(job['duration'] * FPS); mid = n // 2; tmp = out + '.parts'; os.makedirs(tmp, exist_ok=True); jp = os.path.join(tmp, 'job.json')
    json.dump(job, open(jp, 'w'))
    ps = [subprocess.Popen([sys.executable, __file__, jp, str(a), str(b), os.path.join(tmp, f'p{k}.mp4')]) for k, (a, b) in enumerate(((0, mid), (mid, n)))]
    for p in ps:
        if p.wait() != 0: raise SystemExit('render failed')
    wav = os.path.join(tmp, 'mix.wav'); build_audio(job, TEMPLATES[int(job['template'])], wav)
    open(os.path.join(tmp, 'parts.txt'), 'w').write("file 'p0.mp4'\nfile 'p1.mp4'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'parts.txt'), '-i', wav, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', '60', '-crf', '17', '-maxrate', '35M', '-bufsize', '70M',
                    '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    job = json.load(open(sys.argv[1]))
    if sys.argv[2] == '--audio': build_audio(job, TEMPLATES[int(job['template'])], sys.argv[3], stems_dir=(sys.argv[4] if len(sys.argv) > 4 else None))
    elif sys.argv[2] == '--full': full(job, sys.argv[3])
    elif sys.argv[4].endswith('.mp4'): render_range(job, int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        os.makedirs(sys.argv[4], exist_ok=True); r = Reel(job)
        for g in [int(x) for x in sys.argv[5].split(',')]:
            Image.fromarray(r.frame(g)).save(os.path.join(sys.argv[4], f't{r.n}_g{g:05d}.png'))
