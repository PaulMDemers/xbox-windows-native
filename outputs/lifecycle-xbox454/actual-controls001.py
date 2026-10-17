"""Perturb actual receipts/captures in memory; preserve originals."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import graphics_lifecycle as g
sha=lambda b:hashlib.sha256(b).hexdigest()
out=K/'actual-controls001.json';assert not out.exists()
c=json.loads((K/'physical001-collection.json').read_text());s=c['files']['/E/xwn454/runner.txt']['path'];p=Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')).parent
r=json.loads((K/'runtime-review001.json').read_text());assert r['all_allowed_cases_passed'];rows=[]
for row in r['rows']:
 name=row['name'];raw=(p/(name+'.txt')).read_bytes();pixels=(p/(name+'-pixels.bin')).read_bytes();scalar=mutations=0
 def reject(raw,pixels):
  try:g.validate(raw,pixels,row['backend'],0)
  except ValueError:return True
  return False
 assert g.validate(raw,pixels,row['backend'],0)['passed']
 for key,value in g.decode(raw).items():
  changed=raw.replace((key+'='+value+'\r\n').encode(),(key+'=?\r\n').encode());assert changed!=raw and reject(changed,pixels),key;scalar+=1
 for i in range(64):
  for offset in (0,49148,49152,49152+4*(11*128+9),98300):
   changed=bytearray(pixels);changed[i*98304+offset]^=1;assert reject(raw,bytes(changed));mutations+=1
 for changed in (pixels[:-1],pixels+b'\0'):assert reject(raw,changed);mutations+=1
 assert (p/(name+'.txt')).read_bytes()==raw and (p/(name+'-pixels.bin')).read_bytes()==pixels
 rows.append(dict(name=name,scalar_rejections=scalar,pixel_length_rejections=mutations,report_sha256=sha(raw),pixels_sha256=sha(pixels),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows,scope='Mutations of actual complete results, not injected hardware faults'),indent=2)+'\n');print(json.dumps(rows))
