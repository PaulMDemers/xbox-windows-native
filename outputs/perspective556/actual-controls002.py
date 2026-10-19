"""Mutate actual metadata and RGB copies; never alter original cold evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import graphics_perspective as g
out=K/'actual-controls002.json';assert not out.exists()
r=json.loads((K/'runtime-review002.json').read_text());assert r['all_allowed_cases_passed']
c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn556';rows=[]
for name,backend in [('r09fd','default'),('r09fs','hel')]:
 raw=(p/(name+'.txt')).read_bytes();f=g.decode(raw);n=0
 frames=[bytearray((p/(name+'-'+s+'.bin')).read_bytes()) for s in ('clear','draw','source-before','source-after')]
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
 for stream,frame in enumerate(frames):
  offsets=range(0,len(frame),4) if stream>=2 else [stage*16384+pixel*4 for stage in range(5) for pixel in (0,24*64+24,24*64+36,24*64+48,4095)]
  for at in offsets:
   original=frame[at:at+3];frame[at:at+3]=b'\x56\x34\x12'
   try:g.validate(raw,*frames,backend,0)
   except ValueError:n+=1
   else:raise AssertionError('Actual RGB/source mutation accepted')
   frame[at:at+3]=original
 for frame,suffix in zip(frames,('clear','draw','source-before','source-after')):assert bytes(frame)==(p/(name+'-'+suffix+'.bin')).read_bytes()
 rows.append(dict(name=name,metadata_rejections=metadata,pixel_rejections=n-metadata,original_sha256=hashlib.sha256(raw).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print(rows)
