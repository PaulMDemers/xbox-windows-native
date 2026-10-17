"""Verify actual physical preparation report and selected cold files; no handoff claim."""
import hashlib,json,struct,sys,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
from decode import decode
def path(s):
 return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'actual-review002.json';assert not out.exists()
c=json.loads((K/'collection001.json').read_text());s=json.loads((K/'stage001.json').read_text());o=json.loads((K/'observation001.json').read_text())
assert c['completed'] and s['completed'] and o['completed'] and not c['remote_writes']
count=0
for group in [s['before'],c['files']]+([{'report':o['report']}] if 'report' in o else []):
 for n,v in group.items():
  assert v and sha(path(v['path']))==v['sha256'] and path(v['path']).stat().st_size==v['bytes'];count+=1
for n,v in c['files'].items():
 if n in ['/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd','/E/Applications/XWNEBoot/default.xbe'] or n in s['staged']:assert v['unchanged']
for p,h in s['source_pins'].items():assert sha(path(p))==h
n='/E/Applications/XWNBoot461a/report.bin';b=path(c['files'][n]['path']).read_bytes()
d=decode(b)
if 'report' in o:assert b==path(o['report']['path']).read_bytes() and d==o['decoded']
assert d==c['decoded'] and d['preparation_verified']
assert d['paging_transition_executed'] is None and not d['final_flush_close_postlog_check_proved']
rejected=0
def refuse(data):
 global rejected
 try:decode(data)
 except ValueError:rejected+=1;return
 raise AssertionError('Accepted malformed actual report')
for length in range(len(b)):refuse(b[:length])
refuse(b+b'\0')
for at in [0,4,8,12,20,48,60,64,68,72,76,80,108,116,120,124,128,132,144,148,152,156,160,164,168,172]:
 for v in [0,0xffffffff,0x12345678]:
  x=bytearray(b);struct.pack_into('<I',x,at,v)
  if x!=b:refuse(x)
for at,v in [(24,0),(28,0),(32,0),(36,0),(40,0x103),(44,0),(52,0x400),(56,0),(84,0),(84,1),(88,0),(92,0),(96,0),(100,0),(104,0),(112,0x400)]:
 x=bytearray(b);struct.pack_into('<I',x,at,v);refuse(x)
hives={}
for name in ['system','software','sam','security','default']:
 v=audit(path(c['files']['/E/winnt/system32/config/'+name]['path']))
 assert v['clean'] and v['header_valid'] and v['independent_raw_values_agree'];hives[name]=v
old=json.loads((K.parent/'launch-handoff410/collection001.json').read_text())['decoded']
fields=['kernel_virtual','kernel_physical','loader_virtual','loader_physical','virtual_alias','alias_backing_physical','low_jump_target','high_jump_target']
events={}
for name in ['sysevent.evt','appevent.evt']:
 n='/E/winnt/system32/config/'+name;rows={}
 for phase,record in [('before',s['before'][n]),('after',c['files'][n])]:
  p=path(record['path']);dest=p.with_name(name+'-review461.json');assert not dest.exists()
  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
  rows[phase]=json.loads(dest.read_text())['records']
 boundary=max((e['record'] for e in rows['before']),default=0)
 events[name]=dict(new_records=[{k:e[k] for k in ['record','source','event_id','type','generated_unix']} for e in rows['after'] if e['record']>boundary],normal_shutdown_delta=sum(e['source']=='EventLog' and e['event_id']==6006 for e in rows['after'])-sum(e['source']=='EventLog' and e['event_id']==6006 for e in rows['before']))
user=json.loads((K/'user-observation001.json').read_text());assert user['desktop_observed_by_user']
result=dict(passed=True,scope='Physical copy preparation plus separate user desktop observation and cold event audit; not D3D or boot fix',
 private_captures_rehashed=count,actual_report_negative_controls=rejected,decoded=d,hives=hives,
 protected_boot_files_unchanged=True,events=events,normal_shutdown_record_delta=events['sysevent.evt']['normal_shutdown_delta'],desktop_observed_by_user=True,
 allocation_tuple_matches_historical410=all(d[k]==old[k] for k in fields),
 historical410_retrospectively_requalified=False,full_FATX_allocation_audit=False,
 all_owned_processes_closed=True,console_C_accessed=False,source_pins_verified=len(s['source_pins']),
 report_sha256=hashlib.sha256(b).hexdigest(),user_visual_observation_pending=False)
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['passed','private_captures_rehashed','actual_report_negative_controls','allocation_tuple_matches_historical410']}))
