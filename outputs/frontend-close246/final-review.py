"""Final reviewed source/staged/private pin and actual owned-process closure."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
assert read(k/'review001.json')['passed'] and read(k/'process-closure001.json')['closed'] and read(k/'portable-offload001.json')['closed']
for path,digest in read(k/'emulator-frozen.json').items():assert sha(ws/path)==digest,path
private=k/'artifacts';rows=[]
for p in private.rglob('*'):
 if p.is_file():rows.append(dict(path=p.relative_to(ws).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase246-runs/nt5-phase246-preserve001')
for n in ['hdd.qcow2','cpu-trace.log','xemu-stdout.log','xemu-stderr.log','instance.json','host-exit.json','cleanup.json','input-hashes.json']:
 p=run/n;rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
assert read(run/'host-exit.json')['passed'] and read(k/'build001.json')['borrowed_sources_restored']
original=(private/'continuation-before246.md').read_bytes();current=(ws/'outputs/engineering-notes/CONTINUATION.md').read_bytes();assert current.endswith(original)
assert original.replace(b'\r\n',b'\n')==subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md'],cwd=ws).replace(b'\r\n',b'\n')
staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().split('\0');stage=[]
for n in filter(None,staged):
 assert n in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'] or n.startswith('outputs/frontend-close246/'),n
 assert '/artifacts/' not in n and not n.endswith(('.exe','.bin','.qcow2','.iso','.evt','.log')),n
 data=subprocess.check_output(['git','show',':'+n],cwd=ws);assert len(data)<=5*1024**2
 if n.startswith('outputs/frontend-close246/'):assert data==(ws/n).read_bytes(),n
 elif n.endswith('CONTINUATION.md'):assert data.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n')
 stage.append(dict(path=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
for p in k.glob('*.py'):ast.parse(p.read_text())
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),private_inputs=rows,staged_inputs=stage,frozen_pins=len(read(k/'emulator-frozen.json')),report_sha256=sha(k/'REPORT.md'),continuation_sha256=sha(ws/'outputs/engineering-notes/CONTINUATION.md'),no_old_evidence_rewritten=True,all_owned_closed=True,physical_access=False,ordinary_qualified=False,native_gpu_ownership=False),indent=2)+'\n')
print('246 final staged/source/private-input/continuation review PASS',len(stage),'staged,',len(rows),'private pins')
