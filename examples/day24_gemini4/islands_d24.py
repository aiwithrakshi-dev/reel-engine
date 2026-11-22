# Day 24 (Gemini 4: Argon / Carbon, price doubles Dec 1) speech islands, source seconds
# silencedetect -35 dB d=0.15; pauses >= 0.35 s cut, 0.12 s kept after / 0.10 s before; 2.91-3.15 breath dropped
import math
ISL = [(0.00,2.486),(3.530,6.695),(7.348,9.905),(10.037,11.555),(11.843,15.685),(16.027,18.699),
       (18.878,21.667),(21.911,26.922),(27.095,35.418),(35.584,39.49)]
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
