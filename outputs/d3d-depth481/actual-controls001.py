"""Mutation checks of actual depth output; never alter original evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import graphics_depth as g
out=K/'actual-controls001.json';assert not out.exists()
r=json.loads((K/'runtime-review001.json').read_text());assert r['all_allowed_cases_passed']
c=json.loads((K/'physical001-collection.json').read_text());p=Path(c['files']['/E/xwn481/runner.txt']['path']).parent;rows=[]
for name,backend in [('r08bd','default'),('r08bs','hel')]:
 raw=(p/(name+'.txt')).read_bytes();frames=[bytearray((p/(name+'-'+s+'.bin')).read_bytes()) for s in g.SUFFIXES];f=g.decode(raw);n=0
 def refuse(data):
  global n
  try:g.validate(data,frames,backend,0)
  except (ValueError,KeyError):n+=1
  else:raise AssertionError('negative accepted')
 encode=lambda v:(''.join(k+'='+x+'\r\n' for k,x in v.items())).encode()
 for key in f:
  bad=dict(f);del bad[key];refuse(encode(bad));refuse(raw+(key+'='+f[key]+'\r\n').encode())
 for key in g.HRESULTS:
  bad=dict(f);bad[key]='1';refuse(encode(bad))
 for i in range(120):
  bad=dict(f);v=bytearray.fromhex(f['vertices']);v[i]^=1;bad['vertices']=v.hex();refuse(encode(bad))
 metadata=n
 for frame in frames:
  for at in range(0,len(frame),4):
   frame[at]^=1
   try:g.pixels(*frames)
   except ValueError:n+=1
   else:raise AssertionError('actual pixel mutation accepted')
   frame[at]^=1
 for frame,suffix in zip(frames,g.SUFFIXES):assert bytes(frame)==(p/(name+'-'+suffix+'.bin')).read_bytes()
 rows.append(dict(name=name,metadata_rejections=metadata,pixel_rejections=n-metadata,original_sha256=hashlib.sha256(raw).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print(rows)
