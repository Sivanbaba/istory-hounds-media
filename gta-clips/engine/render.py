#!/usr/bin/env python3
"""Stream clip -> 1080x1920 vertical: facecam on top, gameplay below, word captions, hook title.
usage: render.py SPEC.json
spec: {"src": raw.mp4, "words": words.json, "out": out.mp4, "segments": [[a,b],...],
       "face": [x,y,w,h], "game_cx": 960, "hook": "TEXT", "hook_s": 2.5}"""
import sys, json, re, subprocess, os
S = json.load(open(sys.argv[1])); D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(D, 'Montserrat-BlackItalic.ttf')
W, H = 1080, 1920
CAM = S.get('mode') == 'cam'                 # just-chatting: whole frame is the facecam -> one 9:16 crop
fx, fy, fw, fh = S.get('face', [0, 0, 1920, 1080])
FH = 0 if CAM else round(W * fh / fw / 2) * 2   # facecam height on canvas
GH = H - FH                                  # gameplay height
gw = round(1080 * W / GH / 2) * 2            # source crop width for gameplay
gx = max(0, min(1920 - gw, S.get('game_cx', 960) - gw // 2))
CLEAN = lambda w: re.sub(r'(?i)f(u)ck', r'F*CK', re.sub(r'(?i)sh(i)t', 'SH*T', w))
# timeline: map source time -> output time over the kept segments
segs = S['segments']; words = json.load(open(S['words']))
def out_t(t):
    o = 0
    for a, b in segs:
        if a <= t <= b: return o + t - a
        o += b - a
    return None
# group words into 1-3 word captions
caps, cur = [], []
for w in words:
    t0, t1 = out_t(w['s']), out_t(w['e'])
    if t0 is None or t1 is None: continue
    if cur and (len(cur) >= 3 or t0 - cur[-1][2] > 0.35 or cur[-1][0].endswith(('.', '!', '?', ','))):
        caps.append(cur); cur = []
    cur.append((CLEAN(w['w']).upper().strip(','), t0, t1))
if cur: caps.append(cur)
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ass = [f"""[Script Info]
PlayResX: {W}
PlayResY: {H}
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat Black,92,&H00FFFFFF,&H0000E1FF,&H00000000,&H64000000,1,1,0,0,100,100,0,0,1,7,3,5,40,40,0
Style: Tag,Montserrat Black,46,&H00FFFFFF,&H00FFFFFF,&H00FF4191,&H00FF4191,1,1,0,0,100,100,0,0,3,14,0,5,40,40,0
Style: Hook,Montserrat Black,84,&H0000E1FF,&H00FFFFFF,&H00000000,&H64000000,1,1,0,0,100,100,0,0,1,8,3,5,40,40,0
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""]
cy = 1330 if CAM else FH + 330                               # captions just under the facecam, over the gameplay sky
hook_end = S.get('hook_s', 2.5)
for c in caps:
    s, e = c[0][1], max(c[-1][2], c[0][1] + 0.45)
    if s < hook_end: continue
    for i, (w, a, b) in enumerate(c):      # karaoke: current word yellow
        txt = ' '.join(('{\\c&H00E1FF&}' + x + '{\\c&HFFFFFF&}') if j == i else x for j, (x, _, _) in enumerate(c))
        end = c[i+1][1] if i + 1 < len(c) else e
        ass.append(f"Dialogue: 0,{ts(a if i else s)},{ts(end)},Cap,,0,0,0,,{{\\pos({W//2},{cy})}}{txt}")
ass.append(f"Dialogue: 1,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\pos({W//2},{430 if CAM else FH})\\fscx100}}{S['hook']}")
if S.get('overlay'):                     # campaign overlay, e.g. twitch.tv/name, on screen the whole clip
    total = sum(b - a for a, b in segs)
    ass.append(f"Dialogue: 2,{ts(0)},{ts(total)},Tag,,0,0,0,,{{\\pos({W//2},{S.get('overlay_y', 230 if CAM else FH - 40)})}}{S['overlay']}")
open(S['out'] + '.ass', 'w').write('\n'.join(ass))
# zoom punches: quick 12% push-in for 0.45s at these OUTPUT times (big moments)
pz = '+'.join(f'between(t,{p:.2f},{p+0.45:.2f})' for p in S.get('punch', []))
PUNCH = (f"scale=w='{W}*(1+0.12*({pz}))':h=-2:eval=frame,crop={W}:{H}," if pz else '')
# video: trim+concat segments, then stack
parts = ''.join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i, (a, b) in enumerate(segs))
cat = ''.join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a];"
fc = (parts + cat +
      ((f"[v]crop=608:1080:{max(0, min(1312, S.get('cam_cx', 960) - 304))}:0,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,") if CAM else
       (f"[v]split[s1][s2];[s1]crop={fw}:{fh}:{fx}:{fy},scale={W}:{FH}:flags=lanczos,unsharp=5:5:0.8[face];"
        f"[s2]crop={gw}:1080:{gx}:0,scale={W}:{GH}:flags=lanczos[game];"
        f"[face][game]vstack,drawbox=x=0:y={FH-3}:w={W}:h=6:color=black@1:t=fill,")) +
      PUNCH +
      f"ass={S['out']}.ass:fontsdir={D}[vo];"
      f"[a]loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', S['src'], '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]',
    '-r', '60', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
    '-movflags', '+faststart', S['out']])
print(S['out'])
