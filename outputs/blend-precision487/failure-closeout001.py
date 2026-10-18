"""Cold failed-boot closure: no Windows workload receipts, no alpha verdict."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'final-review.json';assert not out.exists()
c=read(K/'collection-completed002.json');s=read(K/'physical001-stage.json');pkg=read(K/'package001.json');w=read(K/'actual-witness002.json')
assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and c['result_namespace_absent'] and w['passed']
assert c['remote_writes_after_original_collection']==[] and sha(K/'physical001-collection.json')==c['resumed_from_sha256']
for n,row in c['files'].items():
 if row:assert sha(host(row['path']))==row['sha256']
for n in s['staged']:assert c['files'][n]['unchanged']
for n in s['before']:assert c['files'][n]['unchanged'],n
assert c['files']['/E/Applications/XWNBoot487a/refusal.bin'] is None
assert not any(n.startswith('/E/xwn487/') for n in c['files'])
hives={}
for name in ['system','software','sam','security','default']:
 n='/E/winnt/system32/config/'+name
 hives[name]=audit(host(c['files'][n]['path']))
 assert hives[name]['clean'] and hives[name]['header_valid'] and hives[name]['independent_raw_values_agree']
events={}
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 n='/E/winnt/system32/config/'+name;p=host(c['files'][n]['path']);dest=p.with_name(label+'-events487.json');assert not dest.exists()
 subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
 assert c['files'][n]['sha256']==s['before'][n]['sha256']
 events[label]=dict(byte_identical_before_after=True,new_records=[],normal_shutdown_delta=0,records=len(read(dest)['records']))
capsule=Path('/mnt/c/xwn487/frozen001');assert not capsule.exists();capsule.mkdir();archived=[]
for j,(n,h) in enumerate(sorted(pkg['dependencies'].items())):
 p=host(n);assert sha(p)==h;dest=capsule/f'{j:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived.append(dict(original=n,path=str(dest),sha256=h))
owned=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  name=p.read_bytes().split(b'\0')[0].rsplit(b'/',1)[-1]
  if name in (b'qemu-system-i386',b'qemu-system-x86_64',b'qemu-nbd',b'nbdfuse'):owned.append(str(p))
 except OSError:pass
assert not owned
record=dict(closed=True,physical_launches=1,arithmetic_characterization_passed=False,windows_workload_observed=False,normal_windows_restart_proved=False,strict_system_qualification=False,late_handoff_boundary=w['actual_witness'],actual_witness_controls=w['negative_controls'],hives=hives,events=events,all_collected_mutable_files_unchanged=True,temporary_hook_removed=True,original_launcher_startup_and_720p_unchanged=True,console_C_accessed=False,partial_collection_preserved=True,missing_file_reads_completed=True,archived_inputs=archived,owned_QEMU_NBD_FUSE_processes=owned,repeat_boot_stability_qualified=False,failure_location_after_last_witness_unknown=True,no_next_launch_queued=True,private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('/mnt/c/xwn487').rglob('*') if p.is_file()},postcollection_source_sha256={str(p):sha(p) for p in [Path(__file__),K/'finish-collection002.py',K/'actual-witness002.py']})
out.write_text(json.dumps(record,indent=2)+'\n');print('Closed failed hardware boot: no Windows test result, hook removed, cold files unchanged.')
