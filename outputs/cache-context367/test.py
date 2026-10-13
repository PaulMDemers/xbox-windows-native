import hashlib,json,struct
from pathlib import Path
from paired_decode import paired
K=Path(__file__).resolve().parent;dest=K/'tests001.json';assert not dest.exists()
root=K.parent/'bandwidth-runtime365/candidate001/artifacts/sample0'
a=(root/'memory-before.bin.cold').read_bytes();b=(root/'memory-before.bin').read_bytes();c=list(struct.unpack('<16640I',a));w=list(struct.unpack('<16640I',b));pack=lambda a:struct.pack('<16640I',*a)
r=paired(a,b);assert r['cold_residency']['complete'] is False and r['cross_capture_cr0']['xor']==10
checks=1;rejected=0
for bits in [0,2,8,10]:
 x=c.copy();x[16]=(x[16]&~10)|bits;v=paired(pack(x),b);assert v['passed'] and not v['cold_residency']['complete'];checks+=1
for word in range(16,96):
 for bit in range(32):
  if word==16 and bit in [1,3]:continue
  x=c.copy();x[word]^=1<<bit
  try:paired(pack(x),b)
  except ValueError:rejected+=1
  else:raise AssertionError((word,bit))
# Changes within a complete warm capture are STILL errors, including MP/TS.
for bit in range(32):
 x=w.copy();x[16]^=1<<bit
 try:paired(a,pack(x))
 except ValueError:rejected+=1
 else:raise AssertionError(bit)
for word,value in [(3,0),(3,64),(14,1),(15,4095),(256+7,3),(178,1)]:
 x=c.copy();x[word]=value
 try:paired(pack(x),b)
 except ValueError:rejected+=1
 else:raise AssertionError((word,value))
assert (K/'decode.py').read_bytes()==(K.parent/'memory-analysis360/decode.py').read_bytes()
dest.write_text(json.dumps(dict(passed=True,positive_checks=checks,rejected_mutations=rejected,actual_cold_sha256=hashlib.sha256(a).hexdigest(),actual_warm_sha256=hashlib.sha256(b).hexdigest(),inputs={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['test.py','paired_decode.py','decode.py']}),indent=2)+'\n');print(checks,rejected)
