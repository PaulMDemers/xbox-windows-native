"""Independent cold review; no physical network access or console mutation."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'));sys.path.insert(0,str(K))
from hive_audit004 import audit
from entry_decode import decode
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'physical-final001.json';assert not out.exists()
c=read(K/'physical001-collection.json');s=read(K/'physical001-stage.json');pkg=read(K/'package001.json');launch=read(K/'physical001-launch.json')
assert c['completed'] and c['protected_code_exact'] and s['completed'] and launch['requested']
assert not s['temporary_startup_added'] and not c['temporary_hook_installed'] and c['remote_writes']==[]
for row in list(s['before'].values())+list(c['files'].values()):
 if row:assert sha(host(row['path']))==row['sha256'] and host(row['path']).stat().st_size==row['bytes']
for n in s['staged']:assert c['files'][n]['unchanged']
for n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert c['files'][n]['unchanged']
hives={};events={}
for name in ['system','software','sam','security','default']:
 n='/E/winnt/system32/config/'+name
 hives[name]={label:audit(host(row['path'])) for label,row in [('before',s['before'][n]),('after',c['files'][n])]}
 assert all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in hives[name].values())
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 n='/E/winnt/system32/config/'+name;parsed={}
 for phase,row in [('before',s['before'][n]),('after',c['files'][n])]:
  p=host(row['path']);dest=p.with_name(label+'-events514-closeout.json');assert not dest.exists()
  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL,timeout=60)
  parsed[phase]=read(dest)['records']
 boundary=max((x['record'] for x in parsed['before']),default=0);new=[x for x in parsed['after'] if x['record']>boundary]
 delta=sum(x['source']=='EventLog' and x['event_id']==6006 for x in parsed['after'])-sum(x['source']=='EventLog' and x['event_id']==6006 for x in parsed['before'])
 events[label]=dict(new_records=new,normal_shutdown_delta=delta,byte_identical_before_after=c['files'][n]['sha256']==s['before'][n]['sha256'],scope='Validated records; active-ring completeness not proved')
remote=s['remote'];entry=c['files'][remote+'/entry.bin'];negatives=0
if entry:
 b=host(entry['path']).read_bytes();decode(b)
 for i in range(len(b)):
  d=bytearray(b);d[i]^=1
  try:decode(bytes(d))
  except ValueError:negatives+=1
  else:raise AssertionError('mutated receipt accepted at '+str(i))
capsule=Path('/mnt/c/xwn514/frozen001');assert not capsule.exists();capsule.mkdir();archived=[]
for j,(n,h) in enumerate(sorted(pkg['dependencies'].items())):
 p=host(n);assert sha(p)==h;dest=capsule/f'{j:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived.append(dict(original=n,path=str(dest),sha256=h))
for row in pkg['files'].values():assert sha(host(row['path']))==row['sha256']
supervisors={a:read(K/f'supervisor-{a}.json') for a in ['stage','launch','observe','collect']}
assert all(v['closed'] for v in supervisors.values())
r=dict(closed=True,physical_launches=1,entry=c['entry'],receipt_mutations_rejected=negatives,
 hives=hives,events=events,all_collected_mutable_files_unchanged=all(c['files'][n]['unchanged'] for n in s['before']),
 staged_files_unchanged=True,temporary_hook_installed=False,original_launcher_startup_and_720p_unchanged=True,console_C_accessed=False,
 historical_preparation_receipts_absent=all(c['files'][remote+'/'+n] is None for n in ['report.bin','refusal.bin','handoff.bin','context.bin','witness.bin']),
 physical_LED_observation='unknown pending user report',actual_physical_kernel_API_statuses='not traced',
 final_flush_close_proved=False,normal_windows_restart_proved=False,windows_boot_proved=False,
 whole_disk_equality='not measured',full_physical_allocation_audit=False,repeat_boot_stability_qualified=False,
 physical_failure_cause_explained=False,gpu_qualified=False,no_next_launch_queued=True,
 archived_inputs=archived,supervisors=supervisors,source_sha256=sha(Path(__file__)),
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('/mnt/c/xwn514').rglob('*') if p.is_file()})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['closed','entry','receipt_mutations_rejected','all_collected_mutable_files_unchanged','historical_preparation_receipts_absent']}))
