# Day 24 audio: VO chain, music bed (Drop_Point drop re-sequenced on bar lines with drop-outs), procedural SFX
# mirroring render_d24_60.py, sidechain duck, master -14 LUFS / limiter -2.9 dBTP.
import sys, json, math, os, subprocess
import numpy as np, soundfile as sf, librosa
from scipy import signal
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from islands_d24 import snapped
SR = 48000; WD = '/home/claude/d24/'
WL = json.load(open(WD + 'words_final_list.json')); _n = {}; WK = {}
for w_, s_, e_ in WL:
    k = ''.join(ch for ch in w_.lower() if ch.isalnum()); i = _n.get(k, 0); _n[k] = i + 1; WK[k + (str(i) if i else '')] = s_
WK['on1'] = 26.85
wt = lambda k: WK[k]
J = [s[2] for s in snapped()][1:]; VO_END = snapped()[-1][3]; END_T = round(VO_END + 0.82, 2); HIT_T = VO_END + 0.28
C1a, C1b, C2a, C3a, C3b = J[1], J[3], J[6], J[7], wt('so')
N = int(END_T * SR) + SR // 10
rng = np.random.default_rng(24)
def sh(x): return subprocess.run(x, shell=True, check=True)

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def bandsweep(n, f0, f1, q=0.6):
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
    n = int(SR * (0.9 + 0.6 * (big > 1))); x = sine_sweep(n, 70, 34) * env(n, 0.001, 0.32 * big)
    x += lp(rng.normal(0, 1, n), 2500) * env(n, 0.0005, 0.03) * 0.8 + hp(rng.normal(0, 1, n), 4000) * env(n, 0.0005, 0.012) * 0.4
    if big > 1: x += lp(rng.normal(0, 1, n), 900) * env(n, 0.01, 0.45) * 0.18
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
    return bandsweep(n, 300, 6000, 0.6) * t ** 2 * 0.5 + sine_sweep(n, 180, 1400) * t ** 3 * 0.15
def s_pop():
    n = int(SR * 0.09); x = sine_sweep(n, 1100, 260) * env(n, 0.0005, 0.03) * 0.7; x[:60] += rng.normal(0, 0.4, 60); return x
def s_swish(): n = int(SR * 0.16); return bandsweep(n, 1500, 7000, 0.5) * np.sin(np.linspace(0, np.pi, n)) * 0.4
def s_slam():
    n = int(SR * 0.07); return np.tanh((lp(rng.normal(0, 1, n), 1800) * env(n, 0.0005, 0.02) + sine_sweep(n, 160, 60) * env(n, 0.001, 0.03)) * 2) * 0.7
def s_sub():
    n = int(SR * 0.7); return np.tanh(sine_sweep(n, 55, 36) * env(n, 0.004, 0.3) * 2.2) * 0.8

EV = []
def ev(t, snd, db=0.0, pan=0.0): EV.append((t, snd, db, pan))
# hook strip_slam: 5 fast slams (one per strip, 3 frames apart at 60 fps) + sub hit
for k in range(5): ev(k * 3 / 60, s_slam(), -4, (-1) ** k * 0.4)
ev(16 / 60, s_sub(), -2)
# big-word type-ons: blip + glitch at the first letter, a tick per letter (1 letter / frame at 30 fps)
TYPE = [(wt('gemini'), 6), (wt('4'), 1), (wt('pro'), 3), (wt('doubles'), 7), (wt('real'), 4), (wt('models'), 6),
        (wt('argon'), 5), (wt('carbon'), 6), (wt('argon1'), 5), (wt('carbon1'), 6), (wt('cybersecurity'), 5), (wt('teams'), 5),
        (wt('gemini2'), 6), (wt('pro1'), 3), (wt('doesnt'), 7), (wt('exist'), 5), (wt('price1'), 5), (wt('doubles1'), 7),
        (wt('december'), 3), (wt('1st'), 1), (wt('batch'), 5), (wt('jobs'), 4), (wt('caching'), 7), (wt('model'), 5)]
for t0, n in TYPE:
    ev(t0, s_blip(), -17, rng.uniform(-.4, .4)); ev(t0, s_glitch(0.09), -22)
    for i in range(n): ev(t0 + i / 30, s_tick(), -28, rng.uniform(-.5, .5))
# jump-cut devices
for jt in (J[0], J[4], J[8]): ev(jt - 2 / 30, s_zap(), -6)                       # neon streaks
for t0 in (C1a, J[5], C2a, C3a): ev(t0 - 0.12, s_whoosh(0.3), -11); ev(t0, s_boom(), -6)   # halftone rings
ev(C2a - 1 / 30, s_swish(), -9); ev(C2a - 1 / 30, s_glitch(0.1), -16)                 # vertical smear
ev(C1a - 0.55, s_riser(0.55), -12); ev(C1a - 7 / 30, s_whoosh(0.3), -8)               # red swoosh into cutaway 1
for t0 in (C1a, C2a, C3a): ev(t0, s_impact(), -6)                                       # cutaway slams
for t0 in (C1b, C3b): ev(t0, s_glitch(0.16), -10); ev(t0, s_impact(), -10)               # cutaway exits
# components: pops on every card / tile / pill / badge, glitch on strike-through and dissolves
POPS = [wt('pro') + 0.25, wt('price'), wt('next'), wt('41'), wt('argon'), wt('carbon'), wt('carbon') + 9 / 30,
        wt('app'), wt('api'), wt('googles'), wt('teams'), wt('can2'), wt('video'), wt('reports'), wt('argons'), wt('api1'), wt('price1'),
        wt('jobs'), wt('caching'), wt('model') + 0.1, wt('gemini3'), wt('send')]
for t0 in POPS: ev(t0, s_pop(), -10, rng.uniform(-.3, .3))
ev(wt('pro') + 6 / 30, s_glitch(0.14), -11); ev(wt('pro') + 6 / 30, s_swish(), -12)      # strike-through
ev(wt('name'), s_impact(), -9); ev(wt('name'), s_glitch(0.12), -14)                     # NOT A REAL MODEL stamp
ev(wt('doubles1'), s_impact(), -11); ev(wt('doubles1'), s_slam(), -8)                    # new price column slams in
for t0 in (wt('argon') - 4 / 30, wt('that') - 4 / 30, wt('december') - 3 / 30, wt('set') - 4 / 30): ev(t0, s_glitch(0.12), -13)
ev(wt('comment') - 1 / 30, s_swish(), -11)
for k in range(4): ev(VO_END + 0.05 + 0.18 * k, s_blip(), -26)
ev(HIT_T, s_impact(1.6), 0)

def place(buf, t, x, db=0.0, pan=0.0):
    i = int(t * SR); g = 10 ** (db / 20); l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    n = min(len(x), len(buf) - i)
    if n <= 0 or i < 0: return
    buf[i:i + n, 0] += x[:n] * g * l * 1.414; buf[i:i + n, 1] += x[:n] * g * r * 1.414
sfx = np.zeros((N, 2))
for t, x, db, pan in EV: place(sfx, t, x, db, pan)

# music: Drop_Point (129.2 BPM) — the drop section re-sequenced on bar lines, drop-out 0.17 s before each slam
m, _ = librosa.load('/home/claude/work/music/Pressure_Line.mp3', sr=SR, mono=False); m = m.T
BEAT = 60 / 99.4; BAR = 4 * BEAT; B0 = 6.06; NB = 8              # slower, calmer bed (Rakshith, 22 Nov: music far under the voice)
body = m[int(B0 * SR):int((B0 + NB * BAR) * SR)]
loop = np.concatenate([body] * 6)
SLAMS = [0.0, C1a, C1b, C2a, C3a, C3b, J[8]]; DROP = 0.17
music = np.zeros((N, 2)); p = 0.0
for k, s0 in enumerate(SLAMS):
    s1 = (SLAMS[k + 1] - DROP) if k + 1 < len(SLAMS) else HIT_T
    L = s1 - s0; a = int(p * SR); n = int(L * SR); seg = loop[a:a + n].copy()
    fi = int(0.003 * SR); fo = int(0.012 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]; seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    music[int(s0 * SR):int(s0 * SR) + len(seg)] += seg
    p = math.ceil((p + (SLAMS[k + 1] - s0 if k + 1 < len(SLAMS) else L)) / BAR - 1e-6) * BAR
sf.write(WD + 'music_bed.wav', music, SR, subtype='PCM_24'); sf.write(WD + 'sfx.wav', sfx, SR, subtype='PCM_24')

vo = WD + 'vo_tight_raw.wav'
sh(f"ffmpeg -v error -y -i {vo} -af \"highpass=f=80,deesser=i=0.4:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4dB,apad=whole_dur={END_T}\" -ar {SR} {WD}vo_proc.wav")
fc = ("[1]volume=-17dB,highpass=f=60,lowpass=f=9000,equalizer=f=1800:t=q:w=1.2:g=-6,equalizer=f=3500:t=q:w=1.2:g=-4[mus];[0]asplit=2[vo][sc];"
      "[mus][sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450:makeup=1[duck];[2]volume=-11dB[sfx];[vo][duck][sfx]amix=inputs=3:normalize=0:duration=first[m]")
sh(f"ffmpeg -v error -y -i {WD}vo_proc.wav -i {WD}music_bed.wav -i {WD}sfx.wav -filter_complex \"{fc}\" -map \"[m]\" -t {END_T} -ar {SR} -c:a pcm_s24le {WD}mix_pre.wav")
sh(f'python3 /home/claude/reel-engine/engine/master.py {WD}mix_pre.wav {WD}mix_final.wav')
# no-music version (optional deliverable)
sh(f"ffmpeg -v error -y -i {WD}vo_proc.wav -i {WD}sfx.wav -filter_complex \"[1]volume=-11dB[s];[0][s]amix=inputs=2:normalize=0:duration=first[m]\" -map \"[m]\" -t {END_T} -ar {SR} -c:a pcm_s24le {WD}mix_pre_nomusic.wav")
sh(f'python3 /home/claude/reel-engine/engine/master.py {WD}mix_pre_nomusic.wav {WD}mix_final_nomusic.wav')
print('events', len(EV), 'END_T', END_T)
