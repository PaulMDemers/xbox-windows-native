"""Mutate actual metadata and RGB copies; never alter original cold evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import graphics_transform as g
out=K/'actual-controls002.json';assert not out.exists()
r=json.loads((K/'runtime-review002.json').read_text());assert r['all_allowed_cases_passed']
c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn493';rows=[]
for name,backend in [('r09ad','default'),('r09as','hel')]:
 raw=(p/(name+'.txt')).read_bytes();f=g.decode(raw);n=0
 frames=[bytearray((p/(name+'-'+s+'.bin')).read_bytes()) for s in ('clear','draw')]
 encode=lambda v:(''.join(k+'='+x+'\r\n' for k,x in v.items())).encode()
 for key in f:
  for remove in (False,True):
   bad=dict(f)
   if remove:del bad[key]
   else:bad[key]='invalid'
   try:g.validate(encode(bad),*frames,backend,0)
   except ValueError:n+=1
   else:raise AssertionError('Metadata negative accepted: '+key)
 metadata=n
 for frame in frames:
  for stage in range(6):
   for region in (0,1,2):
    pixel=g.mask(stage).index(region)
    for byte in range(3):
     at=stage*16384+pixel*4+byte;frame[at]^=1
     try:g.pixels(*frames)
     except ValueError:n+=1
     else:raise AssertionError('Actual RGB mutation accepted')
     frame[at]^=1
 for frame,suffix in zip(frames,('clear','draw')):assert bytes(frame)==(p/(name+'-'+suffix+'.bin')).read_bytes()
 rows.append(dict(name=name,metadata_rejections=metadata,pixel_rejections=n-metadata,original_sha256=hashlib.sha256(raw).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print(rows)
