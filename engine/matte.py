import onnxruntime as ort, numpy as np, cv2, subprocess, sys, time
model=sys.argv[1]; inp=sys.argv[2]; outp=sys.argv[3]; limit=int(sys.argv[4]) if len(sys.argv)>4 else 10**9
so=ort.SessionOptions(); so.intra_op_num_threads=2
sess=ort.InferenceSession(model,so,providers=['CPUExecutionProvider'])
cap=cv2.VideoCapture(inp); W,H=1080,1920
rec=[np.zeros((1,1,1,1),np.float32)]*4; dr=np.array([0.25],np.float32)
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r','30','-i','-','-c:v','ffv1','-pix_fmt','gray',outp],stdin=subprocess.PIPE)
n=0;t0=time.time()
while n<limit:
    ok,f=cap.read()
    if not ok: break
    src=(cv2.cvtColor(f,cv2.COLOR_BGR2RGB).astype(np.float32)/255).transpose(2,0,1)[None]
    fgr,pha,*rec=sess.run(None,{'src':src,'r1i':rec[0],'r2i':rec[1],'r3i':rec[2],'r4i':rec[3],'downsample_ratio':dr})
    ff.stdin.write((pha[0,0]*255+0.5).clip(0,255).astype(np.uint8).tobytes()); n+=1
    if n%50==0: print(n, (time.time()-t0)/n, flush=True)
ff.stdin.close(); ff.wait(); print('frames',n,'sec/frame',(time.time()-t0)/max(n,1))
