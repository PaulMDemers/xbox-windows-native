"""One bounded continuation of the closed340 FTP command failure. No boot or delete API."""
import json, os, sys, time
from pathlib import Path
from engine import ROOTS, digest, allowed
from resume_engine import resume

K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'resume002.json';private=Path('E:/xwn340/resume002');payload=Path('E:/xwn337/package001')
read=lambda p:json.loads(p.read_text())
original=read(K/'physical001.json')
assert not original['complete'] and original.get('quarantined')
assert original['error']=="error_perm('502 Command not implemented.')"
inspection=read(K/'failure-inspection001.json')
assert inspection['actual_bytes'] is None and inspection['launcher_absent']
assert not original['launch_sent'] and original['normal_startup']
assert not out.exists() and not private.exists()
host=read(K/'resume-host001.json')
assert host['passed'] and host['source_sha256']==digest((K/'resume_engine.py').read_bytes())
source_journal=Path('E:/xwn340/stage001/journal.jsonl').read_bytes()
assert digest(source_journal)==original['journal_sha256']
rows=[json.loads(line) for line in source_journal.splitlines()]
package_path=K.parent/'stock-physical337/package001.json';package=read(package_path)
assert digest(package_path.read_bytes())==original['package_sha256']
files=package['files'];directories=set(package['directories'])|set(ROOTS)
for p in files:
    parent=p.rsplit('/',1)[0]
    while parent not in ('/E','/E/Applications'):
        assert allowed(parent);directories.add(parent);parent=parent.rsplit('/',1)[0]
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,put,names,utc
sys.path.insert(0,str(K.parent/'surface-bridge260'))
from atomic_json import write_json
policy=read(W/'tools/hd-overlay-0.2.0.json')['baseline_files']
capture=read(K.parent/'stock-physical337/capture001.json')['files']
private.mkdir(parents=True);(private/'original-journal.jsonl').write_bytes(source_journal)
r=dict(complete=False,started_utc=utc(),console_c_accessed=False,console_f_written=False,
       normal_startup=True,launch_sent=False,original_receipt_sha256=digest((K/'physical001.json').read_bytes()),
       original_journal_sha256=digest(source_journal),package_sha256=digest(package_path.read_bytes()),
       existing_verified=0,new_verified=0,private=str(private),source_pins={})
for p in [K/'engine.py',K/'resume_engine.py',K/'resume002.py',K/'resume-host001.json',K.parent/'demo-audio-level256/common001.py',K.parent/'surface-bridge260/atomic_json.py']:
    r['source_pins'][str(p.relative_to(W))]=digest(p.read_bytes())
write_json(out,r);deadline=time.monotonic()+7200
journal=(private/'journal.jsonl').open('xb',buffering=0)
def record(kind,path,meta):
    assert time.monotonic()<deadline,'Continuation deadline'
    journal.write((json.dumps(dict(utc=utc(),kind=kind,path=path,meta=meta))+'\n').encode());os.fsync(journal.fileno())
    if kind in ('existing_verified','write_verified'):
        key='existing_verified' if kind=='existing_verified' else 'new_verified';r[key]+=1
        if (r['existing_verified']+r['new_verified'])%250==0:
            write_json(out,r);print('E continuation verified',r['existing_verified'],r['new_verified'],flush=True)

class Remote:
    def __init__(self,f):self.f=f
    def inventory(self,roots):
        canonical={p.lower():p for p in set(files)|directories}
        actual_dirs=set();actual_files=set();queue=list(roots)
        while queue:
            folder=queue.pop();assert time.monotonic()<deadline
            actual_dirs.add(folder)
            for name,meta in names(self.f,folder).items():
                raw=folder+'/'+name;assert raw.lower() in canonical,'Unknown owned path: '+raw
                p=canonical[raw.lower()]
                if meta['directory']:
                    assert p in directories and p not in actual_dirs;queue.append(p)
                else:
                    assert p in files and p not in actual_files;actual_files.add(p)
        return actual_dirs,actual_files
    def exists(self,p):
        folder,name=p.rsplit('/',1);return name.lower() in {n.lower() for n in names(self.f,folder)}
    def create(self,p,b):put(self.f,p,b)
    def read(self,p):return get(self.f,p)

def baseline(f):
    checks={p:dict(bytes=len(b),sha256=digest(b))==meta for p,meta in policy.items() for b in [get(f,p)]}
    assert all(checks.values())
    for n in ['system','software','sam','security','default']:
        p='/F/winnt/system32/config/'+n;assert digest(get(f,p))==capture[p]['sha256']
    return checks
try:
    with connect() as f:
        r['baseline_before']=baseline(f);write_json(out,r)
        r.update(resume(files,directories,rows,lambda p:(payload/p.lstrip('/')).read_bytes(),Remote(f),record))
        r['baseline_after']=baseline(f);r['finished_utc']=utc()
except BaseException as exc:
    r.update(complete=False,error=repr(exc),quarantined=True);raise
finally:
    journal.close();r['journal_sha256']=digest((private/'journal.jsonl').read_bytes());write_json(out,r)
print('E staging continuation complete; no Windows launch',r['files'],flush=True)
