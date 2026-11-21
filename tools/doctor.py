#!/usr/bin/env python3
"""Checks that this machine can render every template. Exit 0 = ready."""
import os, sys, shutil, subprocess, importlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.path.join(ROOT, 'engine'))
ok = True
def line(good, msg):
    global ok; ok &= good; print(('  OK  ' if good else '  !!  ') + msg)
print('reel-engine doctor')
line(sys.version_info >= (3, 9), f'python {sys.version.split()[0]} (>= 3.9)')
ff = shutil.which('ffmpeg'); line(bool(ff), f'ffmpeg {ff}')
if ff:
    enc = subprocess.run([ff, '-hide_banner', '-encoders'], capture_output=True, text=True).stdout
    line('libx264' in enc, 'ffmpeg has libx264'); filt = subprocess.run([ff, '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    line('loudnorm' in filt and 'sidechaincompress' in filt, 'ffmpeg has loudnorm + sidechaincompress')
for m in ['numpy', 'cv2', 'PIL', 'soundfile', 'pyloudnorm', 'scipy', 'regex']:
    try: importlib.import_module(m); line(True, f'python module {m}')
    except Exception as e: line(False, f'python module {m}: {e}')
for m in ['onnxruntime', 'faster_whisper', 'googleapiclient']:
    try: importlib.import_module(m); print(f'  OK  optional {m}')
    except Exception: print(f'  --  optional {m} missing (matte / transcription / Drive API)')
from PIL import features
line(bool(features.check('raqm')), 'Pillow RAQM (Kannada shaping)')
from paths import FONT_DIRS
from template_render import FONT_FILES
for f in sorted(set(FONT_FILES.values()) | {'NotoSansKannada%5Bwdth,wght%5D.ttf'}):
    line(any(os.path.exists(os.path.join(d, f)) for d in FONT_DIRS), f'font {f}')
try:
    import templates, face_guard, hooks, captions; line(len(templates.TEMPLATES) == 7 and len(hooks.HOOKS) >= 11, f'7 templates, {len(hooks.HOOKS)} hooks')
except Exception as e: line(False, f'engine import: {e}')
print('READY' if ok else 'NOT READY: fix the !! lines (./setup.sh installs fonts + modules)'); sys.exit(0 if ok else 1)
