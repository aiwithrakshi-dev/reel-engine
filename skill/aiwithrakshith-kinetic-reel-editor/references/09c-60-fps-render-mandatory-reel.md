<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 9c. 60 fps render (mandatory for every reel)

Template: `examples/day4_android_studio/render_day4_60.py`. Frame numbers are 60 fps frames `g`; the timeline logic runs
  in 30-fps units (`f = g // 2`, `SUB = 0 / 0.5`), so every device keeps its approved timing while continuous motion —
  halftone rings, neon streaks, swooshes, screen push-ins, grain — gets real in-between frames. The hook runs per 60 fps frame.
- Usage: `HOOK=<name> python3 render.py <g0> <g1> part.mp4` (two parallel halves), test frames
  `python3 render.py 0 0 test_dir g1,g2,...`.
- Encode `libx264 High, -r 60, CRF 17, -maxrate 35M -bufsize 70M, -preset veryfast, AAC 320k 48 kHz, +faststart`;
  verify `r_frame_rate=60/1` and the frame count (≈ 60 × duration) with ffprobe.
- The A-roll stays at its native cadence (25 fps, frame-held); never motion-interpolate his face.
- Re-measure audio after muxing: true peak must be ≤ −1 dBTP (lower the mix 0.5 dB if needed).

**Setup**: clone this repo (or restore `reel-engine/*` from the Project); fonts Inter Tight (OFL, google/fonts
`ofl/intertight`) + Noto Sans Kannada; RVM
`github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx`;
`pip install -r requirements.txt`.
