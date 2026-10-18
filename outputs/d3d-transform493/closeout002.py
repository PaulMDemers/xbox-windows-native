"""Close the scoped PC result and archive exact inputs before future work."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/d3d-transform493-inputs001')
assert not out.exists() and not capsule.exists()
s=read(K/'ntfs-phase1.json');c=read(K/'ntfs-cold1-002.json');i=read(K/'independent002.json');r=read(K/'runtime-review002.json');m=read(K/'module-review002.json');n=read(K/'actual-controls002.json')
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(k) for k in ['host_quit','host_kill','host_terminate'])
assert i['passed'] and i['closed'] and i['mount_absent'] and i['disk_unchanged'] and c['normal_shutdown_delta']==1
assert r['all_allowed_cases_passed'] and m['passed'] and n['passed']
capsule.mkdir();pins=dict(r['frozen_dependencies']);pins.update({str(p):sha(p) for p in K.glob('*.py')});archived={}
for index,(name,h) in enumerate(sorted(pins.items())):
 p=Path(name);assert sha(p)==h,name;dest=capsule/f'{index:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived[name]=dict(path=str(dest),sha256=h)
for name in ['build001.json','sample-build001.json']:
 for p,h in read(K/name)['headers'].items():assert sha(Path(p))==h
for row in read(K/'build001.json')['rows']:assert sha(Path(row['path']))==row['sha256']
prep=read(K/'ntfs-preparation001.json');P=Path(prep['path'])
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==s['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-d3d-transform493-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'd3d-transform493-pc001/disk.qcow2' in raw):owned.append(str(p))
 except OSError:pass
assert not owned
private={str(p):sha(p) for folder in (P,Path(i['private_path']),capsule) for p in folder.rglob('*') if p.is_file()}
record=dict(scoped_d3d_transform_passed=True,normal_restart=True,owned_processes_open=owned,physical_access=False,independent_files=len(i['rows']),private_files=private,frozen_inputs=archived,actual_controls=n['rows'],module_snapshots=m['rows'],new_system_events=c['new_system_events'],selected_system_event_delta_without_errors_or_warnings=not any(e['type'] in (1,2) for e in c['new_system_events']),known_limitations=['No full NTFS allocation audit','Inherited SOFTWARE typed DRM limitation','Exact raster edges, X byte, padding, clipping, lighting, presentation, textures/depth/blending interactions, performance, games and GPU unqualified','Live module snapshot does not capture previously unloaded modules'])
out.write_text(json.dumps(record,indent=2)+'\n');print('Closed PC D3D transforms PASS, archived inputs:',len(archived))
