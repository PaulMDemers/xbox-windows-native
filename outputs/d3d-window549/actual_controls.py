"""Mutate actual metadata and RGB copies; never alter original cold evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import graphics_scenepresent as g
out=K/'actual-controls001.json';assert not out.exists()
r=json.loads((K/'runtime-review001.json').read_text());assert r['all_allowed_cases_passed']
c=json.loads((K/'collection001.json').read_text());p=Path(c['files']['/E/xwn549/runner.txt']['path']).parent;rows=[]
for name,backend in [('r09cd','default'),('r09cs','hel')]:
 raw=(p/(name+'.txt')).read_bytes();f=g.scene.decode(raw);n=0
 frames=[bytearray((p/(name+'-'+s+'.bin')).read_bytes()) for s in g.SUFFIXES]
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
  offsets=range(0,len(frame),4) if stream in (2,3) else [stage*(25600 if stream in (4,5) else 16384)+pixel*4 for stage in range(5) for pixel in (0,1000,2000,4095)]
  for at in offsets:
   original=frame[at:at+3];frame[at:at+3]=b'\x56\x34\x12'
   try:g.validate(raw,*frames,backend,0)
   except ValueError:n+=1
   else:raise AssertionError('Actual RGB/source mutation accepted')
   frame[at:at+3]=original
 for frame,suffix in zip(frames,g.SUFFIXES):assert bytes(frame)==(p/(name+'-'+suffix+'.bin')).read_bytes()
 rows.append(dict(name=name,metadata_rejections=metadata,pixel_rejections=n-metadata,original_sha256=hashlib.sha256(raw).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print(rows)
