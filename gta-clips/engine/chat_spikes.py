#!/usr/bin/env python3
"""Find hype moments in a Twitch VOD by sampling its chat replay.
usage: chat_spikes.py VIDEO_ID START_S END_S [STEP_S=20] > spikes.json
Samples chat every STEP_S seconds: message rate + hype words ("clip", lmao, kekw...)."""
import sys, json, re, urllib.request, concurrent.futures as cf
CID = 'kd1unb4b3q4t58fwlpcbzcbnm76a8fp'
HASH = 'b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a'
HYPE = re.compile(r'(clip|lol|lmao|lmfao|kekw|omegalul|lul|icant|😂|💀|🤣|wtf|nah+|bro|crazy|aint no way|w+ |holy)', re.I)

def page(vid, off):
    body = json.dumps([{"operationName": "VideoCommentsByOffsetOrCursor",
        "variables": {"videoID": vid, "contentOffsetSeconds": off},
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": HASH}}}]).encode()
    r = urllib.request.Request('https://gql.twitch.tv/gql', body, {'Client-Id': CID, 'Content-Type': 'application/json'})
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(r, timeout=20))
            edges = d[0]['data']['video']['comments']['edges']
            return off, [(e['node']['contentOffsetSeconds'], ''.join(f['text'] for f in e['node']['message']['fragments'])) for e in edges]
        except Exception:
            pass
    return off, []

def main():
    vid, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    out = []
    with cf.ThreadPoolExecutor(8) as ex:
        for off, msgs in ex.map(lambda o: page(vid, o), range(a, b, step)):
            # drop giveaway / command noise: numbers, !commands, @replies, bot lines
            msgs = [(o, t) for o, t in msgs if t.strip() and not re.fullmatch(r'[\d\s.,]+', t.strip()) and not t.strip().startswith(('!', '@')) and 'giveaway' not in t.lower() and 'you have' not in t.lower()]
            if len(msgs) < 3: continue
            span = max(1, msgs[-1][0] - msgs[0][0])
            rate = len(msgs) / span
            hype = sum(1 for _, t in msgs if HYPE.search(t)) / len(msgs)
            out.append({"t": off, "rate": round(rate, 2), "hype": round(hype, 2),
                        "score": round(rate * (0.5 + hype), 2), "sample": [t for _, t in msgs[:6]]})
    base = sorted(x['score'] for x in out)[len(out)//2] if out else 1
    for x in out: x['vs_median'] = round(x['score'] / max(base, 0.01), 2)
    json.dump(sorted(out, key=lambda x: -x['score']), sys.stdout, ensure_ascii=False, indent=1)
main()
