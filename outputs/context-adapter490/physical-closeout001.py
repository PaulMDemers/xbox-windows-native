"""Cold physical closure: distinguish register observation, Windows work and restart."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'physical-final001.json';assert not out.exists()
c=read(K/'physical001-collection.json');s=read(K/'physical001-stage.json');pkg=read(K/'package001.json');context=read(K/'actual-context001.json')
assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and s['completed']
for n,row in c['files'].items():
 if row:assert sha(host(row['path']))==row['sha256'] and host(row['path']).stat().st_size==row['bytes']
for n in s['staged']:assert c['files'][n]['unchanged']
for n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert c['files'][n]['unchanged']
assert c['remote_writes']==[dict(action='rename-owned-hook',source='/E/documents and settings/all users/start menu/programs/startup/xwn490.cmd',destination='/E/xwn490-kit/startup-used.cmd')]
hives={};events={};allnew=[]
for name in ['system','software','sam','security','default']:
 n='/E/winnt/system32/config/'+name
 hives[name]={label:audit(host(row['path'])) for label,row in [('before',s['before'][n]),('after',c['files'][n])]}
 assert all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in hives[name].values())
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 n='/E/winnt/system32/config/'+name;parsed={}
 for phase,row in [('before',s['before'][n]),('after',c['files'][n])]:
  p=host(row['path']);dest=p.with_name(label+'-events490-closeout.json');assert not dest.exists()
  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL,timeout=60)
  parsed[phase]=read(dest)['records']
 boundary=max((x['record'] for x in parsed['before']),default=0);new=[x for x in parsed['after'] if x['record']>boundary]
 delta=sum(x['source']=='EventLog' and x['event_id']==6006 for x in parsed['after'])-sum(x['source']=='EventLog' and x['event_id']==6006 for x in parsed['before'])
 events[label]=dict(new_records=new,normal_shutdown_delta=delta,byte_identical_before_after=c['files'][n]['sha256']==s['before'][n]['sha256'],scope='Validated records; active-ring completeness not proved')
 allnew.extend(dict(log=label,**x) for x in new)
runtime=None;modules=None;controls=None
if (K/'runtime-review001.json').exists():
 runtime=read(K/'runtime-review001.json')
 if runtime['all_allowed_cases_passed']:
  modules=read(K/'module-review001.json');controls=read(K/'actual-controls001.json');assert modules['passed'] and controls['passed']
capsule=Path('/mnt/c/xwn490/frozen001');assert not capsule.exists();capsule.mkdir();archived=[]
for j,(n,h) in enumerate(sorted(pkg['dependencies'].items())):
 p=host(n);assert sha(p)==h;dest=capsule/f'{j:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived.append(dict(original=n,path=str(dest),sha256=h))
samplepass=bool(runtime and runtime['all_allowed_cases_passed'] and modules and controls)
normal=bool(samplepass and runtime['runner']['restart_request']=='1' and events['system']['normal_shutdown_delta']==1)
r=dict(closed=True,physical_launches=1,register_observation_passed=context['passed'],context=context,
 arithmetic_characterization_passed=samplepass,normal_windows_restart_supported=normal,
 strict_system_qualification=normal and not any(x['type'] in (1,2) or x['source']=='Application Popup' for x in allnew),
 result_namespace_present='result_directory' in c,hives=hives,events=events,
 all_collected_mutable_files_unchanged=all(c['files'][n]['unchanged'] for n in s['before']),
 temporary_hook_removed=True,original_launcher_startup_and_720p_unchanged=True,console_C_accessed=False,
 runtime_review=runtime,module_review=modules,actual_arithmetic_controls=controls,
 archived_inputs=archived,repeat_boot_stability_qualified=False,physical_failure_cause_explained=False,
 page_walk_validated=False,gpu_qualified=False,game_compatibility_qualified=False,exact_ideal_alpha_qualified=False,
 no_next_launch_queued=True,source_sha256=sha(Path(__file__)),
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('/mnt/c/xwn490').rglob('*') if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['closed','register_observation_passed','arithmetic_characterization_passed','normal_windows_restart_supported','strict_system_qualification','result_namespace_present']}))
