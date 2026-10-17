"""Pin the successful PC control's complete retained source/capture closure."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/sprites444-inputs001')
assert not out.exists() and not capsule.exists()
state=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text())
ind=json.loads((K/'independent001.json').read_text());r=json.loads((K/'runtime-review001.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline']
assert ind['passed'] and ind['closed'] and ind['mount_absent'] and ind['disk_unchanged'] and cold['normal_shutdown_delta']==1
controls=json.loads((K/'actual-controls001.json').read_text())
capsule.mkdir();pins=dict(r['frozen_dependencies'])
for p in (W/'src/samples/graphics-ladder/sprites.c',W/'src/samples/graphics-ladder/sprites.cmd',W/'tools/build-graphics-samples.py',W/'tests/test_graphics_sprites.py'):pins[str(p)]=sha(p)
archived={}
for i,(path,h) in enumerate(sorted(pins.items())):
 p=Path(path);assert sha(p)==h,path;dest=capsule/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived[path]=dict(path=str(dest),sha256=h)
for name in ('build001.json','sample-build001.json'):
 b=json.loads((K/name).read_text())
 for p,h in b['headers'].items():assert sha(Path(p))==h
assert sha(W/'src/samples/graphics-ladder/sprites.c')==json.loads((K/'sample-build001.json').read_text())['source_sha256']
for row in json.loads((K/'build001.json').read_text())['rows']:assert sha(Path(row['path']))==row['sha256']
prep=json.loads((K/'ntfs-preparation001.json').read_text());P=Path(prep['path'])
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==state['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-sprites444-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'sprites444-pc001/disk.qcow2' in raw):owned.append(str(p))
 except (OSError,ProcessLookupError):pass
assert not owned
private={str(p):sha(p) for folder in (P,Path(ind['private_path']),capsule) for p in folder.rglob('*') if p.is_file()}
record=dict(full_rung04_passed=r['all_allowed_cases_passed'],normal_restart=True,owned_processes_open=owned,independent_files=len(ind['rows']),private_files=private,frozen_inputs=archived,
 actual_mutations_rejected=sum(row['scalar_rejections']+row['pixel_length_rejections'] for row in controls['rows']),
 exact_bytes=sum(row['review']['exact_bytes'] for row in r['rows'] if 'review' in row),
 known_limitations=['No full NTFS allocation audit','Inherited SOFTWARE unknown typed DRM value','GDI readback, not scanout/GPU/performance qualification'])
out.write_text(json.dumps(record,indent=2)+'\n');print('PC control closed:',record['exact_bytes'],'exact bytes;',len(archived),'archived inputs')
