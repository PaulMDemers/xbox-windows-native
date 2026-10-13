"""Modeled transport failures around the actual continuation transaction."""
import copy, json
from pathlib import Path
from engine import ROOTS, LAUNCHER, digest
from resume_engine import resume

K = Path(__file__).resolve().parent
dest = K/'resume-host001.json'
assert not dest.exists()
data = {ROOTS[0]+'/a': b'first', ROOTS[0]+'/b': b'second', LAUNCHER: b'loader'}
files = {p: dict(bytes=len(b), sha256=digest(b)) for p,b in data.items()}
dirs = set(ROOTS)
rows = []
for p in sorted(dirs):
    rows += [dict(kind='mkdir_intent',path=p,meta=None), dict(kind='mkdir_done',path=p,meta=None)]
p = ROOTS[0]+'/a'
rows += [dict(kind='write_intent',path=p,meta=files[p]),dict(kind='write_verified',path=p,meta=files[p])]

class Remote:
    def __init__(self): self.files={p:data[p]};self.dirs=set(dirs);self.writes=[];self.corrupt=False;self.race=False
    def inventory(self,roots): return self.dirs, set(self.files)
    def exists(self,path): return self.race or path in self.files
    def read(self,path): return self.files[path]
    def create(self,path,b):
        assert path not in self.files
        self.writes.append(path);self.files[path]=b+b'!' if self.corrupt else b

cases=[]
def run(name, mutate=lambda r,j:None, passed=False):
    r=Remote();j=copy.deepcopy(rows);mutate(r,j);events=[]
    try:
        result=resume(files,dirs,j,data.__getitem__,r,lambda *x:events.append(x))
        assert passed
        assert result['complete'] and r.writes[-1]==LAUNCHER and r.files==data
    except AssertionError:
        if passed: raise
        assert LAUNCHER not in r.writes
    cases.append(dict(name=name,passed=True,writes=len(r.writes)))
run('exact prior file',passed=True)
run('missing verified',lambda r,j:r.files.clear())
run('changed existing',lambda r,j:r.files.__setitem__(p,b'changed'))
run('unknown owned file',lambda r,j:r.files.__setitem__(ROOTS[0]+'/foreign',b'x'))
run('missing directory',lambda r,j:r.dirs.remove(ROOTS[2]))
run('premature launcher',lambda r,j:r.files.__setitem__(LAUNCHER,data[LAUNCHER]))
run('upload corruption',lambda r,j:setattr(r,'corrupt',True))
run('create race',lambda r,j:setattr(r,'race',True))
run('changed journal hash',lambda r,j:j[-1]['meta'].__setitem__('sha256','0'*64))
run('duplicate verification',lambda r,j:j.append(copy.deepcopy(j[-1])))
def pending(r,j,present):
    q=ROOTS[0]+'/b';j.append(dict(kind='write_intent',path=q,meta=copy.deepcopy(files[q])))
    if present:r.files[q]=data[q]
run('intent complete on disk but unacknowledged',lambda r,j:pending(r,j,True),True)
run('intent absent on disk',lambda r,j:pending(r,j,False),True)
dest.write_text(json.dumps(dict(passed=True,cases=cases,actual_engine=True,transport='modeled',source_sha256=digest((K/'resume_engine.py').read_bytes())),indent=2)+'\n')
print(len(cases),'continuation cases passed')
