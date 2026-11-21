<!-- Generated from SKILL.md by tools/build_skill_refs.py. Edit SKILL.md, not this file. -->

# 6. Understanding the raw video

Detect language (Whisper large-v3, `language=None`, first 12 s). Load audio via librosa (faster-whisper's av path breaks).
- English: `faster-whisper large-v3` word timestamps.
- Kannada: transcribe `language='kn'` + `task='translate'`; the editor **reviews and corrects** the English by meaning
  (Whisper Kannada is unreliable) and builds a phrase table: Kannada phrase ↔ English caption ↔ start/end.
- Word onsets: snap to librosa onsets (−0.08/+0.18 s); verify keywords on spectrograms (plosive bursts, 's' HF onset).
- Silence map: `silencedetect=noise=-35dB:d=0.15`; cut pauses ≥ 0.35 s; islands padded and snapped **outward** to
  whole source frames (never trim inside a word); 20 ms crossfades (`cut_vo.py`). Cut video segment by segment and
  concat (a 10+-trim filter graph OOMs).
- Artifact scan at 10 fps: AI cap crown colour flips / white logo growth (`cap_logo_fix.py` recolours the crown each
  frame; `cap_patch.py` pastes a clean crown), finger warps, garbled AI text → fix or hide under a device/cutaway.
- Matte: `matte.py` (RVM resnet50 ONNX, ~0.35 s/frame) on the tightened timeline + the ~1 s tail for the end hold;
  `subject.py`/`chair_mask.py` when the chair must be in front; 1 px choke, drop specks.
