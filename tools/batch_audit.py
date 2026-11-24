#!/usr/bin/env python3
"""Audit one finished template reel (the audit-loop gate before delivery, SKILL.md §10).

  python3 tools/batch_audit.py <reel_dir>          (expects job.json + reel.mp4 in reel_dir)

1. captions.srt from the job's caption chunks -> tools/qc_audit.py (60 fps, codecs, -14 LUFS, <= -1 dBTP, hook unique,
   captions <= 30 chars and never early) -> qc_report.md
2. dialogue check: Whisper on the FINAL mix vs the job words (word error rate; music must not mask the voice)
3. visual sheets at 3 fps with the safe box + face zone drawn (qc/sheet_XX.jpg) + a join sheet around every cut,
   scene edge and transition (qc/joins.jpg) — look at every sheet.
Prints PASS only when 1 and 2 pass; the visual review is done by eye on the sheets.
"""
import sys, os, json, re, subprocess
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'engine'))
from captions import chunk_words
from template_render import fix_words

rd = sys.argv[1]; job = json.load(open(os.path.join(rd, 'job.json'))); reel = os.path.join(rd, 'reel.mp4')
qc = os.path.join(rd, 'qc'); os.makedirs(qc, exist_ok=True)
words = fix_words([tuple(w) for w in job['words']], job.get('glossary'))
chunks = chunk_words(words, max_words=7, max_chars=30)
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
with open(os.path.join(rd, 'captions.srt'), 'w') as f:
    for i, c in enumerate(chunks, 1): f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")

r = subprocess.run([sys.executable, os.path.join(HERE, 'qc_audit.py'), reel, '--hook', job['hook'], '--srt', os.path.join(rd, 'captions.srt'),
                    '--out', os.path.join(rd, 'qc_report.md')], capture_output=True, text=True)
rep = open(os.path.join(rd, 'qc_report.md')).read() if os.path.exists(os.path.join(rd, 'qc_report.md')) else r.stdout + r.stderr
fails = [l for l in rep.splitlines() if re.search(r'\bFIX\b|\bFAIL\b', l)]

# ---- dialogue intelligibility on the final mix
wav = os.path.join(qc, 'final16k.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', reel, '-ac', '1', '-ar', '16000', wav], check=True)
import soundfile as sf
from faster_whisper import WhisperModel
m = WhisperModel('medium', device='cpu', compute_type='int8', cpu_threads=2)
x, _ = sf.read(wav, dtype='float32'); segs, _ = m.transcribe(x, beam_size=3, language='en')
hyp = re.findall(r"[a-z0-9']+", ' '.join(s.text for s in segs).lower())
ref = re.findall(r"[a-z0-9']+", ' '.join(w[0] for w in words).lower())
d = np.zeros((len(ref) + 1, len(hyp) + 1), int); d[:, 0] = range(len(ref) + 1); d[0, :] = range(len(hyp) + 1)
for i in range(1, len(ref) + 1):
    for j in range(1, len(hyp) + 1):
        d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (ref[i - 1] != hyp[j - 1]))
wer = d[-1, -1] / max(1, len(ref))
wer_ok = wer <= 0.08          # ASR noise on product names; the clean VO itself scores ~0.03-0.06
open(os.path.join(qc, 'final_mix_transcript.txt'), 'w').write(' '.join(hyp))

# ---- sheets at 3 fps with safe box + face zone
fz = job['face']; FX0, FY0, FX1, FY1 = int(fz['x0']) - 24, int(fz['cap_top']) - 24, int(fz['x1']) + 24, int(fz['chin']) + 24
cap = cv2.VideoCapture(reel); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS)
def tile(g):
    cap.set(cv2.CAP_PROP_POS_FRAMES, g); ok, im = cap.read()
    if not ok: return None
    cv2.rectangle(im, (65, 270), (960, 1250), (0, 255, 0), 3); cv2.rectangle(im, (FX0, FY0), (FX1, FY1), (0, 0, 255), 2)
    cv2.putText(im, f'{g / fps:5.2f}s', (20, 70), 0, 2.0, (0, 255, 255), 4); return cv2.resize(im, (270, 480))
gs = list(range(0, n, int(fps // 3))); k = 0
for i in range(0, len(gs), 24):
    ims = [t for t in (tile(g) for g in gs[i:i + 24]) if t is not None]
    while len(ims) % 8: ims.append(np.zeros_like(ims[0]))
    cv2.imwrite(os.path.join(qc, f'sheet_{k:02d}.jpg'), np.vstack([np.hstack(ims[j:j + 8]) for j in range(0, len(ims), 8)]), [cv2.IMWRITE_JPEG_QUALITY, 70]); k += 1
sub = []
for s_ in job['scenes']:
    acc = s_['t0']
    for c_ in s_.get('clips', [])[:-1]: acc += c_['dur']; sub.append(acc)
edges = sorted(set([s['t0'] for s in job['scenes']] + [s['t1'] for s in job['scenes']] + job.get('punch', []) + sub))
rows = []
for e in edges:
    ims = [tile(max(0, int(e * fps) + o)) for o in (-6, -3, -1, 0, 1, 3, 6, 9)]
    rows.append(np.hstack([i if i is not None else np.zeros((480, 270, 3), np.uint8) for i in ims]))
if rows: cv2.imwrite(os.path.join(qc, 'joins.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70])

ra = subprocess.run([sys.executable, os.path.join(HERE, 'audio_audit.py'), rd], capture_output=True, text=True)
audio_ok = ra.returncode == 0
ok = not fails and wer_ok and audio_ok
print('QC', 'PASS' if ok else 'FIX')
print('  audio audit:', 'PASS' if audio_ok else 'FIX', '(qc/audio_report.md)')
for l in ra.stdout.splitlines():
    if '| FAIL |' in l or '| WARN |' in l: print('   ', l)
for l in fails: print('  ', l)
print(f'  dialogue WER on final mix: {wer:.3f} ({"ok" if wer_ok else "FIX: music/SFX masking the voice"})')
print(f'  sheets: {k} + joins ({len(edges)} edges) in {qc}')
