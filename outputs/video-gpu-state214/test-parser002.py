"""Fail-closed synthetic lifecycle/offset/payload corruption coverage."""
import hashlib,json,struct
from pathlib import Path
from snapshot_trace import analyze,OFFSETS
k=Path(__file__).resolve().parent;dest=k/'parser-tests.json';assert not dest.exists();checks=0
def check(value):
 global checks
 checks+=1;assert value
def packet(rows):
 data=bytearray(4096);data[:16]=b'XWN-VID-TRACE01\n';struct.pack_into('<IIII',data,16,len(rows),0,0,0)
 for i,row in enumerate(rows):struct.pack_into('<IIII',data,32+16*i,*row)
 return data
control=[[21400,0,0,0],[21400,1,0,0]];rows=[]
for phase in [0,1]:
 values={offset:offset^0xa5 for offset in OFFSETS};values[0]=0x02a000a3;values[0x600800]=0x03c00000;sum=0
 rows.append([21400,phase,1,0])
 for offset in OFFSETS:rows.append([21401,phase,offset,values[offset]]);sum^=offset^values[offset]
 rows.append([21402,phase,22,sum])
check(analyze(packet(control),0)['passed']);check(not analyze(packet(control),1)['passed'])
check(analyze(packet(rows),1)['passed']);check(not analyze(packet(rows),0)['passed'])
for i in range(len(rows)):
 check(not analyze(packet(rows[:i]+rows[i+1:]),1)['passed'])
 for field in range(4):
  changed=[v[:] for v in rows];changed[i][field]^=1;check(not analyze(packet(changed),1)['passed'])
check(not analyze(packet(rows+[[21403,0,1,0]]),1)['passed'])
check(not analyze(packet(rows+rows[:1]),1)['passed'])
for at in [0,20,24,28]:
 data=packet(rows);data[at]^=1;check(not analyze(data,1)['passed'])
data=packet(rows);struct.pack_into('<I',data,16,255);check(not analyze(data,1)['passed'])
check(analyze(packet([[900,1,2,3]]+rows),1)['passed'])
check(not analyze(packet(rows)[:-1],1)['passed']);check(not analyze(packet(rows),2)['passed'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=sha(Path(__file__)),parser_sha256=sha(k/'snapshot_trace.py'),synthetic=True,guest_launch=False,physical_access=False),indent=2)+'\n');print('Snapshot parser checks PASS:',checks)
