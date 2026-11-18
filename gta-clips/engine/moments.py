#!/usr/bin/env python3
"""Rank clip-worthy moments in a Twitch VOD: streamer audio peaks x real chat reactions.
usage: moments.py VIDEO_ID AUDIO_FILE [TOP=12] > moments.json
Chat counts only laughter/shock (LUL, KEKW, LMAO, 😂, 💀, wtf, nah, omg, no way...), not W-spam or giveaway numbers.
Audio = loudness of 1s windows vs the stream's own median (screams, yelling, big laughs)."""
import sys, json, re, subprocess, urllib.request, concurrent.futures as cf, numpy as np
CID = 'kd1unb4b3q4t58fwlpcbzcbnm76a8fp'
HASH = 'b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a'
LAUGH = re.compile(r'(lul|kekw|omegalul|lmao|lmfao|lol|haha|😂|🤣|💀|icant|i cant|wtf|nah+h|no way|omg|holy|bro what|clip|deadass|crying|dead\b|💀)', re.I)
vid, audio = sys.argv[1], sys.argv[2]; TOP = int(sys.argv[3]) if len(sys.argv) > 3 else 12
DUR = int(sys.argv[4]) if len(sys.argv) > 4 else 0
STEP = int(sys.argv[5]) if len(sys.argv) > 5 else 10
if audio == '-':                                       # chat-only mode (long VODs): no loudness
    n = DUR; loud = np.zeros(n)
else:
  x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '8000', '-f', 's16le', '-']), np.int16).astype(np.float32)
  n = len(x) // 8000
  db = np.array([20 * np.log10(np.sqrt((x[i*8000:(i+1)*8000] ** 2).mean()) + 1) for i in range(n)])
  k = 300; med = np.array([np.median(db[max(0, i-k):i+k:5]) for i in range(n)])
  loud = np.clip(db - med, 0, None)                     # dB above local median
def page(off):
    body = json.dumps([{"operationName": "VideoCommentsByOffsetOrCursor", "variables": {"videoID": vid, "contentOffsetSeconds": off},
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": HASH}}}]).encode()
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request('https://gql.twitch.tv/gql', body, {'Client-Id': CID, 'Content-Type': 'application/json'}), timeout=20))
            return [(e['node']['contentOffsetSeconds'], ''.join(f['text'] for f in e['node']['message']['fragments'])) for e in d[0]['data']['video']['comments']['edges']]
        except Exception: pass
    return []
laugh = np.zeros(n); samples = {}
with cf.ThreadPoolExecutor(10) as ex:
    for msgs in ex.map(page, range(0, n, STEP)):
        for o, t in msgs:
            if o < n and LAUGH.search(t) and not t.strip().startswith(('!', '@')):
                laugh[o] += 1; samples.setdefault(o // 10, []).append(t[:40])
# score each 10s window: chat laughter in the 25s after it + loud audio inside it
W = 10; scores = []
for s in range(0, n - 30, 5):
    a = np.sort(loud[s:s+W])[-3:].mean()
    c = laugh[s+3:s+28].sum()
    scores.append((float(a * 1.0 + c * 0.8), s, float(a), int(c)))
scores.sort(reverse=True); picked = []
for sc, s, a, c in scores:
    if all(abs(s - p['t']) > 90 for p in picked):
        picked.append({"t": s, "score": round(sc, 1), "loud_db": round(a, 1), "chat_laughs": c,
                       "chat": sum((samples.get(b, []) for b in range((s+3)//10, (s+28)//10 + 1)), [])[:8]})
    if len(picked) >= TOP: break
json.dump(picked, sys.stdout, ensure_ascii=False, indent=1)
