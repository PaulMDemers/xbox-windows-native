"""Correct missing static inventory BEFORE a fresh250 attempt, never replay249."""
import hashlib,json,shutil
from pathlib import Path
old=Path(__file__).resolve().parent;k=old.parent/'installer-focus250';k.mkdir(exist_ok=False);ws=old.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
s=read(old/'preserve001/host-state.json');t=read(old/'preserve001/trace.json');a=read(old/'preserve001/audit.json')
assert s['closed'] and s['cleanup_record_exists'] and a['integrity_passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert 'loader_launch' not in t and not t['passed'] and 'inventory001.json' in t['host_traceback']
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-249.ps1','trace.py','schema.py','lifecycle.py','lifecycle246.py','lifecycle247.py','closed.py','worker.py','analyze-worker.py','diagnostic.py','freeze.py','test-diagnostic003.py']
for name in names:
 p=old/name;v=p.read_text().replace('installer-focus249','installer-focus250').replace('phase249','phase250').replace('Invoke-249','Invoke-250')
 if name=='freeze.py':v=v.replace("k.parent/'worker-barrier248/emulator-frozen.json'", "k.parent/'installer-focus249/emulator-frozen.json'")
 (k/name.replace('Invoke-249','Invoke-250')).write_text(v)
for name in ['inputs','ram-source','wizard-build001']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source')
for name in ['build004.json','candidate004-source-pins.json','wizard.c','policy.h','wizard-build001.json','source-review001.json']:shutil.copyfile(old/name,k/name)
for name in ['inventory001.json','inventory.c']:shutil.copyfile(old.parent/'worker-barrier248'/name,k/name)
(k/'preserve001/artifacts').mkdir(parents=True);rows=[]
for row in read(old/'baseline-inputs001.json')['files']:
 p=ws/row['path'];assert sha(p)==row['sha256'];to=k/'preserve001/artifacts'/p.name;shutil.copyfile(p,to);rows.append(dict(path=to.relative_to(ws).as_posix(),sha256=sha(to)))
(k/'baseline-inputs001.json').write_text(json.dumps(dict(passed=True,files=rows,physical_access=False),indent=2)+'\n')
f=read(old/'fixture-preserve001.json');f['new_unique_runtime']='nt5-phase250-preserve001';f['seed_owner']='outputs/installer-focus249/seed001';f['reused_verified_immutable_seed']=True
(k/'fixture-preserve001.json').write_text(json.dumps(f,indent=2)+'\n')
(k/'parent001.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),new_build=False,emulator_from='outputs/worker-barrier247/build004.json',wizard_from='outputs/installer-focus249/wizard-build001.json',fix='Missing read-only inventory manifest supplied before launch; no guest/policy/binary change',prior249_remains_failed=True,prior249_windows_launch=False,physical_access=False),indent=2)+'\n')
print('250 fresh kit prepared with missing inventory; compiled binaries/seed unchanged')
