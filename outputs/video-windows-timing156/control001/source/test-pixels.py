"""Reject partial/truncated/wrong-channel cold images without guest intervention."""
import hashlib,json
from pathlib import Path
from pixels import reference,observed
from protocol import expected_bytes,W,H
k=Path(__file__).resolve().parent;target=k/'pixel-tests.json';assert not target.exists()
rows=[]
for index in [0,2,8,14]:
    good=expected_bytes(index);assert reference(good,index) and observed(good,index)
    failures=[('missing',None),('truncated',good[:-4]),('extra',good+b'\0')]
    for channel in range(3):
        for label,at in [('top',0),('bottom',(W*H-1)*4)]:
            bad=bytearray(good);bad[at+channel]^=1;failures.append((f'{label}-channel{channel}',bytes(bad)))
    for name,data in failures:
        assert not reference(data,index) and not observed(data,index);rows.append(f'{index}:{name}')
    alpha=bytearray(good);alpha[-1]^=1
    assert observed(bytes(alpha),index) and not reference(bytes(alpha),index)
target.write_text(json.dumps(dict(passed=True,rejected=rows,checks=len(rows),
    alpha_scope_explicit=True,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest()
    for n in ['pixels.py','protocol.py','test-pixels.py']}),indent=2)+'\n')
print(len(rows),'cold pixel corruption gates passed')
