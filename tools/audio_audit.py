#!/usr/bin/env python3
"""Audio audit for a template reel: voice, music bed and SFX measured separately, then the final mix.

  python3 tools/audio_audit.py <reel_dir>        (needs job.json; reel.mp4 for the final-mix checks)

Rebuilds the mix with build_audio(..., stems_dir) so the voice / music / SFX stems carry exactly the levels that went
into the mix, then checks (SKILL.md §6 + 9f):
  VOICE   no clipping, no clicks at the silence-cut joins, steady level (3 s short-term spread), no dead air
  MUSIC   >= 18 dB under the voice while he talks (target ~20), never swells over the voice in pauses, still audible
  SFX     every hit audible (>= voice - 24 LU) but never louder than the voice (+3 LU max), never masking a word
  MIX     -14 LUFS +-1, true peak <= -1 dBTP, opening hit not a jump-scare, no dropout > 0.45 s before the end
Writes <reel_dir>/qc/audio_report.md and prints AUDIO PASS / AUDIO FIX.
"""
import sys, os, json, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'engine'))

rd = os.path.abspath(sys.argv[1]); os.chdir(rd)
job = json.load(open('job.json')); dur = job['duration']
qc = os.path.join(rd, 'qc'); st = os.path.join(qc, 'stems'); os.makedirs(st, exist_ok=True)
from template_render import build_audio
from templates import TEMPLATES
build_audio(job, TEMPLATES[int(job['template'])], os.path.join(st, 'mix_check.wav'), stems_dir=st)

def load(p):
    y, sr = sf.read(p, always_2d=True); return y.mean(1), sr
vo, sr = load(os.path.join(st, 'vo.wav')); mu, _ = load(os.path.join(st, 'music.wav')); sx, _ = load(os.path.join(st, 'sfx.wav'))
n = min(len(vo), len(mu), len(sx)); vo, mu, sx = vo[:n], mu[:n], sx[:n]
meter = pyln.Meter(sr, block_size=0.4)

def mom(y, hop=0.1, win=0.4):
    """momentary loudness (LUFS, 400 ms) every 100 ms; -70 for silence"""
    W, H = int(win * sr), int(hop * sr); out = []
    for i in range(0, max(1, len(y) - W), H):
        seg = y[i:i + W]
        if np.max(np.abs(seg)) < 1e-5: out.append(-70.0); continue
        L = meter.integrated_loudness(np.stack([seg, seg], 1))
        out.append(max(-70.0, L if np.isfinite(L) else -70.0))
    return np.array(out)

# speech mask from the job's words (reel time), merged across short gaps
iv = []
for w in job['words']:
    s, e = float(w[1]), float(w[2])
    if iv and s - iv[-1][1] < 0.25: iv[-1][1] = max(iv[-1][1], e)
    else: iv.append([s, e])
Mv, Mm, Ms = mom(vo), mom(mu), mom(sx)
k = min(len(Mv), len(Mm), len(Ms)); Mv, Mm, Ms = Mv[:k], Mm[:k], Ms[:k]
tc = np.arange(k) * 0.1 + 0.2                              # window centres
speech = np.zeros(k, bool)
for s, e in iv: speech |= (tc >= s + 0.1) & (tc <= e - 0.1)
gap = ~speech & (tc < iv[-1][1] if iv else True)

rows = []; fails = 0; warns = 0
def row(area, check, ok, detail, warn=False):
    global fails, warns
    st_ = 'PASS' if ok else ('WARN' if warn else 'FAIL'); fails += (st_ == 'FAIL'); warns += (st_ == 'WARN')
    rows.append(f'| {area} | {check} | {st_} | {detail} |')

def integ(y, mask_t):
    idx = np.zeros(len(y), bool)
    for c in tc[mask_t]: idx[int((c - 0.05) * sr):int((c + 0.05) * sr)] = True
    seg = y[idx]
    if len(seg) < sr * 0.5: return -70.0
    L = meter.integrated_loudness(np.stack([seg, seg], 1)); return L if np.isfinite(L) else -70.0

Lv = integ(vo, speech); Lm_s = integ(mu, speech); Lm_g = integ(mu, gap) if gap.sum() > 5 else -70.0
# ---- VOICE
clip = float(np.mean(np.abs(vo) > 0.985)) * 100
row('Voice', 'no clipping', clip < 0.01, f'{clip:.3f} % samples at full scale')
prep = json.load(open('prep.json')) if os.path.exists('prep.json') else {}
joins = [float(c) for c in prep.get('cuts', [])]
from scipy.signal import butter, sosfilt
hp = sosfilt(butter(4, 4000, 'hp', fs=sr, output='sos'), vo)
bad = []
for c in joins:
    i = int(c * sr)
    if i < sr * 0.06 or i > len(hp) - sr * 0.06: continue
    e_join = np.sqrt(np.mean(hp[i - int(0.003 * sr):i + int(0.003 * sr)] ** 2)) + 1e-9
    around = np.concatenate([hp[i - int(0.06 * sr):i - int(0.01 * sr)], hp[i + int(0.01 * sr):i + int(0.06 * sr)]])
    e_ref = np.sqrt(np.mean(around ** 2)) + 1e-9
    if 20 * np.log10(e_join / e_ref) > 12: bad.append(round(c, 2))
row('Voice', 'no clicks at silence-cut joins', not bad, f'{len(joins)} joins checked' + (f'; clicks at {bad}' if bad else ''))
short = [Mv[i] for i in range(k) if speech[i] and Mv[i] > -50]
spread = float(np.percentile(short, 90) - np.percentile(short, 10)) if len(short) > 10 else 0.0
row('Voice', 'steady level (momentary P90-P10 while talking)', spread <= 12, f'{spread:.1f} LU (<= 12)', warn=spread <= 15)
# ---- MUSIC
d_s = Lv - Lm_s
row('Music', 'under the voice while talking (target ~20 dB)', d_s >= 17.5, f'voice {Lv:.1f} / music {Lm_s:.1f} LUFS -> {d_s:.1f} dB', warn=d_s >= 15)
row('Music', 'never swells over the voice in pauses', Lm_g <= Lv - 6, f'music in pauses {Lm_g:.1f} LUFS ({Lv - Lm_g:.1f} dB under the voice)')
row('Music', 'bed audible (not lost)', Lm_s >= Lv - 32, f'{d_s:.1f} dB under (<= 32)', warn=True)
# ---- SFX
pk = []
for i in range(1, k - 1):
    if Ms[i] > -45 and Ms[i] >= Ms[i - 1] and Ms[i] >= Ms[i + 1]: pk.append(Ms[i])
loud = max(pk) if pk else -70
row('SFX', 'no hit louder than the voice (+3 LU max)', loud <= Lv + 3, f'loudest hit {loud:.1f} LUFS vs voice {Lv:.1f}')
soft = float(np.median(pk)) if pk else -70
row('SFX', 'hits audible (median >= voice - 24 LU)', soft >= Lv - 24, f'median hit {soft:.1f} LUFS ({len(pk)} hits)', warn=soft >= Lv - 28)
voiced = speech & (Mv > Lv - 10)
dd = (Mv - Ms)[voiced]
mask = float(np.mean(dd < 4)) * 100 if voiced.sum() else 0
worst = [round(float(x), 1) for x in tc[voiced][dd < 4][:8]]
row('SFX', 'never masks a word (SFX within 4 LU of the voice while talking)', mask <= 3,
    f'{mask:.1f} % of voiced windows (<= 3 %)' + (f'; at {worst} s' if worst else ''), warn=mask <= 6)
row('Music', 'under the voice while talking (target ~20 dB)', True, 'see above') if False else None
# ---- FINAL MIX
if os.path.exists('reel.mp4'):
    fm = os.path.join(st, 'final.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'reel.mp4', '-vn', '-ac', '2', '-ar', str(sr), fm], check=True)
    y, _ = sf.read(fm); L = pyln.Meter(sr).integrated_loudness(y)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', fm, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    import re
    m = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr); tp = float(m[-1]) if m else 0.0
    lra = re.findall(r'LRA:\s+([\d.]+) LU', r.stderr); lra = float(lra[-1]) if lra else 0.0
    row('Mix', 'integrated loudness -14 LUFS +-1', abs(L + 14) <= 1, f'{L:.1f} LUFS')
    row('Mix', 'true peak <= -1 dBTP', tp <= -1.0, f'{tp:.1f} dBTP')
    row('Mix', 'loudness range (LRA) <= 9 LU', lra <= 9, f'{lra:.1f} LU', warn=lra <= 11)
    Mf = mom(y.mean(1))
    row('Mix', 'opening hit not a jump-scare (first 1 s <= mix + 6 LU)', Mf[:8].max() <= L + 6, f'max {Mf[:8].max():.1f} LUFS')
    end_i = int((dur - 0.6) / 0.1); quiet = Mf[:end_i] < -42; run = mx = 0
    for q in quiet: run = run + 1 if q else 0; mx = max(mx, run)
    row('Mix', 'no dropout / dead air before the end', mx * 0.1 <= 0.45, f'longest quiet stretch {mx * 0.1:.1f} s')
hdr = ['# Audio audit', '', f'**Result: {"PASS" if not fails else "FIX"}** ({fails} fail, {warns} warn)', '',
       '| Area | Check | Result | Detail |', '|---|---|---|---|']
open(os.path.join(qc, 'audio_report.md'), 'w').write('\n'.join(hdr + rows) + '\n')
print('\n'.join(rows)); print('AUDIO', 'PASS' if not fails else 'FIX')
for f in ('vo.wav', 'music.wav', 'sfx.wav', 'mix_check.wav', 'final.wav'):
    try: os.remove(os.path.join(st, f))
    except OSError: pass
sys.exit(0 if not fails else 1)
