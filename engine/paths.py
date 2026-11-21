"""One place for every path. Override with env vars on another machine:
  REEL_HOME   repo root (auto-detected)
  REEL_FONTS  fonts dir           (default <repo>/work/fonts)
  REEL_WORK   scratch / per-reel  (default <repo>/work)
  REEL_D4     Day 4 example media (default <repo>/work/d4, falls back to /home/claude/d4)
  REEL_MODELS models dir          (default <repo>/work/models)"""
import os
HOME = os.environ.get('REEL_HOME') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
WORK = os.environ.get('REEL_WORK') or os.path.join(HOME, 'work')
FONTS = os.environ.get('REEL_FONTS') or os.path.join(WORK, 'fonts')
MODELS = os.environ.get('REEL_MODELS') or os.path.join(WORK, 'models')
_d4 = os.path.join(WORK, 'd4')
D4 = os.environ.get('REEL_D4') or (_d4 if os.path.isdir(_d4) else '/home/claude/d4')
FONT_DIRS = [d for d in (FONTS, os.path.join(WORK, 'fonts'), os.path.expanduser('~/.reel_engine/fonts'),
                         '/home/claude/work/fonts', '/home/claude/d4/fonts') if d]


def font_path(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p): return p
    raise FileNotFoundError(f'{name} not found in {FONT_DIRS}: run ./setup.sh')


def work(*p): os.makedirs(WORK, exist_ok=True); return os.path.join(WORK, *p)
