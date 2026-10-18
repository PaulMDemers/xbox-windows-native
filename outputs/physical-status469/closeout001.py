"""Join immutable physical raw status, primary preparation and cold evidence."""
import hashlib,json,struct
from pathlib import Path
from refusal_decode import decode_refusal
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(K/'stage001.json');c=read(K/'collection001.json');a=read(K/'cold-review001.json')
assert s['completed'] and c['completed'] and a['selected_cold_audit_passed']
assert not c['remote_writes'] and not c['console_C_accessed']
for n in list(s['before'])+list(s['staged']):assert c['files'][n]['unchanged'],n
assert all(not v['new_records'] and v['normal_shutdown_delta']==0 for v in a['events'].values())
data=Path(c['files']['/E/Applications/XWNBoot468a/refusal.bin']['path']).read_bytes()
d=decode_refusal(data);assert d==c['refusal_decoded']==a['refusal']
m=d['marker'];assert m['last_status']==0x808 and m['completed']==0 and m['started_mask']==1
assert m['transaction']==0 and m['polls']==2 and m['io_writes']==4 and m['acknowledgments']==0
rejected=0
for n in range(192):
 try:decode_refusal(data[:n])
 except ValueError:rejected+=1
 else:raise AssertionError('truncation accepted')
for value in [0,0x800,0x10,0x810]:
 q=bytearray(data);struct.pack_into('<I',q,112,value);struct.pack_into('<I',q,144,value)
 try:decode_refusal(q)
 except ValueError:rejected+=1
 else:raise AssertionError('Nonerror status accepted as original predicate failure')
source=read(K/'status-source-review.json')
for v in source['sources']:assert sha(Path(v['private_file']))==v['sha256']
r=dict(closed=True,physical_launches=1,raw_marker_captured=True,raw_status='0x0808',
 first_marker_result=5,first_transaction_started=True,completed_transactions=0,
 refusal_before_original_loader=True,second_marker_not_reached=True,
 original_boot_failure_explained=False,diagnostic_bug='host-busy bit3 wrongly rejected',
 new_windows_events=0,hives_clean=5,selected_cold_audit_passed=True,full_FATX_scan=False,
 unchanged_before_files=len(s['before']),unchanged_staged_files=len(s['staged']),
 actual_refusal_negative_controls=rejected+a['actual_refusal_negative_controls'],
 console_C_accessed=False,normal_windows_shutdown=False,new_user_screen_observation=False,
 no_repeat_queued=True,all_owned_controller_processes_closed=True,
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn469').rglob('*') if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='private_files'}))
