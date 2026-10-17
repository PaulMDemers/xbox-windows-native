"""Mutate actual complete cases in memory without changing their evidence."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_sprites as g
out=K/'actual-controls001.json';assert not out.exists()
def hostpath(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
c=json.loads((K/'physical001-collection.json').read_text());root=hostpath(c['files']['/E/xwn451/runner.txt']['path']).parent
review=json.loads((K/'runtime-review001.json').read_text());rows=[]
for row in review['rows']:
 if 'review' not in row:continue
 name=row['name'];backend=row['backend'];fmt=row['format']
 raw=(root/(name+'.txt')).read_bytes();captures={k:(root/(name+'-'+k+'.bin')).read_bytes() for k in g.KINDS}
 g.validate(raw,captures,backend,fmt,0);scalar=pixel=0
 def rejects(r,c):
  try:g.validate(r,c,backend,fmt,0)
  except (ValueError,KeyError):return True
  return False
 for key,value in g.decode(raw).items():
  changed=raw.replace((key+'='+value+'\r\n').encode(),(key+'=?\r\n').encode());assert changed!=raw
  assert rejects(changed,captures),key;scalar+=1
 for kind,data in captures.items():
  for offset in range(0,len(data),97):
   changed=bytearray(data);changed[offset]^=1;c=dict(captures);c[kind]=bytes(changed);assert rejects(raw,c);pixel+=1
  c=dict(captures);c[kind]=data+b'\0';assert rejects(raw,c);pixel+=1
 assert (root/(name+'.txt')).read_bytes()==raw
 for k,data in captures.items():assert (root/(name+'-'+k+'.bin')).read_bytes()==data
 rows.append(dict(name=name,scalar_rejections=scalar,pixel_length_rejections=pixel,originals_unchanged=True))
record=dict(passed=bool(rows),rows=rows,scope='Actual successful case mutations in memory; failed cases remain failed; not injected hardware faults')
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
