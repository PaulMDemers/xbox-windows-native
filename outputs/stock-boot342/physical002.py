"""Single stock-E physical Windows boot; restore normal E startup before collecting."""
import json,sys,time,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,get,put,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
action=sys.argv[1];assert action in ['launch','observe','collect']
out=K/'physical001';record=out/'trial.json';art=K/'artifacts/physical001';remote='/E/xwnstock342'
startup='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
normal=Path('E:/xwn337/package001'+startup).read_bytes()
test=b'@echo off\r\nC:\\xwnstock342\\runner.exe /physical\r\nexit\r\n'
read=lambda p:json.loads(p.read_text());pkg=read(K/'package.json');installed=read(K.parent/'stock-physical337/package001.json')
for path,digest in read(K/'frozen002.json').items():assert sha((W/path).read_bytes())==digest,path
lookup={p.lower():p for p in installed['files']}
def translate(p):return '/E/'+p[3:] if p.startswith('/F/') else p.replace('/XWNFBoot/','/XWNEBoot/')
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files'];fixed={lookup[translate(p).lower()]:installed['files'][lookup[translate(p).lower()]]['sha256'] for p in policy}
def check_fixed(f,test_enabled=False):
    result={p:sha(get(f,p))==(sha(test) if p.lower()==startup.lower() and test_enabled else h) for p,h in fixed.items()};assert all(result.values()),result;return result
def keep(p,b):
    dest=art/p.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(b);assert dest.read_bytes()==b;return dict(bytes=len(b),sha256=sha(b))
def launch():
    sys.path.insert(0,str(K.parent/'stock-stage340'))
    from completion002 import staged
    staged()
    allocation=read(K.parent/'stock-scan341/before/allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
    assert not out.exists();out.mkdir();art.mkdir(parents=True)
    r=dict(launch_requested=False,startup_enabled=False,physical_access=True,console_c_accessed=False,console_f_written=False,namespace=remote,created_utc=utc(),payloads=[],writes=[]);write_json(record,r)
    with connect() as f:
        check_fixed(f);assert get(f,startup)==normal
        for n in ['system','software','sam','security','default']:
            path='/E/winnt/system32/config/'+n;assert sha(get(f,path))==installed['files'][path]['sha256']
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E')}
        try:
            f.mkd(remote)
            for row in pkg['helpers']:
                b=(Path('E:/xwn342/payload')/row['name']).read_bytes();assert sha(b)==row['sha256'];p=remote+'/'+row['name']
                r['writes'].append(p);write_json(record,r);put(f,p,b);r['payloads'].append(dict(path=p,sha256=sha(b)))
            r['writes'].append(startup);write_json(record,r);put(f,startup,test);r['startup_enabled']=True;write_json(record,r);check_fixed(f,True)
        except BaseException as exc:
            # This one startup file is owned by this exact attempt; preserve the failure.
            r['prelaunch_error']=repr(exc);write_json(record,r)
            put(f,startup,normal);r['startup_enabled']=False;r['normal_startup_restored']=True;write_json(record,r);raise
        r.update(launch_requested=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNEBoot\\default.xbe');write_json(record,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=repr(exc)
        write_json(record,r)
    print('One physical stock E Windows boot accepted/recorded; never relaunch',flush=True)
def observe():
    assert read(record)['launch_requested'] and not (out/'return.json').exists()
    r=dict(dashboard_return=False,offline_observed=False,samples=[]);deadline=time.monotonic()+1200
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3):row['dashboard']=True
        except Exception as exc:row['error']=type(exc).__name__;r['offline_observed']=True
        r['samples'].append(row);r['dashboard_return']=row['dashboard'] and r['offline_observed'];write_json(out/'return.json',r)
        if r['dashboard_return']:break
        time.sleep(5)
    r.update(closed=True,closed_utc=utc());write_json(out/'return.json',r);print('Stock E dashboard return',r['dashboard_return'],flush=True)
def collect():
    trial=read(record);assert trial['launch_requested'];dest=out/'collection.json';assert not dest.exists()
    r=dict(completed=False,startup_restored=False,files={},inventories={});write_json(dest,r)
    with connect() as f:
        assert get(f,startup) in (normal,test);put(f,startup,normal);r['startup_restored']=True;trial['startup_enabled']=False;write_json(record,trial);write_json(dest,r)
        check_fixed(f)
        for name in ['attempt.log','wizard201.log','setup-before.log','setup-after.log','state207.log','audio207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]:
            p=remote+'/'+name;b=get(f,p,optional=True);r['files'][p]=None if b is None else keep(p,b)
        paths=list(fixed)+['/E/winnt/setupapi.log','/E/winnt/system32/xwn-video-trace.bin']+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]
        inf=names(f,'/E/winnt/inf');r['inventories']['/E/winnt/inf']=inf
        paths+=['/E/winnt/inf/'+n for n,v in inf.items() if not v['directory']]
        for p in dict.fromkeys(paths):
            b=get(f,p);r['files'][p]=keep(p,b)
            if '/config/' in p:assert get(f,p)==b
        for row in trial['payloads']:assert sha(get(f,row['path']))==row['sha256']
        r['protected_files_unchanged']=all(r['files'][p]['sha256']==h for p,h in fixed.items())
        # F rollback's protected payloads and five hives must remain unchanged.
        r['original_F_and_loader_unchanged']={p:dict(bytes=len(b),sha256=sha(b))==meta for p,meta in policy.items() for b in [get(f,p)]};assert all(r['original_F_and_loader_unchanged'].values())
        original=read(K.parent/'stock-physical337/capture001.json')['files']
        for n in ['system','software','sam','security','default']:
            p='/F/winnt/system32/config/'+n;assert sha(get(f,p))==original[p]['sha256']
        r.update(completed=True,completed_utc=utc(),dashboard_available=True);write_json(dest,r)
    print('Stock E evidence captured; normal startup restored first, F rollback verified',flush=True)
globals()[action]()
