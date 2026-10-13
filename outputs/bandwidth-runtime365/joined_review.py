import json,hashlib,struct
from pathlib import Path
from joined_identity import join
K=Path(__file__).resolve().parent;out=K/'candidate001';dest=out/'joined-review.json';assert not dest.exists();root=out/'artifacts'
b=(root/'sample0/bandwidth.bin').read_bytes();a=(root/'sample0/memory-after.bin').read_bytes();r=join(b,a)
w=list(struct.unpack('<133392I',b));checks=0
for slot in range(4):
 for offset in (4,5,6,12):
  x=w.copy();x[16+slot*33344+offset]+=4096
  try:join(struct.pack('<133392I',*x),a)
  except ValueError:checks+=1
  else:raise AssertionError((slot,offset))
r.update(actual_mutations_rejected=checks,bandwidth_sha256=hashlib.sha256(b).hexdigest(),memory_sha256=hashlib.sha256(a).hexdigest(),inputs={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['joined_identity.py','joined_review.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print('Additional actual identity join passed',checks)
