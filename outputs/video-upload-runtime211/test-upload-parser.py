"""Synthetic contract tests only; malformed packets must fail closed."""
import copy,hashlib,json
from pathlib import Path
from upload_analysis import analyze
k=Path(__file__).resolve().parent;dest=k/'upload-parser-tests.json';assert not dest.exists()
def make(enabled):
 rows=[];requests=[0]*15;boxes=[0]*15;bs=[0]*15
 for step in range(40):
  for phase in range(4):
   if enabled and phase in [1,2]:
    for i,b in [(1,131072),(2,600)]:requests[i]+=1;boxes[i]+=1;bs[i]+=b
   d=[0x41555758,119,632,enabled,15,0,0,0]+[0]*150
   for i in range(15):
    a=8+i*10;d[a:a+10]=[requests[i],requests[i],0,boxes[i],bs[i]&0xffffffff,bs[i]>>32,0,0,0,0]
   rows.extend([['UPLOAD_WORD_tag_index_value',step*4+phase,j,v] for j,v in enumerate(d)])
  rows.append(['UPLOAD_STEP_exact',step,1,0])
 return rows
log=lambda rows:'\n'.join(' '.join(map(str,r)) for r in rows)+'\n'
rows=make(1);assert analyze(log(rows),1)['passed'] and analyze(log(make(0)),0)['passed']
tests=[]
def reject(name,fn):
 r=copy.deepcopy(rows);fn(r);assert not analyze(log(r),1)['passed'],name;tests.append(name)
for n,idx,val in [('magic',0,0),('abi',1,118),('length',2,628),('mode',3,0),('kinds',4,14),('errors',5,1),('overflow',6,1),('reserved',7,1),('row-reserved',17,1),('range',0,1<<32),('negative',0,-1)]:
 reject(n,lambda r,i=idx,v=val:r[i].__setitem__(3,v))
reject('missing-word',lambda r:r.pop(40))
reject('duplicate-index',lambda r:r[10].__setitem__(2,9))
reject('missing-step',lambda r:r.pop(632))
reject('wrong-step',lambda r:r[632].__setitem__(1,1))
reject('request-conservation',lambda r:r[8].__setitem__(3,1))
reject('zero-byte-box',lambda r:r[11].__setitem__(3,1))
reject('null-bytes-exceed-total',lambda r:r[14].__setitem__(3,4))
assert not analyze(log(make(0)),1)['passed'];tests.append('zero-enabled-coverage')
reject('malformed-line',lambda r:r[5].append(0))
r=dict(passed=True,synthetic_only=True,physical_access=False,guest_launch=False,rejections=tests,
 source_pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['upload_analysis.py','test-upload-parser.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print('Upload parser positive modes and%d rejections PASS'%len(tests))
