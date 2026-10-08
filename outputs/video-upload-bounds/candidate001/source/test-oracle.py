"""Boundary/overlap pixel and 64-bit counter protocol tests; no guest evidence."""
import hashlib,json,struct
from pathlib import Path
from protocol import expected_bytes,fnv,validate_log
k=Path(__file__).resolve().parent
def base(x,y):return ((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255)
checks=0
for kind in range(6):
 data=expected_bytes(kind);assert len(data)==393216
 for repeat in [6,12]:assert data==expected_bytes(kind+repeat);checks+=1
 for x,y in [(0,0),(19,19),(383,255)]:assert struct.unpack_from('<I',data,(y*384+x)*4)[0]==base(x,y);checks+=1
for kind,points in [(0,[(20,20,0x2bc757),(51,35,0x2bc757),(52,35,base(52,35))]),(1,[(20,20,0xdd2597),(51,20,0xdd2597),(52,20,base(52,20))]),(2,[(20,20,0xdd2597),(51,20,0xdd2597),(20,21,base(20,21))]),(3,[(40,40,base(20,20)),(167,135,base(147,115)),(168,135,base(168,135))]),(4,[(20,20,0x2bc757),(215,175,0x2bc757),(100,100,base(100,100))]),(5,[(20,20,0x2bc757),(51,35,0x2bc757),(52,35,base(52,35))])]:
 for x,y,want in points:assert struct.unpack_from('<I',expected_bytes(kind),(y*384+x)*4)[0]==want;checks+=1
lines=[]
def add(s,*v):lines.append(s+' '+' '.join(map(str,v)))
add('ATTEMPT_ONCE',128,18,98304);add('INSTALL_IDLE_START',0,0,0);add('DRIVER_REVISION_GEOMETRY',109,1024,576)
counter={i:0 for i in range(2,19)};counter[17]=0xfffffff0
for n in range(18):
 add('CLIP_TYPE_LEFT_TOP',2,0,0);add('CLIP_RIGHT_BOTTOM',1024,576,n)
 add('CASE_API',n,1,1);add('PIXELS_BAD_CHANGED',98304,0,[512,32,32,12288,512,512][n%6]);digest=fnv(expected_bytes(n));add('REFERENCE_HASH_BYTES',digest,393216,digest);add('SOURCE_HASH_PAIR',1,1,0)
 after=counter.copy();after[2]+=1;after[16]+=1;total=(counter[18]<<32|counter[17])+2048;after[17]=total&0xffffffff;after[18]=total>>32
 for i in range(2,19):add('QUIET_COUNTER',i,counter[i],counter[i]);add('REFERENCE_COUNTER',i,counter[i],counter[i]);add('DRAW_COUNTER',i,counter[i],after[i])
 counter=after;add('COHERENCE_ACTIVE',0,1,0)
add('RELEASED',1,0,0);add('COMPLETE',0,18,18*98304);add('INSTALL_IDLE_END',0,0,0);add('NORMAL_RESTART_REQUEST',0,0,0)
raw=('\n'.join(lines)+'\n').encode();valid=validate_log(raw);assert valid['passed'] and valid['profile_attribution_passed'] and all(v['upload_bytes']==2048 for v in valid['cases']);checks+=1
mutations={
 'small_clip':raw.replace(b'CLIP_RIGHT_BOTTOM 1024 576 0',b'CLIP_RIGHT_BOTTOM 100 576 0',1),
 'complex_clip':raw.replace(b'CLIP_TYPE_LEFT_TOP 2 0 0',b'CLIP_TYPE_LEFT_TOP 3 0 0',1),
 'pixels':raw.replace(b'PIXELS_BAD_CHANGED 98304 0',b'PIXELS_BAD_CHANGED 98304 1',1),
 'coherence':raw.replace(b'COHERENCE_ACTIVE 0 1 0',b'COHERENCE_ACTIVE 1 1 0',1),
 'api':raw.replace(b'CASE_API 0 1 1',b'CASE_API 0 1 0',1),
 'missing_end':raw.rsplit(b'NORMAL_RESTART_REQUEST',1)[0],
 'extra':raw+b'EXTRA 0 0 0\n',
 'quiet':raw.replace(b'QUIET_COUNTER 3 0 0',b'QUIET_COUNTER 3 1 0',1),
 'wrap_without_high':raw.replace(b'DRAW_COUNTER 18 0 1',b'DRAW_COUNTER 18 0 0',1),
 'repeat':raw.replace(b'DRAW_COUNTER 2 0 1',b'DRAW_COUNTER 2 0 2',1),
 'saturated':raw.replace(b'DRAW_COUNTER 2 0 1',b'DRAW_COUNTER 2 0 4294967295',1)}
for name,bad in mutations.items():
 assert bad!=raw
 result=validate_log(bad);assert not (result['passed'] and result['profile_attribution_passed']),name
 checks+=1
dest=k/'oracle-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,host_only=True,checks=checks,mutations=list(mutations),pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-oracle.py']}),indent=2)+'\n',encoding='utf-8')
print('Host oracle/protocol checks passed:',checks)
