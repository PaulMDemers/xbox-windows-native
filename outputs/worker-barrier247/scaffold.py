"""Fresh247 worker diagnostic; copy inputs/helpers, never closed outcomes."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'frontend-close246';ws=k.parents[1]
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-246.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','schema.py','lifecycle.py','lifecycle246.py','closed.py','test-closed.py','test-lifecycle002.py','test-pair-updated.py','test-guards003-updated.py','record-processes.ps1']
for name in names:
 p=k/name.replace('Invoke-246','Invoke-247');assert not p.exists()
 s=(old/name).read_text().replace('frontend-close246','worker-barrier247').replace('phase246','phase247').replace('Invoke-246','Invoke-247')
 if name=='Run.ps1':s=s.replace('xemu-frontend246.exe','xemu-worker247.exe')
 if name=='freeze.py':s=s.replace("k.parent/'gpu-lifecycle245/emulator-frozen.json'","k.parent/'frontend-close246/emulator-frozen.json'")
 if name=='record-processes.ps1':
  s=s.replace('foreach($phase in 246)','foreach($phase in 247)').replace('"outputs/frontend-close$phase"','"outputs/worker-barrier$phase"')
  s=s.replace("unified_sessions=@{build45619='closed0';matrix11204='closed0'}","unified_sessions=@{records='host-state and matrix retain actual owned identities'}")
 p.write_text(s)
for name in ['fixture-preserve001.json','inventory001.json','inventory.c']:shutil.copyfile(old/name,k/name)
p=k/'fixture-preserve001.json';d=json.loads(p.read_text());d['new_unique_runtime']='nt5-phase247-preserve001';d['compiled_emulator_from']='outputs/worker-barrier247/build001.json';p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
(k/'preserve001/artifacts').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for row in json.loads((old/'baseline-inputs001.json').read_text())['files']:
 p=ws/row['path'];assert sha(p)==row['sha256'];to=k/'preserve001/artifacts'/p.name;shutil.copyfile(p,to);rows.append(dict(path=to.relative_to(ws).as_posix(),sha256=sha(to)))
(k/'baseline-inputs001.json').write_text(json.dumps(dict(passed=True,files=rows,physical_access=False),indent=2)+'\n')
# Exact parent capsule; reusable GDB source is a primary input to guard tests.
shutil.copytree(old/'source',k/'source')
s=(old/'build.py').read_text().replace('246','247').replace('frontend','worker')
s=s.replace("prior=ws/'outputs/gpu-lifecycle244';pins=json.loads((prior/'candidate005-source-pins.json').read_text())","prior=ws/'outputs/frontend-close246';pins=json.loads((prior/'candidate001-source-pins.json').read_text())")
s=s.replace("prior/'artifacts/build005/source'","prior/'artifacts/build001/source'").replace("sha(k/'worker.c')","sha(k/'worker.c')")
(k/'build.py').write_text(s)
print('247 fresh input kit prepared; no guest launch')
