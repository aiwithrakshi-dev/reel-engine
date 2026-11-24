# /temp-1 Red Kinetic as a job-driven template (no per-reel script needed).
# Talk: his real room (graded, no matte), white label pill + giant red 3D italic keyword in the HEAD band above the cap,
#       one-line 3D white/red English caption in the CAPTION band under the chin, red edge glow, halftone band, glint,
#       pixel blocks, grain. Scene: full cutaway: blurred B-roll backdrop + red-framed B-roll card with push-in,
#       title pill in the HEAD band, caption continues at the bottom.
# Every readable box goes through self.check() (safe zone + face oval). Sizes are checked at their PEAK pop scale.
import math, random
import numpy as np, cv2
from PIL import Image, ImageDraw

W, H, FPS = 1080, 1920, 60
RED = (0xE3, 0x12, 0x1B); RED_DK = (0x7A, 0x03, 0x06); WHITE = (255, 255, 255)
CXS = 512                                   # centre line of the safe box (65..960)


def _red3d_text(txt, font, ext=6, face=(255, 255, 255), side=RED, shadow=110):
    """One line: white face, red stepped extrusion down-right, soft dark shadow. RGBA uint8."""
    asc, desc = font.getmetrics(); tw = int(font.getlength(txt)); pad = ext + 18
    im = Image.new('RGBA', (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((pad + ext + 3, pad + ext + 4), txt, font=font, fill=(0, 0, 0, shadow))
    for k in range(ext, 0, -1): d.text((pad + k * 0.7, pad + k), txt, font=font, fill=side + (255,))
    d.text((pad, pad), txt, font=font, fill=face + (255,))
    return np.asarray(im)


def _pill(txt, font, bg=RED, fg=(255, 255, 255), padx=26, pady=12):
    asc, desc = font.getmetrics(); tw = int(font.getlength(txt)); w = tw + 2 * padx; h = asc + desc + 2 * pady
    im = Image.new('RGBA', (w + 24, h + 28), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 18, 14 + w, 18 + h), h // 2, fill=(0, 0, 0, 90))            # drop shadow
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), h // 2, fill=bg + (255,))
    d.text((10 + padx, 10 + pady - 2), txt, font=font, fill=fg + (255,))
    return np.asarray(im)


def _fit_pill(txt, spec, size, padx=26, pady=12, maxw=780):
    """Pill whose font shrinks until its PEAK (1.12x pop) width fits the safe box (895 px wide)."""
    from template_render import font
    while True:
        pl = _pill(txt, font(spec, size), padx=padx, pady=pady)
        if (pl.shape[1] - 24) <= maxw or size <= 24: return pl
        size -= 2


def _pop(a, n=4):                          # 0 -> overshoot -> 1 over n frames (60 fps)
    seq = [0.0, 0.62, 1.12, 1.0] if n == 4 else [0.0, 0.5, 0.9, 1.12, 1.04, 1.0]
    return seq[min(max(a, 0), len(seq) - 1)] if a < len(seq) else 1.0


class StyleT1:
    # ---------------------------------------------------------------- shared caches
    def _t1(self):
        if hasattr(self, '_t1c'): return self._t1c
        from template_render import font
        fz = self.face; job = self.job
        cap_top = int(job['face']['cap_top']); chin = int(job['face']['chin'])
        head_bottom = cap_top - 26 - int(job.get('punch_px', 0))           # nothing below this in the HEAD band
        c = dict(f_label=font('intertight-i:600', 40), f_cap=font('intertight-i:800', job.get('caption_px', 50)),
                 f_title=font('intertight-i:800', 44), f_kick=font('intertight-i:500', 34),
                 head_bottom=head_bottom, chin=chin)
        # caption band: the line's PEAK (1.12x pop) box starts 6 px under the face zone; bottom edge <= 1248
        sample = _red3d_text('Ag', c['f_cap'], ext=6); half = sample.shape[0] * 1.12 / 2 - 16
        c['cap_cy'] = int(min(1248 - half, self.face.box[3] + half + 6))
        # red edge glow (rim light) — corners/edges only, zero inside an ellipse that covers the head and body
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - 540) / 600) ** 2 + ((yy - 960) / 1050) ** 2)
        g = np.clip((r - 0.92) / 0.35, 0, 1) ** 1.5
        c['glow'] = (g * 0.33)[..., None]; c['glow_col'] = np.array(RED, np.float32)
        self._t1c = c; self._t1_big = {}; self._t1_txt = {}
        return c

    def _t1_bigword(self, txt, avail_h):
        k = (txt, avail_h)
        if k not in self._t1_big:
            from fx import BigWord
            cap = int(min(150, max(84, avail_h)))
            self._t1_big[k] = BigWord(txt, cap, maxw=760)
        return self._t1_big[k]

    def _t1_caption(self, c, t, cy, check_face=True):
        ch = self.chunk_at(t, max_words=7, max_chars=30)
        if not ch: return
        txt = ch['text'] if 'text' in ch else ' '.join(w[0] for w in ch['words'])
        key = ('cap', txt)
        if key not in self._t1_txt: self._t1_txt[key] = _red3d_text(txt, self._t1()['f_cap'], ext=6)
        lay = self._t1_txt[key]
        MAXW = 820                                               # peak (1.12x) footprint must stay inside x 65-960
        if lay.shape[1] > MAXW:                                  # standard size; shrink only an over-long line
            s = MAXW / lay.shape[1]; lay = cv2.resize(lay, (MAXW, int(lay.shape[0] * s)), interpolation=cv2.INTER_AREA)
        a = int(round((t - ch['start']) * FPS)); s = _pop(a)
        from template_render import comp
        # check the PEAK (1.12x) footprint once per line, then draw
        ph, pw = lay.shape[0] * 1.12, lay.shape[1] * 1.12
        peak = (int(CXS - pw / 2 + 18), int(cy - ph / 2 + 16), int(CXS + pw / 2 - 18), int(cy + ph / 2 - 16))
        self.check(peak, 'caption', t, face=check_face)
        comp(c, lay, CXS, cy, scale=s)

    def _t1_headline(self, c, t):
        hh = self.head_at(t)
        if not hh: return
        i, h = hh; C = self._t1(); from template_render import comp
        lab_key = ('lab', h['label'])
        if h.get('label'):
            if lab_key not in self._t1_txt: self._t1_txt[lab_key] = _fit_pill(h['label'], 'intertight-i:600', 40)
            pl = self._t1_txt[lab_key]
        else: pl = None
        ph = (pl.shape[0] - 28) if pl is not None else 0
        top = 282; gap = 20
        avail = C['head_bottom'] - top - (ph + gap if pl is not None else 0) - 14
        bw = self._t1_bigword(h['big'], avail)
        base = C['head_bottom'] - bw.ext - 6                  # baseline of the big word
        cap_top = base - bw.cap
        # label pill sits right above the word (small gap, no floating)
        if pl is not None and t >= h['label_t']:
            a = int(round((t - h['label_t']) * FPS)); s = _pop(a)
            cy = cap_top - gap - ph / 2
            pk = (int(CXS - pl.shape[1] * 1.12 / 2 + 12), int(cy - ph * 1.12 / 2), int(CXS + pl.shape[1] * 1.12 / 2 - 12), int(cy + ph * 1.12 / 2))
            self.check(pk, 'label pill', t)
            comp(c, pl, CXS, cy, scale=s)
        if t >= h['big_t']:
            f30 = (t - h['big_t']) * 30.0
            step = h.get('step', 1.0)
            n = len([L for L in bw.letters if L is not None])
            starts = [int(round(k * step)) for k in range(len(bw.letters))]
            # halftone band behind the word (head band only), 6 frames after the first letter
            j = int((t - h['big_t']) * FPS)
            if 0 <= j < 14: self._t1_halftone(c, j, cap_top, base)
            # glint: a light sweep across the word once it is typed
            peak = (int(CXS - bw.width / 2 - 26), int(cap_top - 14), int(CXS + bw.width / 2 + 30), int(base + bw.ext + 4))
            self.check(peak, 'big word', t)
            bw.draw(c, CXS, base, 0, int(f30), starts=starts)
            done_t = h['big_t'] + (starts[-1] + 2) / 30.0
            if done_t <= t < done_t + 0.35: self._t1_glint(c, (t - done_t) / 0.35, peak)
            if 0 <= j < 10: self._t1_blocks(c, j, peak, seed=i)

    # ---------------------------------------------------------------- overlays (new in the job-driven /temp-1)
    def _t1_halftone(self, c, j, y0, y1):
        """Dot band that blooms out from behind the keyword — confined to the HEAD band (never reaches the cap)."""
        C = self._t1(); top, bot = 276, C['head_bottom'] - 2
        k = j / 14.0; op = 0.55 * math.sin(math.pi * k)
        if op <= 0.02: return
        cy = (y0 + y1) / 2; r_ = 40 + 520 * k
        for yy in range(top + 6, bot, 18):
            for xx in range(80, 948, 18):
                d = math.hypot((xx - CXS) / 1.6, (yy - cy) * 1.9)
                if abs(d - r_) < 70:
                    rad = 2 + 4 * (1 - abs(d - r_) / 70)
                    cv2.circle(c, (xx, yy), int(rad), tuple(float(RED[q] * op + c[yy, xx, q] * (1 - op)) for q in range(3)), -1)

    def _t1_glint(self, c, p, box):
        x0, y0, x1, y1 = box; y0 = max(270, y0); y1 = min(self._t1()['head_bottom'], y1)
        if y1 <= y0: return
        xc = x0 + (x1 - x0 + 200) * p - 100
        xs = np.arange(x0, x1)[None, :]; ys = np.arange(y0, y1)[:, None]
        band = np.clip(1 - np.abs(xs - xc + (ys - y0) * 0.35) / 36, 0, 1)[..., None] * 0.55
        reg = c[y0:y1, x0:x1]; bright = ((reg[..., 0] > 140) & (reg[..., 1] < 110))[..., None]   # only over the red letters
        c[y0:y1, x0:x1] = reg + (255 - reg) * band * bright

    def _t1_blocks(self, c, j, box, seed=0):
        rnd = random.Random(seed * 31 + j // 2); x0, y0, x1, y1 = box; hb = self._t1()['head_bottom']
        cols = [RED, (0xF0, 0x6A, 0x72), (255, 255, 255), (0xAA, 0, 0)]
        for _ in range(4 if j < 6 else 2):
            s = rnd.choice((12, 18, 24, 30)); x = int(rnd.uniform(x0 - 30, x1 + 10) // 6 * 6)
            y = int(rnd.uniform(max(272, y0 - 20), min(hb - s, y1)) // 6 * 6)
            if y + s <= hb and 66 <= x and x + s <= 958: c[y:y + s, x:x + s] = np.array(rnd.choice(cols), np.float32)

    # ---------------------------------------------------------------- talk
    def t1_talk(self, t):
        C = self._t1()
        # the graded room only changes with the SOURCE frame (25-30 fps) and the punch state: cache it (render ~2x faster)
        cuts = self.job.get('punch') or []
        key = (int(t * self.src.fps + 1e-6), sum(1 for x in cuts if x <= t) % 2)
        if getattr(self, '_bkey', None) != key:
            b_ = self.base(t); self._bimg = b_ * (1 - 0.75 * C['glow']) + C['glow_col'] * C['glow']; self._bkey = key
        c = self._bimg.copy()
        self._t1_headline(c, t)
        self._t1_caption(c, t, C['cap_cy'])
        from fx import grain
        grain(c, int(t * FPS), amt=3.0)
        return c

    # ---------------------------------------------------------------- scene (full cutaway)
    def _media(self, path, t_in):
        if path.endswith(('.mp4', '.mov', '.webm')):
            if not hasattr(self, '_vids'): self._vids = {}
            if path not in self._vids:
                from template_render import Source
                fps_ = cv2.VideoCapture(path).get(cv2.CAP_PROP_FPS) or 30
                s = Source(path, fps=fps_); self._vids[path] = s
            s = self._vids[path]; dur = s.n / s.fps
            return s.at(min(t_in, dur - 0.05))
        return self.img(path).astype(np.float32)

    def _t1_shot(self, t, sc):
        """Multi-shot scenes: sc['clips'] = [{image, in, dur, crop, fill, fx}] cut in order; else the scene itself."""
        if not sc.get('clips'): return dict(sc), 0, sc['t0']
        acc = sc['t0']
        for k, c in enumerate(sc['clips']):
            last = k == len(sc['clips']) - 1
            if last or t < acc + c['dur']:
                sh = dict(sc); sh.update(c); sh['dur'] = c.get('dur', sc['t1'] - acc) if not last else sc['t1'] - acc
                return sh, k, acc
            acc += c['dur']

    def t1_scene(self, t, sc, i):
        from template_render import comp, rounded_card
        sh, k, s0 = self._t1_shot(t, sc)
        if sh.get('fill'): return self._t1_fill(t, sc, sh, i, k, s0)
        C = self._t1(); is_vid = sh['image'].endswith(('.mp4', '.mov', '.webm'))
        m = self._media(sh['image'], max(0.0, t - s0) + sh.get('in', 0))
        mkey = (i, k, -1 if not is_vid else int((max(0.0, t - s0) + sh.get('in', 0)) * 30))
        if sh.get('crop'):   # [x0, y0, x1, y1] fractions: zoom the card onto the UI element being named
            x0_, y0_, x1_, y1_ = sh['crop']; hh_, ww_ = m.shape[:2]
            m = m[int(y0_ * hh_):int(y1_ * hh_), int(x0_ * ww_):int(x1_ * ww_)]
        mh, mw = m.shape[:2]
        # backdrop: cover-fit, heavy blur, darkened
        s = max(W / mw, H / mh); bg = cv2.resize(m, (int(mw * s) + 2, int(mh * s) + 2), interpolation=cv2.INTER_AREA)
        oy, ox = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2; bg = bg[oy:oy + H, ox:ox + W]
        if getattr(self, '_skey', None) != mkey:
            c = cv2.GaussianBlur(cv2.resize(bg, (W // 4, H // 4)), (0, 0), 6); c = cv2.resize(c, (W, H))
            if 'dark' not in C:   # near-black stage with a deep red falloff (screenshots are mostly white: keep it dark)
                yy = np.linspace(0, 1, H)[:, None, None]; C['dark'] = (np.array((10, 9, 12), np.float32) * (1 - yy) + np.array((34, 4, 8), np.float32) * yy) * np.ones((1, W, 1), np.float32)
            c = C['dark'] + c * 0.16
            self._sbg = c * (1 - C['glow']) + C['glow_col'] * C['glow']; self._skey = mkey
        c = self._sbg.copy()
        # card: fit inside x 82..942, y 400..1110, push-in over the scene
        p = min(1.0, max(0.0, (t - sc['t0']) / max(0.1, sc['t1'] - sc['t0'])))   # transitions sample outside [t0, t1]
        cw_max, ch_max = 800, 680; ar = mw / mh
        cw, chh = (cw_max, int(cw_max / ar)) if cw_max / ar <= ch_max else (int(ch_max * ar), ch_max)
        ps_ = min(1.0, max(0.0, (t - s0) / max(0.1, (sh['dur'] if 'dur' in sh and sc.get('clips') else sc['t1'] - sc['t0']))))
        if is_vid: z = 1.0 + 0.06 * ps_; dx = 0.0
        else:      # stills get a Ken Burns move: push-in + slow lateral drift (direction alternates per scene)
            z = 1.0 + 0.14 * ps_; dx = (0.5 - ps_) * 0.06 * (1 if (i + k) % 2 else -1)
        crop_w, crop_h = int(mw / z), int(mh / z)
        ox_ = int(np.clip((mw - crop_w) / 2 + dx * mw, 0, mw - crop_w))
        mc = m[(mh - crop_h) // 2:(mh - crop_h) // 2 + crop_h, ox_:ox_ + crop_w]
        key = None
        card = rounded_card(mc, cw, chh, r=30, border=6, border_col='#E3121B', shadow=True)
        a = max(0, int(round((t - sc['t0']) * FPS))); ps = [0.0, 0.62, 1.06, 1.0][min(a, 3)] if a < 4 else 1.0
        if k > 0:   # quick cut inside the scene: 3-frame scale kick instead of a re-pop
            b = int(round((t - s0) * FPS)); ps = [1.04, 1.02, 1.01][b] if 0 <= b < 3 else 1.0
        cy = 755
        pk = (int(CXS - cw * 1.06 / 2 - 6), int(cy - chh * 1.06 / 2 - 6), int(CXS + cw * 1.06 / 2 + 6), int(cy + chh * 1.06 / 2 + 6))
        self.check(pk, 'cutaway card', t, face=False)
        comp(c, card, CXS, cy, scale=ps)
        # title pill (HEAD band) + kicker
        if sh.get('title'):
            k2 = ('ttl', sh['title'])
            if k2 not in self._t1_txt: self._t1_txt[k2] = _fit_pill(sh['title'], 'intertight-i:800', 44, padx=30, pady=14)
            pl = self._t1_txt[k2]; tcy = max(330, cy - chh / 2 - 20 - (pl.shape[0] - 28) / 2)
            same = k > 0 and sc['clips'][k - 1].get('title', sc.get('title')) == sh['title']
            s2 = 1.0 if same else _pop((a - 2) if k == 0 else int(round((t - s0) * FPS)))
            pk = (int(CXS - pl.shape[1] * 1.12 / 2 + 12), int(tcy - (pl.shape[0] - 28) * 1.12 / 2), int(CXS + pl.shape[1] * 1.12 / 2 - 12), int(tcy + (pl.shape[0] - 28) * 1.12 / 2))
            self.check(pk, 'cutaway title', t, face=False)
            comp(c, pl, CXS, tcy, scale=s2)
        if sh.get('credit') and chh <= 600:   # small source credit under the card
            k3 = ('cr', sh['credit'])
            if k3 not in self._t1_txt:
                from template_render import text
                self._t1_txt[k3] = text(sh['credit'], 'intertight-i:500', 26, fill='#FFFFFF', shadow=(2, 2, 3, 0.6))
            box = comp(c, self._t1_txt[k3], CXS, cy + chh / 2 + 30, alpha=0.8); self.check(box, 'credit', t, face=False)
        self._t1_caption(c, t, C['cap_cy'], check_face=False)
        from fx import grain
        grain(c, int(t * FPS), amt=3.0)
        return c

    def _t1_fill(self, t, sc, sh, i, k, s0):
        """Full-bleed B-roll: the clip covers the whole 1080x1920 frame (cover-fit, focus fx/fy), slow push-in,
        dark top/bottom gradients so the title pill (HEAD band) and the caption stay readable."""
        from template_render import comp, text
        C = self._t1(); is_vid = sh['image'].endswith(('.mp4', '.mov', '.webm'))
        tin = max(0.0, t - s0) + sh.get('in', 0)
        m = self._media(sh['image'], tin)
        if sh.get('crop'):
            x0_, y0_, x1_, y1_ = sh['crop']; hh_, ww_ = m.shape[:2]
            m = m[int(y0_ * hh_):int(y1_ * hh_), int(x0_ * ww_):int(x1_ * ww_)]
        mh, mw = m.shape[:2]
        dur_ = sh['dur'] if sc.get('clips') else sc['t1'] - sc['t0']
        ps_ = min(1.0, max(0.0, (t - s0) / max(0.1, dur_)))
        z = (1.0 + 0.08 * ps_) if is_vid else (1.0 + 0.16 * ps_)
        s = max(W / mw, H / mh) * z
        bw, bh = int(mw * s) + 2, int(mh * s) + 2
        fx, fy = sh.get('fx', 0.5), sh.get('fy', 0.5)
        if not is_vid: fx = fx + (0.5 - ps_) * 0.08 * (1 if (i + k) % 2 else -1)
        ox = int(np.clip(fx * bw - W / 2, 0, bw - W)); oy = int(np.clip(fy * bh - H / 2, 0, bh - H))
        # resize only the visible window (faster than resizing the whole cover image)
        x0s, y0s = ox / s, oy / s; ws, hs = W / s, H / s
        win = m[int(y0s):int(np.ceil(y0s + hs)) + 1, int(x0s):int(np.ceil(x0s + ws)) + 1]
        c = cv2.resize(win, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        if 'fillgrad' not in C:
            yy = np.linspace(0, 1, H)[:, None, None]
            g = np.clip(1 - yy / 0.26, 0, 1) ** 1.6 * 0.72 + np.clip((yy - 0.55) / 0.45, 0, 1) ** 1.4 * 0.78
            C['fillgrad'] = (1 - g).astype(np.float32)
        c = c * 0.92 * C['fillgrad']
        c = c * (1 - C['glow']) + C['glow_col'] * C['glow']
        b = int(round((t - s0) * FPS))
        if k > 0 and 0 <= b < 3:   # quick cut: 3-frame zoom kick
            zk = [1.05, 1.025, 1.01][b]; cc = cv2.resize(c, (int(W * zk), int(H * zk)))
            oy2, ox2 = (cc.shape[0] - H) // 2, (cc.shape[1] - W) // 2; c = cc[oy2:oy2 + H, ox2:ox2 + W]
        a = max(0, int(round((t - sc['t0']) * FPS)))
        if sh.get('title'):
            k2 = ('ttl', sh['title'])
            if k2 not in self._t1_txt: self._t1_txt[k2] = _fit_pill(sh['title'], 'intertight-i:800', 44, padx=30, pady=14)
            pl = self._t1_txt[k2]; tcy = 352
            same = k > 0 and sc['clips'][k - 1].get('title', sc.get('title')) == sh['title']
            s2 = 1.0 if same else _pop((a - 2) if k == 0 else b)
            pk = (int(CXS - pl.shape[1] * 1.12 / 2 + 12), int(tcy - (pl.shape[0] - 28) * 1.12 / 2), int(CXS + pl.shape[1] * 1.12 / 2 - 12), int(tcy + (pl.shape[0] - 28) * 1.12 / 2))
            self.check(pk, 'cutaway title', t, face=False)
            comp(c, pl, CXS, tcy, scale=s2)
        if sh.get('credit'):
            k3 = ('cr', sh['credit'])
            if k3 not in self._t1_txt: self._t1_txt[k3] = text(sh['credit'], 'intertight-i:500', 26, fill='#FFFFFF', shadow=(2, 2, 3, 0.6))
            box = comp(c, self._t1_txt[k3], CXS, 412, alpha=0.75); self.check(box, 'credit', t, face=False)
        self._t1_caption(c, t, C['cap_cy'], check_face=False)
        from fx import grain
        grain(c, int(t * FPS), amt=3.0)
        return c
