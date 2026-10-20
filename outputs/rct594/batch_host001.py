"""MIT. Exercise actual batch verifier transport/retry/identity/deadline boundaries."""
import ftplib,hashlib,json,tempfile,types
from pathlib import Path
import batch_read001 as b
K=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest();cases=[]
for mode in ['pass','502-once','timeout-twice','550-refuse','changed-read','wrong-hash','deadline']:
    sessions=[];attempts=0;calls=0;ticks=0
    class Session:
        def __init__(self):self.closed=False;self.paths=[]
        def close(self):self.closed=True
    def connect(**kw):
        assert kw=={'timeout':15};f=Session();sessions.append(f);return f
    def get(f,path):
        global attempts,calls
        assert not f.closed;f.paths.append(path);calls+=1
        if path=='p1':
            attempts+=1
            if mode=='502-once' and attempts==1:raise ftplib.error_perm('502 Command not implemented')
            if mode=='timeout-twice':raise TimeoutError()
            if mode=='550-refuse':raise ftplib.error_perm('550 refused')
            if mode=='changed-read' and attempts==2:return b'changed'
            if mode=='wrong-hash':return b'wrong'
        return path.encode()
    def clock():
        global ticks
        ticks+=1
        return ticks*700 if mode=='deadline' else 0
    b.time=types.SimpleNamespace(monotonic=clock)
    m=types.SimpleNamespace(connect=connect,get=get,sha=sha,write_json=lambda p,r:None)
    expected={f'p{i}':dict(bytes=len(f'p{i}'),sha256=sha(f'p{i}'.encode())) for i in range(35)}
    record={}
    try:b.verify_batch(m,expected,record,None,'verified');passed=True
    except (AssertionError,TimeoutError,ftplib.error_perm):passed=False
    assert passed==(mode in ['pass','502-once']),mode
    assert all(s.closed for s in sessions)
    assert all(len(set(s.paths))<=16 for s in sessions)
    if mode=='pass':assert len(sessions)==3 and calls==70
    if mode=='502-once':assert len(record['read_failures'])==1 and attempts==3
    if mode=='timeout-twice':assert attempts==2 and len(record['read_failures'])==2
    if mode=='550-refuse':assert attempts==1 and len(sessions)==1
    if mode=='changed-read':assert attempts==2 and len(sessions)==1
    if mode=='wrong-hash':assert attempts==2 and len(sessions)==1
    if mode=='deadline':assert not sessions
    cases.append(dict(case=mode,expected_result=True,connections=len(sessions),read_calls=calls))
out=K/'batch-host001.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=sha((K/'batch_read001.py').read_bytes()),scope='Actual batch verifier under fake read-only transport; no console access.'),indent=2)+'\n');print('Passed',len(cases),'batch transport cases')
