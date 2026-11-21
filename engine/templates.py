# The 7 reel templates (/temp-1 ... /temp-7). Single source of truth: the renderer reads these specs and
# tools/template_docs.py writes templates/temp-N/TEMPLATE.md from them.
#
# Shared by EVERY template (non-negotiable):
#   - 1080x1920, 60 fps, H.264 + AAC, -14 LUFS / <= -1 dBTP
#   - Instagram safe zone x 65-960, y 270-1250 for every readable/persistent element
#   - FACE-CLEAR: no text / component / effect layer on the face oval (engine/face_guard.py)
#   - layout grid: 6 columns inside the safe box (65..960, gutter 20), rows: HEAD band y 280-430 (above the cap),
#     FACE band (cap..chin, nothing on it), CAPTION band chin+40 .. 1245
#   - captions synced to speech (never early), max 30 chars per line, every visual event gets an SFX
#   - unique hook from engine/hooks.py (not used in the last 5 reels), tinted with the template accent
SAFE = (65, 270, 960, 1250)

TEMPLATES = {
    1: dict(
        key='kinetic-red', name='Red Kinetic (house style)', ref='Rakshith: Kling 4.0 + Day 4 reels',
        best_for='AI tool launches, news drops, hype explainers', energy='high',
        look='His room kept and dimmed; giant red 3D italic words type on BEHIND his head; neon streaks, halftone rings, '
             'pixel blocks, red-framed screen cutaways, chest-row tiles.',
        grade=dict(sat=0.8, contrast=1.0, gain=(1.0, 1.0, 1.0), vignette=0.0, blur_bg=3),
        fonts=dict(head='intertight-i:900', label='intertight-i:400', caption='intertight-i:700'),
        palette=dict(accent='#E3121B', text='#FFFFFF', bg='#000000'),
        headline=dict(zone='above-cap, behind head (matte)', anim='type-on 1 letter/frame, 3D extrude, pixel blocks'),
        captions=dict(style='karaoke', zone='caption band', font_px=44, case='as spoken'),
        scenes=['red-framed screen window on blurred backdrop', 'chest-row tiles/pills'],
        transitions=['neon streak', 'halftone ring', 'smear', 'swoosh', 'negative/ghost cut'],
        hook='any unused hook (red accent)', pace='event every 0.3-0.5 s; cut every ~3 s',
        music='120-135 BPM dark trap / 808', renderer='examples/day4_android_studio/render_day4_60.py'),
    2: dict(
        key='minimal-cinematic', name='Minimal Cinematic', ref='@tahacreate',
        best_for='calm tutorials, design/process explainers, "how to" talks', energy='calm',
        look='Cool teal grade with soft vignette; small clean white words appear one by one on the chest band; hook on a '
             'blurred abstract frame; white explainer pages with black type and a growing tree diagram; accent words '
             'in serif italic; soft blur dissolves.',
        grade=dict(sat=0.72, contrast=1.08, gain=(0.86, 1.0, 1.02), lift=(4, 10, 12), vignette=0.45),
        fonts=dict(caption='inter:600', accent='playfair-i:600', title='inter:700', sub='inter:500'),
        palette=dict(accent='#FFFFFF', text='#FFFFFF', bg='#FDFDFD', ink='#111111'),
        headline=dict(zone='none on talk (keywords become larger caption words)', anim='blur-in fade 6 frames'),
        captions=dict(style='minimal-words', zone='chest band (chin+70)', font_px=44, max_words=3, case='as spoken',
                      keyword='Playfair italic 76 px'),
        scenes=['abstract blurred hook page', 'white explainer page: title + sub + tree diagram', 'white page + rounded image card'],
        transitions=['blur dissolve 8 frames'], hook='letterbox_open (white accent)', pace='scene every ~4 s, word every 0.3 s',
        music='70-95 BPM cinematic pulse / soft piano', renderer='engine/template_render.py'),
    3: dict(
        key='editorial-script', name='Editorial Script', ref='@ahmadjamilofficial1',
        best_for='mindset, creativity, storytelling, motivational takes', energy='medium',
        look='Moody low-key grade; headline above the head mixes a heavy white sans word with an overlapping red '
             'script/serif-italic word; B-roll inside big rounded cards on black; colour-wash flashes between scenes.',
        grade=dict(sat=0.9, contrast=1.15, gain=(1.04, 0.97, 0.92), lift=(0, 0, 0), vignette=0.55),
        fonts=dict(label='inter:800', head='intertight:900', script='playfair-i:700', caption='inter:700'),
        palette=dict(accent='#E8132E', text='#FFFFFF', bg='#070707'),
        headline=dict(zone='HEAD band above the cap', anim='word pop 1.15->1.0, script word wipes in left->right'),
        captions=dict(style='single-word', zone='chest band', font_px=40, case='as spoken'),
        scenes=['rounded B-roll card (radius 40) on black with headline overlapping its top'],
        transitions=['colour wash (red->orange->yellow) 5 frames', 'hard cut on beat'], hook='face_punch (red accent)',
        pace='cut every ~1.7 s (fastest template)', music='85-105 BPM moody lo-fi / cinematic',
        renderer='engine/template_render.py'),
    4: dict(
        key='listicle-chapters', name='Listicle Chapters', ref='@weblyfe',
        best_for='"N tips/steps/tools" lists, book or course summaries', energy='medium',
        look='Clean daylight talking head; white rounded pill captions with word-by-word reveal (spoken words black, '
             'next words grey); torn-paper title banner on the hook; full-screen gradient chapter cards with '
             '"TIP #n" in mono, a serif uppercase title typing on and a floating image card; big gold numbers.',
        grade=dict(sat=1.0, contrast=1.04, gain=(1.0, 1.0, 1.03), vignette=0.15),
        fonts=dict(caption='montserrat:700', mono='spacemono-b', title='playfair:800', number='playfair:900'),
        palette=dict(accent='#F4B73F', text='#111111', pill='#FFFFFF',
                     chapters=[('#6CA8DB', '#18385F'), ('#6969D7', '#171760'), ('#D96B93', '#601831'),
                               ('#71D0E1', '#1F5966'), ('#CB6ED2', '#571A5B'), ('#A7C6B5', '#3A4A42')]),
        headline=dict(zone='torn banner y 270-560 on the hook; chapter cards full screen', anim='letter type-on'),
        captions=dict(style='pill-reveal', zone='caption band (y 1150-1230)', font_px=36, max_words=5, case='as spoken'),
        scenes=['torn-paper banner', 'gradient chapter card: TIP #n + serif title + image card', 'gold number at top'],
        transitions=['whip slide 6 frames'], hook='shutter_blinds (chapter colour)', pace='chapter every ~8-10 s',
        music='100-118 BPM upbeat house / groove', renderer='engine/template_render.py'),
    5: dict(
        key='bold-yellow-creator', name='Bold Yellow Creator', ref='@artzenmedia',
        best_for='creator tips, tool walkthroughs, Canva/app tutorials', energy='high',
        look='Warm golden-hour grade; huge condensed yellow headline with a small caps label above the head; one white '
             'condensed word at a time on the chest; screen recordings on a white grid page; 3D phone on a purple '
             'grid with an iMessage bubble; glowing gradient comment CTA.',
        grade=dict(sat=1.08, contrast=1.1, gain=(1.08, 1.0, 0.86), vignette=0.35),
        fonts=dict(label='anton', head='anton', caption='anton', bubble='inter:600'),
        palette=dict(accent='#F7E733', text='#FFFFFF', grid_bg='#FCFCFC', purple=('#2A2F8F', '#05040F'), bubble='#1E8BFF',
                     cta=('#22E1FF', '#8E2BFF')),
        headline=dict(zone='HEAD band above the cap', anim='letters drop in with motion blur + yellow glow'),
        captions=dict(style='single-word-condensed', zone='chest band', font_px=60, case='UPPER'),
        scenes=['white grid page + screenshot card (slow push)', 'purple grid + phone mockup + iMessage bubble'],
        transitions=['zoom-blur push 6 frames'], hook='zoom_punch (yellow accent)', pace='scene every ~5 s',
        music='120-130 BPM bright electronic / future bass', renderer='engine/template_render.py'),
    6: dict(
        key='orange-explainer', name='Orange Explainer', ref='@hammadkhalid8',
        best_for='business, money, book lessons, frameworks', energy='high',
        look='Dark studio talking head; two-line bold italic captions below the chin, the key line in a gold gradient; '
             'full-screen orange grid-paper scenes with white swooshes, white serif titles, tweet/quote cards, '
             'image cards and icon tiles.',
        grade=dict(sat=0.95, contrast=1.12, gain=(1.03, 1.0, 0.95), vignette=0.4),
        fonts=dict(caption='montserrat-i:900', title='playfair:800', card='inter:600'),
        palette=dict(accent='#FFC93C', accent2='#F29E12', text='#FFFFFF', bg='#FC8F00', grid='#FFA42E'),
        headline=dict(zone='captions carry the headline (two-line block)', anim='words pop in as spoken'),
        captions=dict(style='two-line-gold', zone='caption band (chin+24 .. 1245): gold 62 px + white 38 px', font_px=62, case='UPPER'),
        scenes=['orange grid page + serif title + quote/tweet card', 'orange grid page + image card'],
        transitions=['orange swoosh wipe 8 frames'], hook='strip_slam (orange accent)', pace='scene every ~3 s',
        music='100-118 BPM confident hip-hop / groove', renderer='engine/template_render.py'),
    7: dict(
        key='saas-split', name='SaaS Split-Screen', ref='@marcel_grauu',
        best_for='product demos, SaaS / app features, before-after workflows', energy='medium',
        look='Split screen: product panel on top over a soft lavender page with blue glow blobs, face cam below; big '
             'blue kinetic word on the panel synced to speech; full-blue word flashes; UI cards with a blue '
             'word highlight.',
        grade=dict(sat=0.92, contrast=1.05, gain=(0.98, 1.0, 1.03), vignette=0.2),
        fonts=dict(word='intertight:800', ui='inter:500'),
        palette=dict(accent='#0000FB', text='#0000FB', bg='#F6F6FC', blob='#C9C6FF'),
        headline=dict(zone='top panel y 280-700', anim='word pop 0.85->1.06->1.0'),
        captions=dict(style='panel-kinetic-word', zone='top panel (face cam below, nothing on it)', font_px=120, case='as spoken'),
        scenes=['top panel UI card (image) over lavender', 'full-blue word flash'],
        transitions=['soft scale cut'], hook='halftone_iris (blue accent)', pace='panel change every ~3 s',
        music='100-115 BPM clean tech house / lo-fi', renderer='engine/template_render.py'),
}


def get(n):
    if isinstance(n, str): n = int(n.replace('/temp-', '').replace('temp-', ''))
    return TEMPLATES[n]
