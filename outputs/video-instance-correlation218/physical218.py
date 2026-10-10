"""Single query-only stock probe; new F app, small E reports, no Windows changes."""
import sys,os,json,hashlib,datetime,importlib.util,struct,time,ftplib,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
record=k/'physical001.json';art=k/'artifacts/physical-run001'
plan=json.loads((k/'physical-plan.json').read_text())
spec=importlib.util.spec_from_file_location('ftp218',ws/'outputs/fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(r):
    tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(record)
def keep(name,data):
    p=art/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data,'Preserved data changed: '+name
    else:p.write_bytes(data)
    return dict(path=p.relative_to(ws).as_posix(),bytes=len(data),sha256=sha(data))
def names(f,path):
    f.cwd(path);pwd=f.pwd();assert pwd.replace('\\','/').rstrip('/').lower()==path.rstrip('/').lower(),(path,pwd)
    lines=[];f.retrlines('LIST',lines.append);parts=[v.split(None,8) for v in lines]
    assert all(len(v)==9 for v in parts),'Unparsed LIST'
    return {v[8].lower() for v in parts}
def fixed():
    capture=json.loads((ws/'outputs/video-upload-runtime211/capture.json').read_text())
    assert capture['passed']
    mutable=('/config/system','/config/software','/config/default','/config/sam','/config/security',
             '/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')
    return [v for v in capture['files'] if not v['path'].endswith(mutable)]
def pins():
    for name,digest in json.loads((k/'physical-inputs.json').read_text()).items():
        assert sha(Path(name).read_bytes())==digest,'Changed physical input: '+name
    assert sha((k/'artifacts/physical001/default.xbe').read_bytes())==plan['payload_sha256']
    assert json.loads((k/'review218.json').read_text())['build005_calibrated_on_emulator']
    assert json.loads((k/'e-audit007.json').read_text())['passed']
def launch():
    pins();assert not record.exists() and not art.exists(),'Never repeat physical001'
    r=dict(scope=__doc__,physical_result=True,created_utc=utc(),launch_requested=False,
           collected=False,physical_qualified=False,gpu_alias_proven=False,nt5_ownership_granted=False,
           before={},after={},prepared_only=False,keyboard_user_reported_always_unplugged=True)
    with m.connect() as f:
        m.owner(f);r['banner']=f.getwelcome();e=names(f,'/E');assert 'xwninst218d' not in e,'Preserve old E reports'
        root=names(f,'/F');parent_exists='applications' in root
        if parent_exists:assert 'xwninstance218' not in names(f,'/F/Applications'),'Preserve old app'
        paths=[v['path'] for v in fixed()]+['/F/winnt/system32/config/'+n for n in ['system','software','default','sam','security']]
        for i,path in enumerate(paths):
            data=m.get(f,path);v=keep('before/%03d.bin'%i,data);r['before'][path]=v
            expected=next((v['sha256'] for v in fixed() if v['path']==path),None)
            if expected:assert sha(data)==expected,'Installed baseline drift: '+path
        print('Owned dashboard and installed baseline verified; unique paths absent',flush=True)
        r['preflight_passed']=True;save(r)
        if not parent_exists:f.mkd('/F/Applications');r['created_applications_parent']=True;save(r)
        f.mkd(plan['remote_app_folder']);r['created_app_folder']=True;save(r)
        payload=(k/'artifacts/physical001/default.xbe').read_bytes()
        m.put(f,plan['remote_app_folder']+'/default.xbe',payload)
        r['uploaded_sha256']=sha(payload);r['readback_verified']=True;save(r)
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC F:\Applications\XWNInstance218\default.xbe');save(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save(r);print('Single stock instance218 launch requested; never relaunch',flush=True)
def observe():
    r=json.loads(record.read_text());assert r['launch_requested'] and not r['collected']
    until=time.monotonic()+120;attempts=[]
    while time.monotonic()<until:
        try:
            with m.connect() as f:
                m.owner(f);present='xwninst218d' in names(f,'/E')
                attempts.append(dict(utc=utc(),dashboard_ftp=True,report_root_present=present))
                if present:
                    r['observed_return_utc']=utc();r['return_observations']=attempts;save(r)
                    print('Dashboard returned and fresh report directory exists',flush=True);return
        except Exception as exc:attempts.append(dict(utc=utc(),error=repr(exc)))
        time.sleep(5)
    r['return_observations']=attempts;r['observation_bound_utc']=utc();save(r)
    print('Return/report not established within bound; no relaunch',flush=True)
def collect():
    pins();r=json.loads(record.read_text());assert r['launch_requested'] and not r['collected']
    with m.connect() as f:
        m.owner(f);r['dashboard_ftp_at_collection']=True
        for i,(path,before) in enumerate(r['before'].items()):
            data=m.get(f,path);v=keep('after/%03d.bin'%i,data);v['unchanged']=v['sha256']==before['sha256'];r['after'][path]=v;save(r)
        r['baseline_unchanged']=all(v['unchanged'] for v in r['after'].values())
        r['reports']={}
        for name in plan['expected_reports']:
            data=m.get(f,plan['ftp_log_root']+'/'+name,optional=True)
            r['reports'][name]=None if data is None else keep('reports/'+name,data);save(r)
        r['app_payload_unchanged']=sha(m.get(f,plan['remote_app_folder']+'/default.xbe'))==plan['payload_sha256']
    r['collected']=True;r['collected_utc']=utc()
    r['probe_completed']=all(r['reports'].values())
    if r['probe_completed']:
        text=(art/'reports/report.txt').read_text();r['report']=text
        r['probe_completed']='COMPLETE 1 LOG_OK 1 STOCK_RESTART_REQUEST' in text
        assert all(r['reports'][n]['bytes']==20480 for n in ['cpu0.bin','cpu1.bin','gpu0.bin','gpu1.bin'])
        c0,c1,g0,g1=[struct.unpack('<5120I',(art/'reports'/n).read_bytes()) for n in ['cpu0.bin','cpu1.bin','gpu0.bin','gpu1.bin']]
        rev=tuple(x for b in reversed([c0[i:i+4] for i in range(0,5120,4)]) for x in b)
        obs=dict(cpu_stable=c0==c1,gpu_stable=g0==g1,nonzero_words=sum(v!=0 for v in c0),
                 distinct_blocks=len(set(c0[i:i+4] for i in range(0,5120,4))),
                 forward_mismatches=sum(x!=y for x,y in zip(c0,g0)),reverse16_mismatches=sum(x!=y for x,y in zip(rev,g0)))
        r['independent_comparison']=obs
        match=re.search(r'RESULT cpu_stable=(\d+) gpu_stable=(\d+) nonzero_words=(\d+) distinct_blocks=(\d+) forward_mismatches=(\d+) reverse16_mismatches=(\d+) correlation=(\d+)',text)
        r['guest_comparison_matches']=bool(match) and list(map(int,match.groups()[:6]))==list(map(int,obs.values()))
        r['informative_correlation']=obs['cpu_stable'] and obs['gpu_stable'] and obs['nonzero_words']>=256 and obs['distinct_blocks']>=64 and (obs['forward_mismatches']==0 or obs['reverse16_mismatches']==0)
        r['observed_kernel']=re.search(r'KERNEL (\d+) (\d+) (\d+) (\d+)',text).groups()
    r['probe_collection_passed']=r['probe_completed'] and r['baseline_unchanged'] and r['app_payload_unchanged'] and r.get('guest_comparison_matches',False)
    save(r);print(json.dumps({n:r.get(n) for n in ['probe_collection_passed','baseline_unchanged','probe_completed','independent_comparison','informative_correlation']}),flush=True)
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ['launch','observe','collect']
    globals()[sys.argv[1]]()
