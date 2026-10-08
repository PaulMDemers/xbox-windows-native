"""Independent rectangle union and exact image checks before any guest launch."""
import hashlib,json,struct
from pathlib import Path
from protocol import rectangles,points,expected_bytes
k=Path(__file__).resolve().parent;dest=k/'oracle-tests.json';assert not dest.exists()
counts=[512,896,368,0,960,512];checks=0
for n in range(18):
 p=points(n);assert len(p)==counts[n%6];checks+=1
 raw=expected_bytes(n);assert len(raw)==393216;checks+=1
 actual=struct.unpack('<98304I',raw)
 for y in range(256):
  for x in range(384):
   hit=any(l<=x<r and t<=y<b for l,t,r,b in rectangles(n%6))
   want=0x2bc757 if hit else ((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255)
   assert actual[y*384+x]==want
 checks+=1
 if n>=6:assert raw==expected_bytes(n%6);checks+=1
record=dict(passed=True,host_only=True,checks=checks,changed_pixels=counts,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-oracle.py']})
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(record)
