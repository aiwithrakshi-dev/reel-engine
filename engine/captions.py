# Burned-in captions for the kinetic reel (1080x1920, safe zone x 65-960 / y 270-1250) + SRT export.
#
# Two house styles:
#   karaoke : Inter Tight Bold Italic 44 px, white with dark stroke, one line, the word being spoken turns red.
#             (SKILL §8 default for talking-head stretches)
#   chip    : the reference-reel style ("SAVE [THIS]", "JUST [DROPPED]", "[FIX] SINGLE FRAMES"): 2-4 heavy upright caps
#             words, ONE keyword on a red rounded box, pops in with a stepped overshoot. Use for punch lines over
#             cutaways / slates, or as the whole caption track for fast "news drop" reels.
#
#   from captions import chunk_words, phrases_to_chunks, CaptionTrack, write_srt
#   chunks = chunk_words(words)                 # words: [(text, start, end), ...] in REEL seconds
#   track  = CaptionTrack(chunks, mode='karaoke', y_bottom=1245)
#   track.draw(canvas, t)                       # canvas float32 HxWx3 (0..255), t in reel seconds
#   write_srt(chunks, 'captions.srt')
import os, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
SAFE = (65, 270, 960, 1250)
RED = (0xE3, 0x12, 0x1B)
_HERE = os.path.dirname(os.path.abspath(__file__))
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import FONT_DIRS


def _find(name):
    for d in FONT_DIRS:
        if d and os.path.exists(os.path.join(d, name)): return os.path.join(d, name)
    raise FileNotFoundError(f'{name} not found in {FONT_DIRS}; download Inter Tight (OFL) into work/fonts')


_fc = {}
def font(weight, size, italic):
    k = (weight, size, italic)
    if k not in _fc:
        f = ImageFont.truetype(_find('InterTight-Italic%5Bwght%5D.ttf' if italic else 'InterTight%5Bwght%5D.ttf'), size)
        try: f.set_variation_by_axes([weight])
        except Exception: pass
        _fc[k] = f
    return _fc[k]


# ------------------------------------------------------------------ chunking
STOP_END = re.compile(r'[.,!?;:…]$')
FUNC = {'and', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'is', 'are', 'for', 'with', 'your', 'my', 'from', 'than', 'can', 'it', 'that'}

def chunk_words(words, max_words=5, max_chars=30, gap=0.25, min_dur=0.45):
    """words: [(text, start, end)] reel seconds -> chunks [{'words': [...], 'start', 'end', 'text'}].
    Breaks on punctuation, on pauses >= gap, and at max_words / max_chars (one line)."""
    chunks, cur = [], []
    def flush():
        if cur:
            chunks.append({'words': list(cur), 'start': cur[0][1], 'end': cur[-1][2], 'text': ' '.join(w[0] for w in cur)})
            cur.clear()
    for i, w in enumerate(words):
        text = w[0].strip()
        if not text: continue
        cand = ' '.join([c[0] for c in cur] + [text])
        if cur and (len(cur) >= max_words or len(cand) > max_chars or w[1] - cur[-1][2] >= gap):
            prev = cur[-1][0]; glued = (prev.lower() in FUNC or re.match(r'^[\d+%$]+$', prev) or
                                        (prev[:1].isupper() and text[:1].isupper() and not STOP_END.search(prev)))
            carry = cur.pop() if len(cur) > 1 and glued and w[1] - cur[-1][2] < gap else None
            flush()                                      # never end a line on "and / the / a / to ..."
            if carry: cur.append(carry)
        cur.append((text, float(w[1]), float(w[2])))
        if STOP_END.search(text): flush()
    flush()
    for a, b in zip(chunks, chunks[1:]):           # hold each chunk until the next starts (no flicker), min duration
        a['end'] = max(a['end'], min(b['start'], a['start'] + min_dur))
    return chunks


def phrases_to_chunks(phrases, max_words=5, max_chars=30):
    """Kannada reels: phrases [(kannada_text, english_text, start, end)] -> English chunks timed to the Kannada span.
    Long English lines are split; word times are spread by character length inside the span (never early)."""
    out = []
    for kn, en, s, e in phrases:
        toks = en.split(); n = max(1, len(' '.join(toks)))
        t = s; tw = []
        for tok in toks:
            d = (e - s) * (len(tok) + 1) / (n + 1); tw.append((tok, t, t + d)); t += d
        out.extend(chunk_words(tw, max_words, max_chars, gap=10))
    return out


def write_srt(chunks, path):
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    with open(path, 'w', encoding='utf-8') as f:
        for i, c in enumerate(chunks, 1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text'].strip(' ,')}\n\n")


# ------------------------------------------------------------------ rendering
def _clean(t, upper=False):
    t = t.strip(' ,.;:')
    return t.upper() if upper else t


def _layer_karaoke(words, active, size=44):
    f = font(700, size, True); sp = f.getlength(' '); stroke = 3
    widths = [f.getlength(w) for w in words]; tw = int(sum(widths) + sp * (len(words) - 1)) + 2 * stroke + 16
    th = int(size * 1.45) + 2 * stroke
    im = Image.new('RGBA', (tw + 24, th + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 12 + stroke + 8; y = 12 + stroke
    for i, w in enumerate(words):                                   # soft shadow
        d.text((x + 3, y + 5), w, font=f, fill=(0, 0, 0, 150)); x += widths[i] + sp
    im = im.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(im); x = 12 + stroke + 8
    for i, w in enumerate(words):
        col = RED + (255,) if i == active else (255, 255, 255, 255)
        d.text((x, y), w, font=f, fill=col, stroke_width=stroke, stroke_fill=(10, 8, 10, 255)); x += widths[i] + sp
    return np.asarray(im).astype(np.float32) / 255


def _layer_chip(words, key, size=50, track=3):
    f = font(850, size, False); sp = f.getlength(' ') * 1.2
    def tl(w): return sum(f.getlength(ch) for ch in w) + track * (len(w) - 1)
    widths = [tl(w) for w in words]; padx, pady = 16, 10
    tw = int(sum(widths) + sp * (len(words) - 1) + 2 * padx) + 20; th = int(size * 1.25 + 2 * pady)
    im = Image.new('RGBA', (tw + 24, th + 28), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 12 + padx; y = 14 + pady
    for i, w in enumerate(words):                                   # shadow pass
        if i == key: d.rounded_rectangle((x - padx + 6, y - pady + 8, x + widths[i] + padx + 6, y + size * 1.05 + pady + 8), 12, fill=(0, 0, 0, 120))
        else:
            xx = x
            for ch in w: d.text((xx + 3, y + 5), ch, font=f, fill=(0, 0, 0, 170)); xx += f.getlength(ch) + track
        x += widths[i] + sp
    im = im.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(im); x = 12 + padx
    for i, w in enumerate(words):
        if i == key: d.rounded_rectangle((x - padx * 0.6, y - pady * 0.6, x + widths[i] + padx * 0.6, y + size * 1.02 + pady * 0.6), 10, fill=RED + (255,))
        xx = x
        for ch in w: d.text((xx, y), ch, font=f, fill=(255, 255, 255, 255)); xx += f.getlength(ch) + track
        x += widths[i] + sp
    return np.asarray(im).astype(np.float32) / 255


def _over(canvas, lay, cx, y_bottom, scale=1.0):
    if scale != 1.0:
        h, w = lay.shape[:2]; im = Image.fromarray((lay * 255).astype(np.uint8)).resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        lay = np.asarray(im).astype(np.float32) / 255
    h, w = lay.shape[:2]; x0 = int(cx - w / 2); y0 = int(y_bottom - h)
    x0 = max(SAFE[0] - 12, min(x0, SAFE[2] + 12 - w))              # clamp inside the safe zone (layer padding allowed)
    a = lay[..., 3:4]; reg = canvas[y0:y0 + h, x0:x0 + w]
    reg[:] = reg * (1 - a[:reg.shape[0], :reg.shape[1]]) + lay[:reg.shape[0], :reg.shape[1], :3] * 255 * a[:reg.shape[0], :reg.shape[1]]
    return (x0, y0, x0 + w, y0 + h)


KEY_HINT = re.compile(r'(\d|^[A-Z][a-z]+[A-Z]|free|new|now|stable|beta|days|weeks|every|all|same|fix|drop|build|prompt|agent|plan|save)', re.I)

def pick_key(words):
    """Which word of a chip caption gets the red box: digits / product names / power words, else the longest."""
    best, bs = 0, -1
    for i, w in enumerate(words):
        s = len(w) * 0.1 + (2 if KEY_HINT.search(w) else 0) + (1 if w[:1].isupper() else 0)
        if s > bs: best, bs = i, s
    return best


class CaptionTrack:
    """mode: 'karaoke' | 'chip'. y_bottom: bottom of the caption line (<= 1245). cx: centre x (512 = safe-zone centre).
    face_box: (x0, y0, x1, y1) in reel px the caption must never overlap; hidden: list of (t0, t1) with no captions
    (e.g. while the same headline word is typing)."""
    def __init__(self, chunks, mode='karaoke', y_bottom=1245, cx=512, face_box=None, hidden=(), fps=60, avoid=()):
        self.chunks, self.mode, self.yb, self.cx, self.face, self.hidden, self.fps = chunks, mode, y_bottom, cx, face_box, list(hidden), fps
        self.avoid = list(avoid)   # other boxes (chest row y-band etc.) the caption must not touch
        self._cache = {}; self.boxes = []

    def at(self, t):
        if any(a <= t < b for a, b in self.hidden): return None
        for c in self.chunks:
            if c['start'] <= t < c['end']: return c
        return None

    def draw(self, canvas, t):
        c = self.at(t)
        if c is None: return None
        words = [_clean(w[0], upper=self.mode == 'chip') for w in c['words']]
        if self.mode == 'chip':
            key = c.get('key', pick_key(words)); k = ('chip', c['start'], key)
            if k not in self._cache: self._cache[k] = _layer_chip(words, key)
            age = int((t - c['start']) * 30)                         # stepped pop in 30-fps units
            scale = [0.82, 1.07, 1.0][min(age, 2)]
            box = _over(canvas, self._cache[k], self.cx, self.yb, scale)
        else:
            active = max([i for i, w in enumerate(c['words']) if w[1] <= t] or [0])
            k = ('kar', c['start'], active)
            if k not in self._cache: self._cache[k] = _layer_karaoke(words, active)
            box = _over(canvas, self._cache[k], self.cx, self.yb)
        if self.face and not (box[3] <= self.face[1] or box[1] >= self.face[3] or box[2] <= self.face[0] or box[0] >= self.face[2]):
            raise ValueError(f'caption {c["text"]!r} overlaps the face box at t={t:.2f}s: move y_bottom')
        for a in self.avoid:
            if not (box[3] <= a[1] or box[1] >= a[3] or box[2] <= a[0] or box[0] >= a[2]):
                raise ValueError(f'caption {c["text"]!r} overlaps {a} at t={t:.2f}s: raise the chest row or lower DY')
        self.boxes.append(box); return box


def apply_glossary(chunks, glossary):
    """Fix ASR spellings in captions with the reel's verified terms (facts.md), e.g. {'Juni': 'Junie',
    'Anti -Gravity': 'Antigravity', 'Cling': 'Kling'}. Case-insensitive, whole words."""
    pats = [(re.compile(r'(?<!\w)' + re.escape(k) + r'(?!\w)', re.I), v) for k, v in sorted(glossary.items(), key=lambda kv: -len(kv[0]))]
    for c in chunks:
        txt = c['text']
        for p, v in pats: txt = p.sub(v, txt)
        if txt != c['text']:
            toks = txt.split()
            if len(toks) == len(c['words']): c['words'] = [(t, w[1], w[2]) for t, w in zip(toks, c['words'])]
            else:   # tokens merged/split: spread the new tokens over the chunk span
                s, e = c['start'], c['words'][-1][2]; n = len(toks)
                c['words'] = [(t, s + (e - s) * i / n, s + (e - s) * (i + 1) / n) for i, t in enumerate(toks)]
            c['text'] = txt
    return chunks
