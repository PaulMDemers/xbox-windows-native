"""New E-only allocation diagnostic. No original launcher/menu/Windows changes."""
import importlib.util,json,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn410')
spec=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from decode import decode
sys.path.insert(0,str(W/'outputs/demo-audio-level256'))
from common001 import put
read=m.read;sha=m.sha;utc=m.utc;save=m.write_json
REMOTE='/E/Applications/XWNBoot410a'
BUILD=P/'build002/default.xbe'

def verify():
    m.ticket();r=read(K/'build002.json');assert r['status']=='compiled'
    b=BUILD.read_bytes();assert sha(b)==r['sha256']
    review=read(K/'source-review001.json');assert review['reviewed'] and review['qualified_wrapper_sha256']==sha(b)
    tests=read(K/'decoder001.json');assert tests['passed'] and tests['actual_x86_host_cases']==21
    for name,h in tests['files'].items():assert sha(Path(name).read_bytes())==h,name
    for name,h in read(W/'outputs/media-physical407/source-pins.json').items():assert sha((W/name).read_bytes())==h,name
    return b

def stage():
    b=verify();out=K/'stage001.json';assert not out.exists()
    r=dict(completed=False,utc=utc(),remote=REMOTE,console_C_accessed=False,original_launcher_changed=False,
           windows_startup_changed=False,physical_writes=[],before={},source_pins={})
    for p in [K/'physical.py',K/'decode.py',K/'logger.S',K/'verify002.S',K/'source-review001.json',K/'build002.py',K/'build002.json',K/'decoder001.json',BUILD]:
        r['source_pins'][str(p)]=sha(p.read_bytes())
    with m.connect() as f:
        assert 'xwnboot410a' not in {n.lower() for n in m.names(f,'/E/Applications')}
        for path,h in m.installed().items():
            data=m.get(f,path);assert sha(data)==h,path;r['before'][path]=h
        for path in [m.START,'/E/winnt/system32/config/system','/E/winnt/system32/config/software',
                     '/E/winnt/system32/config/sysevent.evt','/E/winnt/system32/config/appevent.evt']:
            r['before'][path]=sha(m.get(f,path))
        save(out,r);r['physical_writes'].append(REMOTE);save(out,r);f.mkd(REMOTE)
        owner=json.dumps(dict(project='xbox-windows-native',purpose='pre-paging relocated copy observation',cookie='41000101',sha256=sha(b))).encode()
        for name,data in [('owner.json',owner),('default.xbe',b)]:
            path=REMOTE+'/'+name;r['physical_writes'].append(path);save(out,r);put(f,path,data)
            assert m.get(f,path)==data
        r.update(completed=True,completed_utc=utc(),xbe_sha256=sha(b),owner_sha256=sha(owner));save(out,r)
    print('Diagnostic staged/read back in new E folder; installed files unchanged',flush=True)

def launch():
    b=verify();r=read(K/'stage001.json');assert r['completed'];out=K/'launch001.json';assert not out.exists()
    for p,h in r['source_pins'].items():assert sha(Path(p).read_bytes())==h,p
    with m.connect() as f:
        for p,h in r['before'].items():assert sha(m.get(f,p))==h,p
        assert m.get(f,REMOTE+'/default.xbe')==b
        assert m.get(f,REMOTE+'/report.bin',optional=True) is None
        x=dict(utc=utc(),launch_requested=True,command=r'SITE EXEC E:\Applications\XWNBoot410a\default.xbe',
               windows_boot_requested=False,diagnostic_returns_to_dashboard=True,console_C_accessed=False)
        save(out,x);f.sock.settimeout(20)
        try:x['reply']=f.sendcmd(x['command'])
        except Exception as e:x['reply_uncertain']=type(e).__name__
        save(out,x)
    print('One diagnostic launch recorded; never retry this launch',flush=True)

def collect():
    verify();assert read(K/'launch001.json')['launch_requested']
    out=K/'collection001.json';assert not out.exists();before=read(K/'stage001.json')
    r=dict(completed=False,started_utc=utc(),console_C_accessed=False,physical_writes=False,observations=[])
    save(out,r);deadline=time.monotonic()+90;data=None
    while time.monotonic()<deadline:
        time.sleep(5)
        try:
            with m.connect(timeout=3) as f:
                data=m.get(f,REMOTE+'/report.bin',optional=True)
            r['observations'].append(dict(utc=utc(),dashboard=True,report_bytes=None if data is None else len(data)))
            save(out,r)
            if data is not None:break
        except (OSError,EOFError) as e:
            r['observations'].append(dict(utc=utc(),dashboard=False,error=type(e).__name__));save(out,r)
    if data is not None:
        private=P/'physical001';private.mkdir(exist_ok=False)
        (private/'report.bin').write_bytes(data);r['report_sha256']=sha(data)
        try:r['decoded']=decode(data)
        except ValueError as e:r['decode_error']=str(e)
    with m.connect() as f:
        r['protected']={p:sha(m.get(f,p))==h for p,h in before['before'].items()}
        r['diagnostic_xbe_exact']=sha(m.get(f,REMOTE+'/default.xbe'))==before['xbe_sha256']
        r['owner_exact']=sha(m.get(f,REMOTE+'/owner.json'))==before['owner_sha256']
    r.update(completed=True,completed_utc=utc(),protected_exact=all(r['protected'].values()),
             historical_failure_cause_established=False,full_allocation_audit=False)
    save(out,r);print(json.dumps({k:r.get(k) for k in ['completed','decoded','decode_error','protected_exact']}),flush=True)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','collect')
    globals()[sys.argv[1]]()
