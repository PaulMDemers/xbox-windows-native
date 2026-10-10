"""Synthetic parser tests cannot qualify an emulator or physical run."""
import hashlib,json,struct
from pathlib import Path
from probe_trace import analyze
k=Path(__file__).resolve().parent;dest=k/'parser-tests.json';assert not dest.exists()
def trace(rows):
 b=bytearray(4096);b[:16]=b'XWN-VID-TRACE01\n';struct.pack_into('<I',b,16,len(rows))
 for i,row in enumerate(rows):struct.pack_into('<IIII',b,32+16*i,*row)
 return bytes(b)
checks=0
def check(value):
 global checks;checks+=1;assert value
rows=[[21300,1,16384,0],[21301,0x200000,0,0],[21302,15365,4,0],[21303,1,16384,0]]
valid=trace(rows);off=trace([[21300,0,0,0]])
check(analyze(valid,1)['passed']);check(analyze(off,0)['passed'])
check(not analyze(valid,0)['passed']);check(not analyze(off,1)['passed'])
for i in range(4):
 check(not analyze(trace(rows[:i]+rows[i+1:]),1)['passed'])
 check(not analyze(trace(rows+[rows[i]]),1)['passed'])
for row in range(4):
 for col in range(4):
  p=[list(x) for x in rows];p[row][col]^=1
  check(not analyze(trace(p),1)['passed'])
for address in [0,0xfffff,0x100001,0x03bfc001,0x03c00000,0xffffffff]:
 p=[list(x) for x in rows];p[1][1]=address;check(not analyze(trace(p),1)['passed'])
for address in [0x100000,0x03bfc000]:
 p=[list(x) for x in rows];p[1][1]=address;check(analyze(trace(p),1)['passed'])
for index,value in [(16,255),(20,1),(24,1),(28,1)]:
 b=bytearray(valid);struct.pack_into('<I',b,index,value);check(not analyze(b,1)['passed'])
for b in [valid[:-1],valid+b'\0',b'\0'*4096,trace([])]:check(not analyze(b,1)['passed'])
check(not analyze(valid,2)['passed'])
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 parser_sha256=hashlib.sha256((k/'probe_trace.py').read_bytes()).hexdigest(),synthetic=True,guest_launch=False,physical_access=False),indent=2)+'\n')
print('Fail-closed trace parser checks:',checks)
