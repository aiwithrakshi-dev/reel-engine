# Day 7 (Kling 4.0: one AI shot, keyframes, references) speech islands, source seconds
# silencedetect -35 dB d=0.15; pauses >= 0.35 s cut, 0.12 s kept after / 0.10 s before; 2.91-3.15 breath dropped
import math
ISL = [(0.08,1.099),(1.419,2.467),(2.650,5.367),(5.762,10.990),(11.244,14.991),(15.188,17.128),
       (17.323,18.207),(18.406,20.767),(20.916,28.152),(28.306,36.33)]
def snapped():
    out=[]; t=0.0
    for a,b in ISL:
        a2=round(math.floor(a/0.04+1e-6)*0.04,2); b2=round(math.ceil(b/0.04-1e-6)*0.04,2)
        out.append((a2,b2,t,t+(b2-a2))); t+=b2-a2
    return out
def src_to_reel(ts):
    best=None
    for a,b,r0,r1 in snapped():
        if a-1e-6<=ts<=b+1e-6: return r0+(ts-a)
        if ts<a and best is None: best=r0
    return best
def reel_to_src(t):
    for a,b,r0,r1 in snapped():
        if t < r1-1e-9: return a+max(0,t-r0)
    a,b,r0,r1=snapped()[-1]; return b+(t-r1)
if __name__=='__main__':
    for i,(a,b,r0,r1) in enumerate(snapped(),1): print(i,f'{a:.2f}-{b:.2f}  reel {r0:.2f}-{r1:.2f}')
