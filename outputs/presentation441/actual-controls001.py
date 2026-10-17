"""Mutate actual complete reports/captures in memory; never alter evidence files."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_present as g
out=K/'actual-controls001.json';assert not out.exists()
c=json.loads((K/'physical001-collection.json').read_text());path=c['files']['/E/xwn441/runner.txt']['path'];root=Path('/mnt/'+path[0].lower()+path[2:].replace('\\','/')).parent
assert json.loads((K/'runtime-review001.json').read_text())['all_allowed_cases_passed']
rows=[]
for name,backend in [('r03d','default'),('r03s','hel')]:
 raw=(root/(name+'.txt')).read_bytes();captures={k:(root/(name+'-'+k+'.bin')).read_bytes() for k in ('source','before','after')}
 g.validate(raw,captures,backend,0);scalar=pixel=0
 def rejects(r,c):
  try:g.validate(r,c,backend,0)
  except (ValueError,KeyError):return True
  return False
 for key,value in g.decode(raw).items():
  changed=raw.replace((key+'='+value+'\r\n').encode(),(key+'=?\r\n').encode());assert changed!=raw
  assert rejects(changed,captures),key;scalar+=1
 for kind,data in captures.items():
  width,height=(128,112) if kind=='source' else (256,192);stride=width*height*4
  for stage in range(4):
   for x,y in [(0,0),(16,16),(48,40),(width-1,height-1)]:
    changed=bytearray(data);changed[stage*stride+(y*width+x)*4]^=1
    c=dict(captures);c[kind]=bytes(changed);assert rejects(raw,c);pixel+=1
  c=dict(captures);c[kind]=data[:-1];assert rejects(raw,c);pixel+=1
 assert (root/(name+'.txt')).read_bytes()==raw
 for k,data in captures.items():assert (root/(name+'-'+k+'.bin')).read_bytes()==data
 rows.append(dict(name=name,scalar_rejections=scalar,pixel_length_rejections=pixel,originals_unchanged=True))
record=dict(passed=True,rows=rows,scope='Actual report/capture mutations in memory; not injected driver faults')
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
