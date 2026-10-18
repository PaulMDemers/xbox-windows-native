"""Join actual primary/refusal records with selected cold-file/event evidence."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
from decode import decode
from refusal_decode import decode_refusal
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'cold-review001.json';assert not out.exists()
s=json.loads((K/'physical001-stage.json').read_text());c=json.loads((K/'physical001-collection.json').read_text())
assert s['completed'] and c['completed'] and c['hook_removed']
files=0
for group in [s['before'],c['files']]:
 for n,v in group.items():
  if v is None:assert n.endswith(('/report.bin','/refusal.bin'));continue
  p=path(v['path']);assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'];files+=1
for p,h in s['source_pins'].items():assert sha(path(p))==h,p
for n,v in c['files'].items():
 if n in s['staged'] or n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert v['unchanged']
remote='/E/Applications/XWNBoot475a';primary=c['files'][remote+'/report.bin'];ref=c['files'][remote+'/refusal.bin']
r=dict(scope='Diagnostic observation plus selected cold audit; not a boot fix',private_captures_verified=files,console_C_accessed=False,
 primary_present=primary is not None,refusal_present=ref is not None,protected_boot_files_unchanged=True,
 full_FATX_allocation_audit=False,D3D_test=False,root_cause_of_original_launcher_established=False)
if primary:
 b=path(primary['path']).read_bytes()
 try:r['primary']=decode(b)
 except ValueError as e:r['primary_parse_error']=str(e)
if ref:
 b=path(ref['path']).read_bytes()
 try:r['refusal']=decode_refusal(b)
 except ValueError as e:r['refusal_parse_error']=str(e)
 if 'refusal' in r and 'primary' in r:
  q=struct.unpack('<48I',b);a=struct.unpack('<44I',path(primary['path']).read_bytes())
  assert q[10:18]==(a[5],a[30],a[31],a[24],a[25],a[26],a[28],a[29]);r['paired_first_state_exact']=True
 if 'refusal' in r:
  negatives=0
  for offset in [0,4,8,12,16,36,40,44,48,52,56,60,76,80,84,88,92,96,100,104,108,112,116,152,156,160,164,168,172,176,180,184,188]:
   m=bytearray(b);struct.pack_into('<I',m,offset,0xffffffff)
   try:decode_refusal(m)
   except ValueError:negatives+=1;continue
   raise AssertionError('Malformed actual refusal accepted')
  r['actual_refusal_negative_controls']=negatives
r['hives']={}
for name in ['system','software','sam','security','default']:
 v=audit(path(c['files']['/E/winnt/system32/config/'+name]['path']))
 assert v['clean'] and v['header_valid'] and v['independent_raw_values_agree'];r['hives'][name]=v
r['events']={}
for name in ['sysevent.evt','appevent.evt']:
 n='/E/winnt/system32/config/'+name;rows={}
 for phase,v in [('before',s['before'][n]),('after',c['files'][n])]:
  p=path(v['path']);dest=p.with_name(name+'-review475.json');assert not dest.exists()
  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
  rows[phase]=json.loads(dest.read_text())['records']
 boundary=max((x['record'] for x in rows['before']),default=0)
 r['events'][name]=dict(new_records=[{k:x[k] for k in ['record','source','event_id','type','generated_unix']} for x in rows['after'] if x['record']>boundary],normal_shutdown_delta=sum(x['source']=='EventLog' and x['event_id']==6006 for x in rows['after'])-sum(x['source']=='EventLog' and x['event_id']==6006 for x in rows['before']))
r.update(selected_cold_audit_passed=True,missing_refusal_does_not_prove_handoff=True,all_owned_runtime_processes_closed=True)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r.get(k) for k in ['selected_cold_audit_passed','primary','refusal','primary_parse_error','refusal_parse_error','events']}))
