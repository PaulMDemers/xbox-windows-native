"""Verify frozen source, compiled sections, and fresh654 tests before staging."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'review001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
def sections(b):
 assert b[:6]==b'\x7fELF\x01\x01'
 offset=struct.unpack_from('<I',b,32)[0];stride,count,strings=struct.unpack_from('<HHH',b,46)
 hs=[struct.unpack_from('<10I',b,offset+i*stride) for i in range(count)]
 h=hs[strings];names=b[h[4]:h[4]+h[5]]
 return {names[h[0]:].split(b'\0')[0].decode():b[h[4]:h[4]+h[5]] for h in hs if h[1]!=8}
r=dict(passed=False,physical_access=False,sections=[],source_sha256=sha(Path(__file__).read_bytes()))
try:
 b=read(K/'build001.json');assert b['status']=='compiled' and b['host']['passed'] and b['host']['cases']==9600
 for n,h in b['source_pins'].items():assert sha((K/n).read_bytes())==h,n
 c=read(K/'compiled-wrapper001.json');assert c['passed'] and c['cases']==100
 assert sha((K/'compiled_wrapper.py').read_bytes())==c['source_sha256']
 a=read(K/'source-review001.json');assert a['passed'] and len(a['checks'])==10
 assert sha((K/'source_review.py').read_bytes())==a['source_sha256']
 for obj in ('xwn_hd_adapter.o','xwn_hd_profile.o','BootLibrary.o','BootInterrupts.o'):
  before=sections((Path('C:/xwn651/source001/obj')/obj).read_bytes())
  after=sections((Path('C:/xwn654/source001/obj')/obj).read_bytes())
  for sec in ('.text','.rodata'):
   assert before.get(sec,b'')==after.get(sec,b''),(obj,sec)
   r['sections'].append(dict(object=obj,section=sec,bytes=len(after.get(sec,b'')),sha256=sha(after.get(sec,b''))))
 for n in ('xwn_hd_native.c','xwn_hd_adapter.c','xwn_hd_profile.c','readback651.h','trace649.h'):
  assert (Path('C:/xwn651/source001/drivers/video')/n).read_bytes()==(Path('C:/xwn654/source001/drivers/video')/n).read_bytes()
 xbe=Path('C:/xwn654/build001/default.xbe').read_bytes()
 assert sha(xbe)==b['outputs']['default.xbe']['sha256']
 assert c['image_sha256']==b['outputs']['image-crom.bin']['sha256']
 r.update(passed=True,only_source_change='drivers/video/led651.h',host_cases=9600,compiled_wrapper_cases=100,xbe=b['outputs']['default.xbe'],
          limitations=['Only masked timing subset is reported; no complete snapshot export',
                       'Indication describes captured post-result state after original failure blanking',
                       'Existing timer can hang; diagnostic is watched only',
                       'Code layout and post-result indication duration change; no repeatability or fix claim',
                       'No physical result yet; automatic storage logging deferred'])
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=r['passed'],sections=len(r['sections']))))
