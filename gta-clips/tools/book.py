"""Book reviewed clips on Post for Me (TikTok at slot, Instagram +15 min, YouTube +30 min).
usage: POSTFORME_API_KEY=... python3 book.py plan.json [key ...]
plan.json = {"date":"2026-11-19","prefix":"d19","skip_hub_tiktok":false,
  "clips":[{"key":"x1","acct":"bolted","slot":"15:30","file":"out_x1.mp4","title":"...","caption":"...","replace":"old_key_or_null"}]}
Hub clips: pass the _c.mp4 cover version as file (thumbnail_timestamp_ms 100 is set automatically).
external_id = clips-{acct}-{prefix}{key}-{platform}  (keep the date prefix: reused ids are silently skipped).
Slot "25:30" = 01:30 next day. Log appended to posted_{prefix}.json."""
import os,sys,json,time,requests,datetime as dt
K=os.environ['POSTFORME_API_KEY'];B='https://api.postforme.dev/v1';H={'Authorization':'Bearer '+K}
ACCTS={'bolted':{'tiktok':'spc_PWq5BzlWpV4NYcu8i7Qfe','instagram':'spc_k9WvI9Ip8vkbTZnAIciaU','youtube':'spc_mfIszziXNV9dlWdcAeVk'},
       'hub':{'tiktok':'spc_aiarv0av0BGB2D60aS5Fg','instagram':'spc_bAxFKMHpfikh3wTvGkLy','youtube':'spc_UFEzbpNPPB1nGDt5NOAy'},
       'anger':{'tiktok':'spc_4r6HNZBE2IFX8KDlIf','instagram':'spc_V00jmGukgjHYn0hWhfR8B','youtube':'spc_9Pzev6dosx6niTesgu3n7'}}
def call(m,u,**kw):
    for i in range(8):
        r=requests.request(m,B+u,headers=H,timeout=600,**kw)
        if r.status_code==429: time.sleep(10*(i+1)); continue
        return r
    return r
plan=json.load(open(sys.argv[1])); only=sys.argv[2:]; pre=plan['prefix']
y,mo,d=map(int,plan['date'].split('-'))
logf=f'posted_{pre}.json'; log=json.load(open(logf)) if os.path.exists(logf) else []
for c in plan['clips']:
    k,an=c['key'],c['acct']
    if only and k not in only: continue
    if c.get('replace'):
        for p in call('GET','/social-posts',params={'status':'scheduled','limit':100}).json().get('data',[]):
            if p['external_id'].startswith(f"clips-{an}-{pre}{c['replace']}-"):
                print('delete',p['external_id'],call('DELETE','/social-posts/'+p['id']).status_code)
    hh,mm=map(int,c['slot'].split(':'))
    t0=dt.datetime(y,mo,d,tzinfo=dt.timezone.utc)+dt.timedelta(hours=hh,minutes=mm)
    u=call('POST','/media/create-upload-url',json={}).json()
    with open(c['file'],'rb') as fh: requests.put(u['upload_url'],data=fh,headers={'Content-Type':'video/mp4'},timeout=600).raise_for_status()
    media={'url':u['media_url']}
    if an=='hub': media['thumbnail_timestamp_ms']=100
    for i,(p,cfg) in enumerate([('tiktok',{'title':c['title'],'privacy_status':'public','is_ai_generated':False}),
        ('instagram',{'placement':'reels','share_to_feed':True}),
        ('youtube',{'title':c['title']+' #shorts','category_id':'20','made_for_kids':False,'privacy_status':'public'})]):
        if an=='hub' and p=='tiktok' and plan.get('skip_hub_tiktok'): continue
        body={'caption':c['caption'],'media':[media],'social_accounts':[ACCTS[an][p]],'platform_configurations':{p:cfg},
              'external_id':f'clips-{an}-{pre}{k}-{p}','scheduled_at':(t0+dt.timedelta(minutes=15*i)).strftime('%Y-%m-%dT%H:%M:%SZ')}
        r=call('POST','/social-posts',json=body); print(body['external_id'],r.status_code); j=r.json(); log.append({x:j.get(x) for x in ('id','external_id','scheduled_at','status','caption')})  # never log social_accounts (holds tokens)
json.dump(log,open(logf,'w'),indent=1)
