"""Final outputs for EVERY reel, every template (Rakshith, 22 Nov 2026):

  1. Instagram thumbnail      <slug>_thumbnail.jpg (1080x1920) + <slug>_thumbnail_grid.jpg (3:4 profile-grid crop)
  2. 4K 60 fps video          <slug>_4k_60fps.mp4  (2160x3840, 60 fps, H.264 High 5.2, AAC 320k) + the 1080p 60 fps master
  3. Instagram caption        caption.txt — short and SEO-friendly (main keyword in the first line, <= 125 chars before "more",
                              comment-keyword CTA, 3-5 lowercase hashtags ending #aiwithrakshith) + alt text + pinned comment
  4. Instagram DM             dm_message.txt — the reply he sends to everyone who comments the keyword
  5. DM document              <slug>_dm_<doc>.docx + .pdf — the promised checklist/guide, full explanation, "AI with Rakshith"
                              watermark on every page (tools/dm_doc.js)

  python3 tools/reel_outputs.py --video final.mp4 --post post.json --out pkg/ [--thumb cover.png | --thumb-t 2.4] [--no-4k]

post.json:
  { "slug": "day24_gemini4", "keyword": "MODEL",
    "caption": ["hook line with the main keyword", "one fact", "Comment MODEL ... CTA"], "hashtags": ["#gemini4", ...],
    "alt_text": "...", "pinned_comment": "...", "dm_message": "... {link} ...",
    "thumb_title": "optional cover title (templates without an on-screen headline)", "thumb_sub": "optional line",
    "dm_doc": { ...spec for tools/dm_doc.js... } }
"""
import argparse, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'engine'))
from paths import font_path


def sh(cmd): subprocess.run(cmd, check=True)


def thumbnail(video, out_jpg, out_grid, t=None, src=None):
    if src: sh(['ffmpeg', '-v', 'error', '-y', '-i', src, '-q:v', '2', out_jpg])
    else: sh(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', video, '-frames:v', '1', '-q:v', '2', out_jpg])
    sh(['ffmpeg', '-v', 'error', '-y', '-i', out_jpg, '-vf', 'crop=1080:1440:0:240', '-q:v', '2', out_grid])


def title_overlay(jpg, title, sub=None, grid=None, y=250, serif=True):
    """Cover title above the cap for templates that keep the talking head clean (e.g. /temp-2): white type with a soft
    shadow, centred on the safe-zone centre line x 512, kept inside y 250-460 so the face and the 3:4 grid crop stay clear."""
    from PIL import ImageFilter
    im = Image.open(jpg).convert('RGBA'); lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sh)
    def F(name, size, w):
        f = ImageFont.truetype(font_path(name), size)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        return f
    fa = F('PlayfairDisplay-Italic%5Bwght%5D.ttf' if serif else 'InterTight%5Bwght%5D.ttf', 132, 600 if serif else 900)
    while d.textlength(title, font=fa) > 860: fa = F('PlayfairDisplay-Italic%5Bwght%5D.ttf' if serif else 'InterTight%5Bwght%5D.ttf', fa.size - 6, 600 if serif else 900)
    rows = [(title, fa, y)] + ([(sub, F('Inter%5Bopsz,wght%5D.ttf', 46, 600), y + fa.size + 16)] if sub else [])
    for t, f, yy in rows:
        w = d.textlength(t, font=f); ds.text((512 - w / 2 + 3, yy + 6), t, font=f, fill=(0, 0, 0, 160)); d.text((512 - w / 2, yy), t, font=f, fill=(255, 255, 255, 255))
    out = Image.alpha_composite(Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6))), lay).convert('RGB')
    out.save(jpg, quality=92)
    if grid: out.crop((0, 240, 1080, 1680)).save(grid, quality=92)


def master_4k(video, out):
    """2160x3840 60 fps master. The engine renders at 1080x1920 and the A-roll is 1080p, so this is a Lanczos upscale with
    light sharpening (sharper type and graphics after Instagram's re-encode); it is not new detail."""
    sh(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', 'scale=2160:3840:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,fps=60',
        '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.2', '-preset', 'veryfast', '-crf', '16', '-maxrate', '90M', '-bufsize', '180M',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', out])
    p = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                        '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip()
    assert p.startswith('2160,3840,60/1'), p
    return p


def caption_checks(post):
    lines = post['caption']; tags = post['hashtags']; first = lines[0]; kw = post.get('keyword', '')
    return [('first line <= 125 chars (shows before "more")', len(first) <= 125),
            ('main keyword in the first line', any(k.lower() in first.lower() for k in post.get('seo_keywords', [first.split()[0]]))),
            ('2-4 short lines (minimum caption)', 2 <= len(lines) <= 4),
            ('CTA uses the comment keyword', bool(kw) and kw in lines[-1]),
            ('3-5 hashtags, lowercase', 3 <= len(tags) <= 5 and all(t == t.lower() and t.startswith('#') for t in tags)),
            ('ends with #aiwithrakshith', tags[-1] == '#aiwithrakshith'),
            ('alt text present (SEO)', len(post.get('alt_text', '')) >= 40)]


def watermark_png(path, text='AI with Rakshith'):
    S = 1600; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(font_path('InterTight%5Bwght%5D.ttf'), 150)
    try: f.set_variation_by_axes([800])
    except Exception: pass
    w = d.textlength(text, font=f); d.text(((S - w) / 2, S / 2 - 90), text, font=f, fill=(227, 18, 27, 30))
    im.rotate(35, resample=Image.BICUBIC).save(path)


def dm_doc(spec, out_base, workdir):
    wm = os.path.join(workdir, 'watermark.png'); watermark_png(wm, spec.get('watermark', 'AI with Rakshith'))
    js = os.path.join(workdir, 'dm_spec.json'); json.dump(spec, open(js, 'w'), ensure_ascii=False)
    sh(['node', os.path.join(HERE, 'dm_doc.js'), js, wm, out_base + '.docx'])
    subprocess.run(['zip', '-d', out_base + '.docx', '*/'], capture_output=True)
    sh(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(out_base) or '.', out_base + '.docx'])
    os.remove(wm); os.remove(js)
    return out_base + '.docx', out_base + '.pdf'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--video', required=True); ap.add_argument('--post', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--thumb'); ap.add_argument('--thumb-t', type=float, default=2.0)
    ap.add_argument('--no-4k', action='store_true'); a = ap.parse_args()
    post = json.load(open(a.post)); os.makedirs(a.out, exist_ok=True); slug = post['slug']; res = {}
    th, tg = (os.path.join(a.out, f'{slug}_thumbnail.jpg'), os.path.join(a.out, f'{slug}_thumbnail_grid.jpg'))
    thumbnail(a.video, th, tg, a.thumb_t, a.thumb); res['thumbnail'] = th
    if post.get('thumb_title'): title_overlay(th, post['thumb_title'], post.get('thumb_sub'), tg)
    v1080 = os.path.join(a.out, f'{slug}_1080p_60fps.mp4')
    if os.path.abspath(a.video) != os.path.abspath(v1080): shutil.copy(a.video, v1080)
    res['video_1080p'] = v1080
    if not a.no_4k: v4k = os.path.join(a.out, f'{slug}_4k_60fps.mp4'); master_4k(a.video, v4k); res['video_4k'] = v4k
    cap = '\n'.join(post['caption']) + '\n\n' + ' '.join(post['hashtags'])
    extra = f"\n\n---\nAlt text (Advanced settings > Accessibility):\n{post['alt_text']}\n\nPinned comment:\n{post['pinned_comment']}\n"
    open(os.path.join(a.out, 'caption.txt'), 'w').write(cap + extra); res['caption'] = cap
    open(os.path.join(a.out, 'dm_message.txt'), 'w').write(post['dm_message'] + '\n')
    if post.get('dm_doc'):
        name = re.sub(r'[^a-z0-9]+', '_', post['dm_doc']['title'].lower()).strip('_')[:40]
        res['dm_doc'] = dm_doc(post['dm_doc'], os.path.join(a.out, f'{slug}_dm_{name}'), a.out)
    checks = caption_checks(post)
    rep = '# Instagram outputs\n\n| Check | Result |\n|---|---|\n' + ''.join(f"| {k} | {'PASS' if v else 'FIX'} |\n" for k, v in checks)
    open(os.path.join(a.out, 'outputs_report.md'), 'w').write(rep)
    print(rep); print(json.dumps(res, indent=1))
    if not all(v for _, v in checks): sys.exit(1)


if __name__ == '__main__':
    main()
