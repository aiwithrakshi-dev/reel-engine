# Day-4 framing (closer shot, no chair mask needed: the chair stays in the softened room plate behind the type)
import cv2, numpy as np
def combined_alpha(bgr, pa):
    a = pa.astype(np.float32) / 255
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.25).astype(np.uint8), connectivity=8)
    if n > 2:
        small = np.isin(lab, [i for i in range(1, n) if st[i, 4] < 6000]); a[small] = 0
    a = cv2.erode(a, np.ones((3, 3), np.uint8))          # ~1 px choke
    return cv2.GaussianBlur(a, (0, 0), 0.8)
