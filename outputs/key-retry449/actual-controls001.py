"""Negative controls of actual qualified physical RGB32 diagnostic receipts."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_keyprobe as g
def hostpath(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'actual-controls001.json';assert not out.exists()
r=json.loads((K/'runtime-review001.json').read_text());c=json.loads((K/'physical001-collection.json').read_text())
root=hostpath(c['files']['/E/xwn449/runner.txt']['path']).parent;rows=[]
for row in r['rows']:
 if not row.get('review',{}).get('semantics_passed'):continue
 name,backend=row['name'],row['backend'];raw=(root/(name+'.txt')).read_bytes();src=(root/(name+'-source.bin')).read_bytes();dst=(root/(name+'-dest.bin')).read_bytes()
 pins={str(p):sha(p) for p in root.glob(name+'*')};scalar=pixel=0
 def rejects(report,source,dest):
  try:g.validate(report,source,dest,backend,0)
  except (ValueError,KeyError):return True
  return False
 for k,v in g.decode(raw).items():
  changed=raw.replace((k+'='+v+'\r\n').encode(),(k+'=?\r\n').encode());assert changed!=raw and rejects(changed,src,dst),k;scalar+=1
 for offset in range(0,len(dst),4):
  changed=bytearray(dst);changed[offset]^=1;assert rejects(raw,src,changed);pixel+=1
 for offset in range(0,len(src),37):
  changed=bytearray(src);changed[offset]^=1;assert rejects(raw,changed,dst);pixel+=1
 assert rejects(raw,src[:-1],dst) and rejects(raw,src,dst+b'\0');pixel+=2
 for p,h in pins.items():assert sha(Path(p))==h
 rows.append(dict(name=name,scalar_rejections=scalar,pixel_length_rejections=pixel,originals_unchanged=True))
out.write_text(json.dumps(dict(passed=bool(rows),rows=rows,scope='Actual passing physical cases mutated only in memory'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
