# Audio: VO chain, music bed (Black_Asphalt re-sequenced on the beat with drop-outs), procedural SFX,
# B-roll stereo proof in cutaway 2, sidechain duck, loudness to -14 LUFS / -1 dBTP.
import sys, json, math, random, subprocess, os
import numpy as np, soundfile as sf, librosa
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__))
from islands import snapped
SR = 48000; WD = '/home/claude/d4/'
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

# ---------------------------------------------------------------- SFX events (mirror render_d4.py)
EV = []
def ev(t, snd, db=0.0, pan=0.0): EV.append((t, snd, db, pan))
C1a, C2b = 2.15, 12.10
ev(0.0, s_impact(1.2), -1); ev(0.0, s_glitch(0.25), -8)
TYPE = [(wt('claude'), 6, 1), (wt('codex'), 6, 1), (wt('android'), 7, 1), (wt('studio'), 6, 1), (wt('test'), 4, 1), (wt('agent'), 5, 1), (wt('stable'), 6, 1), (wt('freelancers'), 11, 1),
        (wt('40'), 3, 1), (wt('agents'), 6, 1), (wt('claude2') - 0.1, 8, 1), (wt('difference'), 11, 1), (wt('project'), 7, 1),
        (wt('build'), 10, 1), (wt('previews'), 8, 1), (wt('run'), 10, 1), (wt('check'), 9, 1), (wt('own3'), 7, 1),
        (wt('plan') - 0.2, 8, 1), (wt('agents2'), 6, 1), (wt('days'), 4, 1), (wt('build2'), 5, 1)]
for t0, n, st in TYPE:
    ev(t0, s_blip(), -17, rng.uniform(-.4, .4)); ev(t0, s_glitch(0.09), -22)
    for i in range(n): ev(t0 + i * st / 30, s_tick(), -28, rng.uniform(-.5, .5))
for jt in (J[2], J[9]): ev(jt - 2 / 30, s_zap(), -6)
ev(C1a, s_zap(), -10)
for t0 in (C1a, J[1], J[3], J[7]): ev(t0 - 0.12, s_whoosh(0.3), -11); ev(t0, s_boom(), -6)
ev(J[4] - 1 / 30, s_swish(), -9); ev(J[4] - 1 / 30, s_glitch(0.1), -16)
for t0, L in ((C1a, 0.5), (J[1], 0.6), (J[5], 0.6)): ev(t0 - L, s_riser(L), -12); ev(t0 - 7 / 30, s_whoosh(0.3), -8)
for t0 in (C1a, J[1], J[5], J[7]): ev(t0, s_impact(), -6)
for t0 in (J[0], C2b, J[6], J[8]): ev(t0, s_glitch(0.16), -10); ev(t0, s_impact(), -10)
for t0 in (wt('test') - 1 / 30, wt('check')): ev(t0, s_impact(), -12)
POPS = [wt('claude') + 2 / 30, wt('codex') + 2 / 30, wt('release'), wt('not'), wt('claude2'), wt('codex2'), wt('juni'), wt('anti'),
        wt('project') + 2 / 30, wt('build') + 2 / 30, wt('composed') + 2 / 30, wt('already'), wt('apps'), wt('weeks'),
        wt('comment') + 4 / 30, wt('guide'), wt('guide') + 2 / 30, wt('5'), wt('send')]
POPS += [wt('client') + k * 0.1 for k in range(3)]
for t0 in POPS: ev(t0, s_pop(), -10, rng.uniform(-.3, .3))
for t0 in (wt('project'), wt('build'), wt('composed')): ev(t0 + 4 / 30, s_tick(), -14)
for t0 in (wt('beta'), wt('weeks') + 0.1, wt('stable') - 4 / 30, wt('days') - 4 / 30): ev(t0, s_glitch(0.12), -13)
for k in ('settings', 'tools', 'ai', 'comment', 'now', 'client'): ev(wt(k) - 1 / 30, s_swish(), -11)
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
SLAMS = [0.0, 2.15, J[0], J[1], 12.10, J[5], J[6], J[7], J[8]]; DROP = 0.17
music = np.zeros((N, 2)); p = 0.0
for k, s0 in enumerate(SLAMS):
    s1 = (SLAMS[k + 1] - DROP) if k + 1 < len(SLAMS) else HIT_T
    L = s1 - s0; a = int(p * SR); n = int(L * SR)
    seg = loop[a:a + n].copy()
    fi = int(0.003 * SR); fo = int(0.012 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]; seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    music[int(s0 * SR):int(s0 * SR) + len(seg)] += seg
    p = math.ceil((p + (SLAMS[k + 1] - s0 if k + 1 < len(SLAMS) else L)) / BAR - 1e-6) * BAR  # next slam lands on a downbeat
sf.write(WD + 'music_bed.wav', music, SR, subtype='PCM_24')

br = np.zeros((N, 2)); sf.write(WD + 'broll_pan.wav', br, SR, subtype='PCM_24')
sf.write(WD + 'sfx.wav', sfx, SR, subtype='PCM_24')

# ---------------------------------------------------------------- VO chain + mix (ffmpeg)
vo = WD + 'vo_tight_raw.wav'
sh(f"ffmpeg -v error -y -i {vo} -af \"highpass=f=80,deesser=i=0.4:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4dB,apad=whole_dur={END_T}\" -ar {SR} {WD}vo_proc.wav")
fc = ("[1]volume=-14dB[mus];[0]asplit=2[vo][sc];[mus][sc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=260:makeup=1[duck];"
      "[2]volume=0dB[sfx];[3]volume=-14dB[br];[vo][duck][sfx][br]amix=inputs=4:normalize=0:duration=first[m]")
sh(f"ffmpeg -v error -y -i {WD}vo_proc.wav -i {WD}music_bed.wav -i {WD}sfx.wav -i {WD}broll_pan.wav -filter_complex \"{fc}\" -map \"[m]\" -t {END_T} -ar {SR} -c:a pcm_s24le {WD}mix_pre.wav")
sh(f'python3 {WD}scripts/master.py')
print('events', len(EV), 'END_T', END_T)
