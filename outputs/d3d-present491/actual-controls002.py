"""Mutate copies of actual presentation reports/captures, never original evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import decoder002 as g
out=K/'actual-controls002.json';assert not out.exists()
r=json.loads((K/'runtime-review002.json').read_text());assert r['all_allowed_cases_passed']
c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn491';rows=[]
for name,backend in [('r08dd','default'),('r08ds','hel')]:
 raw=(p/(name+'.txt')).read_bytes();f=g.decode(raw);n=0
 frames={s:bytearray((p/(name+'-'+s+'.bin')).read_bytes()) for s in ('source','post','before','after')}
 encode=lambda v:(''.join(k+'='+x+'\r\n' for k,x in v.items())).encode()
 for key in f:
  for remove in (False,True):
   bad=dict(f)
   if remove:del bad[key]
   else:bad[key]='invalid'
   try:g.validate(encode(bad),frames,backend,0)
   except ValueError:n+=1
   else:raise AssertionError('Metadata negative accepted: '+key)
 metadata=n
 for kind,frame in frames.items():
  width,height=(128,112) if kind in ('source','post') else (256,192)
  points=[(0,0),(20,20),(50,50),(100,90),(width-1,height-1)]
  for stage in range(4):
   for x,y in points:
    for byte in range(4):
     at=4*(stage*width*height+y*width+x)+byte;frame[at]^=16
     try:g.pixels(frames)
     except ValueError:n+=1
     else:raise AssertionError('Actual pixel mutation accepted')
     frame[at]^=16
 for kind,frame in frames.items():assert bytes(frame)==(p/(name+'-'+kind+'.bin')).read_bytes()
 rows.append(dict(name=name,metadata_rejections=metadata,pixel_rejections=n-metadata,original_sha256=hashlib.sha256(raw).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print(rows)
