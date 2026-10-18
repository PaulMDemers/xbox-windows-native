"""Close the failed alpha qualification without rewriting its oracle or receipts."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/d3d-blend484-inputs001')
assert not out.exists() and not capsule.exists()
s=read(K/'ntfs-phase1.json');c=read(K/'ntfs-cold1-002.json');i=read(K/'independent002.json');r=read(K/'runtime-review001.json');m=read(K/'module-review002.json');a=read(K/'failure-analysis001.json')
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(k) for k in ['host_quit','host_kill','host_terminate'])
assert i['passed'] and i['closed'] and i['mount_absent'] and i['disk_unchanged'] and c['normal_shutdown_delta']==1
assert not r['all_allowed_cases_passed'] and m['passed'] and not a['qualification_passed']
assert all(x['process_exit']==0 and x['review_failure']=='a0 pixel 8,8' for x in r['rows'])
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
  args=p.read_bytes().split(b'\0');name=args[0].rsplit(b'/',1)[-1]
  if name in (b'qemu-system-i386',b'qemu-system-x86_64',b'qemu-nbd',b'nbdfuse'):owned.append(str(p))
 except OSError:pass
assert not owned
folders=(P,Path(i['private_path']),Path(read(K/'independent001.json')['private_path']),capsule)
private={str(p):sha(p) for folder in folders for p in folder.rglob('*') if p.is_file()}
record=dict(closed=True,scoped_blend_passed=False,normal_restart=True,owned_processes_open=owned,physical_access=False,independent_files=len(i['rows']),private_files=private,frozen_inputs=archived,module_snapshots=m['rows'],failure_analysis=a,new_system_events=c['new_system_events'],oracle_unchanged=True,old_success_only_closeout_executed=False,old_success_only_mutations_executed=False,known_limitations=['Endpoint alpha0 and alpha255 violate the original exact-color oracle','Fixed-point arithmetic is a hypothesis, not traced implementation','No full NTFS allocation audit','Inherited SOFTWARE typed DRM limitation','No Xbox alpha qualification, presentation, performance, games or GPU result'])
out.write_text(json.dumps(record,indent=2)+'\n');print('Closed failed PC alpha qualification; archived inputs:',len(archived))
