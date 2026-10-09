"""Meaningful positive/negative bounds, frame contract and argument checks."""
import hashlib,json,struct
from pathlib import Path
from close_frame import capture_frame
k=Path(__file__).resolve().parent;dest=k/'close-frame-tests.json';assert not dest.exists()
def scenario(delta=8,arg=1880,limit=0x10000,base=0x20000,ret=0x767a599b,missing=False):
    cpu=dict(ESP=0x18000,EBP=0x18000+delta);teb=0x70000
    def read(a,n):
        if a==teb+8:return struct.pack('<I',limit)
        if a==teb+4:return struct.pack('<I',base)
        if missing:raise AssertionError('E14')
        assert a==cpu['EBP'] and n==12
        return struct.pack('<3I',0x19000,ret,arg)
    return read,cpu,teb,1880
checks=[]
for name,kwargs,want in [('verified frame',{},True),('FPO/incorrect EBP',dict(delta=4),False),
    ('wrong handle',dict(arg=1884),False),('frame outside stack',dict(base=0x1800a),False),
    ('kernel return',dict(ret=0x82400000),False),('nonresident frame',dict(missing=True),False)]:
    try:r=capture_frame(*scenario(**kwargs));ok=True
    except AssertionError:ok=False
    assert ok==want,name
    checks.append(dict(case=name,accepted=ok))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=checks,guest_access=False,
    pins={n:sha(k/n) for n in ['close_frame.py','test-close-frame.py']}),indent=2)+'\n')
print('Six bounded frame contract cases passed')
