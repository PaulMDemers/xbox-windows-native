import hashlib,json,struct
from pathlib import Path
from protocol import *
k=Path(__file__).resolve().parent
source=[base(x+17,y+23) for y in range(80) for x in range(128)]
for x in range(8,28):source[24*128+x]=0xffffff
raw=struct.pack('<10240I',*source);meta=[96,16,fnv(raw)];assert source_valid(raw,meta)
checks=1
for n in range(18):
 b=expected_bytes(n,raw);pixels=struct.unpack('<98304I',b);l,t=POSITIONS[n%6]
 for x,y in [(0,0),(383,255),(144,56),(239,199),(240,200),(20,20),(120,70),(96,24)]:
  expected=0x462daa if 144<=x<240 and 56<=y<200 else source[(y-t)*128+x-l] if l<=x<l+128 and t<=y<t+80 else base(x,y)
  assert pixels[y*384+x]==expected;checks+=1
 assert b==expected_bytes(n%6,raw);checks+=1
for offset,value in [(0,0),(24*128+8,0x123456),(79*128+127,0xffffff)]:
 bad=source.copy();bad[offset]=value;data=struct.pack('<10240I',*bad);assert not source_valid(data,[96,16,fnv(data)]);checks+=1
assert not source_valid(raw,[]) and not source_valid(raw[:-1],meta);checks+=2
for bad in [None,b'',b'ATTEMPT_ONCE 136 18 98304\n',b'garbage']:
 assert not validate_log(bad)['passed'];checks+=1
pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['probe.c','protocol.py','test-oracle.py']}
(k/'oracle-tests.json').write_text(json.dumps(dict(passed=True,checks=checks,pins=pins,limits='Composition and malformed source/log checks; actual NT5 font and USER behavior require guest runs.'),indent=2)+'\n')
print(checks,'oracle checks passed')
