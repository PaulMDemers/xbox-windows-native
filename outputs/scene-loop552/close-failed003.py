"""Close one ordinary PC fixture and archive all exact launch inputs."""
import hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'final-review.json';archive=Path('/home/paul/xbox-windows-native/scene-loop552-inputs001')
assert not out.exists() and not archive.exists()
s=read(K/'ntfs-phase1.json');c=read(K/'ntfs-cold1-002.json');r=read(K/'pixel-review003.json')
i=read(K/'independent003.json');m=read(K/'module-review003.json')
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(n) for n in ('host_quit','host_kill','host_terminate'))
assert c['complete'] and c['normal_shutdown_delta']==1 and r['pixel_endpoints_passed'] and not r['all_allowed_cases_passed'] and len(r['rows'])==2
assert i['passed'] and i['closed'] and i['mount_absent'] and i['disk_unchanged'] and m['passed']
prep=read(K/'ntfs-preparation001.json');P=Path(prep['path'])
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==s['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-scene-loop552-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'scene-loop552-pc001/disk.qcow2' in raw):owned.append(str(p))
 except OSError:pass
assert not owned
pins=r['frozen_dependencies'];assert shutil.disk_usage(archive.parent).free-sum(Path(p).stat().st_size for p in pins)>20*1024**3
archive.mkdir();saved={}
for j,(n,h) in enumerate(sorted(pins.items())):
 p=Path(n);assert sha(p)==h;dest=archive/f'{j:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h;saved[n]=dict(path=str(dest),sha256=h)
for row in read(K/'build001.json')['rows']:assert sha(Path(row['path']))==row['sha256']
psapi=next(x for x in i['rows'] if x['path']=='winnt/system32/psapi.dll');assert psapi['sha256']==read(K/'dynamic-import001.json')['dll_sha256']
result=dict(closed=True,scoped_sustained_scene_passed=False,pixel_endpoints_passed=True,timing_gate_failed=True,normal_restart=True,scene_processes=2,physical_access=False,owned_processes_open=owned,archived_inputs=saved,new_system_events=c['new_system_events'],known_limitations=['160 repeated frames and final release do not establish long-run leak freedom','Phase API timings exclude capture I/O and explicit pauses; not FPS, scanout or physical-console speed','Inherited SOFTWARE typed DRM limitation; no independent full NTFS allocation audit','No GPU, games or ideal-alpha qualification'])
out.write_text(json.dumps(result,indent=2)+'\n');print('Closed552 timing FAILED, pixel-only endpoints pass:',len(saved),'archived inputs')
