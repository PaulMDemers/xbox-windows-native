"""Rehash the closed PC and physical evidence and record remaining limitations."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];X=K.parent/'graphics-xbox438'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def hostpath(s):
 return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
assert not (K/'final-review.json').exists() and not (X/'final-review.json').exists()
prep=json.loads((K/'ntfs-preparation001.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline']
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(Path(prep['path'])/'disk.qcow2')==state['disk_sha256']
assert sha(Path(prep['path'])/'probe.img')==prep['floppy_sha256']
pc=json.loads((K/'runtime-review002.json').read_text());assert pc['all_allowed_cases_passed']
ind=json.loads((K/'independent001.json').read_text());assert ind['passed'] and ind['closed'] and ind['disk_unchanged'] and ind['mount_absent']
for p,h in pc['frozen_dependencies'].items():assert sha(Path(p))==h,p
for key in [K,X]:
 b=json.loads((key/'build001.json').read_text());assert b['exit_code']==0
 for p,h in b['headers'].items():assert sha(Path(p))==h,p
 for row in b['rows']:assert sha(Path(row['path']))==row['sha256']
private={}
for root in [Path(prep['path']),Path(ind['private_path'])]:
 for p in root.rglob('*'):
  if p.is_file():private[str(p)]=sha(p)
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  raw=p.read_bytes()
  if b'xwn-graphics437-pc-phase1\0' in raw or (b'qemu-nbd\0' in raw and b'graphics437-pc001/disk.qcow2' in raw):owned.append(str(p))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not owned and not list(Path(prep['path']).glob('phase*/qmp.sock'))
pcfinal=dict(scoped_sample_passed=True,private_files_rehashed=len(private),private_files=private,frozen_dependencies_verified=len(pc['frozen_dependencies']),independent_files=len(ind['rows']),actual_negative_controls=json.loads((K/'controls001.json').read_text())['actual_mutations_rejected'],owned_processes_open=owned,full_ntfs_allocation_audit=False,complete_typed_registry_qualification=False,hardware_acceleration_proved=False,source_and_floppy_unchanged=True)
(K/'final-review.json').write_text(json.dumps(pcfinal,indent=2)+'\n')
r=json.loads((X/'runtime-review001.json').read_text());assert r['all_allowed_cases_passed'] and r['normal_restart_supported']
c=json.loads((X/'physical001-collection.json').read_text());assert c['completed'] and c['hook_removed']
stage=json.loads((X/'physical001-stage.json').read_text());xpins={}
for row in list(c['files'].values())+list(stage['before'].values()):
 p=hostpath(row['path']);assert sha(p)==row['sha256'];xpins[str(p)]=row['sha256']
for p,h in r['frozen_dependencies'].items():assert sha(hostpath(p))==h
popups=[]
path=hostpath(c['files']['/E/winnt/system32/config/sysevent.evt']['path']).with_name('system-events.json')
newids={v['record'] for v in r['events']['system']['new_records']}
for e in json.loads(path.read_text())['records']:
 if e['record'] in newids and e['source']=='Application Popup':popups.append({n:e[n] for n in ['record','source','event_id','strings']})
assert len(popups)==2
xfinal=dict(scoped_sample_passed=True,strict_system_qualified=False,strict_limitations=['Ftdisk49','Two shutdown-time rundll32 initialization popups','Inherited unknown typed SOFTWARE DRM value','No full FATX allocation audit'],popups=popups,normal_restart_supported=True,hook_removed=True,protected_code_and_720p_unchanged=True,private_files_rehashed=len(xpins),private_files=xpins,frozen_dependencies_verified=len(r['frozen_dependencies']),actual_negative_controls=json.loads((X/'controls001.json').read_text())['actual_mutations_rejected'],hardware_acceleration_proved=False,visual_qualified=False,physical_access_closed=True)
(X/'final-review.json').write_text(json.dumps(xfinal,indent=2)+'\n')
print(json.dumps({'pc_private_files':len(private),'physical_private_files':len(xpins),'all_sample_cases_passed':True,'physical_strict_system_qualified':False,'owned_pc_processes_open':owned}))
