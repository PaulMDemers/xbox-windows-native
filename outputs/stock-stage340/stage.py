"""One physical create-only E stage; normal startup remains and no boot command exists."""
import json,os,sys,time
from pathlib import Path
from engine import stage,digest,ROOTS
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'physical001.json';P=Path('E:/xwn340/stage001');payload=Path('E:/xwn337/package001')
assert not dest.exists() and not P.exists()
read=lambda p:json.loads(p.read_text())
assert read(K/'host001.json')['passed']
repeat=read(K.parent/'stock-repeat339/emu001/repeat-proof.json');assert repeat['passed']
package=read(K.parent/'stock-physical337/package001.json');assert package['prepared'] and package['startup_normal'] and len(package['changes'])==7
capture=read(K.parent/'stock-physical337/capture001.json');policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,get,put,names,utc
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
P.mkdir(parents=True);r=dict(complete=False,started_utc=utc(),console_c_accessed=False,console_c_written=False,console_f_written=False,normal_startup=True,launch_sent=False,package_sha256=digest((K.parent/'stock-physical337/package001.json').read_bytes()),verified_files=0,private=str(P))
write_json(dest,r);deadline=time.monotonic()+2400
journal=(P/'journal.jsonl').open('xb',buffering=0)
def record(kind,path,meta):
    assert time.monotonic()<deadline,'Total stage deadline'
    journal.write((json.dumps(dict(utc=utc(),kind=kind,path=path,meta=meta))+'\n').encode());os.fsync(journal.fileno())
    if kind=='write_verified':
        r['verified_files']+=1
        if r['verified_files']%250==0:write_json(dest,r);print('Verified E files',r['verified_files'],flush=True)
class Remote:
    def __init__(self,f):self.f=f;self.cache={}
    def exists(self,p):
        folder,name=p.rsplit('/',1)
        self.cache[folder]={n.lower() for n in names(self.f,folder)}
        return name.lower() in self.cache[folder]
    def mkdir(self,p):
        self.f.mkd(p);folder,name=p.rsplit('/',1);self.cache[folder].add(name.lower());self.cache[p]=set()
    def create(self,p,b):put(self.f,p,b);folder,name=p.rsplit('/',1);self.cache[folder].add(name.lower())
    def read(self,p):return get(self.f,p)
try:
    with connect(timeout=15) as f:
        r['baseline_preflight']={p:dict(bytes=len(b),sha256=digest(b))==meta for p,meta in policy.items() for b in [get(f,p)]}
        assert all(r['baseline_preflight'].values())
        for n in ['system','software','sam','security','default']:
            path='/F/winnt/system32/config/'+n
            assert digest(get(f,path))==capture['files'][path]['sha256'],'Current hive changed since capture'
        capacity=read(K.parent/'stock-drive333/physical001/trial.json')
        # Exact native capacity record is inspected separately; conservative 1GiB+pagefile bound.
        allocated=sum(((v['bytes']+16383)//16384)*16384 for v in package['files'].values())+(len(package['directories'])+20)*16384
        assert allocated+256*1024**2<2944663552
        r['projected_allocated_bytes']=allocated
        r.update(stage(package['files'],package['directories'],lambda p:(payload/p.lstrip('/')).read_bytes(),Remote(f),record))
        r['baseline_after']={p:dict(bytes=len(b),sha256=digest(b))==meta for p,meta in policy.items() for b in [get(f,p)]};assert all(r['baseline_after'].values())
        for n in ['system','software','sam','security','default']:
            path='/F/winnt/system32/config/'+n
            assert digest(get(f,path))==capture['files'][path]['sha256'],'Original F hive changed during E stage'
        r['finished_utc']=utc()
except BaseException as exc:r.update(complete=False,error=repr(exc),quarantined=True);raise
finally:
    journal.close();r['journal_sha256']=digest((P/'journal.jsonl').read_bytes());write_json(dest,r)
print('Physical E staged and verified; normal startup, no Windows launch',r['verified_files'],flush=True)
