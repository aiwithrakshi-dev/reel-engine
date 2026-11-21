# Day-4 cap artifact: the AI crown intermittently grows a big white logo. Detect bright, unsaturated pixels on the
# crown (inside the person matte, above the red brim, away from the white piping) and inpaint them crown-grey.
import cv2, numpy as np, subprocess, json, sys
def fix(f, al, thr=250):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV); h,s,v=[hsv[...,i].astype(int) for i in range(3)]
    A=al>140
    y0,y1,x0,x1=380,700,250,800
    sub=(slice(y0,y1),slice(x0,x1))
    red=(((h<9)|(h>168))&(s>90)&(v>70))[sub]
    a=A[sub]
    crown=np.zeros_like(a)
    for x in range(a.shape[1]):
        col=np.where(a[:,x])[0]
        if len(col)==0: continue
        t=col[0]; rr=np.where(red[t:,x])[0]
        b=t+rr[0]-9 if len(rr) else min(a.shape[0],t+80)
        if b>t+3: crown[t+3:b,x]=True
    dist=cv2.distanceTransform((~red).astype(np.uint8),cv2.DIST_L2,3)
    logo=crown&(v[sub]>120)&(s[sub]<80)&(dist>16)
    nl,lab,st,_=cv2.connectedComponentsWithStats(logo.astype(np.uint8))
    keep=np.zeros_like(logo)
    for k in range(1,nl):
        if st[k,4]>=60: keep|=lab==k
    n=int(keep.sum())
    if n<thr: return f,n
    body=crown&~cv2.dilate(keep.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)&(v[sub]<110)
    if body.sum()<200: return f,n
    fs=f[sub].astype(np.float32); base=np.median(fs[body],axis=0)
    m=cv2.GaussianBlur(cv2.dilate(keep.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),(0,0),2.0)[...,None]
    lum=fs.mean(2,keepdims=True); tex=(lum-cv2.GaussianBlur(lum,(0,0),3)[...,None])*0.15
    rep=base[None,None,:]+tex
    out=f.copy(); out[sub]=np.clip(fs*(1-m)+rep*m,0,255).astype(np.uint8)
    return out,n
if __name__=='__main__':
    src,alp,out=sys.argv[1],sys.argv[2],sys.argv[3]
    v=cv2.VideoCapture(src); a=cv2.VideoCapture(alp); log=[]
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','12','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    i=0
    while True:
        ok,f=v.read(); ok2,al=a.read()
        if not ok or not ok2: break
        g,n=fix(f,al[...,0]); log.append(n); ff.stdin.write(g.tobytes()); i+=1
    ff.stdin.close(); ff.wait(); json.dump(log,open(out+'.log.json','w')); print('frames',i,'fixed',sum(1 for n in log if n>=250))
