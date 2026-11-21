import cv2, numpy as np
import os as _os; CHAIR=cv2.imread(_os.path.join(_os.environ.get('REEL_REEL_DIR') or _os.environ.get('REEL_WORK','/home/claude/work'),'chair_mask.png'),0).astype(np.float32)/255
CHAIR_D=cv2.dilate((CHAIR>0.5).astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32)
EXCL=np.ones((1920,1080),np.float32); cv2.fillPoly(EXCL,[np.array([(0,640),(165,640),(165,860),(120,995),(0,995)],np.int32)],0); EXCL=cv2.GaussianBlur(EXCL,(0,0),3)
K45=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(45,45)); K35=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(35,35))
def wood_mask(bgr):
    hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV); h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    w=((h>=8)&(h<=24)&(s>70)&(v>60)).astype(np.uint8)
    return cv2.GaussianBlur(cv2.dilate(w,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),1.5)
def combined_alpha(bgr,pa):
    pa=pa.astype(np.float32)/255
    core=cv2.dilate((pa>0.9).astype(np.uint8),K45).astype(np.float32)
    near=cv2.dilate((pa>0.5).astype(np.uint8),K35).astype(np.float32)
    allowed=np.maximum(core,CHAIR_D)
    wm=wood_mask(bgr)
    ch=CHAIR*(1-wm*(1-near))            # remove wood from the chair mask only away from the person
    ch=cv2.morphologyEx(ch,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    a=np.maximum(pa,ch)
    a=np.where((a<0.95)&(CHAIR_D<0.5),a*(1-wm),a)   # wood fringe on person edges outside the chair
    a*=allowed*EXCL
    n,lab,st,_=cv2.connectedComponentsWithStats((a>0.25).astype(np.uint8),connectivity=8)
    if n>2:
        small=np.isin(lab,[i for i in range(1,n) if st[i,4]<6000]); a[small]=0
    a=cv2.erode(a,np.ones((3,3),np.uint8))          # ~1 px choke
    return cv2.GaussianBlur(a,(0,0),0.8)
