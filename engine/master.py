# loudness to -14 LUFS integrated with a true-peak lookahead limiter (ceiling -1.2 dBTP)
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x, sr = sf.read('/home/claude/d4/mix_pre.wav'); meter = pyln.Meter(sr)
def tp(y): return 20*np.log10(np.abs(signal.resample_poly(y, 4, 1, axis=0)).max()+1e-12)
def limit(y, ceil_db=-2.9):
    c = 10**(ceil_db/20); up = np.abs(signal.resample_poly(y, 4, 1, axis=0)).max(1).reshape(-1, 4).max(1)[:len(y)]
    g = np.minimum(1, c/np.maximum(up, 1e-9))
    la = int(0.003*sr); g = np.minimum.accumulate(np.concatenate([g[la:], np.ones(la)])[::-1])[::-1] if False else g
    # lookahead min filter then smooth release
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(g, size=2*la+1, mode='nearest')
    rel = np.exp(-1/(0.06*sr)); out = np.empty_like(g); s = 1.0
    for i in range(len(g)):
        s = g[i] if g[i] < s else g[i] + (s - g[i])*rel; out[i] = s
    return y*out[:, None]
y = x.copy()
for it in range(4):
    L = meter.integrated_loudness(y); y = y*10**((-14.0-L)/20); y = limit(y)
    print(it, 'LUFS', round(meter.integrated_loudness(y),2), 'TP', round(tp(y),2))
sf.write('/home/claude/d4/mix_final.wav', y, sr, subtype='PCM_24')
