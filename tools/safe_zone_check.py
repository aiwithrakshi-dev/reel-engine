#!/usr/bin/env python3
"""Instagram Reels safe-zone overlay + contact sheet for a 1080x1920 video.

Usage:
  python3 tools/safe_zone_check.py reel.mp4 --fps 12 --out qc/
Writes qc/safe_zone_sheet_XX.png (frames with the green safe box, red outer margins and the
3:4 profile-grid crop in cyan) so every frame can be checked by eye. Nothing readable may sit
outside the green box.
"""
import argparse, os, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SAFE = (65, 270, 960, 1250)      # x0, y0, x1, y1  (Meta Reels margins + right action rail)
GRID = (0, 240, 1080, 1680)      # 3:4 profile-grid centre crop


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def frames(path, fps):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


def overlay(img):
    im = Image.fromarray(img).convert("RGBA")
    shade = Image.new("RGBA", im.size, (255, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    x0, y0, x1, y1 = SAFE
    for box in [(0, 0, W, y0), (0, y1, W, H), (0, y0, x0, y1), (x1, y0, W, y1)]:
        d.rectangle(box, fill=(255, 0, 0, 55))
    d.rectangle(SAFE, outline=(0, 255, 0, 255), width=6)
    d.rectangle(GRID, outline=(0, 220, 255, 200), width=3)
    return Image.alpha_composite(im, shade).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=12, help="audit rate (>= 12 recommended)")
    ap.add_argument("--out", default="qc")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--rows", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    info = probe(a.video)
    s = info["streams"][0]
    if (s["width"], s["height"]) != (W, H):
        print(f"WARNING: video is {s['width']}x{s['height']}, expected {W}x{H} (scaled for the check)")
    tw, th = 180, 320
    per = a.cols * a.rows
    sheet, k, page = None, 0, 0
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for i, f in enumerate(frames(a.video, a.fps)):
        if k == 0:
            sheet = Image.new("RGB", (a.cols * tw, a.rows * (th + 20)), (20, 20, 20))
        t = overlay(f).resize((tw, th), Image.LANCZOS)
        x, y = (k % a.cols) * tw, (k // a.cols) * (th + 20)
        sheet.paste(t, (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + th + 1), f"{i / a.fps:6.2f}s", fill=(230, 230, 230), font=font)
        k += 1
        if k == per:
            sheet.save(os.path.join(a.out, f"safe_zone_sheet_{page:02d}.png")); page += 1; k = 0
    if k:
        sheet.save(os.path.join(a.out, f"safe_zone_sheet_{page:02d}.png")); page += 1
    print(f"{page} sheet(s) written to {a.out}/ at {a.fps} fps. Green = safe box {SAFE}, cyan = 3:4 grid crop.")


if __name__ == "__main__":
    main()
