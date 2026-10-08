"""Host protocol mutation checks, not guest evidence."""
import hashlib,json
from pathlib import Path
from protocol import validate_log,fnv,expected_bytes
k=Path(__file__).resolve().parent;dest=k/'oracle-tests.json';assert not dest.exists();rows=[]
def add(n,*v):rows.append(n+' '+' '.join(map(str,v)))
def shot(i):
 add('SHOT',i,12288,0);h=fnv(expected_bytes(i));add('DIGEST',h,h,49152);add('DRIVER',109,1024,576);add('COHERENCE',0,1,0);add('SHOT_RELEASE',i,1,1)
add('ATTEMPT_ONCE',126,3,110592);add('INSTALL_IDLE_START',0,0,0)
for i in range(3):
 add('ABSENT_BEFORE',i,2,0);shot(i*3);add('CREATED',i,0x100+i,0);add('ATTACHED',i,1,0);add('SWITCHED',i,1,0);shot(i*3+1);add('RESTORED',i,1,1);add('CLOSED',i,1,0);add('ABSENT_AFTER',i,2,0);shot(i*3+2);add('CYCLE_COMPLETE',i,3,0)
for n in ['INPUT_RESTORED','INPUT_CLOSED','CLASS_CLOSED']:add(n,1,0,0)
add('COMPLETE',0,3,110592);add('INSTALL_IDLE_END',0,0,0);add('NORMAL_RESTART_REQUEST',0,0,0)
data=('\r\n'.join(rows)+'\r\n').encode();assert validate_log(data)['passed'];tests=[]
for old,new in [('SWITCHED 1 1 0','SWITCHED 1 0 5'),('RESTORED 1 1 1','RESTORED 1 1 0'),('CLOSED 1 1 0','CLOSED 1 0 170'),('ABSENT_AFTER 1 2 0','ABSENT_AFTER 1 0 0'),('SHOT 4 12288 0','SHOT 4 12288 1'),('SHOT_RELEASE 4 1 1','SHOT_RELEASE 4 1 0'),('COHERENCE 0 1 0','COHERENCE 0 0 0'),('COMPLETE 0 3 110592','COMPLETE 1 3 110592')]:
 assert old.encode() in data;assert not validate_log(data.replace(old.encode(),new.encode(),1))['passed'];tests.append(old)
assert not validate_log(data.split(b'NORMAL_RESTART_REQUEST')[0])['passed'];tests.append('missing shutdown')
assert not validate_log(data+rows[-1].encode())['passed'];tests.append('extra shutdown')
b=bytearray(expected_bytes(4));b[123]^=1;assert bytes(b)!=expected_bytes(4) and fnv(b)!=fnv(expected_bytes(4));tests.append('RGB mutation')
r=dict(passed=True,synthetic_host_protocol_only=True,guest_qualified=False,rejected=tests,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-oracle.py']})
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('11 meaningful protocol/pixel mutations rejected')
