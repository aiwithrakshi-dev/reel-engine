#!/usr/bin/env python3
"""Build job JSONs for the 15.5 s Day 4 demo of every template (/temp-2 ... /temp-7).
Paths come from REEL_D4 (default /home/claude/d4). Output: examples/templates_demo/jobs/temp-N.json"""
import os, json
D4 = os.environ.get('REEL_D4', '/home/claude/d4'); WEB = f'{D4}/web'; HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 15.5
HEADS = [dict(label='claude and codex inside', big='ANDROID STUDIO', label_t=0.0, big_t=2.26),
         dict(label='and they can', big='TEST', label_t=3.24, big_t=4.4),
         dict(label='bring your own', big='AGENT', label_t=6.08, big_t=6.76),
         dict(label='not a', big='BETA', label_t=8.96, big_t=9.5),
         dict(label='pick from more than', big='40 AGENTS', label_t=10.02, big_t=10.9),
         dict(label='your pick', big='ANY AGENT', label_t=12.26, big_t=12.26)]
for i in range(len(HEADS) - 1): HEADS[i]['until'] = HEADS[i + 1]['label_t']
HEADS[-1]['until'] = DUR
IMG = dict(sel=f'{WEB}/agent_selector.png', reg=f'{WEB}/agent_registry.png', emu=f'{WEB}/emulator_environment_86a016acf3_ZrhT3l.webp',
           rev=f'{WEB}/change_review_177f39b007_2qhMik.webp', cc=f'{WEB}/change_review_177f39b007_2qhMik.webp', leak=f'{WEB}/Leak_Canary_AI_Fix_Zoomed_in_6c582c3d5a_Z17WTmJ.webp')
MUSIC = {2: 'Night_Run_Sequence', 3: 'Midnight_Bounce', 4: 'Glitch_Bounce_Loop', 5: 'Pressure_Line', 6: 'Drop_Point', 7: 'Black_Asphalt',
         8: 'Midnight_Bounce', 9: 'Glitch_Bounce_Loop', 10: 'Pressure_Line', 11: 'Black_Asphalt', 12: 'Night_Run_Sequence',
         13: 'Drop_Point', 14: 'Midnight_Bounce', 15: 'Night_Run_Sequence', 16: 'Glitch_Bounce_Loop'}
NAMES = [(12.26, 'Claude', 'C', '#D97757'), (13.22, 'Codex', 'X', '#111111'), (14.02, 'Junie', 'J', '#21C25E'), (14.70, 'Antigravity', 'A', '#4285F4')]
SCENES = {
    2: [dict(t0=2.15, t1=6.12, title='Agents inside Android Studio', sub='Claude and Codex, side by side', items=['Claude', 'Codex']),
        dict(t0=10.04, t1=12.1, title='40+ agents', sub='pick the one you trust', image=IMG['reg'])],
    3: [dict(t0=2.3, t1=4.3, image=IMG['cc']), dict(t0=6.1, t1=8.0, image=IMG['sel']), dict(t0=10.04, t1=12.1, image=IMG['reg']),
        dict(t0=13.2, t1=15.0, image=IMG['emu'])],
    4: [dict(t0=3.2, t1=6.1, kicker='STEP #1', title='Claude and Codex test their own code', image=IMG['cc']),
        dict(t0=10.04, t1=12.9, kicker='STEP #2', title='Pick from 40+ agents', image=IMG['reg'])],
    5: [dict(t0=2.15, t1=6.12, image=IMG['cc']), dict(t0=10.04, t1=12.6, title='Which agent do you pick?', image=IMG['sel'])],
    6: [dict(t0=2.6, t1=5.6, title='Stable, not beta', quote=dict(name='Android Developers', handle='Android Studio release notes',
                                                                       text='Bring Your Own Agent is now\nin the stable release.')),
        dict(t0=10.04, t1=12.2, title='40+ agents', image=IMG['reg'])],
    7: [dict(t0=2.15, t1=5.0, title='Agents inside Android Studio', image=IMG['cc']),
        dict(t0=10.6, t1=13.2, title='Pick from 40+ agents', image=IMG['reg'])],
    8: [dict(t0=3.2, t1=6.1, items=['Claude', 'Codex', 'Tests its own code']), dict(t0=10.04, t1=12.1, image=IMG['reg'])],
    9: [dict(t0=2.15, t1=5.0, title='Inside Android Studio', items=['Claude', 'Codex', 'Test own code']),
        dict(t0=10.04, t1=11.95, kicker='Pick from 40+ agents', image=IMG['reg'])],
    10: [dict(t0=2.15, t1=5.0, image=IMG['cc']), dict(t0=10.04, t1=12.1, image=IMG['reg'])],
    11: [dict(t0=2.3, t1=4.3, image=IMG['cc']), dict(t0=10.04, t1=11.95, stat='40+', title='agents', sub='to pick from in Android Studio')],
    12: [dict(t0=2.15, t1=4.2, image=IMG['cc']), dict(t0=10.04, t1=12.0, image=IMG['reg'])],
    13: [dict(t0=2.3, t1=4.6, image=IMG['cc'], title='Claude + Codex in Android Studio'), dict(t0=10.04, t1=12.1, image=IMG['reg'], title='Pick from 40+ agents')],
    14: [dict(t0=2.2, t1=4.4, title='Inside Android Studio', icon='A'), dict(t0=10.04, t1=12.1, image=IMG['reg'])],
    15: [dict(t0=2.15, t1=5.0, image=IMG['cc'], title='Claude + Codex'),
         dict(t0=12.15, t1=15.5, rows=[dict(t=t, name=n, val='Yes') for t, n, _, _ in NAMES], head=['AGENT', 'IN STUDIO'])],
    16: [dict(t0=6.1, t1=9.0, polaroid=True, name='Rakshith', badge='STABLE', items=['Claude', 'Codex']),
         dict(t0=10.04, t1=12.1, image=IMG['reg'])],
}
HOOKS = {2: 'letterbox_open', 3: 'face_punch', 4: 'shutter_blinds', 5: 'zoom_punch', 6: 'strip_slam', 7: 'halftone_iris',
         8: 'rgb_converge', 9: 'pixel_assemble', 10: 'strip_slam', 11: 'slice_glitch', 12: 'shutter_blinds', 13: 'zoom_punch',
         14: 'halftone_iris', 15: 'red_wipe', 16: 'letterbox_open'}
os.makedirs(f'{HERE}/jobs', exist_ok=True)
for n in range(2, 17):
    job = dict(template=n, aroll=f'{D4}/aroll_patched30.mp4', src_fps=30, dy=60, duration=DUR,
               face=dict(cap_top=505, chin=1100, x0=330, x1=750), words=f'{D4}/words_reel.json', headlines=HEADS,
               scenes=SCENES[n], hook=HOOKS[n], vo=f'{D4}/vo_proc.wav', music=f'{D4}/music/{MUSIC[n]}.mp3', music_db=-16,
               glossary=os.path.join(HERE, '..', 'day4_android_studio', 'glossary.json'))
    if n == 11: job['headlines'] = [dict(h, stamp=True) if h['big'] == 'BETA' else h for h in HEADS]
    if n == 9: job['tiles'] = [dict(t=t, label=str(k + 1)) for k, (t, _, _, _) in enumerate(NAMES)]
    if n == 14: job['dock'] = [dict(t=t, label=l, color=c) for t, _, l, c in NAMES]
    if n == 10: job['brand'] = 'Android Studio'
    if n == 2: job['hook_until'] = 2.15
    if n == 4: job['banner'] = [0.0, 3.1, 'ANDROID STUDIO + AI', 'BRING YOUR OWN AGENT']
    if n == 7: job['flash'] = [6.76, 9.5]
    json.dump(job, open(f'{HERE}/jobs/temp-{n}.json', 'w'), indent=1)
print('jobs written')
