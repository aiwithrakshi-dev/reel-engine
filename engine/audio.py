# Audio: VO chain, music bed (Black_Asphalt re-sequenced on the beat with drop-outs), procedural SFX,
# B-roll stereo proof in cutaway 2, sidechain duck, loudness to -14 LUFS / -1 dBTP.
import sys, json, math, random, subprocess, os
import numpy as np, soundfile as sf, librosa
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__))
from islands import snapped
SR = 48000; WD = '/home/claude/work/'
WK = json.load(open(WD + 'words_final.json')); wt = lambda k: WK[k]
J = [s[2] for s in snapped()][1:]; VO_END = snapped()[-1][3]; END_T = round(VO_END + 0.82, 2); HIT_T = VO_END + 0.28
N = int(END_T * SR) + SR // 10
F = lambda t: int(round(t * 30)); fr = lambda f: f / 30.0
rng = np.random.default_rng(3)
def sh(x): return subprocess.run(x, shell=True, check=True)

# ---------------------------------------------------------------- SFX synthesis
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d); return e
def bandsweep(n, f0, f1, q=0.6):
    """noise whose band centre sweeps f0->f1 (STFT mask)."""
    x = rng.normal(0, 1, n + 2048); S = librosa.stft(x, n_fft=1024, hop_length=256)
    fr_ = librosa.fft_frequencies(sr=SR, n_fft=1024); T = S.shape[1]
    c = np.exp(np.linspace(np.log(f0), np.log(f1), T))
    M = np.exp(-((np.log(fr_[:, None] + 1) - np.log(c[None, :])) ** 2) / (2 * q * q))
    y = librosa.istft(S * M, hop_length=256, length=n + 2048)[:n]; return y / (np.abs(y).max() + 1e-9)
def sine_sweep(n, f0, f1):
    f = np.exp(np.linspace(np.log(f0), np.log(f1), n)); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def lp(x, fc): b, a = signal.butter(2, fc / (SR / 2)); return signal.lfilter(b, a, x)
def hp(x, fc): b, a = signal.butter(2, fc / (SR / 2), 'high'); return signal.lfilter(b, a, x)

def s_impact(big=1.0):
    n = int(SR * (0.9 + 0.6 * (big > 1))); x = sine_sweep(n, 70, 34) * env(n, 0.001, 0.32 * big) * 1.0
    x += lp(rng.normal(0, 1, n), 2500) * env(n, 0.0005, 0.03) * 0.8
    x += hp(rng.normal(0, 1, n), 4000) * env(n, 0.0005, 0.012) * 0.4
    if big > 1:  # tail
        x += lp(rng.normal(0, 1, n), 900) * env(n, 0.01, 0.45) * 0.18
    return np.tanh(x * 1.6) * 0.9
def s_glitch(L=0.2):
    n = int(SR * L); x = np.zeros(n); i = 0
    while i < n:
        seg = int(SR * rng.uniform(0.008, 0.03)); fq = rng.uniform(300, 3500)
        t = np.arange(min(seg, n - i)) / SR; sq = np.sign(np.sin(2 * np.pi * fq * t)) * rng.uniform(0.2, 0.8)
        if rng.random() < 0.3: sq = np.round(rng.normal(0, 1, len(t)) * 3) / 3 * 0.5
        x[i:i + len(t)] = sq; i += seg + int(SR * rng.uniform(0, 0.012))
    return hp(x, 200) * np.linspace(1, 0.4, n) * 0.5
def s_tick(): n = int(SR * 0.012); return hp(rng.normal(0, 1, n), 3000) * env(n, 0.0002, 0.002) * 0.6
def s_blip():
    n = int(SR * 0.05); fq = rng.choice([1200, 1500, 1800, 2400]); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * fq * t)) * env(n, 0.001, 0.015) * 0.25
def s_zap():
    n = int(SR * 0.42); x = bandsweep(n, 400, 7000, 0.5) * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * 0.7
    t = np.arange(n) / SR; buzz = signal.sawtooth(2 * np.pi * (90 + 60 * np.sin(2 * np.pi * 23 * t)) * t) * 0.18 * np.sin(np.linspace(0, np.pi, n))
    return np.tanh((x + hp(buzz, 300)) * 1.5) * 0.6
def s_whoosh(L=0.38): n = int(SR * L); return bandsweep(n, 250, 3500, 0.7) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.6
def s_boom(): n = int(SR * 0.6); return np.tanh(sine_sweep(n, 62, 38) * env(n, 0.003, 0.22) * 1.8) * 0.75
def s_riser(L):
    n = int(SR * L); t = np.linspace(0, 1, n)
    x = bandsweep(n, 300, 6000, 0.6) * t ** 2 * 0.5 + sine_sweep(n, 180, 1400) * t ** 3 * 0.15
    return x
def s_pop():
    n = int(SR * 0.09); x = sine_sweep(n, 1100, 260) * env(n, 0.0005, 0.03) * 0.7
    x[:60] += rng.normal(0, 0.4, 60); return x
def s_swish(): n = int(SR * 0.16); return bandsweep(n, 1500, 7000, 0.5) * np.sin(np.linspace(0, np.pi, n)) * 0.4

# ---------------------------------------------------------------- SFX events (mirror render.py timeline)
EV = []
def ev(t, snd, db=0.0, pan=0.0): EV.append((t, snd, db, pan))
ev(0.0, s_impact(1.2), -1); ev(0.0, s_glitch(0.25), -8)
# big word type-ons: per-letter ticks (-28 dB) + one data blip/glitch burst at reveal start
TYPE = [  # (start_time, n_letters, step_frames)
    (wt('ಕಟ್ಇಲ್ಲ'), 3, 2), (wt('ಎಡಿಟಿಂಗ್'), 7, 2), (wt('ಒಂದೇ2'), 3, 2), (wt('ಟೇಕಲ್ಲಿ'), 4, 2), (wt('ಸೇವ್'), 4, 2),
    (wt('ಕೀಫ್ರೇಮ್ಸ್'), 8, 2), (wt('ಬಳಸ್ತೀನಿ'), 6, 2), (wt('30'), 2, 2), (wt('ಸೆಕೆಂಡ್'), 7, 2), (wt('ಹತ್ತು'), 2, 2),
    (wt('ಕೀಫ್ರೇಮ್ಸ್2'), 9, 2), (wt('ಕಥೆಯಲ್ಲಿ'), 5, 2), (wt('ಒಂದೊಂದು'), 6, 2), (wt('ಕೀಫ್ರೇಮಲ್ಲಿ'), 4, 2), (wt('ಒಂದೇ4'), 4, 2),
    (wt('ಹದಿನೈದು'), 2, 2), (wt('ರೆಫರೆನ್ಸ್'), 10, 2), (wt('ಸ್ಟೀರಿಯೋ'), 6, 2), (wt('ಸೌಂಡ್'), 5, 2), (wt('ಕೀಫ್ರೇಮ್ಸ್3') - 2 / 30, 11, 1),
    (wt('ಹತ್ತು2'), 2, 2), (wt('ಪ್ರಾಂಪ್ಟ್'), 7, 2), (wt('ಪ್ರಾಂಪ್ಟ್2'), 6, 2)]
for t0, n, st in TYPE:
    ev(t0, s_blip(), -17, rng.uniform(-.4, .4)); ev(t0, s_glitch(0.09), -22)
    for i in range(n): ev(t0 + i * st / 30, s_tick(), -28, rng.uniform(-.5, .5))
# neon streaks (zap-whoosh)
for jt in (J[0], J[6], J[12]): ev(jt - 2 / 30, s_zap(), -6)
# halftone rings (air whoosh + low boom)
r9c = fr(F(wt('ಹದಿನೈದು')) - 2)
for t0 in (J[1], J[3], J[4], J[7], r9c, J[13]): ev(t0 - 0.12, s_whoosh(0.3), -11); ev(t0, s_boom(), -6)
# vertical smear
ev(J[2] - 1 / 30, s_swish(), -9); ev(J[2] - 1 / 30, s_glitch(0.1), -16)
# risers into cutaways + swooshes
ev(9.95 if J[4] - 9.95 > 0.5 else J[4] - 0.75, s_riser(J[4] - 9.95), -12); ev(J[4] - 7 / 30, s_whoosh(0.3), -8)
ev(J[8] - 0.42, s_riser(0.42), -12); ev(J[10] - 0.6, s_riser(0.6), -13); ev(J[10] - 7 / 30, s_whoosh(0.3), -8)
# slam hits on cutaway entries
for t0 in (J[4], J[8], J[10]): ev(t0, s_impact(), -6)
ev(wt('30'), s_impact(), -9)
# exits: negative flash = glitch burst + hit
for t0 in (J[5], J[9], J[11]): ev(t0, s_glitch(0.16), -10); ev(t0, s_impact(), -10)
# card / pill / icon pops
POPS = [J[1] + 9 / 30, wt('AI'), wt('ಮಾಡಿದೀನಿ'), wt('ಸೇವ್'), J[4] + 4 / 30, J[4] + 8 / 30, wt('ನಟನ'), wt('ಪ್ರಾಪ್ಸ್'), wt('ಲುಕ್'),
        J[8] + 3 / 30, fr(F(J[12] + 0.1))]
f1 = F(wt('ಕೀಫ್ರೇಮ್ಸ್')) + 4; POPS += [fr(f1 + 4 * k) for k in range(3)]
POPS += [fr(F(wt('ಒಂದೊಂದು')) + 11 * k) for k in range(3)]
POPS += [fr(F(wt('ಇಮೇಜಸ್')) + 3 * k) for k in range(3)]
POPS += [fr(F(J[13]) + 3), wt('ಹತ್ತನ್ನೂ'), wt('ಕಳಿಸ್ತೀನಿ'), fr(max(F(wt('ಬೇಕಾ')), F(wt('ಪ್ರಾಂಪ್ಟ್')) + 14))]
for t0 in POPS: ev(t0, s_pop(), -10, rng.uniform(-.3, .3))
ev(wt('ರೀತಿ'), s_pop(), -10); ev(wt('ರೀತಿ') + 0.02, s_tick(), -14)
# 10 rapid pops (fan) and 10 deal ticks (grid)
fan0 = F(wt('ಕೀಫ್ರೇಮ್ಸ್2')) + 2 * 9 + 4
for k in range(10): ev(fr(fan0 + 2 * k), s_pop(), -14, -0.6 + k * 0.13)
for k in range(10): ev(fr(F(wt('ಇವು')) + 2 * k), s_tick(), -16, -0.5 + k * 0.11); ev(fr(F(wt('ಇವು')) + 2 * k), s_pop(), -18)
# cutaway 3 cut hits
d3 = (J[11] - J[10]) / 3
for k in (1, 2): ev(J[10] + k * d3, s_impact(), -13)
# marker swishes
ev(fr(F(wt('ಮುಂದೆ')) - 1), s_swish(), -11); ev(fr(F(wt('ಕಮೆಂಟ್'))), s_swish(), -11)
# CTA hold flicker blips + final button hit
for k in range(4): ev(VO_END + 0.05 + 0.18 * k, s_blip(), -26)
ev(HIT_T, s_impact(1.6), 0)

def place(buf, t, x, db=0.0, pan=0.0):
    i = int(t * SR); g = 10 ** (db / 20); l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    n = min(len(x), len(buf) - i)
    if n <= 0 or i < 0: return
    buf[i:i + n, 0] += x[:n] * g * l * 1.414; buf[i:i + n, 1] += x[:n] * g * r * 1.414
sfx = np.zeros((N, 2))
for t, x, db, pan in EV: place(sfx, t, x, db, pan)

# ---------------------------------------------------------------- music bed (re-sequenced on bar lines)
m, msr = librosa.load(WD + 'music/Black_Asphalt.mp3', sr=SR, mono=False)
m = m.T; BEAT = 0.46365; BAR = 4 * BEAT; B0 = 3.727; NB = 12
body = m[int(B0 * SR):int((B0 + NB * BAR) * SR)]
loop = np.concatenate([body] * 4)
SLAMS = [0.0, J[4], J[5], J[8], J[9], J[10], J[11]]; DROP = 0.17
music = np.zeros((N, 2)); p = 0.0
for k, s0 in enumerate(SLAMS):
    s1 = (SLAMS[k + 1] - DROP) if k + 1 < len(SLAMS) else HIT_T
    L = s1 - s0; a = int(p * SR); n = int(L * SR)
    seg = loop[a:a + n].copy()
    fi = int(0.003 * SR); fo = int(0.012 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]; seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    music[int(s0 * SR):int(s0 * SR) + len(seg)] += seg
    p = math.ceil((p + (SLAMS[k + 1] - s0 if k + 1 < len(SLAMS) else L)) / BAR - 1e-6) * BAR  # next slam lands on a downbeat
sf.write(WD + 'music_bed.wav', music, SR, subtype='PCM_24')

# ---------------------------------------------------------------- B-roll native audio in cutaway 2, auto-panned L -> R
b, bsr = librosa.load(WD + 'broll_audio.wav', sr=SR, mono=True, offset=24.125, duration=J[9] - J[8] + 0.05)
n = len(b); pan = np.linspace(-1, 1, n)
br = np.zeros((N, 2)); i0 = int(J[8] * SR)
gl = np.cos((pan + 1) * np.pi / 4); gr = np.sin((pan + 1) * np.pi / 4)
fade = np.ones(n); k = int(0.03 * SR); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
br[i0:i0 + n, 0] = b * gl * fade; br[i0:i0 + n, 1] = b * gr * fade
# envelope per video frame for the pulsing speaker icons
fl = int(SR / 30); Le, Re = [], []
for q in range(0, n, fl):
    Le.append(float(np.sqrt(np.mean((b[q:q + fl] * gl[q:q + fl]) ** 2)))); Re.append(float(np.sqrt(np.mean((b[q:q + fl] * gr[q:q + fl]) ** 2))))
mx = max(Le + Re) + 1e-9
json.dump({'L': [x / mx for x in Le], 'R': [x / mx for x in Re]}, open(WD + 'pan_env.json', 'w'))
sf.write(WD + 'broll_pan.wav', br, SR, subtype='PCM_24')
sf.write(WD + 'sfx.wav', sfx, SR, subtype='PCM_24')

# ---------------------------------------------------------------- VO chain + mix (ffmpeg)
vo = WD + 'vo_tight_raw.wav'
sh(f"ffmpeg -v error -y -i {vo} -af \"highpass=f=80,deesser=i=0.4:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4dB,apad=whole_dur={END_T}\" -ar {SR} {WD}vo_proc.wav")
fc = ("[1]volume=-14dB[mus];[0]asplit=2[vo][sc];[mus][sc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=260:makeup=1[duck];"
      "[2]volume=0dB[sfx];[3]volume=-14dB[br];[vo][duck][sfx][br]amix=inputs=4:normalize=0:duration=first[m]")
sh(f"ffmpeg -v error -y -i {WD}vo_proc.wav -i {WD}music_bed.wav -i {WD}sfx.wav -i {WD}broll_pan.wav -filter_complex \"{fc}\" -map \"[m]\" -t {END_T} -ar {SR} -c:a pcm_s24le {WD}mix_pre.wav")
sh(f'python3 {WD}scripts/master.py')
print('events', len(EV), 'END_T', END_T)
