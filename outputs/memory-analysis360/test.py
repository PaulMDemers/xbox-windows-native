import hashlib,json,struct
from pathlib import Path
from decode import cpu,decode
from paired_decode import paired
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'tests002.json';assert not dest.exists()
P=K.parent/'memory-physical359/artifacts/candidate001/E/xwnmemory359candidate001/sample0'
cold=(P/'memory-before.bin.cold').read_bytes();warm=(P/'memory-before.bin').read_bytes()
w=list(struct.unpack('<16640I',warm));c=tuple(w[16:96]);checks=0
def no(fn,*args):
 global checks
 try:fn(*args)
 except ValueError:checks+=1;return
 raise AssertionError('Invalid state accepted')
assert c[16]==0x800 and c[14]==0x508 and set(c[56:78])=={0x07070707}
original=paired(cold,warm);assert original['passed'];checks+=1
# Inactive raw encodings are not architectural fixed-range policy.
for byte in range(256):
 v=list(c);v[56:78]=[byte*0x01010101]*22
 pat,resolve,ranges=cpu(tuple(v));assert resolve(0x1000)==6;checks+=1
 # Once enabled, reserved fixed-range encodings must still refuse.
 v[16]|=0x400
 if byte not in [0,1,4,5,6]:no(cpu,tuple(v))
 else:
  pat,resolve,ranges=cpu(tuple(v));assert resolve(0x1000)==byte;checks+=1
# Enabled valid fixed range overrides variable WB below1MiB only.
v=list(c);v[16]|=0x400;v[56:78]=[0x04040404]*22
_,resolve,_=cpu(tuple(v));assert resolve(0x1000)==4 and resolve(0x3700000)==6;checks+=1
for index,bit in [(16,0x800),(14,0x200),(14,0x100),(16,0x1000),(0,0x40000000),(2,0x20)]:
 v=list(c);v[index]^=bit;no(cpu,tuple(v))
# Packet equality, identity, geometry, error/exception and actual page gates remain.
for index in [0,1,2,3,*range(4,14),*range(16,176),178,179,180,181,255]:
 v=list(w);v[index]^=1;no(paired,cold,struct.pack('<16640I',*v))
for page in [0,2024,2025,4049]:
 for field in range(4):
  v=list(w);v[256+4*page+field]^=1;no(paired,cold,struct.pack('<16640I',*v))
# Original incomplete355 residency stays incomplete, not a complete cold result.
P=K.parent/'memory-runtime355/candidate001/artifacts/sample0'
v=list(struct.unpack('<16640I',(P/'memory-after.bin').read_bytes()));v[1]=357;v[180]=v[13]//4;v[181]=1
assert not paired((P/'memory-before.bin').read_bytes(),struct.pack('<16640I',*v))['cold_residency']['complete'];checks+=1
r=dict(passed=True,checks=checks,scope='Host decoder tests with actual saved packets plus explicit mutations; no hardware/cache writes or new boot',inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [K/'decode.py',K/'paired_decode.py',K/'test.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(checks)
