import sys, json, soundfile as sf, numpy as np
sys.path.insert(0,'scripts'); from islands import snapped
from faster_whisper import WhisperModel
m=WhisperModel('large-v3',device='cpu',compute_type='int8',cpu_threads=2,download_root='models')
x,sr=sf.read('vo_tight_raw.wav'); x=x.mean(1) if x.ndim>1 else x
import librosa; x16=librosa.resample(x,orig_sr=sr,target_sr=16000).astype(np.float32)
out=[]
for i,(a,b,r0,r1) in enumerate(snapped(),1):
    if i<3: continue
    seg=x16[int(r0*16000):int(r1*16000)]
    segs,_=m.transcribe(seg,language='kn',word_timestamps=True,beam_size=5,vad_filter=False,condition_on_previous_text=False)
    for s in segs:
        for w in s.words: out.append(dict(island=i,word=w.word.strip(),start=round(r0+w.start,3),end=round(r0+w.end,3),p=round(w.probability,2)))
    print(i,' '.join(o['word']+'@'+str(o['start']) for o in out if o['island']==i),flush=True)
json.dump(out,open('whisper_words_3on.json','w'),ensure_ascii=False,indent=0)
