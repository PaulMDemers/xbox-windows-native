"""Paired E-only driver diagnostic; original startup/driver restored each cycle."""
import json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,put,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'))
from atomic_json import write_json
read=lambda p:json.loads(p.read_text())
START='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
DLL='/E/winnt/system32/xwnown.dll'
HIVES=['system','software','sam','security','default']
LOGS=['attempt.log','wizard201.log','setup-before.log','setup-after.log','state207.log','audio207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]+[('sample%d/memory-%s.bin'%(i,t))+suffix for i in range(5) for t in ['before','after'] for suffix in ['', '.cold']]
LOGS += ['sample%d/bandwidth.bin'%i for i in range(5)]
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
installed=read(K.parent/'stock-physical337/package001.json')['files']
lookup={p.lower():p for p in installed}
translate=lambda p:'/E/'+p[3:] if p.startswith('/F/') else p.replace('/XWNFBoot/','/XWNEBoot/')
fixed={lookup[translate(p).lower()]:installed[lookup[translate(p).lower()]]['sha256'] for p in policy}
def read_path(p):
    assert p.startswith(('/E/','/F/')) and '\\' not in p and '..' not in p.split('/') and '//' not in p
    return p
def write_path(p,case):
    read_path(p);ns='/E/xwnbandwidth363'+case
    assert p in [START,DLL] or p.startswith(ns+'/') and p[len(ns)+1:] in [v['name'] for v in read(K/'package.json')['helpers']]
    return p
def fetch(f,p,optional=False):return get(f,read_path(p),optional=optional)
def store(f,p,b,case):ticket();put(f,write_path(p,case),b)
def keep(root,p,b):
    q=root/read_path(p).lstrip('/');q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();q.write_bytes(b);assert q.read_bytes()==b
    return dict(bytes=len(b),sha256=sha(b))
def pins():
    ticket()
    for n,h in read(K/'frozen.json').items():assert sha((W/n).read_bytes())==h,n
def capture(case):
    pins();out=K/case;dest=out/'before.json';assert not out.exists();out.mkdir()
    art=K/'artifacts'/(case+'-before');assert not art.exists();art.mkdir(parents=True)
    r=dict(completed=False,physical_writes=False,console_C_accessed=False,files={},started_utc=utc());write_json(dest,r)
    with connect() as f:
        for p,h in fixed.items():
            b=fetch(f,p);assert sha(b)==h,('Baseline mismatch',p);r['files'][p]=keep(art,p,b)
        assert fetch(f,START)==Path('E:/xwn337/package001'+START).read_bytes()
        for p in list(policy)+['/F/winnt/system32/config/'+n for n in HIVES]+['/E/winnt/system32/config/'+n for n in HIVES+['sysevent.evt','appevent.evt']]+['/E/winnt/setupapi.log','/E/winnt/system32/xwn-video-trace.bin']:
            if p in r['files']:continue
            b=fetch(f,p)
            if p in policy:assert dict(bytes=len(b),sha256=sha(b))==policy[p]
            if '/config/' in p:assert fetch(f,p)==b
            r['files'][p]=keep(art,p,b)
        r.update(completed=True,completed_utc=utc());write_json(dest,r)
    print('Fresh rollback captured; original E startup/driver and F baseline verified',case,flush=True)
def launch(case):
    assert read(K.parent/'bandwidth-runtime362/candidate001/audit.json')['scoped_combined_passed'] and read(K.parent/'bandwidth-runtime362/candidate001/closure.json')['closed']
    pins();out=K/case;dest=out/'trial.json';assert not dest.exists();before=read(out/'before.json');assert before['completed']
    scan=read(out/'before-allocation.json');assert scan['allocation_consistent'] and not scan['errors'] and not scan['orphan_cluster_count']
    root=K/'artifacts'/(case+'-before');normal=(root/START.lstrip('/')).read_bytes();original=(root/DLL.lstrip('/')).read_bytes()
    remote='/E/xwnbandwidth363'+case;test=('@echo off\r\nC:\\'+remote.rsplit('/',1)[1]+'\\runner.exe /physical\r\nexit\r\n').encode()
    driver=Path('E:/xwn361/build001/diagnostic001/xwnown.dll');data=driver.read_bytes();assert sha(data)==read(K.parent/'bandwidth361/build001.json')['cases']['diagnostic001']['sha256']
    r=dict(launch_requested=False,startup_enabled=False,driver_restored=False,namespace=remote,created_utc=utc(),payloads=[],writes=[],console_C_accessed=False,original_driver_sha256=sha(original),test_driver_sha256=sha(data));write_json(dest,r)
    with connect() as f:
        for p,v in before['files'].items():assert sha(fetch(f,p))==v['sha256'],('Changed since fresh capture',p)
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E')}
        try:
            f.mkd(remote)
            for row in read(K/'package.json')['helpers']:
                b=(Path('E:/xwn363/payload')/row['name']).read_bytes();assert sha(b)==row['sha256'];p=remote+'/'+row['name'];r['writes'].append(p);write_json(dest,r);store(f,p,b,case);r['payloads'].append(dict(path=p,sha256=sha(b)))
            r['writes'].append(DLL);write_json(dest,r);store(f,DLL,data,case)
            r['writes'].append(START);write_json(dest,r);store(f,START,test,case);r['startup_enabled']=True;write_json(dest,r)
        except BaseException as e:
            r['prelaunch_error']=repr(e);write_json(dest,r);store(f,START,normal,case);store(f,DLL,original,case);r.update(startup_enabled=False,driver_restored=True);write_json(dest,r);raise
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe');write_json(dest,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as e:r['reply_uncertain']=repr(e)
        write_json(dest,r)
    print('One physical diagnostic launch recorded; never retry',case,flush=True)
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
    normal=(root/START.lstrip('/')).read_bytes();original=(root/DLL.lstrip('/')).read_bytes()
    r=dict(completed=False,startup_restored=False,driver_restored=False,files={},inventories={});write_json(dest,r)
    with connect() as f:
        store(f,START,normal,case);r['startup_restored']=True;trial['startup_enabled']=False;write_json(out/'trial.json',trial);write_json(dest,r)
        current=fetch(f,DLL);q=art/'tested-driver.dll';q.write_bytes(current);r['tested_driver_verified']=sha(current)==trial['test_driver_sha256'];r['tested_driver_sha256']=sha(current)
        store(f,DLL,original,case);r['driver_restored']=True;trial['driver_restored']=True;write_json(out/'trial.json',trial);write_json(dest,r)
        for name in LOGS:
            p=trial['namespace']+'/'+name;b=fetch(f,p,True);r['files'][p]=None if b is None else keep(art,p,b)
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
    print('Normal startup and original driver restored; evidence captured',case,flush=True)
if __name__=='__main__':
    case,action=sys.argv[1:];assert case in ['candidate001'] and action in ['capture','launch','observe','collect'];globals()[action](case)
