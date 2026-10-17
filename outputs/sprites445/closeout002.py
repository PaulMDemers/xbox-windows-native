"""Preserve unsupported-mode diagnostic and all source/transport ordering limits."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/sprites445-inputs001')
assert not out.exists() and not capsule.exists()
r=json.loads((K/'runtime-review002.json').read_text());ind=json.loads((K/'independent002.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert r['mode_request_refused'] and r['sample_cases_executed']==0 and state['closed'] and not state['deadline'] and cold['normal_shutdown_delta']==1
assert ind['passed'] and ind['closed'] and ind['mount_absent'] and ind['disk_unchanged']
pins=dict(r['frozen_dependencies'])
for p in [K/'review002.py',K/'independent002.py',K/'closeout002.py',W/'src/samples/graphics-ladder/sprites.c',W/'src/samples/graphics-ladder/sprites.cmd',W/'tools/build-graphics-samples.py',W/'tests/test_graphics_sprites.py']:pins[str(p)]=sha(p)
capsule.mkdir();archived={}
for i,(name,h) in enumerate(sorted(pins.items())):
 p=Path(name);assert sha(p)==h;dest=capsule/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h;archived[name]=dict(path=str(dest),sha256=h)
for name in ('build001.json','sample-build001.json'):
 b=json.loads((K/name).read_text())
 for p,h in b['headers'].items():assert sha(Path(p))==h
for row in json.loads((K/'build001.json').read_text())['rows']:assert sha(Path(row['path']))==row['sha256']
prep=json.loads((K/'ntfs-preparation001.json').read_text());P=Path(prep['path'])
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==state['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-sprites445-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'sprites445-pc001/disk.qcow2' in raw):owned.append(str(p))
 except (OSError,ProcessLookupError):pass
assert not owned
private={str(p):sha(p) for folder in (P,Path(ind['private_path']),capsule) for p in folder.rglob('*') if p.is_file()}
record=dict(full_rung04_passed=False,diagnostic_only=True,sample_cases_executed=0,mode_refused=True,normal_restart=True,owned_processes_open=owned,independent_files=len(ind['rows']),private_files=private,frozen_inputs=archived,limitations=['Preflight publication0.407723seconds after launch; not deployment qualification','No full NTFS allocation audit','Inherited SOFTWARE DRM typed-value limitation','No Xbox/scanout/GPU/D3D/performance claim'])
out.write_text(json.dumps(record,indent=2)+'\n');print('Refusal diagnostic closed;',len(archived),'inputs archived.')
