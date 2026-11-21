# Face-clear guard: NO text layer, edit/effect layer or component layer may sit on Rakshith's face.
#
# Two mechanisms:
#   1. protect_face(canvas, pre, zone)  restores the face oval from the frame as it was BEFORE the overlay FX pass
#      (neon streaks, halftone rings, swooshes, pixel blocks, stickers, badges...). Call it right after drawing the
#      FX layers on every talking-head frame, so no effect can ever paint over his face.
#   2. FaceZone.check(box, what, t)     raises if a text/component box (headline, label, caption, chest row, card,
#      pill, badge) intersects the face zone, so layout mistakes fail the render instead of reaching the reel.
#
# Allowed on the face: only WHOLE-FRAME transitions that transform the entire picture for <= 0.2 s (the hook opener,
# negative flash, RGB/magenta ghost, smear, radial blur). They are not layers on top of him.
#
#   zone = FaceZone.from_head(cap_top=505, chin=1100, x0=330, x1=750)      # measured per reel (reel coords)
#   pre = c.copy(); draw_fx(c); protect_face(c, pre, zone)
import numpy as np, cv2


class FaceZone:
    def __init__(self, cx, cy, rx, ry, margin=24):
        self.cx, self.cy, self.rx, self.ry, self.m = cx, cy, rx + margin, ry + margin, margin
        self._mask = None

    @classmethod
    def from_head(cls, cap_top, chin, x0, x1, margin=24):
        """Head measured over ALL frames (min cap-top, max chin, widest left/right, reel coordinates)."""
        return cls((x0 + x1) / 2, (cap_top + chin) / 2, (x1 - x0) / 2, (chin - cap_top) / 2, margin)

    @classmethod
    def from_alpha(cls, alphas, dy=0, margin=24, head_ratio=1.32):
        """Estimate from matte frames (H x W float 0..1, source coords): cap top = first row where the centre
        columns are solid; head width = alpha width 15 % of a head-height below the top; chin = top + ratio*width."""
        tops, x0s, x1s = [], [], []
        for a in alphas:
            col = a[:, a.shape[1] // 2 - 60:a.shape[1] // 2 + 60].mean(1)
            rows = np.where(col > 0.5)[0]
            if not len(rows): continue
            t = int(rows[0]); probe = a[min(a.shape[0] - 1, t + 120)] > 0.5; xs = np.where(probe)[0]
            if len(xs): tops.append(t); x0s.append(xs[0]); x1s.append(xs[-1])
        t, x0, x1 = min(tops) + dy, min(x0s), max(x1s)
        return cls.from_head(t, t + head_ratio * (x1 - x0), x0, x1, margin)

    @property
    def box(self):
        return (int(self.cx - self.rx), int(self.cy - self.ry), int(self.cx + self.rx), int(self.cy + self.ry))

    def mask(self, H=1920, W=1080, feather=18):
        if self._mask is None:
            m = np.zeros((H, W), np.float32)
            cv2.ellipse(m, (int(self.cx), int(self.cy)), (int(self.rx), int(self.ry)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
            self._mask = cv2.GaussianBlur(m, (0, 0), feather)[..., None]
        return self._mask

    def hits(self, box):
        """True if an axis-aligned box (x0, y0, x1, y1) touches the face oval."""
        x0, y0, x1, y1 = box
        px = min(max(self.cx, x0), x1); py = min(max(self.cy, y0), y1)    # closest point of the box to the centre
        return ((px - self.cx) / self.rx) ** 2 + ((py - self.cy) / self.ry) ** 2 <= 1.0

    def check(self, box, what='layer', t=None):
        if self.hits(box):
            raise ValueError(f'{what} {box} sits on the face zone {self.box}' + (f' at {t:.2f}s' if t is not None else '') +
                             ' — move it above the cap, below the chin or beside the head')


def protect_face(canvas, pre, zone, feather=18):
    """Put the face oval back exactly as it was before the overlay FX were drawn."""
    m = zone.mask(canvas.shape[0], canvas.shape[1], feather)
    canvas[:] = canvas * (1 - m) + pre * m
