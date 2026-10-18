"""Read-only final join of the watched physical refusal and immutable captures."""
import hashlib,json,struct
from pathlib import Path
from decode import decode
from refusal_decode import decode_refusal
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
s=read(K/'stage001.json');c=read(K/'collection001.json');a=read(K/'cold-review002.json')
assert s['completed'] and c['completed'] and a['selected_cold_audit_passed']
assert not c['remote_writes'] and not c['console_C_accessed']
for n,v in s['before'].items():assert c['files'][n]['unchanged'],n
for n in s['staged']:assert c['files'][n]['unchanged'],n
assert all(not v['new_records'] and v['normal_shutdown_delta']==0 for v in a['events'].values())
root='/E/Applications/XWNBoot466a/'
p=Path(c['files'][root+'report.bin']['path']).read_bytes();r=Path(c['files'][root+'refusal.bin']['path']).read_bytes()
assert decode(p)==c['decoded']==a['primary']
ref=decode_refusal(r);assert ref==c['refusal_decoded']==a['refusal']
assert ref['reason']==12 and ref['primary_return_status']==5 and ref['close_state']==2
observed=read(K/'observation001.json')['report'];assert Path(observed['path']).read_bytes()==p
words=list(struct.unpack('<24I',r));negative=0
for i,v in [(4,13),(5,0),(5,1),(5,8),(6,0x103),(8,0),(9,1),(11,0),(12,0),(13,0),(16,0x400)]:
 q=words[:];q[i]=v
 try:decode_refusal(struct.pack('<24I',*q))
 except ValueError:negative+=1
 else:raise AssertionError(('bad refusal accepted',i))
private={str(f):dict(bytes=f.stat().st_size,sha256=sha(f.read_bytes())) for f in Path('C:/xwn467/physical001').rglob('*') if f.is_file()}
result=dict(closed=True,physical_boot_passed=False,deliberate_new_marker_refusal=True,
 first_marker_result=5,raw_SMBus_status_unknown=True,second_marker_not_reached_by_refusal_path=True,
 old_intermittent_failure_explained=False,unchanged_before_files=len(s['before']),unchanged_staged_files=len(s['staged']),
 selected_cold_audit_passed=True,hives_clean=5,new_windows_events=0,full_FATX_scan=False,
 actual_refusal_negative_controls=a['actual_refusal_negative_controls']+negative,
 console_C_accessed=False,physical_launches=1,no_repeat_queued=True,private_files=private,
 all_owned_subprocesses_closed=True,closed_sessions=[43710,4824,17949],
 preserved_failures=['cold-review001-failure.json'],next='new refusal-only full marker record; no gate relaxation')
out.write_text(json.dumps(result,indent=2)+'\n')
