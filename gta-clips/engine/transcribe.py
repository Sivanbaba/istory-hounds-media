#!/usr/bin/env python3
"""Word-timed transcript of a stream clip: Gemini on 10s chunks (keeps timings honest).
usage: transcribe.py CLIP.mp4 OUT.json   -> [{"w": word, "s": start, "e": end}] (game lines dropped)"""
import sys, os, json, base64, subprocess, urllib.request, concurrent.futures as cf, tempfile
src, out = sys.argv[1], sys.argv[2]
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
tmp = tempfile.mkdtemp(); CH = 10.0
KEYS = [os.environ.get(k) for k in ('GEMINI_API_KEY','GEMINI_API_KEY_2','GEMINI_API_KEY_3') if os.environ.get(k)]
def one(i):
    a = i * CH; fn = f'{tmp}/{i}.mp3'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-t',str(CH),'-i',src,'-ac','1','-ar','16000','-b:a','64k',fn])
    body = {"contents":[{"parts":[{"inline_data":{"mime_type":"audio/mp3","data":base64.b64encode(open(fn,'rb').read()).decode()}},
        {"text":"This is 10 seconds of a gaming livestream. Transcribe ONLY the streamer talking (skip in-game characters, music, sound effects). "
                 "Return a JSON list of words: {\"w\": word, \"s\": start_seconds, \"e\": end_seconds}, times relative to this 10 second clip (0-10). Keep swear words as said. Empty list if the streamer says nothing."}]}],
        "generationConfig":{"response_mime_type":"application/json","temperature":0}}
    for k in KEYS * 2:
        try:
            r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={k}", json.dumps(body).encode(), {"Content-Type":"application/json"})
            d = json.load(urllib.request.urlopen(r, timeout=120))
            ws = json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
            return [{"w": x["w"], "s": round(a + min(float(x["s"]), CH), 2), "e": round(a + min(float(x["e"]), CH), 2)} for x in ws]
        except Exception as e:
            err = e
    print('chunk', i, 'failed', err, file=sys.stderr); return []
with cf.ThreadPoolExecutor(6) as ex:
    words = [w for ch in ex.map(one, range(int(dur // CH) + (dur % CH > 0.5))) for w in ch]
json.dump(words, open(out, 'w'), indent=0)
print(' '.join(f"[{w['s']:.0f}]{w['w']}" if i % 8 == 0 else w['w'] for i, w in enumerate(words)))
