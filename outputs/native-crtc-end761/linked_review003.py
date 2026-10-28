from pathlib import Path
import json,hashlib,struct,re,datetime
k=Path('outputs/native-crtc-end761');p=Path('C:/xwn761/build002');h=Path('C:/xwn761/host002');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'scope':'Verify tested bridge/payload and compiled frontend page/plan bytes linked in PE and XBE','objects':{}}
try:
 pe=(p/'main.exe').read_bytes();xbe=(p/'bin/default.xbe').read_bytes()
 for f in ['bridge.bin','payload.bin']:
  b=(h/f).read_bytes();assert pe.count(b)==xbe.count(b)==1
 for name in ['page002.obj','plan.obj','layout.obj','main.obj']:
  b=(p/name).read_bytes();count=struct.unpack_from('<H',b,2)[0];sections=[]
  for i in range(count):
   name8,_,_,size,raw,rel,_,nrel,_,flags=struct.unpack_from('<8sIIIIIIHHI',b,20+i*40)
   if name8.rstrip(b'\0')!=b'.text' or not size:continue
   code=b[raw:raw+size];masked=set()
   for j in range(nrel):
    off,_,typ=struct.unpack_from('<IIH',b,rel+j*10);assert typ in (6,20);masked.update(range(off,off+4))
   pattern=b''.join(b'.' if j in masked else re.escape(bytes([c])) for j,c in enumerate(code))
   matches=list(re.finditer(pattern,pe,re.S));assert len(matches)==1,(name,len(matches))
   linked=matches[0].group();assert xbe.count(linked)==1
   sections.append({'bytes':size,'relocations':nrel,'nonrelocation_bytes_exact':True,'PE_offset':matches[0].start(),'XBE_offset':xbe.index(linked)})
  assert sections;r['objects'][name]=sections
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={n:sha(p/n) for n in ['main.exe','bin/default.xbe','main.obj','page002.obj','plan.obj','layout.obj']};r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(k/'linked-review001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS tested object instructions and payload/bridge bytes linked exactly')
