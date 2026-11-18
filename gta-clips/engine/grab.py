#!/usr/bin/env python3
"""Grab a section of a Twitch VOD from its link without downloading the whole thing.
usage: grab.py VOD_URL START_S END_S OUT.mp4 [QUALITY=1080p60]"""
import sys, subprocess, urllib.request, tempfile, os, re
url, a, b, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
q = sys.argv[5] if len(sys.argv) > 5 else '1080p60'
m3u = subprocess.check_output(['yt-dlp', '-g', '-f', f'{q}/best', url], text=True).strip().splitlines()[0]
base = m3u.rsplit('/', 1)[0]
pl = urllib.request.urlopen(m3u).read().decode().splitlines()
segs, t, init = [], 0.0, None
for i, line in enumerate(pl):
    if line.startswith('#EXT-X-MAP:'):
        init = re.search(r'URI="([^"]+)"', line).group(1)
    if line.startswith('#EXTINF:'):
        d = float(line[8:].split(',')[0]); name = pl[i+1]
        if t + d > a and t < b: segs.append((t, name))
        t += d
tmp = tempfile.mkdtemp()
ext = 'mp4' if init else 'ts'   # newer VODs use fragmented MP4 segments with an init header
with open(f'{tmp}/all.{ext}', 'wb') as f:
    if init: f.write(urllib.request.urlopen(f'{base}/{init}', timeout=60).read())
    for _, name in segs:
        f.write(urllib.request.urlopen(f'{base}/{name}', timeout=60).read())
start = a - segs[0][0]
subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-ss', str(start), '-i', f'{tmp}/all.{ext}', '-t', str(b - a),
                       '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', out])
print(out, len(segs), 'segments')
