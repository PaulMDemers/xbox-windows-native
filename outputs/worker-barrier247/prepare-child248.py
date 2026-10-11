"""New248 host-corrected child; exact same compiled247 worker, no old replay."""
import hashlib,json,shutil
from pathlib import Path
old=Path(__file__).resolve().parent;k=old.parent/'worker-barrier248';k.mkdir(exist_ok=False);ws=old.parents[1]
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-247.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','schema.py','lifecycle.py','lifecycle246.py','lifecycle247.py','closed.py','test-closed.py','test-lifecycle002.py','test-pair-updated.py','test-guards003-updated.py','worker.py','analyze-worker.py','prelaunch-review.py','record-processes.ps1']
for name in names:
 s=(old/name).read_text().replace('worker-barrier247','worker-barrier248').replace('phase247','phase248').replace('Invoke-247','Invoke-248')
 if name=='trace.py':
  assert s.count("assert r['frontend_closed_reread']==reply")==1
  s=s.replace("assert r['frontend_closed_reread']==reply","assert r['frontend_closed_reread']==r['frontend_closed_report']")
 if name=='freeze.py':s=s.replace("k.parent/'frontend-close246/emulator-frozen.json'","k.parent/'worker-barrier247/emulator-frozen.json'")
 if name=='record-processes.ps1':s=s.replace('foreach($phase in 247)','foreach($phase in 248)')
 if name=='prelaunch-review.py':
  s=s.replace("parent=k.parent/'frontend-close246/artifacts/build001/source'","parent=k.parent/'frontend-close246/artifacts/build001/source'")
  s=s.replace("for name in ['worker-test003','worker-proof002','pair-test002'","for name in ['pair-test002'")
  s=s.replace("read(k/'worker-test003.json')","read(k.parent/'worker-barrier247/worker-test003.json')")
  s=s.replace("(k/'worker.c')","(k.parent/'worker-barrier247/worker.c')")
 (k/name.replace('Invoke-247','Invoke-248')).write_text(s)
for name in ['fixture-preserve001.json','inventory001.json','inventory.c','worker.c','build004.json','candidate004-source-pins.json','DESIGN.md','test-worker-proof002.py']:shutil.copyfile(old/name,k/name)
p=k/'test-worker-proof002.py';p.write_text(p.read_text().replace('worker-proof002.json','worker-proof001.json'))
p=k/'fixture-preserve001.json';d=json.loads(p.read_text());d['new_unique_runtime']='nt5-phase248-preserve001';d['compiled_emulator_from']='outputs/worker-barrier247/build004.json';p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source');(k/'preserve001/artifacts').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for row in json.loads((old/'baseline-inputs001.json').read_text())['files']:
 p=ws/row['path'];assert sha(p)==row['sha256'];to=k/'preserve001/artifacts'/p.name;shutil.copyfile(p,to);rows.append(dict(path=to.relative_to(ws).as_posix(),sha256=sha(to)))
(k/'baseline-inputs001.json').write_text(json.dumps(dict(passed=True,files=rows,physical_access=False),indent=2)+'\n')
(k/'parent001.json').write_text(json.dumps(dict(implementation_from='outputs/worker-barrier247/build004.json',new_build=False,executable_sha256=json.loads((old/'build004.json').read_text())['executable_sha256'],host_fix='Compare immutable UI report with saved UI report, not reused worker reply variable',prior_trace_failed=True,source_sha256=sha(Path(__file__)),physical_access=False),indent=2)+'\n')
print('248 fresh host-corrected child prepared; exact same compiled247 binary')
