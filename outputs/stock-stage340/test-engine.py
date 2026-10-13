import json
from pathlib import Path
from engine import *
class Remote:
    def __init__(self):self.data={};self.dirs=set();self.writes=[];self.fail='';self.corrupt=False
    def exists(self,p):return p in self.data or p in self.dirs
    def mkdir(self,p):self.dirs.add(p)
    def create(self,p,b):
        self.writes.append(p)
        if p==self.fail:raise OSError('Modeled uncertain upload')
        self.data[p]=b
    def read(self,p):return self.data[p]+(b'!' if self.corrupt else b'')
data={'/E/winnt/a':b'abc',LAUNCHER:b'loader'};files={p:dict(bytes=len(b),sha256=digest(b)) for p,b in data.items()};n=0
r=Remote();events=[];result=stage(files,[],data.__getitem__,r,lambda *v:events.append(v));assert result['complete'] and r.writes==['/E/winnt/a',LAUNCHER];n+=1
for bad in ['/C/winnt/a','/F/winnt/a','/E/Applications/Other/a','/E/winnt/../a','/E/winnt//a','/E/winnt/a:stream','/E/winnt/a\\b']:
    assert not allowed(bad);n+=1
for mode in ['existing','changed_source','upload_error','readback_error','foreign_file']:
    r=Remote();events=[];reader=data.__getitem__
    if mode=='existing':r.dirs.add('/E/winnt')
    if mode=='changed_source':reader=lambda p:b'wrong'
    if mode=='upload_error':r.fail='/E/winnt/a'
    if mode=='readback_error':r.corrupt=True
    if mode=='foreign_file':r.data['/E/winnt/a']=b'foreign'
    try:stage(files,[],reader,r,lambda *v:events.append(v))
    except (AssertionError,OSError):pass
    else:raise AssertionError(mode)
    assert LAUNCHER not in r.writes
    if mode in ['existing','changed_source']:assert not r.writes and not events
    n+=1
dest=Path(__file__).with_name('host001.json');assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,cases=n,interfaces='Exact transaction engine; modeled remote filesystem/transfer, no physical writes'),indent=2)+'\n');print('Passed',n,'create-only transaction cases')
