"""Actual report negatives and pixel mutations of the passing plain operations."""
import json,sys
from pathlib import Path
from launch_gate import sha
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_keyprobe as g
out=K/'actual-controls001.json';assert not out.exists()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());root=Path(cold['private_path'])/'files/xwn446'
review=json.loads((K/'runtime-review001.json').read_text());rows=[]
for row in review['rows']:
 name,backend,code=row['name'],row['backend'],row['process_exit']
 paths=[root/(name+s) for s in ('.txt','-source.bin','-dest.bin')];pins={str(p):sha(p) for p in paths}
 raw,src,dst=[p.read_bytes() for p in paths];g.validate(raw,src,dst,backend,code)
 scalar=pixel=0
 def rejects(r,s,d):
  try:g.validate(r,s,d,backend,code)
  except (ValueError,KeyError):return True
  return False
 for key,value in g.decode(raw).items():
  changed=raw.replace((key+'='+value+'\r\n').encode(),(key+'=?\r\n').encode());assert changed!=raw and rejects(changed,src,dst),key;scalar+=1
 for stage in range(0,12,2):
  assert row['review']['rows'][stage]['passed']
  for offset in range(stage*3072,(stage+1)*3072,4):
   changed=bytearray(dst);changed[offset]^=1;assert rejects(raw,src,changed);pixel+=1
 for offset in range(0,len(src),37):
  changed=bytearray(src);changed[offset]^=1;assert rejects(raw,changed,dst);pixel+=1
 assert rejects(raw,src[:-1],dst) and rejects(raw,src,dst+b'\0');pixel+=2
 for p,h in pins.items():assert sha(p)==h
 rows.append(dict(name=name,scalar_rejections=scalar,pixel_length_rejections=pixel,originals_unchanged=True))
record=dict(passed=True,rows=rows,scope='Actual report/transport/source and passing plain-stage pixel mutations; original keyed failures retained')
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
