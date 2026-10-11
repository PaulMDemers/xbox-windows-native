"""Hash existing closed private evidence/images; no launch or disk collection."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'private-artifacts001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert read(k/'process-closure001.json')['closed']
rows=[]
for kit in ['gpu-preserve-entry239','gpu-preserve-entry240','gpu-preserve-empty241']:
 root=k.parent/kit
 for path in sorted(root.rglob('*')):
  if path.is_file() and ('artifacts' in path.parts or 'build-logs' in path.parts):rows.append(dict(path=path.relative_to(ws).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
 # Explicitly inspect the private junction capsule; do not depend on traversal semantics.
 if kit=='gpu-preserve-empty241':
  for path in sorted((root/'artifacts/build001').rglob('*')):
   if path.is_file() and path.relative_to(ws).as_posix() not in {v['path'] for v in rows}:rows.append(dict(path=path.relative_to(ws).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
disks=[]
f=read(k/'fixture-seed001.json');base=Path(f['fixture_path_windows']);assert sha(base)==f['seed_sha256']
for p in [base,base.with_name('seed001-preparation.qcow2')]+[Path(f'E:/Codex-private-artifacts/xbox-windows-feasibility/phase{phase}-runs/nt5-phase{phase}-{case}/hdd.qcow2') for phase,case in [(239,'control001'),(240,'preserve001'),(241,'preserve001')]]:
 assert p.exists();disks.append(dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
record=dict(passed=True,closed_private_artifacts=rows,closed_disks=disks,physical_access=False,scope='Existing retained private evidence hashes only, not all-file/durability qualification')
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
pins=read(k/'emulator-frozen.json')
for path,digest in pins.items():assert sha(ws/path)==digest,path
python=[]
for kit in ['gpu-preserve-entry239','gpu-preserve-entry240','gpu-preserve-empty241']:
 for p in (k.parent/kit).glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p));python.append(dict(path=p.relative_to(ws).as_posix(),sha256=sha(p)))
(k/'final-source-review001.json').write_text(json.dumps(dict(passed=True,frozen_pins_unchanged=len(pins),python=python,report_sha256=sha(k/'REPORT.md'),no_native_ownership=True,physical_access=False),indent=2)+'\n',encoding='utf-8')
print('Closed private hashes/frozen source review PASS',len(rows),'artifacts',len(disks),'images')
