"""Close the diagnostic with immutable dependencies, independent reads and scope."""
import json
from pathlib import Path
from launch_gate import sha
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/key-semantics446-inputs001')
assert not out.exists() and not capsule.exists()
state=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text())
ind=json.loads((K/'independent001.json').read_text());r=json.loads((K/'runtime-review001.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline']
assert ind['passed'] and ind['closed'] and ind['mount_absent'] and ind['disk_unchanged'] and cold['normal_shutdown_delta']==1
controls=json.loads((K/'actual-controls001.json').read_text());assert controls['passed']
capsule.mkdir();pins=dict(r['frozen_dependencies']);archived={}
for i,(path,h) in enumerate(sorted(pins.items())):
 p=Path(path);assert sha(p)==h,path;dest=capsule/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived[path]=dict(path=str(dest),sha256=h)
for name in ('build001.json','sample-build001.json'):
 b=json.loads((K/name).read_text())
 for p,h in b['headers'].items():assert sha(p)==h
assert sha(W/'src/samples/graphics-ladder/keyprobe.c')==json.loads((K/'sample-build001.json').read_text())['source_sha256']
for row in json.loads((K/'build001.json').read_text())['rows']:assert sha(row['path'])==row['sha256']
prep=json.loads((K/'ntfs-preparation001.json').read_text());P=Path(prep['path'])
assert sha(prep['source'])==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==state['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-key-semantics446-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'key-semantics446-pc001/disk.qcow2' in raw):owned.append(str(p))
 except (OSError,ProcessLookupError):pass
assert not owned
private={str(p):sha(p) for folder in (P,Path(ind['private_path']),capsule) for p in folder.rglob('*') if p.is_file()}
record=dict(complete_observation=all(row['review']['complete_observation'] for row in r['rows']),semantics_passed=r['all_semantics_passed'],normal_restart=True,owned_processes_open=owned,independent_files=len(ind['rows']),private_files=private,frozen_inputs=archived,
 actual_mutations_rejected=sum(row['scalar_rejections']+row['pixel_length_rejections'] for row in controls['rows']),
 captured_bytes=sum(row['review']['captured_bytes'] for row in r['rows']),
 known_limitations=['Keyed pixel failures remain failures','Low16 comparison is explanatory model, not traced instructions','No full NTFS allocation audit','Inherited SOFTWARE unknown typed DRM value','No scanout/GPU/performance or Xbox qualification'])
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('Closed:',record['captured_bytes'],'captured bytes;',len(archived),'archived inputs')
