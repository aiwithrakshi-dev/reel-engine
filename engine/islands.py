# Day 4 (Android Studio BYOA) speech islands, source seconds (silencedetect -35 dB; only pauses >= 0.35 s are cut)
ISL = [(0.00,6.11),(6.458,10.345),(10.683,16.508),(16.803,17.885),(18.03,20.087),(20.276,22.888),
       (23.094,26.498),(26.741,29.297),(29.453,32.51),(32.751,37.235),(37.435,41.13)]
def snapped():
    out=[]; t=0.0
    for a,b in ISL:
        import math; a2=round(math.floor(a/0.04+1e-6)*0.04,2); b2=round(math.ceil(b/0.04-1e-6)*0.04,2)
        out.append((a2,b2,t,t+(b2-a2))); t+=b2-a2
    return out
def src_to_reel(ts):
    for a,b,r0,r1 in snapped():
        if a-1e-6<=ts<=b+1e-6: return r0+(ts-a)
    return None
def reel_to_src(t):
    for a,b,r0,r1 in snapped():
        if t < r1-1e-9: return a+max(0,t-r0)
    a,b,r0,r1=snapped()[-1]; return b+(t-r1)
if __name__=='__main__':
    for i,(a,b,r0,r1) in enumerate(snapped(),1): print(i,f'{a:.2f}-{b:.2f}  reel {r0:.2f}-{r1:.2f}')
