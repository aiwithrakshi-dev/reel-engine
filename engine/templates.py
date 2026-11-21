# The 16 reel templates (/temp-1 ... /temp-16). Single source of truth: the renderer reads these specs and
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
    8: dict(
        key='warm-cinematic', name='Warm Cinematic', ref='t-8 (Amazon-seller explainer)',
        best_for='expert explainers, "most people never see this" insights, calm authority', energy='medium',
        look='Warm golden grade; headline words blur in one by one at the top-left, the key word in an orange gradient; '
             'punch-in cuts (1.14x) on every second headline; small lowercase word captions under the chin; dark checklist '
             'page with typed check items and a rounded live picture-in-picture of him; warm light-leak flash transitions.',
        grade=dict(sat=1.04, contrast=1.08, gain=(1.10, 1.0, 0.84), vignette=0.45),
        fonts=dict(head='inter:600', key='inter:700 gradient', caption='inter:600', checklist='inter:500'),
        palette=dict(accent='#F0782A', key=('#FFD36A', '#F0782A'), text='#FFFFFF', page='#1D1D1F'),
        headline=dict(zone='HEAD band, left-aligned x 92', anim='word-by-word blur-in 0.18 s'),
        captions=dict(style='single-word-lowercase', zone='under the chin (punch-in aware)', font_px=36, case='lower'),
        scenes=['dark checklist page + live PiP card', 'image card + live PiP'],
        transitions=['warm light-leak flash 12 frames', 'punch-in cut'], hook='rgb_converge (orange accent)',
        pace='headline every ~2-3 s, punch-in on alternate headlines', music='85-100 BPM warm lo-fi / soft house',
        renderer='engine/template_render.py'),
    9: dict(
        key='peach-premium', name='Peach Premium', ref='t-9 (video-editor tips)',
        best_for='"3 ways / 3 tips" lists, creative-tool tips, premium tutorials', energy='medium',
        look='Neon room kept; white heavy chest captions with the key word in orange serif italic; orange 3D number '
             'tiles pop in on a spoken list; soft peach gradient pages with a sliding title and floating white shortcut '
             'cards; image card with an orange caps kicker.',
        grade=dict(sat=1.08, contrast=1.08, gain=(1.0, 0.98, 1.02), vignette=0.3),
        fonts=dict(caption='inter:800', key='playfair-i:700', tile='playfair:800', title='inter:700'),
        palette=dict(accent='#F26B1D', key='#FF7A2E', page='#FFF6F0', tile=('#F26A21', '#962E06')),
        headline=dict(zone='captions carry the keyword; peach page titles', anim='slide-in from right with blur'),
        captions=dict(style='chest-line-serif-key', zone='caption band', font_px=46, max_words=3, case='as spoken'),
        scenes=['peach page + floating shortcut cards', 'peach page + kicker + image card'],
        transitions=['soft blur dissolve 10 frames'], hook='pixel_assemble (orange accent)', pace='scene every ~3-4 s',
        music='100-115 BPM bright pop / chill house', renderer='engine/template_render.py'),
    10: dict(
        key='card-stage', name='Card Stage', ref='t-10 (Submagic)',
        best_for='app / AI-tool reviews, "this tool just ..." launches, SaaS features', energy='high',
        look='Light stage: he lives inside a big rounded card on an off-white page with the brand pill top-left; the '
             'headline word appears as giant outlined purple type behind the card; for features he drops into a dome at '
             'the bottom while the UI card sits on top; key words in a purple gradient.',
        grade=dict(sat=1.05, contrast=1.06, gain=(1.0, 0.98, 1.04), vignette=0.0),
        fonts=dict(caption='inter:700', key='intertight:800 gradient', outline='intertight:900 outline', brand='intertight:800'),
        palette=dict(accent='#8A3BFF', brand='#FF5A1F', page='#F7F6FA'),
        headline=dict(zone='giant outline word behind the card', anim='fade-in 0.3 s'),
        captions=dict(style='chest-line-purple-key', zone='on the card, under the chin', font_px=42, max_words=3, case='as spoken'),
        scenes=['UI card on top + speaker in a dome at the bottom'], transitions=['scale cut 8 frames'],
        hook='strip_slam (purple accent)', pace='scene every ~3-5 s', music='120-128 BPM upbeat tech house',
        renderer='engine/template_render.py'),
    11: dict(
        key='green-terminal', name='Green Terminal', ref='t-11 (Claude Code reel)',
        best_for='money / numbers stories, dev & AI-agent tools, "I built X" breakdowns', energy='high',
        look='Black page with a green dot grid and glow; facecam in a green-bordered card at the bottom, graphics on '
             'top: white label + green glowing slot-machine counter or serif italic word, red rotated stamp for '
             '"not / irrelevant" beats, cream stat pages with a big red number counting up.',
        grade=dict(sat=0.95, contrast=1.06, gain=(1.0, 1.0, 1.0), vignette=0.0),
        fonts=dict(label='inter:800', counter='intertight:900 glow', accent='playfair-i:700', stat='intertight:900'),
        palette=dict(accent='#36F06A', stamp='#E5322D', page='#040605', cream='#F2EEE6', stat='#E23B2E'),
        headline=dict(zone='graphics area y 280-620 above the facecam card', anim='slot-machine roll 0.45 s / stamp slam'),
        captions=dict(style='single-word', zone='y 660 between graphics and facecam', font_px=42, case='as spoken'),
        scenes=['cream stat page (count-up)', 'green-bordered image card above the facecam'],
        transitions=['RGB glitch 6 frames'], hook='slice_glitch (green accent)', pace='graphic change every ~1.5-2 s',
        music='130-145 BPM dark synth / hacker', renderer='engine/template_render.py'),
    12: dict(
        key='cream-editorial', name='Cream Editorial', ref='t-12 (OmniRoute reel)',
        best_for='"free / unlimited" reveals, dev-tool deep dives, documentary tone', energy='medium',
        look='Cream panel across the top with condensed serif-italic caps words (spoken word in black, the big word in a '
             'coral gradient); he sits lower in his darkened room; dark pages with a terminal/image card and big white '
             'condensed italic words.',
        grade=dict(sat=0.88, contrast=1.12, gain=(1.02, 0.98, 0.95), vignette=0.5),
        fonts=dict(word='playfair-i:800 condensed 0.7x', big='playfair-i:800 condensed gradient'),
        palette=dict(accent='#E8603C', panel='#E7DCCF', big=('#FFB09A', '#E8603C'), page='#111111'),
        headline=dict(zone='cream panel y 270-640 above his head', anim='pop 0.85 -> 1.05 -> 1'),
        captions=dict(style='one-word-condensed-italic', zone='cream panel y 575', font_px=84, case='UPPER'),
        scenes=['dark page + image card + big italic word'], transitions=['blur dissolve 8 frames'],
        hook='shutter_blinds (coral accent)', pace='word every 0.3 s, scene every ~3 s', music='90-110 BPM moody electronic',
        renderer='engine/template_render.py'),
    13: dict(
        key='kanglish-tech-split', name='Kanglish Tech Split', ref='t-13 (Hinglish tech reel)',
        best_for='KANNADA / Kanglish tool news, app walkthroughs, "free alternative" reels', energy='high',
        look='Dark-teal room; a navy panel across the top with a small label and a neon glowing keyword; uppercase '
             'romanised captions in blue highlight chips; full-screen app windows on a navy grid that bend in like paper.',
        grade=dict(sat=0.9, contrast=1.1, gain=(0.92, 1.0, 1.06), vignette=0.4),
        fonts=dict(label='inter:700', neon='intertight:900 glow', chip='inter:800'),
        palette=dict(accent='#8A5CFF', chip='#4A4AE8', panel='#0A0E1C', grid='#1A2240'),
        headline=dict(zone='navy panel y 285-655', anim='pop + violet glow'),
        captions=dict(style='uppercase-chip', zone='under the chin', font_px=32, max_words=4, case='UPPER'),
        scenes=['navy grid page + app window card + title'], transitions=['paper bend 12 frames'],
        hook='zoom_punch (violet accent)', pace='chip every phrase, window every ~2-3 s', music='110-125 BPM Indian pop-tech / upbeat',
        renderer='engine/template_render.py'),
    14: dict(
        key='glass-dock', name='Glass Dock', ref='t-14 (Hinglish AI-tools reel)',
        best_for='"N free AI tools" roundups, app recommendations, creator tool stacks', energy='high',
        look='Warm amber grade; a frosted glass dock on the chest where app icons pop in one by one; big yellow gradient '
             'word with a small white line above it; dark page where a folder tile shoots coloured light beams and '
             'icons; UI card in the top half with him below.',
        grade=dict(sat=1.05, contrast=1.08, gain=(1.12, 1.0, 0.8), vignette=0.4),
        fonts=dict(big='intertight:900 gradient', small='inter:600', caption='inter:600'),
        palette=dict(accent='#F5B70F', big=('#FFEA5C', '#F2A20A'), page='#14161C'),
        headline=dict(zone='caption band (small line + big yellow word)', anim='pop 0.8 -> 1.06 -> 1'),
        captions=dict(style='chest-line-yellow-key', zone='caption band', font_px=38, max_words=4, case='as spoken'),
        scenes=['dark page + light-beam burst', 'UI card top half + speaker below'], transitions=['zoom-blur 8 frames'],
        hook='halftone_iris (amber accent)', pace='icon every spoken name, scene every ~3 s', music='100-115 BPM Indian indie / lo-fi',
        renderer='engine/template_render.py'),
    15: dict(
        key='clean-white-split', name='Clean White Split', ref='t-15 (all-AI-in-one-app reel)',
        best_for='cost comparisons, "replace N subscriptions", tool tours', energy='medium',
        look='Talking head with navy label boxes and a dark pill of tool logos; for features a white UI panel slides down '
             'from the top while he shrinks into the lower half; cream cost table with a navy header, rows typed as he '
             'names them, red italic total and an arrow to a navy answer box.',
        grade=dict(sat=0.95, contrast=1.08, gain=(1.0, 1.0, 1.02), vignette=0.35),
        fonts=dict(label='inter:700 / playfair-i:700', caption='inter:700', key='playfair-i:700', table='inter:500-800'),
        palette=dict(accent='#1C2340', navy='#1C2340', total='#D62F2F', panel='#FBFBFC', cream='#EFE7DA'),
        headline=dict(zone='navy label y 370 (talk) / y 755 (panel)', anim='box wipes open, then text'),
        captions=dict(style='chest-line-serif-key', zone='caption band', font_px=42, max_words=4, case='as spoken'),
        scenes=['white panel slides down + image + navy label', 'cream cost table typed row by row'],
        transitions=['hard cut (panel slide is the motion)'], hook='red_wipe (navy accent)', pace='row per spoken item',
        music='95-110 BPM clean corporate / lo-fi', renderer='engine/template_render.py'),
    16: dict(
        key='lime-polaroid', name='Lime Polaroid', ref='sezz0283 (agency reel)',
        best_for='agency / founder intros, client results, case studies, service offers', energy='medium',
        look='Soft white-to-green page; he shrinks into a white polaroid card with a "+ name" label and a black ribbon '
             'badge; words below with a lime highlighter on key words; a tree line to lime circles; phone mockups with '
             'results; full-frame talk with lime-boxed key words.',
        grade=dict(sat=1.02, contrast=1.04, gain=(1.0, 1.02, 0.98), vignette=0.0),
        fonts=dict(caption='inter:600', key='inter:700 on lime box', label='inter:700', badge='inter:800'),
        palette=dict(accent='#C8F135', lime='#C8F135', page='#F5F8F2', ink='#161616'),
        headline=dict(zone='words under the polaroid / chest line', anim='lime box sweeps open under the key word'),
        captions=dict(style='lime-highlight-line', zone='under the card or chin', font_px=44, max_words=3, case='as spoken'),
        scenes=['polaroid card + badge + highlighted words + tree', 'phone mockup with a result screen'],
        transitions=['scale cut 8 frames'], hook='letterbox_open (lime accent)', pace='card/phone switch every ~3-4 s',
        music='95-110 BPM feel-good house', renderer='engine/template_render.py'),
}


def get(n):
    if isinstance(n, str): n = int(n.replace('/temp-', '').replace('temp-', ''))
    return TEMPLATES[n]
