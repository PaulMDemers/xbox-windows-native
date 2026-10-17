"""Mutate actual complete inventory scalars and every capability byte."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import graphics_discovery as g
out=K/'actual-controls001.json';assert not out.exists()
c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn455'
r=json.loads((K/'runtime-review001.json').read_text());assert r['all_allowed_cases_passed'];rows=[]
for row in r['rows']:
 name=row['name'];raw=(p/(name+'.txt')).read_bytes();caps=(p/(name+'-caps.bin')).read_bytes();scalar=mutations=0
 def reject(a,b):
  try:g.validate(a,b,row['backend'],0)
  except ValueError:return True
  return False
 assert g.validate(raw,caps,row['backend'],0)['passed']
 for key,value in g.decode(raw).items():
  changed=raw.replace((key+'='+value+'\r\n').encode(),(key+'=?\r\n').encode());assert changed!=raw and reject(changed,caps),key;scalar+=1
 for offset in range(len(caps)):
  changed=bytearray(caps);changed[offset]^=1;assert reject(raw,bytes(changed));mutations+=1
 if caps:assert reject(raw,caps[:-1]);mutations+=1
 assert reject(raw,caps+b'\0');mutations+=1
 assert (p/(name+'.txt')).read_bytes()==raw and (p/(name+'-caps.bin')).read_bytes()==caps
 rows.append(dict(name=name,scalar_rejections=scalar,capability_length_rejections=mutations,mutation_field_note='Inherited capability_length_rejections field counts capability bytes/lengths in this inventory',report_sha256=hashlib.sha256(raw).hexdigest(),caps_sha256=hashlib.sha256(caps).hexdigest(),originals_unchanged=True))
out.write_text(json.dumps(dict(passed=True,rows=rows,scope='Actual inventory mutations; reported capabilities are not rendering evidence'),indent=2)+'\n');print(json.dumps(rows))
