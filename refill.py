"""Daily finite-year Buffer refill. Standard library only; no paid API calls."""
import datetime as dt,json,os,sys,urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).parent
TZ=ZoneInfo('Asia/Karachi')
CHANNEL='6ac4a54b6a5c39ccb62ce610'
def api(query,variables=None):
    key=os.environ.get('BUFFER_API_KEY')
    if not key: raise RuntimeError('Missing BUFFER_API_KEY repository secret')
    req=urllib.request.Request('https://api.buffer.com',data=json.dumps({'query':query,'variables':variables or {}}).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    # Never automatically retry a mutation: its first response may have been lost.
    try:
        with urllib.request.urlopen(req,timeout=45) as r: body=json.load(r)
    except Exception:
        raise RuntimeError('Buffer request failed; no automatic retry. Inspect Actions and Buffer queue.') from None
    if body.get('errors'): raise RuntimeError('Buffer GraphQL request rejected; check current schema and permissions')
    return body['data']
def plan(rows,posts,now):
    # An existing scheduled/sent/sending post occupies its local calendar day.
    occupied={dt.datetime.fromisoformat(p['dueAt'].replace('Z','+00:00')).astimezone(TZ).date().isoformat() for p in posts if p.get('dueAt') and p['status'] in ('scheduled','sent','sending')}
    future=sum(p['status']=='scheduled' for p in posts)
    if any(p['status']=='error' for p in posts): raise RuntimeError('Buffer reports a failed post; inspect before refilling')
    selected=[]
    for row in rows:
        due=dt.datetime.combine(dt.date.fromisoformat(row['date']),dt.time(20,0),TZ)
        if now < due <= now+dt.timedelta(days=7) and row['date'] not in occupied and future+len(selected)<10:
            selected.append((row,due))
    return selected

def run():
    rows=json.loads((ROOT/'calendar.json').read_text());now=dt.datetime.now(TZ)
    if now.date()>dt.date.fromisoformat(rows[-1]['date']):
        print('Calendar complete. No more posts will be created.');return
    org=os.environ.get('BUFFER_ORGANIZATION_ID')
    if not org:
        org=api('query { channel(input: {id: '+json.dumps(CHANNEL)+'}) { organizationId } }')['channel']['organizationId']
    board=os.environ.get('BUFFER_BOARD_ID')
    if not board:
        boards=api('query { channel(input: {id: '+json.dumps(CHANNEL)+'}) { metadata { ... on PinterestMetadata { boards { serviceId } } } } }')['channel']['metadata']['boards']
        if len(boards)!=1: raise RuntimeError('Set BUFFER_BOARD_ID to Subscription Planning & Renewal Checklists; do not guess a board')
        board=boards[0]['serviceId']
    posts=[];cursor=None
    query='query($input: PostsInput!, $after: String) { posts(first: 100, after: $after, input: $input) { edges { node { id dueAt status text } } pageInfo { hasNextPage endCursor } } }'
    for page in range(20):
        result=api(query,{'input':{'organizationId':org,'filter':{'channelIds':[CHANNEL],'status':['scheduled','sent','sending','error']}},'after':cursor})['posts']
        posts.extend(e['node'] for e in result['edges'])
        if not result['pageInfo']['hasNextPage']:break
        cursor=result['pageInfo']['endCursor']
    else: raise RuntimeError('Incomplete pagination; refusing to schedule')
    base=os.environ.get('PUBLIC_MEDIA_BASE','https://raw.githubusercontent.com/QaziIhsanAhmad/renewal-desk-automation/main').rstrip('/')
    if not base.startswith('https://'): raise RuntimeError('PUBLIC_MEDIA_BASE must be an HTTPS public directory containing media/')
    chosen=plan(rows,posts,now)
    for row,due in chosen:
        url=base+'/'+row['image']
        try:
            with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as r:
                if not r.headers.get('Content-Type','').startswith('image/'):raise ValueError()
        except Exception:raise RuntimeError('Public image unavailable; no post created') from None
        payload={'channelId':CHANNEL,'text':row['text'],'schedulingType':'automatic','mode':'customScheduled','dueAt':due.astimezone(dt.timezone.utc).isoformat(),'needsApproval':False,'saveToDraft':False,'aiAssisted':True,'assets':[{'image':{'url':url}}],'metadata':{'pinterest':{'boardServiceId':board,'title':row['title'],'url':row['url']}}}
        if '--check' in sys.argv:
            print('Would schedule:',row['date'],row['title']);continue
        result=api('mutation($input: CreatePostInput!) { createPost(input: $input) { ... on PostActionSuccess { post { id dueAt status } } ... on MutationError { message } } }',{'input':payload})['createPost']
        post=result.get('post')
        if not post or post.get('status')!='scheduled':raise RuntimeError('Buffer did not confirm scheduling; inspect queue before rerun')
        print('Scheduled',row['date'],'post',post['id'])
    print('Checked',len(posts),'existing posts; candidates',len(chosen),'; revenue unavailable')
if __name__=='__main__':
    try:run()
    except Exception as exc:
        print('STOP:',str(exc),file=sys.stderr);sys.exit(1)
