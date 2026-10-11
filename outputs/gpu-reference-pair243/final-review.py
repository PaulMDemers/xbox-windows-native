"""Final text/private pin review only; no guest operations or cold recollection."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review001.json';assert not dest.exists();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for kit in [k.parent/'gpu-reference-pair242',k]:
 for p,h in read(kit/'emulator-frozen.json').items():assert sha(ws/p)==h,p
 assert read(kit/'review001.json')['passed']
 for py in kit.glob('*.py'):ast.parse(py.read_text(encoding='utf-8'))
assert read(k/'process-closure001.json')['closed'] and read(k/'process-closure001.json')['no_root_guest_queued']
assert read(k/'portable-final-offload001.json')['closed']
assert read(k/'portable-final-offload001.json')['free_c']>=20*1024**3
for name in ['portable-offload001.json','portable-final-offload001.json']:
 d=read(k/name)
 for e in d['entries']:
  assert e['original_path_preserved'] and not e['disk_backing_chains_moved'] and e['owned_vm_closed']
  for row in e['files']:
   p=Path(e['source'])/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
old=k.parent/'gpu-reference-pair242/artifacts/continuation-before242.md';cont=ws/'outputs/engineering-notes/CONTINUATION.md';assert cont.read_bytes().endswith(old.read_bytes())
assert cont.read_bytes().replace(b'\r\n',b'\n').endswith(subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md']))
private=[]
for kit in [k.parent/'gpu-reference-pair242',k]:
 for p in kit.rglob('*'):
  if p.is_file() and 'artifacts' in p.parts:private.append(dict(path=p.relative_to(ws).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
closed=[]
for phase in [242,243]:
 run=Path(f'E:/Codex-private-artifacts/xbox-windows-feasibility/phase{phase}-runs/nt5-phase{phase}-preserve001')
 assert read(run/'host-exit.json')['passed'] and read(run/'cleanup.json')
 p=run/'hdd.qcow2';closed.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),owned_vm_closed=True))
dest.write_text(json.dumps(dict(passed=True,private_artifacts=private,closed_images=closed,frozen_sources_preserved=True,old_continuation_tail_preserved=True,no_recollection=True,no_root_guest_queued=True,physical_access=False,scope='Private hash retention, frozen/source/continuation review, actual completed offloads; no new durability experiment'),indent=2)+'\n',encoding='utf-8')
print('242/243 final source/private hash review PASS',len(private),'artifacts')
