"""List today's GTA 6 Twitch clips for big streamers (public Twitch GQL, no login needed).
usage: python3 find_clips.py [since_iso] [login ...]   -> prints views, secs, login, time, slug, title
Skip slugs already in used_slugs.txt (same folder you run from)."""
import sys,os,requests
CID='kd1unb4b3q4t58fwlpcbzcbnm76a8fp'
since=sys.argv[1] if len(sys.argv)>1 else ''
logins=sys.argv[2:] or ['kaicenat','xqc','lacy','ohnepixel','agent00','jasontheween','jynxzi','caseoh_','summit1g','plaqueboymax','stableronaldo','valkyrae','emiru','pokimane','cinna']
used=open('used_slugs.txt').read() if os.path.exists('used_slugs.txt') else ''
for l in logins:   # ONE login per query (alias limit + GQL service errors)
    q='{user(login:"%s"){stream{game{name} viewersCount} clips(criteria:{period:LAST_DAY},first:50){edges{node{slug title viewCount durationSeconds createdAt game{name}}}}}}'%l
    try: u=requests.post('https://gql.twitch.tv/gql',headers={'Client-Id':CID},json={'query':q},timeout=15).json()['data']['user']
    except Exception as e: print(l,'error',e); continue
    if not u: continue
    for e in ((u.get('clips') or {}).get('edges') or []):
        n=e['node']
        if (n['game'] or {}).get('name')!='Grand Theft Auto VI' or n['slug'] in used or n['createdAt']<since: continue
        print(n['viewCount'],n['durationSeconds'],l,n['createdAt'][5:16],n['slug'],n['title'][:70])
