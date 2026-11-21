"""Templates /temp-8 ... /temp-16 (second reference batch). Mixed into template_render.Reel.

Every method returns a float RGB canvas (H, W, 3). Readable boxes go through self.check(box, what, t, face=<zone|bool>),
which stops the render if a box leaves the safe zone or touches the face oval of the layout in use.
Shared layout helpers:
  fit(t, s, cap_y)          A-roll scaled by s with his cap at cap_y, blurred room fill around it  -> canvas, zone
  card_frame(...)           A-roll crop as a rounded card (PiP / polaroid / dome)                   -> RGBA, zone
"""
import math, re, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from face_guard import FaceZone

W, H = 1080, 1920


def _tr():  # late import (template_render imports this module)
    import template_render as T
    return T


def squeeze(lay, k):
    """Condensed look: scale an RGBA text layer horizontally."""
    h, w = lay.shape[:2]
    return np.asarray(Image.fromarray(lay).resize((max(1, int(w * k)), h), Image.BICUBIC))


def outline_text(s, spec, size, col, width=4, maxw=None):
    T = _tr(); f = T.font(spec, size)
    while maxw and f.getlength(s) > maxw and size > 30: size = int(size * 0.94); f = T.font(spec, size)
    asc, desc = f.getmetrics(); pad = width + 20; w = int(f.getlength(s)) + 2 * pad; h = asc + desc + 2 * pad
    m1 = Image.new('L', (w, h), 0); ImageDraw.Draw(m1).text((pad, pad), s, font=f, fill=255, stroke_width=width, stroke_fill=255)
    m2 = Image.new('L', (w, h), 0); ImageDraw.Draw(m2).text((pad, pad), s, font=f, fill=255)
    a = np.clip(np.asarray(m1).astype(np.int16) - np.asarray(m2), 0, 255).astype(np.uint8)
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = T.rgb(col); out[..., 3] = a; return out


def rrect(w, h, r, fill, border=0, border_col=(255, 255, 255, 255), shadow=0):
    pad = 30 if shadow else 0; im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad + 4, pad + 12, pad + w + 4, pad + h + 12), r, fill=shadow)
        sl = Image.new('RGBA', im.size, (0, 0, 0, 0)); sl.putalpha(sh.filter(ImageFilter.GaussianBlur(14))); im = Image.alpha_composite(im, sl)
    d = ImageDraw.Draw(im)
    if border: d.rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, fill=border_col); d.rounded_rectangle((pad + border, pad + border, pad + w - 1 - border, pad + h - 1 - border), max(1, r - border), fill=fill)
    else: d.rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, fill=fill)
    return np.asarray(im)


def blob_page(base, blobs):
    T = _tr(); c = np.full((H, W, 3), T.rgb(base), np.float32); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for cx, cy, r, col, a in blobs:
        g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * a
        c = c * (1 - g) + np.array(T.rgb(col), np.float32) * g
    return c


def pop(b, a=0.55, over=1.1):
    if b < 0: return 0.0
    if b < 0.08: return a + (over - a) * b / 0.08
    if b < 0.16: return over + (1 - over) * (b - 0.08) / 0.08
    return 1.0


class StylesB:
    # ------------------------------------------------------------- shared helpers
    def _cache(self, key, fn):
        if not hasattr(self, '_kc'): self._kc = {}
        if key not in self._kc: self._kc[key] = fn()
        return self._kc[key].copy() if isinstance(self._kc[key], np.ndarray) else self._kc[key]

    def zone_of(self, s, ox, oy):
        """Face oval of the job face after scaling the shifted frame by s and moving its origin to (ox, oy)."""
        f = self.job['face']
        return FaceZone.from_head(oy + f['cap_top'] * s, oy + f['chin'] * s, ox + f['x0'] * s, ox + f['x1'] * s)

    def fit(self, t, s, cap_y, darken=0.55):
        T = _tr(); src = T.grade(self.shifted(t), self.spec['grade']); f = self.job['face']
        sw, sh = int(W * s), int(H * s); fr = cv2.resize(src, (sw, sh), interpolation=cv2.INTER_AREA)
        ox, oy = (W - sw) // 2, int(round(cap_y - f['cap_top'] * s))
        bg = cv2.GaussianBlur(cv2.resize(src[0:int(H * 0.55)], (W, H)), (0, 0), 28) * darken
        key = ('fitmask', sw, sh, oy)
        def mk():
            m = np.ones((sh, sw), np.float32); r = np.linspace(0, 1, 50)
            m[:, :50] *= r[None, :]; m[:, -50:] *= r[::-1][None, :]
            if oy > 0: m[:60] *= np.linspace(0, 1, 60)[:, None]
            return m[..., None]
        m = self._cache(key, mk)
        y0, y1 = max(0, oy), min(H, oy + sh); sy0 = y0 - oy
        sub = fr[sy0:sy0 + (y1 - y0)]; mm = m[sy0:sy0 + (y1 - y0)]
        bg[y0:y1, ox:ox + sw] = bg[y0:y1, ox:ox + sw] * (1 - mm) + sub * mm
        return bg, self.zone_of(s, ox, oy)

    def crop_card(self, t, x0, y0, x1, y1, w, r=30, border=0, border_col=(255, 255, 255, 255), label=None, label_h=0):
        """Rounded card of the shifted frame region (x0..x1, y0..y1) scaled to width w (+ optional bottom label strip)."""
        T = _tr(); src = T.grade(self.shifted(t), self.spec['grade'])
        k = w / (x1 - x0); h = int((y1 - y0) * k); im = cv2.resize(src[y0:y1, x0:x1], (w, h), interpolation=cv2.INTER_AREA)
        b = border; tot_h = h + 2 * b + label_h
        card = Image.new('RGBA', (w + 2 * b, tot_h), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, w + 2 * b - 1, tot_h - 1), r, fill=border_col if b or label_h else (0, 0, 0, 0))
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), max(4, r - b), fill=255)
        p = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).convert('RGBA'); p.putalpha(m); card.alpha_composite(p, (b, b))
        if label:
            lay = T.text(label, 'inter:700', 38, fill='#111111'); lp = Image.fromarray(lay)
            card.alpha_composite(lp, (int((w + 2 * b - lp.width) / 2), int(h + b + (label_h - lp.height) / 2)))
        return np.asarray(card), k

    def words_line(self, c, t, ch, cy, spec, size, fill, key_spec=None, key_size=None, key_fill=None, key_box=None,
                   zone=True, shadow=(0, 3, 8, 0.55), maxw=860, what='caption', upper=False):
        """One caption line, words appear on their own start time; keywords (headline words) get the key style."""
        T = _tr(); items = []
        for w, s, e in ch['words']:
            if t < s: break
            word = w.strip(',.!?'); word = word.upper() if upper else word
            key = re.sub(r'\W', '', w).lower() in self.bigset and key_spec
            lay = T.text(word, key_spec if key else spec, key_size if key else size,
                         fill=(key_fill if key else fill) if not (key and isinstance(key_fill, tuple)) else '#FFFFFF',
                         grad=key_fill if key and isinstance(key_fill, tuple) else None, shadow=None if key and key_box else shadow)
            pd = int((key_size if key else size) * 0.45); items.append((lay, s, pd, bool(key)))
        if not items: return
        gap = int(size * 0.28); ws = [l.shape[1] - 2 * pd for l, _, pd, _ in items]; tot = sum(ws) + gap * (len(ws) - 1)
        sc = min(1.0, maxw / max(1, tot)); x = 512 - tot * sc / 2
        for (lay, s, pd, key), wd in zip(items, ws):
            a = T.ease_out((t - s) / 0.1)
            if key and key_box:
                bw, bh = int(wd * sc + 26), int(size * sc * 1.25); grow = T.ease_out((t - s) / 0.18)
                box = rrect(max(2, int(bw * grow)), bh, 10, key_box); T.comp(c, box, x - 13, cy, anchor='l')
            box = T.comp(c, lay, x - pd * sc, cy, scale=sc, anchor='l', alpha=a); self.check(box, what, t, face=zone)
            x += (wd + gap) * sc

    def dock(self, c, t, items, cy, glass=True, dark=False, zone=True):
        """Row of icon tiles popping in at their times on a frosted (or dark pill) tray. items: [{t, label, color, image?}]"""
        T = _tr(); live = [it for it in items if it['t'] <= t]
        if not live: return False
        n = len(items); tile, gap = 92, 20; full_w = n * tile + (n - 1) * gap + 48
        grow = T.ease_out((t - items[0]['t'] + 0.15) / 0.25); tw = max(60, int(full_w * grow)); th = tile + 36
        x0, y0 = int(512 - tw / 2), int(cy - th / 2)
        if dark:
            T.comp(c, rrect(tw, th, th // 2, (20, 22, 30, 240), border=2, border_col=(70, 76, 96, 255)), 512, cy)
        elif glass:
            reg = c[y0:y0 + th, x0:x0 + tw].copy(); reg = cv2.GaussianBlur(reg, (0, 0), 16) * 0.82 + 255 * 0.14
            m = Image.new('L', (tw, th), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, tw - 1, th - 1), 30, fill=255)
            m = np.asarray(m).astype(np.float32)[..., None] / 255; c[y0:y0 + th, x0:x0 + tw] = c[y0:y0 + th, x0:x0 + tw] * (1 - m) + reg * m
            T.comp(c, rrect(tw, th, 30, (0, 0, 0, 0), border=2, border_col=(255, 255, 255, 110)), 512, cy)
        x = 512 - (n * tile + (n - 1) * gap) / 2 + tile / 2
        for it in items:
            if it['t'] <= t:
                s = pop(t - it['t'])
                if it.get('image'):
                    lay = T.rounded_card(self.img(it['image']), tile, tile, r=22, shadow=False)
                else:
                    col = T.rgb(it.get('color', '#333333')); hi = tuple(min(255, v + 50) for v in col)
                    im = Image.new('RGBA', (tile, tile), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle((0, 0, tile - 1, tile - 1), 22, fill=col + (255,)); d.rounded_rectangle((4, 4, tile - 5, tile // 2), 18, fill=hi + (70,))
                    lab = T.text(it['label'], 'intertight:800', 46); lp = Image.fromarray(lab)
                    im.alpha_composite(lp, ((tile - lp.width) // 2, (tile - lp.height) // 2)); lay = np.asarray(im)
                box = T.comp(c, lay, x, cy, scale=s); self.check(box, 'dock icon', t, face=zone)
            x += tile + gap
        return True

    def word_for(self, t, hold=0.0):
        w = self.word_at(t)
        if w: return w
        prev = [x for x in self.words if x[2] <= t and t - x[2] < hold]
        return prev[-1] if prev else None

    # ============================================================= /temp-8 Warm Cinematic (t-8)
    def _t8_zoom(self, t):
        hh = self.head_at(t); return 1.1 if (hh and hh[0] % 2 == 1 and t >= hh[1]['big_t']) else 1.0

    def t8_talk(self, t):
        T = _tr(); c = self.base(t); s = self._t8_zoom(t); zone = self.face
        if s != 1.0:
            M = np.float32([[s, 0, 540 * (1 - s)], [0, s, 380 * (1 - s)]]); c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
            f = self.face; zone = FaceZone(540 + (f.cx - 540) * s, 380 + (f.cy - 380) * s, (f.rx - f.m) * s, (f.ry - f.m) * s, f.m)
        hh = self.head_at(t)
        if hh:
            i, h = hh; x = 92
            for k, w in enumerate(h['label'].split()):
                ws = h['label_t'] + 0.12 * k
                if t < ws: break
                a = T.ease_out((t - ws) / 0.18); lay = T.text(w, 'inter:600', 64, shadow=(0, 3, 10, 0.5))
                box = T.comp(c, lay, x - 29, 318, anchor='l', alpha=a, blur=int((1 - a) * 9)); self.check(box, 'headline', t, face=zone)
                x += lay.shape[1] - 58 + 18
            if t >= h['big_t']:
                a = T.ease_out((t - h['big_t']) / 0.2)
                lay = T.text(h['big'].title() if len(h['big']) > 3 else h['big'], 'inter:700', 112, grad=('#FFD36A', '#F0782A'), shadow=(0, 4, 12, 0.45), maxw=840)
                box = T.comp(c, lay, 92 - 50, 410, anchor='l', alpha=a, blur=int((1 - a) * 10)); self.check(box, 'headline big', t, face=zone)
        w = self.word_at(t)
        if w and not (hh and t >= hh[1]['big_t'] and re.sub(r'\W', '', w[0]).lower() in self.bigset):
            cy = min(zone.box[3] + 44, 1222)
            box = T.comp(c, T.text(w[0].strip(',.').lower(), 'inter:600', 36, shadow=(0, 3, 8, 0.6)), 512, cy); self.check(box, 'caption', t, face=zone)
        return c

    def t8_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']; c = self._cache('t8bg', lambda: blob_page('#1D1D1F', [(540, 700, 600, '#2A2A2D', 0.8)]))
        if sc.get('items'):
            for k, it in enumerate(sc['items']):
                ts = 0.25 + 0.45 * k
                if a < ts: break
                n = min(len(it), int((a - ts) * 40)); y = 340 + 84 * k
                box_l = rrect(40, 40, 6, (0, 0, 0, 0), border=4, border_col=(240, 240, 240, 255)); T.comp(c, box_l, 150, y)
                if a - ts > 0.15:
                    cv2.line(c, (138, y), (148, y + 10), (240, 240, 240), 5, cv2.LINE_AA); cv2.line(c, (148, y + 10), (166, y - 12), (240, 240, 240), 5, cv2.LINE_AA)
                if n: box = T.comp(c, T.text(it[:n], 'inter:500', 60), 186, y, anchor='l'); self.check(box, 'checklist', t, face=False)
            top = 340 + 84 * len(sc['items']) + 20
        else:
            if sc.get('image'):
                card = T.rounded_card(self.img(sc['image']), 860, 460, r=26); T.comp(c, card, 540, 560, scale=0.94 + 0.06 * T.ease_out(a / 0.3))
            top = 820
        pip, k = self.crop_card(t, 250, 420, 830, 1140, 460 if sc.get('items') else 380, r=34)
        h = pip.shape[0]; cy = min(1250 - h / 2 - 10, top + h / 2); s = 0.9 + 0.1 * T.ease_out(a / 0.3)
        T.comp(c, pip, 540, cy, scale=s)
        return c

    # ============================================================= /temp-9 Peach Premium (t-9)
    def t9_talk(self, t):
        T = _tr(); c = self.base(t); tiles = self.job.get('tiles') or []
        if tiles and tiles[0]['t'] <= t <= tiles[-1]['t'] + 1.4:
            y = min(self.face.box[3] + 64, 1188)
            n = len(tiles); x = 512 - (n * 88 + (n - 1) * 18) / 2 + 44
            for it in tiles:
                if it['t'] <= t:
                    im = Image.new('RGBA', (88, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle((0, 8, 87, 95), 18, fill=(150, 46, 6, 255)); d.rounded_rectangle((0, 0, 87, 86), 18, fill=(242, 106, 33, 255))
                    d.rounded_rectangle((5, 5, 82, 40), 14, fill=(255, 160, 90, 120))
                    lab = Image.fromarray(T.text(it['label'], 'playfair:800', 54)); im.alpha_composite(lab, ((88 - lab.width) // 2, (86 - lab.height) // 2))
                    box = T.comp(c, np.asarray(im), x, y, scale=pop(t - it['t'], 0.55, 1.06)); self.check(box, 'number tile', t)
                x += 106
            return c
        ch = self.chunk_at(t, 3, 22)
        if ch: self.words_line(c, t, ch, min(self.face.box[3] + 70, 1200), 'inter:800', 46, '#FFFFFF', 'playfair-i:700', 58, '#FF7A2E')
        return c

    def t9_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']
        c = self._cache('t9bg', lambda: blob_page('#FFF6F0', [(180, 520, 420, '#FFD2B8', 0.9), (930, 1350, 520, '#FFB58E', 0.8), (700, 300, 300, '#FFE6D6', 0.6)]))
        if sc.get('title'):
            x = 512 + 120 * (1 - T.ease_out(a / 0.35))
            box = T.comp(c, T.text(sc['title'], 'inter:700', 66, fill='#141414', maxw=860), x, 430, alpha=T.ease_out(a / 0.25), blur=int(max(0, 1 - a / 0.3) * 10))
            self.check(box, 'title', t, face=False)
        if sc.get('items'):
            spots = [(340, 640, -4), (720, 800, 3), (360, 970, 2), (720, 1130, -3)]
            for k, it in enumerate(sc['items'][:4]):
                ts = 0.35 + 0.3 * k
                if a < ts: continue
                lab = T.text(it, 'inter:600', 50, fill='#1A1A1A', maxw=420); cw = lab.shape[1] + 6; card = rrect(cw, 124, 22, (255, 255, 255, 250), shadow=70)
                x, y, r = spots[k]; y += 10 * math.sin(a * 1.6 + k); s = pop(a - ts, 0.7, 1.06)
                T.comp(c, card, x, y, scale=s, rot=r); box = T.comp(c, lab, x, y, scale=s, rot=r); self.check(box, 'shortcut card', t, face=False)
        elif sc.get('image'):
            if sc.get('kicker'):
                box = T.comp(c, T.text(sc['kicker'].upper(), 'inter:800', 30, fill='#F26B1D', tracking=3, maxw=860), 512, 560); self.check(box, 'kicker', t, face=False)
            T.comp(c, T.rounded_card(self.img(sc['image']), 820, 560, r=26), 540, 900, scale=0.92 + 0.08 * T.ease_out(a / 0.35))
        return c

    # ============================================================= /temp-10 Card Stage (t-10)
    def _t10_bg(self, t):
        T = _tr(); c = self._cache('t10bg', lambda: blob_page('#F7F6FA', [(900, 300, 380, '#EDE3FF', 0.7)]))
        hh = self.head_at(t)
        if hh and t >= hh[1]['big_t']:
            lay = outline_text(hh[1]['big'].lower(), 'intertight:900', 240, self.pal['accent'], width=5, maxw=840)
            box = T.comp(c, lay, 540, 700, alpha=0.32 * T.ease_out((t - hh[1]['big_t']) / 0.3)); self.check(box, 'outline word', t, face=False)  # behind the card
        if self.job.get('brand') and not self.scene_at(t):
            T.comp(c, rrect(54, 54, 12, T.rgb(self.pal['brand']) + (255,)), 120, 312)
            box = T.comp(c, T.text(self.job['brand'], 'intertight:800', 46, fill='#151515'), 156, 312, anchor='l'); self.check(box, 'brand', t, face=False)
        return c

    def t10_talk(self, t):
        T = _tr(); c = self._t10_bg(t)
        card, k = self.crop_card(t, 60, 330, 1020, 1660, 860, r=46)
        oy = 384; T.comp(c, card, 540, oy + card.shape[0] / 2)
        zone = self.zone_of(k, 540 - 430 - 60 * k, oy - 330 * k)
        ch = self.chunk_at(t, 3, 20)
        if ch: self.words_line(c, t, ch, min(zone.box[3] + 60, 1210), 'inter:700', 42, '#FFFFFF', 'intertight:800', 50, ('#E07BFF', '#7B2CFF'), zone=zone)
        return c

    def t10_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']; c = self._t10_bg(t)
        if sc.get('image'):
            card = T.rounded_card(self.img(sc['image']), 860, 300, r=24)
            T.comp(c, card, 540, 470 - 40 * (1 - T.ease_out(a / 0.3)), alpha=T.ease_out(a / 0.2))
        dome, k = self.crop_card(t, 140, 420, 940, 1220, 560, r=0)
        dh, dw = dome.shape[:2]; m = Image.new('L', (dw, dh), 0); ImageDraw.Draw(m).ellipse((0, 0, dw - 1, dw - 1), fill=255)
        ImageDraw.Draw(m).rectangle((0, dw // 2, dw - 1, dh - 1), fill=255); dome = dome.copy(); dome[..., 3] = np.minimum(dome[..., 3], np.asarray(m))
        top = 640 + 60 * (1 - T.ease_out(a / 0.3)); T.comp(c, dome, 540, top + dh / 2)
        zone = self.zone_of(k, 540 - dw / 2 - 140 * k, top - 420 * k)
        ch = self.chunk_at(t, 3, 20)
        if ch: self.words_line(c, t, ch, min(zone.box[3] + 40, 1222), 'inter:700', 38, '#FFFFFF', 'intertight:800', 46, ('#E07BFF', '#7B2CFF'), zone=zone)
        return c

    # ============================================================= /temp-11 Green Terminal (t-11)
    def _t11_bg(self):
        def mk():
            c = blob_page('#040605', [(540, 520, 460, '#0E4A1A', 0.75)])
            for y in range(14, H, 28):
                for x in range(14, W, 28): c[y:y + 2, x:x + 2] = c[y:y + 2, x:x + 2] * 0.4 + np.array((40, 120, 55)) * 0.6
            return c
        return self._cache('t11bg', mk)

    def _t11_layout(self, c, t):
        T = _tr(); card, k = self.crop_card(t, 180, 440, 900, 1150, 600, r=28, border=3, border_col=(60, 200, 90, 255))
        top = 1250 - card.shape[0]; T.comp(c, card, 540, top + card.shape[0] / 2)
        return self.zone_of(k, 540 - card.shape[1] / 2 + 3 - 180 * k, top + 3 - 440 * k)

    def _t11_big(self, c, t, h):
        T = _tr(); b = t - h['big_t']; big = h['big']
        if h.get('stamp'):
            lay = T.text(big, 'intertight:900', 92, maxw=700); bw, bh = lay.shape[1] - 30, lay.shape[0] - 70
            st = rrect(bw, bh, 14, (229, 50, 45, 245), border=6, border_col=(255, 120, 110, 255))
            s = 1.0 + 0.8 * (1 - T.ease_out(b / 0.12)); T.comp(c, st, 512, 478, scale=s, rot=7, alpha=T.ease_out(b / 0.06))
            box = T.comp(c, lay, 512, 478, scale=s, rot=7, alpha=T.ease_out(b / 0.06)); self.check(box, 'stamp', t, face=False)
        elif re.search(r'\d', big):
            shown = big if b > 0.45 else ''.join(str((int(b * 37) + 3 * k) % 10) if ch.isdigit() else ch for k, ch in enumerate(big))
            lay = T.text(shown, 'intertight:900', 150, fill='#36F06A', glow=('#22FF55', 18, 0.9), maxw=820)
            if b < 0.45: lay = cv2.blur(lay, (1, 25))
            box = T.comp(c, lay, 512, 480); self.check(box, 'counter', t, face=False)
        else:
            lay = T.text(big.lower(), 'playfair-i:700', 118, fill='#3BFF6A', glow=('#1FFF4F', 16, 0.8), maxw=820)
            box = T.comp(c, lay, 512, 480, scale=pop(b, 0.8, 1.06)); self.check(box, 'accent', t, face=False)

    def t11_talk(self, t):
        T = _tr(); c = self._t11_bg(); zone = self._t11_layout(c, t); hh = self.head_at(t)
        if hh:
            i, h = hh; box = T.comp(c, T.text(h['label'], 'inter:800', 50, maxw=840), 512, 330, alpha=T.ease_out((t - h['label_t']) / 0.12))
            self.check(box, 'label', t, face=zone)
            if t >= h['big_t']: self._t11_big(c, t, h)
        w = self.word_at(t)
        if w:
            box = T.comp(c, T.text(w[0].strip(',.'), 'inter:700', 42, shadow=(0, 3, 8, 0.6)), 512, 612)
            self.check(box, 'caption', t, face=zone)
        return c

    def t11_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']
        if sc.get('stat'):
            c = self._cache('t11cream', lambda: blob_page('#F2EEE6', [(540, 900, 600, '#FBF8F2', 0.8)]))
            st = sc['stat']; m = re.match(r'(\D*)(\d+)(.*)', st)
            shown = st if not m or a > 0.6 else f"{m.group(1)}{int(int(m.group(2)) * T.ease_out(a / 0.6))}{m.group(3)}"
            box = T.comp(c, T.text(shown, 'intertight:900', 230, fill='#E23B2E', maxw=860), 512, 560); self.check(box, 'stat', t, face=False)
            if sc.get('title'):
                box = T.comp(c, T.text(sc['title'], 'playfair-i:700', 76, fill='#C8281E', maxw=860), 512, 760, alpha=T.ease_out((a - 0.3) / 0.2)); self.check(box, 'stat title', t, face=False)
            if sc.get('sub'):
                box = T.comp(c, T.text(sc['sub'], 'inter:500', 34, fill='#555555', maxw=860), 512, 850, alpha=T.ease_out((a - 0.5) / 0.2)); self.check(box, 'stat sub', t, face=False)
            return c
        c = self._t11_bg(); zone = self._t11_layout(c, t)
        if sc.get('image'):
            card = T.rounded_card(self.img(sc['image']), 860, 280, r=22, border=3, border_col='#3BE070')
            T.comp(c, card, 540, 430, scale=0.92 + 0.08 * T.ease_out(a / 0.25))
        w = self.word_at(t)
        if w: box = T.comp(c, T.text(w[0].strip(',.'), 'inter:700', 42, shadow=(0, 3, 8, 0.6)), 512, 612); self.check(box, 'caption', t, face=zone)
        return c

    # ============================================================= /temp-12 Cream Editorial (t-12)
    def _t12_panel(self, c, t, zone):
        T = _tr(); ph = 640
        c[:ph] = self._cache('t12panel', lambda: blob_page('#E7DCCF', [(540, 300, 500, '#EFE6DA', 0.8)])[:ph])
        c[ph:ph + 14] *= np.linspace(0.75, 1, 14)[:, None, None]
        hh = self.head_at(t)
        if hh and t >= hh[1]['big_t'] and t - hh[1]['big_t'] < 1.3:
            lay = squeeze(T.text(hh[1]['big'].upper(), 'playfair-i:800', 150, grad=('#FFB09A', '#E8603C'), maxw=1100), 0.7)
            box = T.comp(c, lay, 512, 440, scale=pop(t - hh[1]['big_t'], 0.85, 1.05)); self.check(box, 'big word', t, face=zone)
        if self.job.get('mascot'):
            T.comp(c, T.rounded_card(self.img(self.job['mascot']), 200, 200, r=20, shadow=False), 540, 400)
        w = self.word_for(t, 0.25)
        if w:
            lay = squeeze(T.text(w[0].strip(',.').upper(), 'playfair-i:800', 84, fill='#141414', maxw=1150), 0.7)
            box = T.comp(c, lay, 512, 575); self.check(box, 'caption', t, face=zone)

    def t12_talk(self, t):
        c, zone = self.fit(t, 0.8, 690, darken=0.5); self._t12_panel(c, t, zone); return c

    def t12_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']; c = self._cache('t12dark', lambda: blob_page('#111111', [(540, 760, 520, '#1E1B19', 0.9)]))
        if sc.get('image'):
            T.comp(c, T.rounded_card(self.img(sc['image']), 860, 560, r=22), 540, 720 - 30 * (1 - T.ease_out(a / 0.3)), alpha=T.ease_out(a / 0.2))
        w = self.word_for(t, 0.25)
        if w:
            lay = squeeze(T.text(w[0].strip(',.').upper(), 'playfair-i:800', 96, maxw=1150), 0.7)
            box = T.comp(c, lay, 512, 1110); self.check(box, 'caption', t, face=False)
        return c

    # ============================================================= /temp-13 Kanglish Tech Split (t-13)
    def _t13_chip(self, c, t, zone, cy):
        T = _tr(); ch = self.chunk_at(t, 4, 26)
        if not ch: return
        s = ' '.join(w[0].strip(',.!?') for w in ch['words'] if w[1] <= t).upper()
        if not s: return
        lay = T.text(s, 'inter:800', 32, maxw=820); bw = lay.shape[1] - 2 * int(32 * 0.45) + 28
        T.comp(c, rrect(bw, 52, 6, T.rgb(self.pal['chip']) + (235,)), 512, cy)
        box = T.comp(c, lay, 512, cy); self.check(box, 'caption chip', t, face=zone)

    def t13_talk(self, t):
        T = _tr(); c, zone = self.fit(t, 0.8, 700, darken=0.45); hh = self.head_at(t)
        panel = rrect(900, 370, 30, (10, 14, 28, 235), border=2, border_col=(52, 62, 100, 255)); T.comp(c, panel, 540, 470)
        if hh:
            i, h = hh; box = T.comp(c, T.text(h['label'].upper(), 'inter:700', 34, fill='#9FB2FF', tracking=2, maxw=820), 512, 360); self.check(box, 'label', t, face=zone)
            if t >= h['big_t']:
                lay = T.text(h['big'].lower(), 'intertight:900', 130, glow=('#8A5CFF', 22, 0.9), maxw=820)
                box = T.comp(c, lay, 512, 490, scale=pop(t - h['big_t'], 0.8, 1.06)); self.check(box, 'neon word', t, face=zone)
        self._t13_chip(c, t, zone, min(zone.box[3] + 30, 1218))
        return c

    def t13_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']
        def mk():
            c = blob_page('#090D19', [(540, 700, 560, '#121A33', 0.9)])
            for x in range(0, W, 64): c[:, x:x + 1] = (26, 34, 60)
            for y in range(0, H, 64): c[y:y + 1] = (26, 34, 60)
            return c
        c = self._cache('t13grid', mk)
        if sc.get('image'):
            T.comp(c, T.rounded_card(self.img(sc['image']), 880, 700, r=28, border=6, border_col='#FFFFFF'), 540, 720)
        if sc.get('title'):
            box = T.comp(c, T.text(sc['title'], 'inter:800', 52, maxw=860), 512, 1130, alpha=T.ease_out(a / 0.2)); self.check(box, 'title', t, face=False)
        self._t13_chip(c, t, False, 1215)
        return c

    # ============================================================= /temp-14 Glass Dock (t-14)
    def t14_talk(self, t):
        T = _tr(); c = self.base(t); band = self.face.box[3]
        if self.dock(c, t, self.job.get('dock') or [], min(band + 62, 1188)) and t <= (self.job['dock'][-1]['t'] + 1.6): return c
        hh = self.head_at(t)
        if hh and t >= hh[1]['big_t'] and t - hh[1]['big_t'] < 1.4:
            h = hh[1]; b = t - h['big_t']
            box = T.comp(c, T.text(h['label'], 'inter:600', 30, shadow=(0, 3, 8, 0.6), maxw=840), 512, band + 20); self.check(box, 'small line', t)
            lay = T.text(h['big'].title() if len(h['big']) > 4 else h['big'], 'intertight:900', 74, grad=('#FFEA5C', '#F2A20A'), shadow=(0, 5, 12, 0.5), maxw=820)
            box = T.comp(c, lay, 512, min(band + 78, 1196), scale=pop(b, 0.8, 1.04)); self.check(box, 'yellow word', t)
            return c
        ch = self.chunk_at(t, 4, 26)
        if ch: self.words_line(c, t, ch, min(band + 60, 1205), 'inter:600', 38, '#FFFFFF', 'intertight:800', 44, ('#FFEA5C', '#F2A20A'))
        return c

    def t14_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']
        if sc.get('image'):
            c, zone = self.fit(t, 0.56, 800, darken=0.4)
            T.comp(c, rrect(900, 470, 30, (18, 20, 26, 240), border=2, border_col=(60, 64, 80, 255)), 540, 545)
            T.comp(c, T.rounded_card(self.img(sc['image']), 840, 410, r=20, shadow=False), 540, 545, alpha=T.ease_out(a / 0.2))
            ch = self.chunk_at(t, 4, 26)
            if ch: self.words_line(c, t, ch, min(zone.box[3] + 34, 1222), 'inter:600', 34, '#FFFFFF', zone=zone)
            return c
        c = self._cache('t14dark', lambda: blob_page('#14161C', [(540, 1100, 500, '#1C2030', 0.9)]))
        p = T.ease_out((a - 0.25) / 0.5); base_y = 1060
        if p > 0:
            beams = np.zeros((H, W), np.float32); layer = np.zeros((H, W, 3), np.float32)
            for k, (dx, col) in enumerate([(-230, '#6C7BFF'), (0, '#FF5FD2'), (230, '#8E6BFF')]):
                topy = base_y - 760 * p; pts = np.array([[540 - 30, base_y], [540 + 30, base_y], [540 + dx * p + 110, topy], [540 + dx * p - 110, topy]], np.int32)
                m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [pts], 1.0); m = cv2.GaussianBlur(m, (0, 0), 14)
                layer += m[..., None] * np.array(T.rgb(col), np.float32) * 0.8
            c = np.clip(c + layer, 0, 255)
            for k, col in enumerate(['#FFD54A', '#4AA8FF', '#7CFFB2', '#FF7AA8']):
                q = (a - 0.4 - 0.12 * k) / 0.8
                if 0 < q < 1.2:
                    x = 540 + (k - 1.5) * 150 * q; y = base_y - 650 * T.ease_out(q); cv2.circle(c, (int(x), int(y)), 22, T.rgb(col), -1, cv2.LINE_AA)
        T.comp(c, rrect(170, 140, 30, (90, 168, 245, 255), shadow=60), 540, base_y + 40)
        box = T.comp(c, T.text('G' if not sc.get('icon') else sc['icon'], 'intertight:900', 76, fill='#FFFFFF'), 540, base_y + 40); self.check(box, 'icon', t, face=False)
        if sc.get('title'):
            box = T.comp(c, T.text(sc['title'], 'inter:700', 70, maxw=860), 512, 330, alpha=T.ease_out(a / 0.2)); self.check(box, 'title', t, face=False)
        return c

    # ============================================================= /temp-15 Clean White Split (t-15)
    def _navy_label(self, c, t, s, cy, zone, italic=False, start=0.0):
        T = _tr(); lay = T.text(s, 'playfair-i:700' if italic else 'inter:700', 58, maxw=800); bw = lay.shape[1] - 2 * int(58 * 0.45) + 40
        g = T.ease_out((t - start) / 0.18); T.comp(c, rrect(max(4, int(bw * g)), 92, 8, (28, 35, 64, 250)), 512, cy)
        if g > 0.6: box = T.comp(c, lay, 512, cy); self.check(box, 'navy label', t, face=zone)

    def t15_talk(self, t):
        T = _tr(); c = self.base(t); hh = self.head_at(t)
        if self.job.get('dock') and self.dock(c, t, self.job['dock'], 360, dark=True) and t <= self.job['dock'][-1]['t'] + 1.6: pass
        elif hh and t >= hh[1]['big_t'] and t - hh[1]['big_t'] < 1.2:
            self._navy_label(c, t, hh[1]['big'].lower() + ('?' if hh[0] == 0 else ''), 370, self.face, start=hh[1]['big_t'])
        ch = self.chunk_at(t, 4, 26)
        if ch: self.words_line(c, t, ch, min(self.face.box[3] + 64, 1205), 'inter:700', 42, '#FFFFFF', 'playfair-i:700', 50, '#FFFFFF')
        return c

    def t15_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']
        if sc.get('rows'):
            c = self._cache('t15cream', lambda: np.full((H, W, 3), T.rgb('#EFE7DA'), np.float32))
            x0, x1, y = 100, 960, 340; c[y - 44:y + 44, x0:x1] = T.rgb('#1C2340')
            box = T.comp(c, T.text(sc.get('head', ['TOOL', 'STATUS'])[0], 'inter:700', 42), x0 + 10, y, anchor='l'); self.check(box, 'table head', t, face=False)
            box = T.comp(c, T.text(sc.get('head', ['TOOL', 'STATUS'])[1], 'inter:700', 42), x1 - 160, y); self.check(box, 'table head', t, face=False)
            y += 100
            for r in sc['rows']:
                if t < r['t']: break
                al = T.ease_out((t - r['t']) / 0.15)
                box = T.comp(c, T.text(r['name'], 'inter:500', 56, fill='#1C2340'), x0 + 10, y, anchor='l', alpha=al); self.check(box, 'row', t, face=False)
                box = T.comp(c, T.text(r['val'], 'inter:600', 56, fill='#1C2340'), x1 - 160, y, alpha=al); self.check(box, 'row', t, face=False)
                c[y + 46:y + 48, x0:x1] = (200, 192, 178); y += 96
            if sc.get('total') and t >= sc['total']['t']:
                al = T.ease_out((t - sc['total']['t']) / 0.15)
                box = T.comp(c, T.text(sc['total']['name'], 'inter:800', 42, fill='#1C2340'), x0 + 24, y + 10, anchor='l', alpha=al); self.check(box, 'total', t, face=False)
                box = T.comp(c, T.text(sc['total']['val'], 'playfair-i:700', 42, fill='#D62F2F'), x1 - 110, y + 10, alpha=al); self.check(box, 'total', t, face=False)
                if sc.get('result') and t >= sc['total']['t'] + 0.4:
                    cv2.arrowedLine(c, (x1 - 110, y + 50), (540, y + 150), (28, 35, 64), 4, cv2.LINE_AA, tipLength=0.08)
                    self._navy_label(c, t, sc['result'], y + 210, False, start=sc['total']['t'] + 0.4)
            return c
        k = T.ease_out(a / 0.35); s = 1.0 - 0.42 * k; cap = 505 * (1 - k) + 860 * k
        c, zone = self.fit(t, s, cap, darken=0.5)
        ph = int(820 * k); c[:ph] = np.full((ph, W, 3), T.rgb('#FBFBFC'), np.float32); c[ph:ph + 3] = (226, 226, 230)
        if k > 0.95:
            if sc.get('image'): T.comp(c, T.rounded_card(self.img(sc['image']), 880, 400, r=22), 540, 520)
            if sc.get('title'): self._navy_label(c, t, sc['title'], 755, zone, italic=bool(sc.get('italic')), start=sc['t0'] + 0.4)
        return c

    # ============================================================= /temp-16 Lime Polaroid (sezz0283)
    def _t16_bg(self):
        return self._cache('t16bg', lambda: blob_page('#F5F8F2', [(200, 1500, 650, '#BFE3A8', 0.85), (950, 400, 380, '#E4F2DA', 0.8)]))

    def t16_talk(self, t):
        c = self.base(t); ch = self.chunk_at(t, 3, 22)
        if ch: self.words_line(c, t, ch, min(self.face.box[3] + 68, 1205), 'inter:600', 42, '#FFFFFF', 'inter:700', 42, '#111111', key_box=(200, 241, 53, 255))
        return c

    def t16_scene(self, t, sc, i):
        T = _tr(); a = t - sc['t0']; c = self._t16_bg()
        if sc.get('image') and not sc.get('polaroid'):
            ph = rrect(500, 930, 60, (12, 12, 14, 255), shadow=90); T.comp(c, ph, 540, 770 + 40 * (1 - T.ease_out(a / 0.35)))
            T.comp(c, T.rounded_card(self.img(sc['image']), 460, 890, r=44, shadow=False), 540, 770 + 40 * (1 - T.ease_out(a / 0.35)))
            return c
        card, k = self.crop_card(t, 230, 430, 850, 1050, 540, r=22, border=18, label='+ ' + sc.get('name', 'Rakshith'), label_h=78)
        s = 1.0 + 0.04 * T.ease_out(a / 1.5); cx, cy = 540, 290 + card.shape[0] / 2 + 10
        T.comp(c, card, cx, cy, scale=s)
        x0c, y0c = cx - card.shape[1] / 2 * s + 18 * s, cy - card.shape[0] / 2 * s + 18 * s
        zone = self.zone_of(k * s, x0c - 230 * k * s, y0c - 430 * k * s)
        if sc.get('badge'):
            rib = Image.new('RGBA', (250, 92), (0, 0, 0, 0)); d = ImageDraw.Draw(rib); d.polygon([(0, 0), (250, 0), (222, 46), (250, 92), (0, 92)], fill=(16, 16, 16, 255))
            lb = Image.fromarray(T.text(sc['badge'], 'inter:800', 30)); rib.alpha_composite(lb, (14, (92 - lb.height) // 2))
            box = T.comp(c, np.asarray(rib), cx + card.shape[1] / 2 * s - 60, cy - card.shape[0] / 2 * s + 30, scale=pop(a - 0.3, 0.7, 1.05)); self.check(box, 'badge', t, face=zone)
        bottom = cy + card.shape[0] / 2 * s
        ch = self.chunk_at(t, 3, 22)
        if ch: self.words_line(c, t, ch, bottom + 56, 'inter:600', 46, '#161616', 'inter:700', 46, '#111111', key_box=(200, 241, 53, 255), zone=zone, shadow=None)
        if sc.get('items'):
            q = T.ease_out((a - 0.4) / 0.4); y1 = bottom + 96
            for xx, it in zip((300, 780), sc['items'][:2]):
                cv2.line(c, (540, int(bottom + 110)), (int(540 + (xx - 540) * q), int(y1 + 20)), (150, 170, 140), 3, cv2.LINE_AA)
                if q > 0.9:
                    cv2.circle(c, (xx, int(y1 + 60)), 50, T.rgb('#C8F135'), -1, cv2.LINE_AA)
                    box = T.comp(c, T.text(it, 'inter:700', 26, fill='#1E3A12', maxw=90), xx, y1 + 60); self.check(box, 'tree item', t, face=zone)
        return c
