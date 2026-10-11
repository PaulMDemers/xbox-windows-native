"""Fresh234 worker publication, preserving all closed233 evidence."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'xemu-wait-lifecycle233'
assert not (k/'author.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={}
names=['common.py','typed-state.py','prepare.py','Prepare.ps1','Run.ps1','Invoke-233.ps1','run-emulator.py','supervise-emulator.py','trace.py','audit-emulator.py','test-guards.py','freeze.py','Build002.ps1','build002.py','decode-result.py']
for name in names:
 p=old/name;inputs[p.relative_to(ws).as_posix()]=sha(p);s=p.read_text()
 s=s.replace('wait233','snapshot234').replace('xemu-wait-lifecycle233','xemu-wait-snapshot234').replace('Invoke-233','Invoke-234')
 s=s.replace('build002','build001').replace('candidate002-source-pins','candidate001-source-pins')
 if name=='build002.py':
  s=s.replace('from patch002 import apply','from patch import apply').replace("prior=ws/'outputs/xemu-backend-consume232'","prior=ws/'outputs/xemu-wait-lifecycle233'")
  s=s.replace("pins=json.loads((prior/'candidate001-source-pins.json').read_text())","pins=json.loads((prior/'candidate002-source-pins.json').read_text())")
  s=s.replace("p=prior/('artifacts/wait-source001/pgraph.c' if n.endswith('/pgraph.c') else 'artifacts/build001/source/'+n)","p=prior/'artifacts/build002/source'/n")
  s=s.replace("'hw/xbox/nv2a/pgraph/pgraph.c'])","'hw/xbox/nv2a/pgraph/gl/renderer.c'])")
  s=s.replace("sha(k/'patch002.py')","sha(k/'patch.py')")
 if name=='freeze.py':s=s.replace('xemu-backend-consume232/emulator-frozen.json','xemu-wait-lifecycle233/emulator-frozen.json')
 if name=='trace.py':
  a=s.index('def wait_report(');z=s.index('def wait_dashboard(',a)
  s=s[:a]+'''def wait_report(path):
 deadline=time.monotonic()+12;attempts=0
 while True:
  attempts+=1;reply=cmd('qom-get '+path+' xwn-snapshot234-report')
  m=re.search(r'state=(\\d+)',reply);assert m,reply
  state=int(m[1])
  if state in [3,5]:
   assert state==3 and 'tuple_published=1' in reply,'Worker journal timeout; no tuple accepted'
   return dict(reply=reply,attempts=attempts)
  assert state in [1,2,7] and time.monotonic()<deadline,'Worker publication bound'
  time.sleep(.025)

'''+s[z:]
  a=s.index(' # Two fixed read-only live observations');z=s.index(" cmd('stop');stopped=True",a)
  s=s[:a]+''' # ONE live worker-copy request. The later reads are of its immutable tuple,
 # not contemporaneous stopped PG/FIFO samples or a search for an empty queue.
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 assert 'state=0' in cmd('qom-get '+path+' xwn-snapshot234-report')
 r['snapshot_request_may_be_accepted']=True;save()
 response=cmd('qom-set '+path+' xwn-snapshot234 true')
 assert 'Error' not in response and 'busy' not in response,response
 r['wait_live_snapshot']=wait_report(path);save()
'''+s[z:]
  s=s.replace("r['wait_stopped_before']=wait_report(path);", "r['wait_snapshot_at_stop']=wait_report(path);assert r['wait_snapshot_at_stop']['reply']==r['wait_live_snapshot']['reply'];")
  s=s.replace("r['wait_stopped_after']=wait_report(path);", "r['wait_snapshot_after_preserve']=wait_report(path);assert r['wait_snapshot_after_preserve']['reply']==r['wait_live_snapshot']['reply'];")
  s=s.replace("r.update(passed=state==3 and r['reserved_bytes_unchanged']", "r.update(snapshot_protocol_passed=True,passed=state==3 and r['reserved_bytes_unchanged']")
 q=k/({'Invoke-233.ps1':'Invoke-234.ps1','Build002.ps1':'Build.ps1','build002.py':'build.py'}.get(name,name))
 assert not q.exists();q.write_text(s)
 if q.suffix=='.py':ast.parse(s,filename=str(q))
for n in ['gdbstub/gdbstub.c','gdbstub/system.c']:
 p=old/'source'/n;q=k/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
(k/'author.json').write_text(json.dumps(dict(parent_inputs=inputs,physical_access=False,guest_launch=False),indent=2)+'\n')
print('234 unique harness authored')
