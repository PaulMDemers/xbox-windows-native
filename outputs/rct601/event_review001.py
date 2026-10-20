"""Correct the copied6016 predicate from preserved raw EVENTLOGRECORDs."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'event-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for phase in [0,1]:
 p=Path(f'C:/xwn601/pc001/cold{phase}-002');source=p/'files/WINNT/system32/config/SysEvent.Evt'
 data=source.read_bytes();decoded=json.loads((p/'system-events.json').read_text())['records'];verified=[]
 for r in decoded:
  offset=r['offset'];length,signature,number,tgen,twrite,event=struct.unpack_from('<6I',data,offset)
  assert length>=56 and offset+length<=len(data) and signature==0x654c664c
  assert struct.unpack_from('<I',data,offset+length-4)[0]==length
  assert (number,tgen,twrite,event&65535)==(r['record'],r['generated_unix'],r['written_unix'],r['event_id'])
  namebytes=bytearray();i=offset+56
  while data[i:i+2]!=b'\0\0':
   assert i+2<offset+length;namebytes.extend(data[i:i+2]);i+=2
  assert namebytes.decode('utf-16le')==r['source']
  verified.append(dict(record=number,source=r['source'],event_id=event&65535))
 rows.append(dict(phase=phase,raw_sha256=sha(source),decoded_sha256=sha(p/'system-events.json'),records=verified,
                  shutdown_count=sum(r['source']=='EventLog' and r['event_id']==6006 for r in verified)))
boundary=max(r['record'] for r in rows[0]['records'])
new=[r for r in rows[1]['records'] if r['record']>boundary and r['source']=='EventLog' and r['event_id']==6006]
assert rows[1]['shutdown_count']-rows[0]['shutdown_count']==1 and len(new)==1
out.write_text(json.dumps(dict(passed=True,rows=rows,corrected_normal_shutdown_delta=1,new_shutdown_records=new,
 original_audit_summary_preserved=True,cause='Blind test namespace replacement changed the literal6006 to6016 in cold002.py. Raw records and per-record event list are intact. No disk reopen/recollection.',
 other_namespace_artifacts='vm.py default mouse height600 became601 (unused); trace.c bound60000 became60100ms. Actual runtime bound60.1s, exited in under1s after helper start.'),indent=2)+'\n')
print('Raw EVENTLOGRECORDs confirm one new6006; original wrong6016 summary retained')
