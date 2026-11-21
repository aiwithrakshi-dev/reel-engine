# Rebuilds chair_mask.png (the red/black gaming chair) from one clean A-roll frame.
# RVM mattes the person only; the chair is static, so it is a fixed mask traced from its red piping,
# clipped to a hand-drawn safety polygon. Re-check the polygon if the camera framing ever changes.
# usage: python3 chair_mask.py <aroll_30fps.mp4> [frame_index] -> chair_mask.png
import sys, cv2, numpy as np
src = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
cv = cv2.VideoCapture(src); cv.set(1, n); f = cv.read()[1]
# safety polygon (source 1080x1920 coords) around the chair for Rakshith's usual locked-off framing
poly = np.array([(105,1920),(100,1133),(90,1083),(108,1000),(172,932),(238,848),(320,748),(365,680),(400,660),
                 (680,660),(708,675),(752,770),(845,870),(910,952),(942,1017),(950,1083),(978,1250),(992,1920)], np.int32)
P = np.zeros((1920,1080), np.uint8); cv2.fillPoly(P, [poly], 1)
Pd = cv2.dilate(P, np.ones((15,15), np.uint8))
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); h, s, v = [hsv[..., i].astype(int) for i in range(3)]
red = (((h <= 7) | (h >= 170)) & (s > 110) & (v > 90)).astype(np.uint8) * Pd
M = np.zeros((1920,1080), np.uint8); L = R = None
for y in range(640, 1920):                       # per row: span between outermost left / right piping
    xl = np.nonzero(red[y, :470])[0]; xr = np.nonzero(red[y, 610:])[0]
    if len(xl): L = xl.min() if L is None else (xl.min() if abs(xl.min() - L) < 40 else L)
    if len(xr): R = 610 + xr.max() if R is None else (610 + xr.max() if abs(610 + xr.max() - R) < 40 else R)
    if L is not None and R is not None: M[y, max(0, L - 1):R + 2] = 1
M &= Pd
M = cv2.morphologyEx(M, cv2.MORPH_CLOSE, np.ones((9,9), np.uint8))
M = cv2.morphologyEx(M, cv2.MORPH_OPEN, np.ones((7,7), np.uint8))
M = cv2.medianBlur(M * 255, 21) // 255
M = M & cv2.dilate(P, np.ones((5,5), np.uint8))
cv2.imwrite('chair_mask.png', cv2.GaussianBlur(M * 255, (0,0), 1.2)); print('chair_mask.png written')
