#!/usr/bin/env bash
# One-command setup on any machine (Linux / macOS / WSL). Safe to re-run.
#   ./setup.sh            python deps + fonts + matte model
#   ./setup.sh --no-model skip the 100 MB RVM model (templates 2-7 don't need it)
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd); FONTS=${REEL_FONTS:-$ROOT/work/fonts}; MODELS=${REEL_MODELS:-$ROOT/work/models}
mkdir -p "$FONTS" "$MODELS" work memory
command -v ffmpeg >/dev/null || { echo "!! install ffmpeg first (apt install ffmpeg / brew install ffmpeg)"; exit 1; }
PIP="python3 -m pip install -q -r requirements.txt"
$PIP 2>/dev/null || $PIP --break-system-packages
G=https://raw.githubusercontent.com/google/fonts/main/ofl
get() { [ -s "$FONTS/$2" ] || curl -fsSL "$G/$1/$2" -o "$FONTS/$2" && echo "font $2"; }
get intertight 'InterTight%5Bwght%5D.ttf';  get intertight 'InterTight-Italic%5Bwght%5D.ttf'
get inter 'Inter%5Bopsz,wght%5D.ttf';        get anton 'Anton-Regular.ttf'
get playfairdisplay 'PlayfairDisplay%5Bwght%5D.ttf'; get playfairdisplay 'PlayfairDisplay-Italic%5Bwght%5D.ttf'
get montserrat 'Montserrat%5Bwght%5D.ttf';   get montserrat 'Montserrat-Italic%5Bwght%5D.ttf'
get spacemono 'SpaceMono-Regular.ttf';       get spacemono 'SpaceMono-Bold.ttf'
get notosanskannada 'NotoSansKannada%5Bwdth,wght%5D.ttf'
if [ "${1:-}" != "--no-model" ] && [ ! -s "$MODELS/rvm_resnet50_fp32.onnx" ]; then
  curl -fsSL https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx -o "$MODELS/rvm_resnet50_fp32.onnx"
fi
# DM documents (tools/dm_doc.js): Node + docx, LibreOffice for the PDF copy
if command -v node >/dev/null; then node -e "require('docx')" 2>/dev/null || npm install --no-save --silent docx || echo "!! npm install docx failed"
else echo "!! install Node.js for DM documents (tools/dm_doc.js)"; fi
command -v soffice >/dev/null || echo "!! install LibreOffice (soffice) for the DM document PDF"
[ -f memory/content_log.json ] || echo '{"reels": []}' > memory/content_log.json
python3 tools/doctor.py
