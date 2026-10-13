import hashlib,json,struct
from pathlib import Path
from paired_decode import paired
K=Path(__file__).resolve().parent;dest=K/'pairs001.json';assert not dest.exists()
a=K.parent/'memory-runtime355/candidate001/artifacts/sample0'
cold=(a/'memory-before.bin').read_bytes();full=(a/'memory-after.bin').read_bytes()
w=list(struct.unpack('<16640I',full));w[1]=357;w[179]=0;w[180]=w[13]//4;w[181]=1;warm=struct.pack('<16640I',*w)
assert not paired(cold,warm)['cold_residency']['complete'];assert paired(full,warm)['cold_residency']['complete']
checks=2
for index in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,*range(16,176),176,177,178,179,255,16639]:
 v=list(struct.unpack('<16640I',cold));v[index]^=1
 try:paired(struct.pack('<16640I',*v),warm)
 except ValueError:checks+=1
 else:raise AssertionError(('accepted header mutation',index))
n=struct.unpack('<16640I',cold)[14]
for i in range(n):
 for field in [0,1,2,3]:
  v=list(struct.unpack('<16640I',cold));v[256+i*4+field]^=1
  try:paired(struct.pack('<16640I',*v),warm)
  except ValueError:checks+=1
  else:raise AssertionError(('accepted row mutation',i,field))
for blob in [cold[:-1],cold+b'0']:
 try:paired(blob,warm)
 except ValueError:checks+=1
 else:raise AssertionError('length accepted')
r=dict(passed=True,checks=checks,scope='Actual355 preserved cold/complete bytes with synthetic357 warm markers; NOT new runtime qualification',inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [K/'paired_decode.py',K/'decode.py',K/'test_pairs.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(r['checks'])
