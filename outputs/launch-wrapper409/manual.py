"""Stage a data-only paired probe for File Explorer; NEVER send a launch command."""
import importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
K=Path(__file__).resolve().parent;W=K.parents[1]
spec=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sys.path.insert(0,str(W/'outputs/demo-audio-level256'));from common001 import put
from decode002 import decode
read=m.read;sha=m.sha;save=m.write_json
REMOTE='/E/Applications/XWNBoot409b';P=Path('E:/xwn409')
def verify():
    m.ticket();v=read(K/'variant004.json');b=(P/'manual-build004/default.xbe').read_bytes()
    assert sha(b)==v['sha256'] and v['instructions_unchanged']
    tests=read(K/'decoder004.json');assert tests['passed']
    for p,h in tests['files'].items():assert sha(Path(p).read_bytes())==h,p
    assert read(K/'collection001.json')['protected_exact']
    return b
def stage():
    b=verify();out=K/'manual-stage002.json';assert not out.exists()
    r=dict(completed=False,utc=m.utc(),remote=REMOTE,console_C_accessed=False,launch_requested=False,
           before=read(K/'stage001.json')['before'],writes=[],source_pins={})
    for p in [K/'manual.py',K/'decode002.py',K/'variant004.json',K/'decoder004.json']:
        r['source_pins'][str(p)]=sha(p.read_bytes())
    with m.connect() as f:
        assert 'xwnboot409b' not in {n.lower() for n in m.names(f,'/E/Applications')}
        for p,h in r['before'].items():assert sha(m.get(f,p))==h,p
        save(out,r);r['writes'].append(REMOTE);save(out,r);f.mkd(REMOTE)
        owner=json.dumps(dict(project='xbox-windows-native',purpose='manual File Explorer paired allocation probe',cookie='40900102',sha256=sha(b))).encode()
        for name,data in [('owner.json',owner),('default.xbe',b)]:
            p=REMOTE+'/'+name;r['writes'].append(p);save(out,r);put(f,p,data);assert m.get(f,p)==data
        r.update(completed=True,completed_utc=m.utc(),xbe_sha256=sha(b),owner_sha256=sha(owner));save(out,r)
    print('Paired probe staged; no launch sent',flush=True)
def collect():
    verify();r=read(K/'manual-stage002.json');assert r['completed'];out=K/'manual-collection002.json';assert not out.exists()
    assert (K/'manual-user-return002.json').exists(),'User must report direct launch and dashboard return first'
    for p,h in r['source_pins'].items():assert sha(Path(p).read_bytes())==h,p
    x=dict(completed=False,utc=m.utc(),console_C_accessed=False,physical_writes=False)
    with m.connect() as f:
        data=m.get(f,REMOTE+'/report.bin',optional=True)
        if data is not None:
            folder=P/'physical002';folder.mkdir(exist_ok=False);(folder/'report.bin').write_bytes(data)
            x['report_sha256']=sha(data)
            try:x['decoded']=decode(data,cookie=0x40900102)
            except ValueError as e:x['decode_error']=str(e)
        else:x['report_missing']=True
        x['protected']={p:sha(m.get(f,p))==h for p,h in r['before'].items()}
        x['diagnostic_xbe_exact']=sha(m.get(f,REMOTE+'/default.xbe'))==r['xbe_sha256']
        x['owner_exact']=sha(m.get(f,REMOTE+'/owner.json'))==r['owner_sha256']
    x.update(completed=True,completed_utc=m.utc(),protected_exact=all(x['protected'].values()),historical_failure_cause_established=False)
    save(out,x);print(json.dumps({k:x.get(k) for k in ['completed','decoded','decode_error','report_missing','protected_exact']}))
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('stage','collect')
    globals()[sys.argv[1]]()
