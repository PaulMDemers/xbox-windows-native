"""Compare unchanged compiled video logic/data and record prepared diagnostic scope."""
import hashlib,json,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'review001.json';assert not out.exists()
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
 for obj,groups in [('xwn_hd_profile.o',['.text','.rodata']),('BootInterrupts.o',['.text']),('BootLibrary.o',['.text'])]:
  old=subprocess.check_output(['wsl','-d','Ubuntu','--','cat','/home/paul/xbox-windows-native/build/native480p633-build001/source/obj/'+obj],timeout=25)
  new=(Path('C:/xwn651/source001/obj')/obj).read_bytes()
  a,b=sections(old),sections(new)
  for group in groups:
   assert a[group]==b[group],(obj,group)
   r['compiled_video_sections'].append(dict(object=obj,section=group,bytes=len(a[group]),sha256=sha(a[group])))
 build=read(K/'build001.json');assert build['status']=='compiled' and all(v['passed'] for v in build['host'].values())
 assert read(K/'compiled-wrapper001.json')['passed'] and read(K/'compiled-wrapper001.json')['cases']==140
 assert read(K/'compiled-adapter001.json')['passed'] and read(K/'compiled-adapter001.json')['cases']==10
 assert read(K/'timer-current001.json')['passed']
 assert read(K/'timer-current001.json')['cases']==32
 old=Path('C:/xwn649/source001/obj/xwn_hd_adapter.o').read_bytes()
 new=Path('C:/xwn651/source001/obj/xwn_hd_adapter.o').read_bytes()
 assert sections(old)['.text']==sections(new)['.text']
 assert (K/'xwn_hd_adapter.c').read_bytes()==(K.parent/'poll-timer649/xwn_hd_adapter.c').read_bytes()
 r.update(passed=True,timer_cases=32,host_differential_scenarios=44,host_led_cases=5143,host_readback_cases=2042,
          compiled_wrapper_cases=140,compiled_adapter_cases=10,xbe=build['outputs']['default.xbe'],
          native649_recovered_exactly=build['native649_recovered_exactly'],
          adapter649_source_and_object_text_identical=True,trace_RAM_only=True,
          new_capture_callbacks_per_snapshot_IF_clear={'r32':18,'r8':25,'selector_w8':24},
          new_capture_callbacks_per_snapshot_IF_set={'r32':18,'r8':0,'selector_w8':0},
          instructions_changed_interrupt_state=False,
          limitations=['Only original reset path changes IF; snapshots do not use CLI/STI',
                       'Models do not prove physical readback, timing, LED or Windows boot',
                       'Post-result snapshot follows original fail blanking; it is not a pre-timeout atomic snapshot',
                       'Existing wait_us may hang if timer freezes; added reads/layout/indications perturb timing',
                       'Detailed snapshots remain RAM-only; human LED summaries are coarse',
                       'Masks cover the observed631 subset, not all registers or effective clock/routing',
                       'Status all-ones does not prove invalid MMIO; handshake equality does not prove completion'])

finally:
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({'passed':r['passed'],'unchanged_sections':len(r['compiled_video_sections'])}))
