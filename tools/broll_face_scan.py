#!/usr/bin/env python3
"""Scan every B-roll window a plan uses for faces and black/flash frames or clips that end too early (Rakshith: "don't use any kind of faces" in B-roll).

  python3 tools/broll_face_scan.py <reel_dir> [<reel_dir> ...]

Checks each scene / clip window (image or video, after `crop`) every 0.25 s with the OpenCV frontal-face cascade in
models/. Haar gives false positives on server racks and mics, so LOOK at the flagged frames, then move `in`, add `crop`
or swap the clip for real faces. Exit 1 if anything is flagged.
"""
import sys, os, json, cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
casc = cv2.CascadeClassifier(os.path.join(HERE, '..', 'models', 'haarcascade_frontalface_default.xml'))

def faces(img, crop):
    if crop:
        x0, y0, x1, y1 = crop; h, w = img.shape[:2]; img = img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    g = cv2.cvtColor(cv2.resize(img, (960, max(1, int(960 * img.shape[0] / img.shape[1])))), cv2.COLOR_BGR2GRAY)
    return len(casc.detectMultiScale(g, 1.1, 6, minSize=(48, 48)))

flag = 0
for rd in sys.argv[1:]:
    p = json.load(open(os.path.join(rd, 'plan.json')))
    for s in p.get('scenes', []):
        shots, acc = [], s['t0']
        for c in (s.get('clips') or [s]):
            du = c.get('dur', s['t1'] - acc); shots.append((c, du)); acc += du
        for c, du in shots:
            img, hits = c['image'], []
            if img.endswith(('.mp4', '.mov', '.webm')):
                cap = cv2.VideoCapture(img); fps = cap.get(5) or 30
                for t in np.arange(0, du, 0.25):
                    cap.set(1, int((c.get('in', 0) + t) * fps)); ok, f = cap.read()
                    if ok and faces(f, c.get('crop')): hits.append(round(c.get('in', 0) + t, 2))
                n0 = int(c.get('in', 0) * fps); cap.set(1, n0); dark = []
                cap2 = cv2.VideoCapture(img); nn = int(cap2.get(7)); med = []
                for q in np.linspace(0, max(0, nn - 1), 12).astype(int):
                    cap2.set(1, int(q)); ok2, g2 = cap2.read()
                    if ok2: med.append(cv2.resize(g2, (64, 36)).mean())
                lowkey = np.median(med) < 25 if med else False   # a dark-by-design clip (product on black) is fine
                for k_ in range(int(du * fps)):   # also catch black / flash frames inside the window (stock montages)
                    ok, f = cap.read()
                    if not ok: dark.append('END'); break
                    if not lowkey and cv2.resize(f, (64, 36)).mean() < 12: dark.append(round(c.get('in', 0) + k_ / fps, 2))
                if dark: flag += 1; print(f'{os.path.basename(rd)}  {img}  in {c.get("in", 0)}  -> black/ended frames at {dark[:6]}')
            else:
                f = cv2.imread(img)
                if f is not None and faces(f, c.get('crop')): hits.append('image')
            if hits: flag += 1; print(f'{os.path.basename(rd)}  {img}  in {c.get("in", 0)}  -> faces at {hits[:8]}')
print('FACE SCAN', 'CLEAN' if not flag else f'{flag} window(s) to look at')
sys.exit(1 if flag else 0)
