import numpy as np, soundfile as sf, sys
sys.path.insert(0,'scripts'); from islands import snapped
x,sr=sf.read('main_stereo.wav'); 
segs=snapped(); total=segs[-1][3]; N=int(round(total*sr))
out=np.zeros((N+sr//10,x.shape[1])); xf=int(0.010*sr)  # 10ms each side = 20ms crossfade
for i,(a,b,r0,r1) in enumerate(segs):
    s=int(round(a*sr))-xf; e=int(round(b*sr))+xf; seg=x[max(0,s):e].copy()
    ramp=np.linspace(0,1,2*xf)[:,None]
    if i>0: seg[:2*xf]*=ramp
    if i<len(segs)-1: seg[-2*xf:]*=ramp[::-1]
    d=int(round(r0*sr))-xf
    if d<0: seg=seg[-d:]; d=0
    out[d:d+len(seg)]+=seg
out=out[:N]; sf.write('vo_tight_raw.wav',out,sr,subtype='PCM_24'); print(N/sr)
