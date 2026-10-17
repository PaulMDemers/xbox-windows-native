"""Join current read-only boot bytes to known baseline; no physical cause inference."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
out=K/'review001.json';assert not out.exists()
c=json.loads((K/'capture001.json').read_text());assert c['completed'] and c['remote_writes']==[] and c['temporary_startup_absent']
prior=json.loads((K.parent/'baseline-compare415/physical001.json').read_text())['files']
rows={}
for n,r in c['files'].items():
 b=Path(r['path']).read_bytes();assert sha(b)==r['sha256']
 if n in prior:assert prior[n]['sha256']==r['sha256'],n
 rows[n]=dict(sha256=r['sha256'],matches415=prior[n]['sha256']==r['sha256'] if n in prior else None)
x=Path(c['files']['/E/Applications/XWNEBoot/default.xbe']['path']).read_bytes()
assert sha(x)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
assert x[:4]==b'XBEH';base=struct.unpack_from('<I',x,0x104)[0];count,table=struct.unpack_from('<II',x,0x11c)
assert 0<count<=8 and 0<=table-base<=len(x)-count*56
sections=[]
for i in range(count):
 s=table-base+i*56;off,size=struct.unpack_from('<II',x,s+12)
 assert 0<size and off+size<=len(x)
 assert hashlib.sha1(struct.pack('<I',size)+x[off:off+size]).digest()==x[s+36:s+56]
 sections.append(dict(offset=off,bytes=size,digest_valid=True))
r=dict(passed=True,files=rows,sections=sections,launcher_known_baseline_exact=True,
 temporary_startup_absent=True,mode='720p',console_C_accessed=False,remote_writes=[],
 limitations=['Selected-file and section-digest checks only, not a full filesystem allocation audit',
 'Unchanged bytes do not prove CPU/device state at failed handoff',
 'No attributed boot failure cause; old successful instrumented409/410/414 cases remain distinct'],
 next='One baseline direct boot after full power-off, without a test startup hook; not a D3D retry or proof of a fix')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,files=len(rows),sections=len(sections),launcher_known_baseline_exact=True)))
