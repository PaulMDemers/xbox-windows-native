"""Final immutable/private/report/closure checks, no guest operation or recollection."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert read(k/'review001.json')['passed'] and read(k/'process-closure001.json')['closed']
assert read(k/'process-closure001.json')['no_root_guest_queued']
private=[];reports={}
for kit in [k.parent/'gpu-lifecycle244',k]:
 for p,h in read(kit/'emulator-frozen.json').items():assert sha(ws/p)==h,p
 for p in kit.glob('*.py'):ast.parse(p.read_text())
 for p in kit.rglob('*'):
  if p.is_file() and 'artifacts' in p.parts:private.append(dict(path=p.relative_to(ws).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
 reports[(kit/'REPORT.md').relative_to(ws).as_posix()]=sha(kit/'REPORT.md')
for build in [1,2,3,4,5]:
 root=Path(f'E:/Codex-archive/xbox-windows-native/phase244-build{build:03d}')
 if root.exists():
  for p in root.rglob('*'):
   if p.is_file():private.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
closed=[]
for phase in [244,245]:
 run=Path(f'E:/Codex-private-artifacts/xbox-windows-feasibility/phase{phase}-runs/nt5-phase{phase}-preserve001')
 assert read(run/'host-exit.json')['passed'] and read(run/'cleanup.json')
 for name in ['hdd.qcow2','cpu-trace.log','xemu-stdout.log','xemu-stderr.log']:
  p=run/name;closed.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),owned_vm_closed=True))
cont=ws/'outputs/engineering-notes/CONTINUATION.md'
old=k.parent/'gpu-lifecycle244/artifacts/continuation-before244.md';assert cont.read_bytes().endswith(old.read_bytes())
assert cont.read_bytes().replace(b'\r\n',b'\n').endswith(subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md']))
assert read(k/'portable-offload001.json')['free_c']>=20*1024**3
dest.write_text(json.dumps(dict(passed=True,private_artifacts=private,closed_images_and_logs=closed,reports=reports,source_sha256=sha(Path(__file__)),old_continuation_tail_preserved=True,all_owned_closed=True,physical_access=False,no_recollection=True,no_root_guest_queued=True),indent=2)+'\n')
print('244/245 final immutable/source/private hashes and closure PASS',len(private),'private artifacts')
