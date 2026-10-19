"""Mutate actual telemetry; retain the exact six independently checked scenes."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import graphics_scenebench as b
read=lambda p:json.loads(p.read_text())
r=read(K/'runtime-review002.json');assert r['all_allowed_cases_passed']
c=read(K/'ntfs-cold1-002.json');p=Path(c['private_path'])/'files/xwn550'
out=K/'actual-controls001.json';assert not out.exists();rows=[]
for name,backend in [('costd','default'),('costs','hel')]:
 raw=(p/(name+'-bench.txt')).read_bytes();f=b.scene.scene.decode(raw);n=0
 for key in f:
  for remove in (False,True):
   v=dict(f)
   if remove:del v[key]
   else:v[key]='invalid'
   bad=(''.join(k+'='+x+'\r\n' for k,x in v.items())).encode()
   try:b.validate_report(bad,backend,0)
   except ValueError:n+=1
   else:raise AssertionError(key)
 assert (p/(name+'-bench.txt')).read_bytes()==raw
 rows.append(dict(name=name,rejections=n,original_sha256=hashlib.sha256(raw).hexdigest(),original_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows,scope='Actual telemetry mutations; unchanged scene checker independently checks every one of six child captures'),indent=2)+'\n');print(rows)
