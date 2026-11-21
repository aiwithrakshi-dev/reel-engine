# Repairs AI cap-crown flips (crown turns black with a white logo) by pasting the crown
# from the nearest clean frame, aligned by template matching on brim+face. Streams frames.
import cv2, numpy as np, json, subprocess
def frames():
    cap=cv2.VideoCapture('aroll_tight30.mp4')
    while True:
        ok,f=cap.read()
        if not ok: return
        yield f
def redscore(f):
    c=f[500:720,340:740].astype(int); b,g,r=c[...,0],c[...,1],c[...,2]
    return ((r>120)&(r>g*1.8)&(r>b*1.8)).mean()
def whitescore(f):
    c=f[470:600,380:690]; return (c.min(2)>190).mean()
rs=[];ws=[]
for f in frames(): rs.append(redscore(f)); ws.append(whitescore(f))
rs=np.array(rs); ws=np.array(ws); med=np.median(rs); wmed=np.median(ws); N=len(rs)
bad=[i for i in range(N) if (rs[i]<0.62*med or ws[i]>wmed+0.03) and (40<i<80 or 1130<i<1200)]
good=lambda j: j not in bad and rs[j]>0.85*med and ws[j]<wmed+0.015
def nearest_clean(i):
    for d in range(1,40):
        for j in (i+d,i-d):
            if 0<=j<N and good(j): return j
refs={i:nearest_clean(i) for i in bad}; need=set(refs.values())
store={}
for k,f in enumerate(frames()):
    if k in need: store[k]=f
H,W=1920,1080; mask=np.zeros((H,W),np.float32); cv2.ellipse(mask,(530,548),(200,82),0,0,360,1,-1)
mask[625:]=0; mask=cv2.GaussianBlur(mask,(0,0),9)
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','12','-pix_fmt','yuv420p','aroll_patched30.mp4'],stdin=subprocess.PIPE)
log=[]
for i,f in enumerate(frames()):
    if i in refs:
        ref=store[refs[i]]; tpl=ref[600:900,330:750]
        res=cv2.matchTemplate(f[560:960,280:800],tpl,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(res)
        dx,dy=loc[0]-50,loc[1]-40; M=np.float32([[1,0,dx],[0,1,dy]])
        sh=cv2.warpAffine(ref,M,(W,H),borderMode=cv2.BORDER_REPLICATE); mk=cv2.warpAffine(mask,M,(W,H))[...,None]
        f=(sh*mk+f*(1-mk)).astype(np.uint8); log.append(dict(reel_frame=i,reel_t=round(i/30,2),ref_frame=refs[i],dx=dx,dy=dy,match=round(float(mx),3)))
    ff.stdin.write(f.tobytes())
ff.stdin.close(); ff.wait()
json.dump(log,open('cap_patch_log.json','w'),indent=1); print('patched',[l['reel_frame'] for l in log]); print('min match',min(l['match'] for l in log))
