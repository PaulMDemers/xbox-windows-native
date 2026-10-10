"""Review queued source only; no preparation/runtime/driver qualification."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'guard-review002.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert not (k/'trace001').exists() and not (k/'fixture-trace001.json').exists() and not (k/'emulator-frozen.json').exists()
c=read(k/'closure.json');assert c['closed'] and c['exit_code']==1 and c['wait_attempts']==41 and not c['fixture_created'] and not c['guest_launch']
rows=read(k/'preparation-resource.json')['attempts'];assert len(rows)==41 and all(v['resource_busy'] and not v['case_created'] for v in rows)
r=read(k/'draft-restoration.json');assert r['passed'] and not r['frozen_inputs_changed'] and not r['fixture_created']
correction=read(k/'guard-correction002.json')
assert correction['before_sha256']==r['after']['trace.py']
assert correction['after_sha256']==sha(k/'trace.py')
for name,h in r['after'].items():
 if name!='trace.py' and not name.endswith('.md'):assert sha(k/name)==h,name
host=read(k/'guard-test002.json')
assert host['passed'] and host['checks']==55 and host['source_sha256']==sha(k/'trace.py')
assert host['test_sha256']==sha(k/'test-guards.py')
for name,h in r['parent_source_pins'].items():assert sha(k.parent/'xemu-backend-reason228'/name)==h,name
for name,h in read(k.parent/'xemu-backend-reason228/emulator-frozen.json').items():assert sha(ws/name)==h,name
syntax=[]
for p in k.glob('*.py'):assert p.stat().st_size;ast.parse(p.read_text(),filename=str(p));syntax.append(p.name)
trace=(k/'trace.py').read_text();assert 'dashboard_barrier' in trace and 'Qqemu.PhyMemMode:0' in trace and 'quarantined=True' in trace
assert 'executing_code_pin' not in trace and 'g.bp(site);armed=True' not in trace
assert 'credentials required BEFORE instance creation' in (k/'run-emulator.py').read_text()
assert "r['publication_contract_qualified']=False" in (k/'audit-emulator.py').read_text()
staged={}
for name in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
 if name.startswith('outputs/xemu-backend-dashboard229/'):
  data=subprocess.check_output(['git','show',':'+name],cwd=ws);assert data==(ws/name).read_bytes()
  staged[name]=hashlib.sha256(data).hexdigest()
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),staged_byte_pins=staged,python_syntax=syntax,fixture_created=False,guest_launch=False,physical_access=False,backend_qualified=False,limits='Source-only safety correction: bounded FTP retry and uncertain-mode restoration quarantine, 55 helper failure checks. No229 runtime qualification or ownership grant.'),indent=2)+'\n')
print('229 guard correction source review PASS; runtime unqualified')
