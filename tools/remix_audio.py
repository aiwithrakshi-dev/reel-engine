#!/usr/bin/env python3
"""Re-mix only the audio of a rendered reel (after an audio-audit FIX) without re-rendering the picture.

  python3 tools/remix_audio.py <reel_dir>      -> rebuilds the mix from job.json, muxes it into reel.mp4 (-c:v copy)
"""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'engine'))
from template_render import build_audio
from templates import TEMPLATES
rd = os.path.abspath(sys.argv[1]); os.chdir(rd)
job = json.load(open('job.json'))
build_audio(job, TEMPLATES[int(job['template'])], 'remix.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'reel.mp4', '-i', 'remix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', 'reel_remix.mp4'], check=True)
os.replace('reel_remix.mp4', 'reel.mp4'); os.remove('remix.wav'); print('remixed', rd)
