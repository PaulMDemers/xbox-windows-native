"""Check cached raw event timestamps; record order need not be time order."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'event-timestamps002.json';assert not out.exists()
rows=[]
for phase in [0,1]:
 p=Path(f'C:/xwn614/pc001/cold{phase}-002');raw=p/'files/WINNT/system32/config/SysEvent.Evt';data=raw.read_bytes()
 decoded=json.loads((p/'system-events.json').read_text())['records'];verified=[]
 for r in decoded:
  offset=r['offset'];length,signature,number,tgen,twrite,event=struct.unpack_from('<6I',data,offset)
  assert length>=56 and offset+length<=len(data) and signature==0x654c664c
  assert struct.unpack_from('<I',data,offset+length-4)[0]==length
  assert (number,tgen,twrite,event&65535)==(r['record'],r['generated_unix'],r['written_unix'],r['event_id'])
  i=offset+56;name=bytearray()
  while data[i:i+2]!=b'\0\0':
   assert i+2<offset+length;name.extend(data[i:i+2]);i+=2
  assert name.decode('utf-16le')==r['source']
  verified.append(dict(record=number,source=r['source'],event_id=event&65535,generated_unix=tgen,written_unix=twrite))
 rows.append(dict(phase=phase,raw_sha256=hashlib.sha256(data).hexdigest(),records=verified))
boundary=max(r['record'] for r in rows[0]['records']);new=[r for r in rows[1]['records'] if r['record']>boundary]
stop=[r for r in new if r['source']=='EventLog' and r['event_id']==6006]
start=[r for r in new if r['source']=='EventLog' and r['event_id'] in [6005,6009]]
assert len(stop)==1 and len(start)==2 and all(r['generated_unix']<stop[0]['generated_unix'] for r in start)
out.write_text(json.dumps(dict(passed=True,rows=rows,new_events=new,scope='Cached raw signature/length/source/timestamps agree. Shutdown time follows both startup times in the decoded rows; do not sort chronology by record number. Not clock-performance qualification.'),indent=2)+'\n')
print('604 raw event chronology agrees with normal restart')
