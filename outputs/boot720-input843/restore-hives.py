"""Restore immutable primary hives and matching logs; retain exact preimages."""
import datetime,hashlib,io,json,zipfile
from pathlib import Path
import physical003 as h
K=h.K;W=h.W;P=Path('C:/xwn843/restore001');out=K/'restore-hives001.json'
assert not out.exists() and not P.exists()
pkg=h.read(W/'outputs/boot720-native835/package001.json')
audit=h.read(W/'outputs/boot720-bridge842/audit001.json')
assert audit['completed'] and h.read(W/'outputs/boot720-bridge842/closed001.json')['state']=='CLOSED'
archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');assert h.sha(archive.read_bytes())==pkg['archive_sha256']
items={};metadata={p.lower():v for p,v in pkg['files'].items()}
for name in ['default','sam','security','software','system']:
 for suffix in ['', '.log']:
  path='/E/winnt/system32/config/'+name+suffix
  old=audit['retained'][path];data=Path(old['private_path']).read_bytes();assert h.sha(data)==old['sha256']
  with zipfile.ZipFile(archive) as z:
   meta=metadata[path.lower()];baseline=z.read('payload'+meta['archive_path'])
  assert h.sha(baseline)==meta['sha256'] and len(baseline)==meta['bytes']
  if not suffix:
   assert baseline[:4]==b'regf';end=4096+int.from_bytes(baseline[40:44],'little');assert end<=len(baseline)
   at=4096
   while at<end:
    assert baseline[at:at+4]==b'hbin' and int.from_bytes(baseline[at+4:at+8],'little')==at-4096
    n=int.from_bytes(baseline[at+8:at+12],'little');assert n>=4096 and n%4096==0;at+=n
   assert at==end
  items[path]=(data,baseline)
r={'utc':h.utc(),'completed':False,'runtime_parent':False,'scope':'Immutable primary hives and logs, preimages retained. No startup/display/input binary changes. Trace reused by existing TRACE_REUSE policy.','writes':[],'files':{}}
P.mkdir(parents=True);h.save(out,r)
def get(f,p):
 assert p in items
 b=io.BytesIO()
 def take(v):assert b.tell()+len(v)<=8*1024**2;b.write(v)
 f.retrbinary('RETR '+p,take,65536);return b.getvalue()
try:
 with h.connect() as f:
  for p,(before,baseline) in items.items():
   assert get(f,p)==before
   (P/('before-'+p.rsplit('/',1)[1])).write_bytes(before)
   (P/('baseline-'+p.rsplit('/',1)[1])).write_bytes(baseline)
   r['files'][p]={'before_sha256':h.sha(before),'baseline_sha256':h.sha(baseline),'before_bytes':len(before),'baseline_bytes':len(baseline)}
  h.save(out,r)
  for p,(before,baseline) in items.items():
   if before!=baseline:
    r['writes'].append(p);h.save(out,r)
    for at in range(0,max(1,len(baseline)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+p,io.BytesIO(baseline[at:at+32768]),1024)
   assert get(f,p)==baseline;r['files'][p]['verified']=True;h.save(out,r)
  r['completed']=True
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:h.save(out,r)
print('Immutable primary hives and matching logs restored/readback verified')
