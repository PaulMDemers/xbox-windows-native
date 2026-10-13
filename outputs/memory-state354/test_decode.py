import copy,hashlib,json,struct
from pathlib import Path
from decode import decode,cpu,TABLE
K=Path(__file__).resolve().parent;dest=K/'decoder001.json';assert not dest.exists()
raw=Path('E:/xwn354/host001/synthetic.bin').read_bytes();w=list(struct.unpack('<16640I',raw));r=decode(raw)
assert r['counts']=={'shadow':{'WB':2026},'scanout':{'UC':2025}}
checks=0
def reject(a):
 global checks
 try:decode(struct.pack('<16640I',*a))
 except ValueError:checks+=1;return
 raise AssertionError('accepted invalid packet')
for i in [0,1,2,3,15,176,177,178,255,16639]:
 a=w.copy();a[i]^=1;reject(a)
for i in range(16,176):
 a=w.copy();a[i]^=1;reject(a)
for row in range(4051):
 for field,bit in [(0,1),(1,4096),(2,1),(3,1)]:
  a=w.copy();a[256+4*row+field]^=bit;reject(a)
for i in range(4,9):
 a=w.copy();a[i]=0;reject(a)
for i in (9,10,11,12,13,14):
 a=w.copy();a[i]=0;reject(a)
for n in [0,1,66559,66561]:
 try:decode(raw[:n] if n<66560 else raw+b'\0')
 except ValueError:checks+=1
 else:raise AssertionError('length accepted')
c=tuple(w[16:96]);pats,resolve,ranges=cpu(c)
for pa in (0,4096,0x100000,0x03700000,0x03ffffff):assert resolve(pa)==6;checks+=1
assert resolve(0x04000000)==0;checks+=1
# Explicit type table assertions, separate from the collector's synthetic data.
assert [TABLE[6][t] for t in [0,1,4,5,6,7]]==[0,1,4,5,6,0];checks+=6
# Unsupported global cache mode and undefined overlap must not become UC/WB.
for flag in [0x20000000,0x40000000]:
 a=w.copy();a[16]|=flag;a[96]|=flag;reject(a)
a=w.copy()
for off in (16,96):
 a[off+28]=5;a[off+30]=0xfc000800;a[off+31]=15
reject(a)
# Fixed ranges below1MiB take priority when explicitly enabled, no guessing.
f=list(c);f[16]|=0x400
for i in range(56,78):f[i]=0x04040404
assert cpu(tuple(f))[1](0xa0000)==4 and cpu(tuple(f))[1](0x100000)==6;checks+=2
dest.write_text(json.dumps(dict(passed=True,checks=checks,scope='Synthetic actual-core packet and independent decoder mutations; NOT guest evidence',
 inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [K/'test_decode.py',K/'decode.py',Path('E:/xwn354/host001/synthetic.bin')]},
 expected=r['counts']),indent=2)+'\n');print(checks,'decoder checks passed')
