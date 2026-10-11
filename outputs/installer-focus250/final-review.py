"""Frozen/staged/private review with original failures and runtime limits retained."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert read(k/'closed-review001.json')['review_passed'] and read(k/'process-closure001.json')['closed'] and read(k/'portable-offload001.json')['closed']
assert read(k/'continuation-closed001.json')['all_owned_closed']
private=[];count=0
for phase in [249,250]:
 kit=k.parent/f'installer-focus{phase}'
 for name,digest in read(kit/'emulator-frozen.json').items():assert sha(ws/name)==digest,name;count+=1
 state=read(kit/'preserve001/host-state.json');assert state['closed'] and state['cleanup_record_exists'] and state['audit_exit_code']==0
 run=Path(f'E:/Codex-private-artifacts/xbox-windows-feasibility/phase{phase}-runs/nt5-phase{phase}-preserve001');assert read(run/'host-exit.json')['passed']
 for root in [kit/'artifacts',kit/'preserve001/artifacts']:
  for p in root.rglob('*'):
   if p.is_file():private.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 for name in ['hdd.qcow2','cpu-trace.log','instance.json','host-exit.json','cleanup.json','input-hashes.json']:
  p=run/name;private.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 for p in kit.glob('*.py'):ast.parse(p.read_text())
assert not read(k.parent/'installer-focus249/preserve001/trace.json')['passed'] and read(k/'preserve001/worker.json')['passed']
assert not read(k/'preserve001/audit.json')['strict_qualification_passed'] and not read(k/'closed-review001.json')['original248_cause_resolved']
original=(k.parent/'installer-focus249/artifacts/continuation-before249.md').read_bytes();assert (ws/'outputs/engineering-notes/CONTINUATION.md').read_bytes().endswith(original)
assert original.replace(b'\r\n',b'\n')==subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md'],cwd=ws).replace(b'\r\n',b'\n')
stage=[]
for name in filter(None,subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().split('\0')):
 assert name in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'] or name.startswith(('outputs/installer-focus249/','outputs/installer-focus250/')),name
 assert '/artifacts/' not in name and not name.endswith(('.exe','.bin','.qcow2','.iso','.evt','.log')),name
 data=subprocess.check_output(['git','show',':'+name],cwd=ws)
 if name.startswith(('outputs/installer-focus249/','outputs/installer-focus250/')):assert data==(ws/name).read_bytes(),name
 else:assert data.replace(b'\r\n',b'\n')==(ws/name).read_bytes().replace(b'\r\n',b'\n')
 stage.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
dest.write_text(json.dumps(dict(review_passed=True,frozen_checks=count,private_inputs=private,staged_inputs=stage,prior249_failed=True,scoped250_passed=True,strict_qualified=False,original248_cause_resolved=False,diagnostic_refusal_branch_runtime_exercised=False,no_old_evidence_rewritten=True,original_tail_preserved=True,all_owned_closed=True,physical_access=False,native_gpu_ownership=False),indent=2)+'\n');print('249/250 final review PASS; failure/unobserved branch/strict limits retained')
