"""List today's GTA VI clips from big Kick streamers (public kick.com API works from the cloud env).
usage: python3 find_kick.py [channel ...]
download: yt-dlp -q -o k.mp4 https://kick.com/<channel>/clips/<clip_id> </dev/null   (1080p)"""
import sys,os,json,urllib.request
chs=sys.argv[1:] or ['adinross','xqc','n3on','trainwreckstv']
used=open('used_slugs.txt').read() if os.path.exists('used_slugs.txt') else ''
for c in chs:
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://kick.com/api/v2/channels/{c}/clips?sort=view&time=day',headers={'User-Agent':'Mozilla/5.0'}),timeout=20))
    except Exception as e: print(c,'error',e); continue
    for x in d.get('clips',[]):
        if 'Grand Theft Auto VI' not in ((x.get('category') or {}).get('name') or '') or x['id'] in used: continue
        print(x.get('view_count'),x.get('duration'),c,x.get('created_at','')[5:16],x['id'],(x.get('title') or '')[:60])
