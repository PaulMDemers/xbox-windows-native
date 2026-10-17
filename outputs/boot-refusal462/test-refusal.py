import hashlib,json,struct
from pathlib import Path
from refusal_decode import decode_refusal
K=Path(__file__).resolve().parent;P=Path('E:/xwn462/host001');out=K/'refusal-tests001.json';assert not out.exists()
rejected=0;accepted=[]
def refuse(b):
 global rejected
 try:decode_refusal(b)
 except ValueError:rejected+=1;return
 raise AssertionError('Accepted malformed refusal')
for i in range(55):
 b=(P/f'refusal{i:02d}.bin').read_bytes()
 if len(b)!=96:refuse(b);continue
 r=decode_refusal(b);accepted.append(dict(case=i,reason=r['reason']))
 assert r['deliberate_wrapper_refusal'] and not r['paging_transition_proved']
 for at,value in [(0,0),(4,0),(8,0),(12,0),(16,0),(16,12),(36,3),(40,4),(44,2),(48,2),(52,2),(56,2),(60,2),(76,1),(80,0),(84,0),(88,0),(92,0)]:
  m=bytearray(b);struct.pack_into('<I',m,at,value);refuse(m)
b=(P/'refusal32.bin').read_bytes()
for length in range(96):refuse(b[:length])
refuse(b+b'\0')
for at,value in [(20,0),(24,1),(32,0),(36,0),(44,0),(48,0),(68,1),(72,0)]:
 m=bytearray(b);struct.pack_into('<I',m,at,value);refuse(m)
files=[K/'refusal_decode.py',K/'test-refusal.py']+list(P.glob('refusal*.bin'))
r=dict(passed=True,host_cases=55,accepted_complete_refusals=accepted,malformed_records_rejected=rejected,
 fallback_failure_bytes_not_proof_of_success=True,physical_access=False,
 files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,complete_refusals=len(accepted),negatives=rejected)))
