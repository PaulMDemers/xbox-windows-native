"""Decode actual RCT presentation layout from cached records and creation links."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'layout-review001.json';assert not out.exists()
assert json.loads((K/'review001.json').read_text())['passed']
trace=json.loads((K/'trace-review001.json').read_text())
rows=[r for r in trace['graphics'] if r['api']=='StretchDIBits']
creation={r['id']:r for r in trace['graphics'] if r['api']=='CreateDIBSection' and r['result'] and r.get('output_pointer')}
decoded=[]
for row in rows:
 a=row['args'];h=row['header'];raw=h['raw'];assert h['status']==0 and len(raw)==10
 size,width,height,pb,compression,image_size,xppm,yppm,used,important=raw
 height=height if height<2**31 else height-2**32
 planes=pb&65535;bpp=pb>>16
 assert size==40 and planes==1 and compression==0 and width>0 and height!=0
 stride=((width*bpp+31)//32)*4;extent=stride*abs(height)
 assert (stride,extent)==(h['stride'],h['extent'])
 c=creation[row['bits_created_by_sample']]
 assert a[9]==c['output_pointer'] and raw==c['header']['raw']
 decoded.append(dict(id=row['id'],phase=row['phase'],width=width,height=height,bpp=bpp,stride=stride,extent=extent,bits=a[9],created_by=c['id'],returned_scanlines=row['result'],destination=a[1:5],source=a[5:9]))
assert rows and all(sum(r['phase']==p for r in rows)==32 for p in [0,1])
out.write_text(json.dumps(dict(passed=True,per_phase=[32,32],presentations=decoded,
 scope='Recorded RCT GDI StretchDIBits headers and source pointer linked to successful sampled DIB creation, in the reference-qualified saved scene. Allocation accessibility, palette, actual frame count, timings and Xbox acceleration are not established.'),indent=2)+'\n')
