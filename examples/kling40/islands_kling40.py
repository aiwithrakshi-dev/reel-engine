# island table (source seconds) from Part B §3, verified against silencedetect -35 dB
ISL = [(0.92,2.75),(3.23,4.41),(4.76,8.66),(9.02,10.23),(10.32,12.80),(13.00,18.21),(18.41,20.43),
       (20.68,24.89),(25.13,31.79),(31.96,34.22),(34.52,36.39),(36.66,38.10),(38.45,41.08),(41.35,42.77),(42.99,44.74)]
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
