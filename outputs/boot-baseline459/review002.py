"""Review closed cold-start observation, without claiming a boot stage."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'review002.json';assert not out.exists()
c=json.loads((K/'capture002.json').read_text());a=json.loads((K/'capture001.json').read_text())
old=json.loads((K.parent/'d3d-direct458/physical001-collection.json').read_text())
assert c['completed'] and c['no_test_hook'] and not c['remote_writes'] and not c['host_launch_sent']
r=dict(passed=True,files={},hives={},windows_boot_proved=False,normal_shutdown_proved=False,console_C_accessed=False)
for n,v in c['files'].items():
 b=path(v['path']).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256']
 prior=a['files'].get(n) or old['files'].get(n);assert prior and prior['sha256']==v['sha256'],n
 r['files'][n]=dict(bytes=len(b),sha256=v['sha256'],unchanged=True)
for name in ['system','software','sam','security','default']:
 v=audit(path(c['files']['/E/winnt/system32/config/'+name]['path']))
 assert v['clean'] and v['header_valid'] and v['independent_raw_values_agree'];r['hives'][name]=v
r.update(user_report=c['user_report'],power_off_duration_independently_verified=False,
 events_byte_identical=True,video_trace_unchanged=True,full_FATX_allocation_audit=False,
 failure_stage_unknown=True,remote_writes=[],all_owned_processes_closed=True)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,exact_files=len(r['files']),clean_hives=len(r['hives']))))
