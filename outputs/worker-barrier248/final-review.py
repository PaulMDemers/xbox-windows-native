"""Both closed cases, immutable failures, frozen/staged/private evidence review."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
assert read(k/'diagnostic-review001.json')['review_passed'] and not read(k/'diagnostic-review001.json')['overall_run_passed']
assert read(k/'portable-offload001.json')['closed']
rows=[];count=0
for phase in [247,248]:
 kit=k.parent/('worker-barrier'+str(phase));assert read(kit/'process-closure001.json')['closed']
 for path,h in read(kit/'emulator-frozen.json').items():assert sha(ws/path)==h,path;count+=1
 run=Path(f'E:/Codex-private-artifacts/xbox-windows-feasibility/phase{phase}-runs/nt5-phase{phase}-preserve001')
 assert read(run/'host-exit.json')['passed'] and read(kit/'preserve001/host-state.json')['closed']
 for p in (kit/'artifacts').rglob('*'):
  if p.is_file():rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 for p in (kit/'preserve001/artifacts').rglob('*'):
  if p.is_file():rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 for n in ['hdd.qcow2','cpu-trace.log','xemu-stdout.log','xemu-stderr.log','instance.json','host-exit.json','cleanup.json','input-hashes.json']:
  p=run/n;rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 if phase==248:
  for n in ['runtime-checkpoint001.json','checkpoint-1602.png','checkpoint-1602.json']:
   p=run/n;rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
assert not read(k.parent/'worker-barrier247/preserve001/trace.json')['passed']
assert not read(k.parent/'worker-barrier247/preserve001/worker.json')['passed']
assert not read(k.parent/'worker-barrier247/preserve001/worker-partial002.json')['passed']
assert not read(k/'preserve001/worker.json')['passed'] and read(k/'preserve001/trace.json')['passed']
original=(k.parent/'worker-barrier247/artifacts/continuation-before247.md').read_bytes();current=(ws/'outputs/engineering-notes/CONTINUATION.md').read_bytes();assert current.endswith(original)
assert original.replace(b'\r\n',b'\n')==subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md'],cwd=ws).replace(b'\r\n',b'\n')
stage=[]
for n in filter(None,subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().split('\0')):
 assert n in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'] or n.startswith(('outputs/worker-barrier247/','outputs/worker-barrier248/')),n
 assert '/artifacts/' not in n and not n.endswith(('.exe','.bin','.qcow2','.iso','.evt','.log')),n
 data=subprocess.check_output(['git','show',':'+n],cwd=ws);assert len(data)<5*1024**2
 if n.startswith(('outputs/worker-barrier247/','outputs/worker-barrier248/')):assert data==(ws/n).read_bytes(),n
 else:assert data.replace(b'\r\n',b'\n')==(ws/n).read_bytes().replace(b'\r\n',b'\n')
 stage.append(dict(path=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
for kit in [k,k.parent/'worker-barrier247']:
 for p in kit.glob('*.py'):ast.parse(p.read_text())
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
dest.write_text(json.dumps(dict(review_passed=True,source_sha256=sha(Path(__file__)),frozen_checks=count,private_inputs=rows,staged_inputs=stage,barrier_scope_passed=True,overall248_passed=False,prior247_stays_failed=True,no_old_evidence_rewritten=True,original_continuation_tail_preserved=True,all_owned_closed=True,physical_access=False,ordinary_qualified=False,native_gpu_ownership=False),indent=2)+'\n')
print('247/248 final review PASS, failed qualifications retained',len(stage),'staged,',len(rows),'private pins')
