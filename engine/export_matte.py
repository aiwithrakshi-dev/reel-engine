# luma track matte (white = Rakshith + chair) on the reel timeline, after the cap repair, positioned as in the reel (DY=230)
import os, sys, cv2, numpy as np, subprocess
sys.path.insert(0, os.path.join(os.environ.get('REEL_REEL_DIR', '/home/claude/d4'), 'scripts')); sys.path.insert(1, os.path.dirname(os.path.abspath(__file__))); from subject import combined_alpha
v=cv2.VideoCapture('aroll_patched30.mp4'); a=cv2.VideoCapture('alpha_r50.mkv')
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-tag:v','avc1','deliver/matte.mov'],stdin=subprocess.PIPE)
DY=230; n=0
while True:
    ok,f=v.read(); ok2,al=a.read()
    if not ok or not ok2: break
    m=combined_alpha(f,al[...,0]); out=np.zeros((1920,1080),np.uint8); out[DY:]=(m[:1920-DY]*255).astype(np.uint8)
    ff.stdin.write(out.tobytes()); n+=1
ff.stdin.close(); ff.wait(); print('matte frames',n)
