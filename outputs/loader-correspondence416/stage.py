"""Stage an inactive matched loader candidate and rollback; never launch/activate."""
import importlib.util
import json
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
from common001 import put
ROOT='/E/xwn416-stage'
ACTIVE='/E/Applications/XWNEBoot/'
out=K/'stage001.json'
assert not out.exists()
q=m.read(K/'comparison002.json');assert q['passed'] and q['all_nonmetadata_bytes_exact']
local=Path('E:/xwn416')
for row in q['files']:
    for phase,field in [('candidate','candidate_sha256'),('baseline','baseline_sha256')]:
        assert m.sha((local/phase/row['relative']).read_bytes())==row[field]
m.ticket()
r=dict(completed=False,started_utc=m.utc(),remote=ROOT,inactive=True,launch_requested=False,
       active_files_changed=False,console_C_accessed=False,writes=[],verified={},protected={},
       comparison_sha256=m.sha((K/'comparison002.json').read_bytes()),
       source_sha256=m.sha((K/'stage.py').read_bytes()))
m.write_json(out,r)
try:
    with m.connect() as f:
        assert ROOT.rsplit('/',1)[1].lower() not in {n.lower() for n in m.names(f,'/E')}
        before=m.read(W/'outputs/baseline-compare415/physical001.json')
        for path,row in before['files'].items():
            if '/config/' in path.lower():continue
            data=m.get(f,path)
            assert m.sha(data)==row['sha256'],path
            r['protected'][path]=row['sha256']
        for path in [m.START,'/E/winnt/system32/config/system','/E/winnt/system32/config/software']:
            r['protected'][path]=m.sha(m.get(f,path))
        for row in q['files']:
            assert m.sha(m.get(f,ACTIVE+row['relative']))==row['baseline_sha256']
        for folder in ['', '/candidate','/candidate/loader','/baseline','/baseline/loader']:
            target=ROOT+folder;r['writes'].append(target);m.write_json(out,r);f.mkd(target)
        owner=json.dumps(dict(project='xbox-windows-native',kit=416,inactive=True,
                              comparison_sha256=r['comparison_sha256']),sort_keys=True).encode()
        for row in q['files']:
            for phase,field in [('candidate','candidate_sha256'),('baseline','baseline_sha256')]:
                target=ROOT+'/'+phase+'/'+row['relative']
                data=(local/phase/row['relative']).read_bytes()
                r['writes'].append(target);m.write_json(out,r);put(f,target,data)
                assert m.sha(m.get(f,target))==row[field]
                r['verified'][target]=dict(bytes=len(data),sha256=row[field]);m.write_json(out,r)
        target=ROOT+'/owner.json';r['writes'].append(target);m.write_json(out,r);put(f,target,owner)
        r['verified'][target]=dict(bytes=len(owner),sha256=m.sha(owner))
        for path,h in r['protected'].items():assert m.sha(m.get(f,path))==h,path
        r.update(completed=True,ended_utc=m.utc(),protected_after_exact=True)
except BaseException as e:r['error']=repr(e);raise
finally:m.write_json(out,r)
print(json.dumps(dict(completed=r['completed'],inactive=True,files=len(r['verified']),launch=False)))
