"""Reject deliberate corruptions of the actual complete ordinary log."""
from pathlib import Path
import hashlib,json
from protocol import validate_log
k=Path(__file__).resolve().parent;p=k/'candidate001/artifacts/result.log';data=p.read_bytes();lines=data.decode('ascii').splitlines();assert validate_log(data)['passed']
results=[]
def check(name,changed):
 result=validate_log(('\n'.join(changed)+'\n').encode());assert not result['passed'],name
 results.append(dict(name=name,rejected=True))
def number(name,label,field,value,occurrence=0):
 altered=lines.copy();rows=[i for i,s in enumerate(altered) if s.split()[0]==label];at=rows[occurrence];v=altered[at].split();v[field]=str(value);altered[at]=' '.join(v);check(name,altered)
number('wrong visible position','CURSOR_OVER_DRAW',2,99)
number('wrong restoration position','CURSOR_RESTORED',3,99)
number('wrong cursor case','CURSOR_OVER_DRAW',1,99)
number('hidden incorrectly visible','CURSOR_PHASE',3,1,1)
number('replacement phase missing','CURSOR_PHASE',2,0,2)
number('pixel mismatch','PIXELS_BAD_CHANGED',2,1)
number('reference callback','REFERENCE_CALLBACK_DELTA',2,1)
number('API failure','CASE_API',3,0)
number('source mutation','SOURCE32_HASH_PAIR',2,0)
number('reference mutation','REFERENCE_HASH_BYTES',3,0)
number('coherence failure','COHERENCE_ACTIVE',1,1)
number('active false','COHERENCE_ACTIVE',2,0)
number('empty clip changes pixels','PIXELS_BAD_CHANGED',3,1,23)
number('incomplete count','COMPLETE',2,25)
number('explicit failure','COMPLETE',1,1)
check('missing restart',lines[:-1]);check('truncated case',lines[:100]);check('unexpected suffix',lines+['EXTRA 0 0 0'])
r=dict(passed=True,mutations=results,baseline_passed=True,baseline_sha256=hashlib.sha256(data).hexdigest(),protocol_sha256=hashlib.sha256((k/'protocol.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(k/'protocol-tests.json').write_text(json.dumps(r,indent=2)+'\n');print('Actual-log corruption gates rejected',len(results),'mutations')
