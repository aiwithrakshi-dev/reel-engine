#!/usr/bin/env python3
"""Preview every hook in engine/hooks.py on real frames of a reel (60 fps).

Usage: python3 tools/hook_preview.py reel_60fps.mp4 --start 0.25 --face 530,840 --out hooks_preview.mp4
Writes a 60 fps MP4 (one 1.1 s segment per hook, name in the corner) and a PNG strip of each hook's frames.
"""
import argparse, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
from hooks import HOOKS, apply_hook
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920

def read_frames(path, start, n):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path, '-vf', f'fps=60,scale={W}:{H}', '-frames:v', str(n),
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

def label(img, text):
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 44)
    except OSError: f = ImageFont.load_default()
    d.rounded_rectangle((60, 1720, 60 + 26 * len(text) + 40, 1800), 18, fill=(0, 0, 0))
    d.text((80, 1735), text, font=f, fill=(255, 255, 255)); return np.asarray(im)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--start', type=float, default=0.25)
    ap.add_argument('--face', default='540,760'); ap.add_argument('--seg', type=int, default=66); ap.add_argument('--out', default='hooks_preview.mp4')
    a = ap.parse_args(); face = tuple(int(v) for v in a.face.split(','))
    base = read_frames(a.video, a.start, a.seg)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '60', '-i', '-',
                           '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    strip = []
    for name, (fn, n, energy, sfx) in HOOKS.items():
        row = []
        for g in range(a.seg):
            c = base[min(g, len(base) - 1)].astype(np.float32)
            apply_hook(name, c, g, face=face)
            out = np.clip(c, 0, 255).astype(np.uint8)
            if g in (0, 2, 4, 6, 8, 10, 12, 14, 16, 20): row.append(cv2.resize(out, (135, 240), interpolation=cv2.INTER_AREA))
            ff.stdin.write(label(out, f'{name}  ·  {energy}').tobytes())
        strip.append(np.concatenate(row, 1))
    ff.stdin.close(); ff.wait()
    sheet = Image.fromarray(np.concatenate(strip, 0)); d = ImageDraw.Draw(sheet)
    for i, name in enumerate(HOOKS): d.text((4, i * 240 + 4), name, fill=(255, 255, 0))
    sheet.save(os.path.splitext(a.out)[0] + '_strip.png'); print('wrote', a.out, 'and strip PNG')

if __name__ == '__main__':
    main()
