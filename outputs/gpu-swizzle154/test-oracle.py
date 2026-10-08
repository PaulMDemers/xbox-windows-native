"""Require rectangular Morton bijections, known addresses and negative byte checks."""
import hashlib,json
from pathlib import Path
from oracle import index,expected,compare
assert index(2,3,64,32)==14 and index(3,5,64,32)==39 and index(12,9,64,32)==210
assert index(32,0,64,32)==1024 and index(0,32,32,64)==1024
checks=5
for shape,(w,h) in enumerate([(64,32),(32,64)]):
    assert sorted(index(x,y,w,h) for y in range(h) for x in range(w))==list(range(w*h));checks+=1
    for depth in range(2):
        for stage in range(3):
            ref=expected(shape,depth,stage)
            assert ref[(w*h*(2 if depth else 4)):]==bytes([0xa5])*(32768-w*h*(2 if depth else 4));checks+=1
            for offset in [0,210*(2 if depth else 4),27000,32767]:
                data=bytearray(ref);data[offset]^=1;assert not compare(data,ref)['matched'];checks+=1
p=Path(__file__).with_name('oracle-tests.json');assert not p.exists()
p.write_text(json.dumps(dict(passed=True,checks=checks,test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print(checks,'swizzle oracle checks passed')
