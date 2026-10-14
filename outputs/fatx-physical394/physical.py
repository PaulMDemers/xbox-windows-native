"""One E-only FATX candidate validation with exact rollback and unchanged720p video/audio."""
import json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,put,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'))
from atomic_json import write_json
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
START='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
DLL='/E/winnt/system32/xwnown.dll'
FATX='/E/winnt/system32/drivers/xwnfatx.sys'
CANDIDATE='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'
HIVES=['system','software','sam','security','default']
NS='/E/xwndemo394candidate001'
LOGS=['cmd/'+n for n in ['file-trace.log','files.log','file-complete.txt','saved.bmp','reopened.bmp','note.txt','note-reopened.txt']]+['file-api.log','file-trace.log','files.log','file-complete.txt','saved.bmp','reopened.bmp','note.txt','note-reopened.txt','attempt.log','wizard201.log','setup-before.log','setup-after.log','state207.log','audio207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
fixed={p:v['sha256'] for p,v in read(K.parent/'demo-physical378/physical001/before.json')['files'].items() if p not in [START,'/E/documents and settings/win2k/ntuser.dat'] and '/config/' not in p}
fixed['/E/Applications/XWNEBoot/default.xbe']=read(W/'tools/e-display-policy.json')['profiles']['720p']['sha256']
fixed['/E/winnt/system32/cmd.exe']='4b04da85216ddbd98fa194d71f3c3acf311ac69fbe93444d9bc4c5464177762e'
fixed[START]=read(K.parent/'demo-settings376/package001.json')['startup']['sha256']
def read_path(p):
    assert p.startswith(('/E/','/F/')) and '\\' not in p and '..' not in p.split('/') and '//' not in p
    return p
def fetch(f,p,optional=False):return get(f,read_path(p),optional)
def store(f,p,b,case):
    assert case=='candidate001' and (p in [START,FATX] or p in [NS+'/'+v['name'] for v in read(K/'package.json')['helpers']])
    if p==FATX:assert sha(b) in [fixed[FATX],CANDIDATE]
    if p==START:assert sha(b)==fixed[START] or b==(K/'startup.cmd').read_bytes()
    ticket();put(f,read_path(p),b)
def keep(root,p,b):
    q=root/read_path(p).lstrip('/');q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();q.write_bytes(b);assert q.read_bytes()==b
    return dict(bytes=len(b),sha256=sha(b))
def restore_baseline(f,normal,original,case,r,publish):
    # Normal startup always restored before touching the storage rollback.
    store(f,START,normal,case);r['startup_enabled']=False;r['startup_restored']=True;publish()
    store(f,FATX,original,case);r['driver_restored']=True;publish()

def pins():
    ticket()
    for p,h in read(K/'frozen.json').items():assert sha((W/p).read_bytes())==h,p
def capture(case):
    pins();out=K/case;assert not out.exists();out.mkdir()
    root=K/'artifacts'/(case+'-before');root.mkdir(parents=True)
    r=dict(completed=False,files={},console_C_accessed=False,physical_writes=False,started_utc=utc());write_json(out/'before.json',r)
    with connect() as f:
        paths=list(fixed)+list(policy)+['/F/winnt/system32/config/'+n for n in HIVES]+['/E/winnt/system32/config/'+n for n in HIVES+['sysevent.evt','appevent.evt']]+['/E/winnt/setupapi.log','/E/winnt/system32/xwn-video-trace.bin']
        for p in dict.fromkeys(paths):
            b=fetch(f,p)
            if p in fixed:assert sha(b)==fixed[p],p
            if p in policy:assert sha(b)==policy[p]['sha256'],p
            if '/config/' in p:assert fetch(f,p)==b
            r['files'][p]=keep(root,p,b)
        r.update(completed=True,completed_utc=utc());write_json(out/'before.json',r)
    print('Baseline captured',flush=True)
def launch(case):
    pins();out=K/case;dest=out/'trial.json';assert not dest.exists()
    before=read(out/'before.json');assert before['completed']
    scan=read(out/'before-allocation.json');assert scan['allocation_consistent'] and not scan['errors'] and not scan['orphan_cluster_count']
    normal=(K/'artifacts'/(case+'-before')/START.lstrip('/')).read_bytes()
    original=(K/'artifacts'/(case+'-before')/FATX.lstrip('/')).read_bytes()
    candidate=Path(read(K/'package.json')['candidate']['source']).read_bytes();assert sha(candidate)==CANDIDATE
    assert sha(original)==fixed[FATX]
    test=(K/'startup.cmd').read_bytes();pkg=read(K/'package.json')
    r=dict(launch_requested=False,startup_enabled=False,driver_restored=True,namespace=NS,created_utc=utc(),payloads=[],writes=[],console_C_accessed=False,drivers_changed=True,storage_driver_only=True,original_fatx_sha256=fixed[FATX],candidate_fatx_sha256=CANDIDATE,original_driver_sha256=fixed[DLL],test_driver_sha256=fixed[DLL]);write_json(dest,r)
    with connect() as f:
        for p,v in before['files'].items():assert sha(fetch(f,p))==v['sha256'],p
        assert NS.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E')}
        try:
            f.mkd(NS);f.mkd(NS+'/cmd')
            for row in pkg['helpers']:
                b=Path(row['source']).read_bytes();assert sha(b)==row['sha256'];p=NS+'/'+row['name']
                r['writes'].append(p);write_json(dest,r);store(f,p,b,case);r['payloads'].append(dict(path=p,sha256=sha(b)))
            r['driver_restored']=False;r['writes'].append(FATX);write_json(dest,r);store(f,FATX,candidate,case);r['candidate_staged']=True;write_json(dest,r)
            r['writes'].append(START);write_json(dest,r);store(f,START,test,case);r['startup_enabled']=True;write_json(dest,r)
        except BaseException as e:
            r['prelaunch_error']=repr(e);restore_baseline(f,normal,original,case,r,lambda:write_json(dest,r));raise
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe');write_json(dest,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as e:r['reply_uncertain']=repr(e)
        write_json(dest,r)
    print('Single validation launch recorded',flush=True)
def observe(case):
    out=K/case;assert read(out/'trial.json')['launch_requested'] and not (out/'return.json').exists()
    r=dict(dashboard_return=False,offline_observed=False,samples=[]);deadline=time.monotonic()+1200
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3):row['dashboard']=True
        except Exception as e:row['error']=type(e).__name__;r['offline_observed']=True
        r['samples'].append(row);r['dashboard_return']=row['dashboard'] and r['offline_observed'];write_json(out/'return.json',r)
        if r['dashboard_return']:break
        time.sleep(5)
    r.update(closed=True,closed_utc=utc());write_json(out/'return.json',r);print('Dashboard return',r['dashboard_return'],flush=True)
def collect(case):
    pins();out=K/case;trial=read(out/'trial.json');assert trial['launch_requested'];dest=out/'collection.json';assert not dest.exists()
    before=read(out/'before.json');root=K/'artifacts'/(case+'-before');art=K/'artifacts'/case;assert not art.exists();art.mkdir(parents=True)
    normal=(root/START.lstrip('/')).read_bytes();original=(root/FATX.lstrip('/')).read_bytes();assert sha(original)==fixed[FATX]
    r=dict(completed=False,startup_restored=False,driver_restored=False,drivers_changed=True,storage_driver_only=True,files={},inventories={});write_json(dest,r)
    with connect() as f:
        assert fetch(f,START)==(K/'startup.cmd').read_bytes()
        store(f,START,normal,case);r['startup_restored']=True;trial['startup_enabled']=False;write_json(out/'trial.json',trial);write_json(dest,r)
        tested=fetch(f,FATX);(art/'tested-fatx.sys').write_bytes(tested)
        r['tested_fatx_sha256']=sha(tested);r['tested_fatx_verified']=sha(tested)==CANDIDATE;write_json(dest,r)
        store(f,FATX,original,case);r['driver_restored']=True;trial['driver_restored']=True;write_json(out/'trial.json',trial);write_json(dest,r)
        r['tested_driver_sha256']=sha(fetch(f,DLL));r['tested_driver_verified']=r['tested_driver_sha256']==fixed[DLL]
        for n in LOGS:
            p=NS+'/'+n;b=fetch(f,p,True);r['files'][p]=None if b is None else keep(art,p,b)
        r['intermediate_files_absent']={n:fetch(f,NS+'/'+n,True) is None for n in ['saved.tmp','note.tmp','cmd/saved.tmp','cmd/note.tmp']}
        paths=list(before['files']);inf=names(f,'/E/winnt/inf');r['inventories']['/E/winnt/inf']=inf
        paths+=['/E/winnt/inf/'+n for n,v in inf.items() if not v['directory']]
        for p in dict.fromkeys(paths):
            b=fetch(f,p);r['files'][p]=keep(art,p,b)
            if '/config/' in p:assert fetch(f,p)==b
        r['protected_files_unchanged']=all(r['files'][p]['sha256']==h for p,h in fixed.items())
        r['original_F_and_loader_unchanged']={p:r['files'][p]==v for p,v in before['files'].items() if p.startswith('/F/') or '/XWNFBoot/' in p}
        assert r['protected_files_unchanged'] and all(r['original_F_and_loader_unchanged'].values())
        for row in trial['payloads']:assert sha(fetch(f,row['path']))==row['sha256']
        r.update(completed=True,completed_utc=utc());write_json(dest,r)
    print('Normal startup restored first; captured all evidence',flush=True)
if __name__=='__main__':
    case,action=sys.argv[1:];assert case=='candidate001' and action in ['capture','launch','observe','collect'];globals()[action](case)
