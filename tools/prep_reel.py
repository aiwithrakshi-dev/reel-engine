#!/usr/bin/env python3
"""Prep one raw talking-head video for a job-driven template render (batch-friendly).

  python3 tools/prep_reel.py raw.mp4 asr.json out_dir [--gap 0.32] [--pad 0.10]

Writes out_dir/: aroll_tight.mp4 (source fps, pauses tightened), vo.wav (48 kHz, cleaned VO), words.json
(reel-time [[w, s, e]]), prep.json (islands, cuts, face measurement in source px, suggested dy, duration).
asr.json = faster-whisper output {segments: [{words: [{w, s, e}]}]} on the RAW file.
Pauses longer than --gap are cut down to --gap; every resulting jump cut is listed in prep.json['cuts'] so the
render can hide it (punch-in alternation / transition). Face: OpenCV Haar on 9 frames, head box = face box widened
to the cap and chin (verify on the contact sheet before rendering).
"""
import sys, os, json, subprocess, argparse
import numpy as np, cv2, soundfile as sf

ap = argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('asr'); ap.add_argument('out')
ap.add_argument('--gap', type=float, default=0.32); ap.add_argument('--pad', type=float, default=0.10)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                    'stream=r_frame_rate,width,height:format=duration', '-of', 'json', a.raw]))
num, den = map(int, probe['streams'][0]['r_frame_rate'].split('/')); fps = num / den
dur = float(probe['format']['duration'])

# ---- speech islands from word timings (more reliable than an energy gate for his room tone)
words = [(w['w'].strip(), float(w['s']), float(w['e'])) for s in json.load(open(a.asr))['segments'] for w in s['words'] if w['w'].strip()]
isl = []
for w, s, e in words:
    s0, e0 = max(0.0, s - a.pad), min(dur, e + a.pad + 0.02)
    if isl and s0 - isl[-1][1] <= a.gap: isl[-1][1] = max(isl[-1][1], e0)
    else: isl.append([s0, e0])
# snap to whole source frames (in-points down, out-points up)
isl = [[int(x * fps) / fps, min(dur, (int(y * fps) + 1) / fps)] for x, y in isl]
# merge overlaps after snapping
m = []
for x, y in isl:
    if m and x <= m[-1][1] + 1e-6: m[-1][1] = max(m[-1][1], y)
    else: m.append([x, y])
isl = m
# keep a short natural lead-in on the first island and a tail after the last
isl[0][0] = max(0.0, isl[0][0] - 0.06)
reel = []; t = 0.0
for x, y in isl: reel.append((x, y, t)); t += y - x
D = t

def src_to_reel(s):
    for x, y, r in reel:
        if x - 1e-6 <= s <= y + 1e-6: return r + (s - x)
    return None

W2 = []
for w, s, e in words:
    rs, re_ = src_to_reel(s), src_to_reel(e)
    if rs is None:   # word starts inside a trimmed edge: clamp to the island it belongs to
        nxt = [r for x, y, r in reel if x >= s]; rs = nxt[0] if nxt else D
    if re_ is None: re_ = rs + (e - s)
    W2.append([w, round(rs, 3), round(max(re_, rs + 0.05), 3)])
json.dump(W2, open(os.path.join(a.out, 'words.json'), 'w'), indent=0)

# ---- tight A-roll + VO in one ffmpeg pass
parts_v = ''.join(f"[0:v]trim=start={x:.4f}:end={y:.4f},setpts=PTS-STARTPTS[v{i}];" for i, (x, y) in enumerate(isl))
parts_a = ''.join(f"[0:a]atrim=start={x:.4f}:end={y:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0, y - x - 0.012):.4f}:d=0.012[a{i}];" for i, (x, y) in enumerate(isl))
n = len(isl)
fc = parts_v + parts_a + ''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[v];' + ''.join(f'[a{i}]' for i in range(n)) + \
     f'concat=n={n}:v=0:a=1,highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=8:release=120,aresample=48000[a]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.raw, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '14', '-pix_fmt', 'yuv420p', '-r', f'{num}/{den}', os.path.join(a.out, 'aroll_tight.mp4'),
                '-map', '[a]', '-ac', '1', os.path.join(a.out, 'vo.wav')], check=True)

# ---- face measurement (source px)
cap = cv2.VideoCapture(a.raw); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
casc = cv2.CascadeClassifier(next(p for p in (os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models', 'haarcascade_frontalface_default.xml'), getattr(cv2, 'data', None) and cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') if p and os.path.exists(p)))
boxes = []
for k in np.linspace(0.08, 0.92, 9):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(N * k)); ok, fr = cap.read()
    if not ok: continue
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY); fs = casc.detectMultiScale(g, 1.1, 6, minSize=(180, 180))
    if len(fs): boxes.append(max(fs, key=lambda b: b[2] * b[3]))
if boxes:
    b = np.median(np.array(boxes), 0); fx, fy, fw, fh = [float(v) for v in b]
    cap_top = fy - 0.36 * fh; chin = fy + 1.0 * fh; x0 = fx - 0.10 * fw; x1 = fx + fw * 1.10   # calibrated on his cap/beard (24 Nov 2026)
else:
    cap_top, chin, x0, x1 = 465.0, 1030.0, 350.0, 730.0
face_c = ((x0 + x1) / 2, (cap_top + chin) / 2)
dy = int(max(0, min(505 - cap_top, 1100 - chin)))          # cap >= 505 and chin <= 1100 after the shift
prep = dict(raw=a.raw, fps=fps, src_duration=dur, duration=round(D, 3), islands=[[round(x, 4), round(y, 4)] for x, y in isl],
            cuts=[round(r, 3) for x, y, r in reel[1:]], face_src=dict(cap_top=cap_top, chin=chin, x0=x0, x1=x1),
            face_src_c=face_c, dy=dy, n_face_frames=len(boxes))
json.dump(prep, open(os.path.join(a.out, 'prep.json'), 'w'), indent=1)
print(json.dumps({k: prep[k] for k in ('duration', 'dy', 'face_src', 'n_face_frames')}), 'cuts', len(prep['cuts']))
