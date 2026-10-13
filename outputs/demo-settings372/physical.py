"""E-only demo preferences deployment. No driver replacement or console C access."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,put,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
O=K/'physical001';A=Path('E:/xwn372/physical001');P=Path('E:/xwn372/package001')
START='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
NS='/E/xwndemo372';LAUNCH='/E/Applications/XWNEBoot/default.xbe'
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
installed=read(K.parent/'stock-physical337/package001.json')['files'];lookup={p.lower():p for p in installed}
translate=lambda p:'/E/'+p[3:] if p.startswith('/F/') else p.replace('/XWNFBoot/','/XWNEBoot/')
fixed={lookup[translate(p).lower()]:installed[lookup[translate(p).lower()]]['sha256'] for p in policy}
def path(p):
    assert p.startswith(('/E/','/F/')) and '\\' not in p and '..' not in p.split('/') and '//' not in p;return p
def fetch(f,p,optional=False):return get(f,path(p),optional)
def store(f,p,b):
    allowed=[NS+'/'+n for n in read(K/'package001.json')['files']]+[START]
    assert p in allowed;ticket();put(f,path(p),b)
def capture():
    ticket();assert not O.exists() and not A.exists();O.mkdir();A.mkdir(parents=True)
    r=dict(completed=False,files={},console_C_accessed=False,physical_writes=False,started_utc=utc());write_json(O/'before.json',r)
    with connect() as f:
        assert 'xwndemo372' not in {n.lower() for n in names(f,'/E')}
        expected={**fixed,**{p:v['sha256'] for p,v in policy.items()}}
        paths=list(expected)+[START,'/E/documents and settings/win2k/ntuser.dat']+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default']]
        for p in dict.fromkeys(paths):
            b=fetch(f,p)
            if p in expected:assert sha(b)==expected[p],('Baseline mismatch',p)
            if p==START:assert b==Path('E:/xwn337/package001'+START).read_bytes()
            q=A/p.lstrip('/');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);assert q.read_bytes()==b
            r['files'][p]=dict(bytes=len(b),sha256=sha(b))
        r.update(completed=True,completed_utc=utc());write_json(O/'before.json',r)
    print('E/F baseline and startup preserved; no driver or console C change')
def deploy():
    assert read(K.parent/'demo-runtime373/control001/audit.json')['outline_settings_passed']
    assert read(K.parent/'demo-runtime373/control001/audit.json')['scoped_combined_passed']
    assert not (O/'deployment.json').exists();before=read(O/'before.json');assert before['completed']
    pkg=read(K/'package001.json');r=dict(completed=False,writes=[],console_C_accessed=False,driver_changed=False,started_utc=utc());dest=O/'deployment.json';write_json(dest,r)
    with connect() as f:
        for p,v in before['files'].items():assert sha(fetch(f,p))==v['sha256'],('Changed baseline',p)
        f.mkd(NS)
        try:
            for n,v in pkg['files'].items():
                b=(P/n).read_bytes();assert sha(b)==v['sha256'];r['writes'].append(NS+'/'+n);write_json(dest,r);store(f,NS+'/'+n,b)
            b=(P/'demo-startup.cmd').read_bytes();assert sha(b)==pkg['startup']['sha256'];r['writes'].append(START);write_json(dest,r);store(f,START,b)
            r.update(completed=True,completed_utc=utc(),startup_sha256=sha(b));write_json(dest,r)
        except BaseException as e:
            r['error']=repr(e);store(f,START,(A/START.lstrip('/')).read_bytes());r['startup_restored_on_failure']=True;write_json(dest,r);raise
    print('Demo add-on readback verified; original drivers unchanged')
def launch():
    assert read(O/'deployment.json')['completed'] and not (O/'launch.json').exists()
    with connect() as f:
        assert sha(fetch(f,LAUNCH))==fixed[LAUNCH]
        assert sha(fetch(f,START))==read(K/'package001.json')['startup']['sha256']
        r=dict(requested=True,utc=utc(),command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe',stay_at_desktop=True,console_C_accessed=False);write_json(O/'launch.json',r)
        f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as e:r['reply_uncertain']=type(e).__name__
        write_json(O/'launch.json',r)
    print('Single demo launch recorded; no timed shutdown, do not relaunch')
def collect():
    assert not (O/'collection.json').exists();r=dict(utc=utc(),files={},console_C_accessed=False)
    with connect() as f:
        for n in ['outline-first.txt','outline-applied.txt']:
            b=fetch(f,NS+'/'+n,True);r['files'][n]=None if b is None else dict(sha256=sha(b),text=b.decode('ascii'))
        for p,h in fixed.items():assert sha(fetch(f,p))==h,p
        for p,v in policy.items():assert sha(fetch(f,p))==v['sha256'],p
        r['drivers_and_F_rollback_unchanged']=True
    write_json(O/'collection.json',r);print(json.dumps(r,indent=2))
if __name__=='__main__':
    action=sys.argv[1];assert action in ['capture','deploy','launch','collect'];globals()[action]()
