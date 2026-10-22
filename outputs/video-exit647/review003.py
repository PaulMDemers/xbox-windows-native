"""Compare unchanged compiled video logic/data and record prepared diagnostic scope."""
import hashlib,json,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'review003.json';assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sections(data):
 assert data[:6]==b'\x7fELF\x01\x01'
 offset=struct.unpack_from('<I',data,32)[0];stride,count,strings=struct.unpack_from('<HHH',data,46)
 headers=[struct.unpack_from('<10I',data,offset+i*stride) for i in range(count)]
 h=headers[strings];names=data[h[4]:h[4]+h[5]]
 return {names[h[0]:].split(b'\0')[0].decode():data[h[4]:h[4]+h[5]] for h in headers if h[1]!=8}
r=dict(passed=False,physical_access=False,compiled_video_sections=[],prepared_only=True)
try:
 for obj,groups in [('xwn_hd_adapter.o',['.text']),('xwn_hd_profile.o',['.text','.rodata'])]:
  old=subprocess.check_output(['wsl','-d','Ubuntu','--','cat','/home/paul/xbox-windows-native/build/native480p633-build001/source/obj/'+obj],timeout=25)
  new=(Path('C:/xwn647/source003/obj')/obj).read_bytes()
  a,b=sections(old),sections(new)
  for group in groups:
   assert a[group]==b[group],(obj,group)
   r['compiled_video_sections'].append(dict(object=obj,section=group,bytes=len(a[group]),sha256=sha(a[group])))
 build=read(K/'build003.json');assert build['status']=='compiled' and build['host']['passed']
 assert read(K/'compiled-host001.json')['passed'] and read(K/'compiled-host001.json')['cases']==56
 r.update(passed=True,host_checks=70,compiled_wrapper_cases=56,
          xbe=build['outputs']['default.xbe'],unchanged_original_native_after_removing_diagnostic=build['original_native_recovered_exactly'],
          led_masks={'green_off':5,'red_off':80,'red_amber':245,'amber':255,'red_green':165,'green_amber':95,'unexpected_off':0},
          limitations=['Modeled calls are not physical timing or LED proof','No indication is inconclusive, including SMBus signaling failure or an earlier boot exit',
                       'Green/off only supports setup returned success in this instrumented run','Eight-second post-setup delay and extra SMC writes change timing/state',
                       'Unique launcher location differs from failed645; no boot reliability or fix claim'])
finally:
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({'passed':r['passed'],'unchanged_sections':len(r['compiled_video_sections'])}))
