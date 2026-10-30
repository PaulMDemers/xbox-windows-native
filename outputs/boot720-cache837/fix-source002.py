"""Preserve driver001 link failure; declare the HAL routine's NT calling convention."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720837-source001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'source001.json').read_text());p=B/'fatx/drivers/filesystems/vfatfs/cache837.c'
assert sha(p)==r['new_diagnostic_sources']['cache837.c'];before=sha(p)
p.write_bytes((K/'cache837.c').read_bytes());r['new_diagnostic_sources']['cache837.c']=sha(p)
r['amendment']={'reason':'driver001 link failure: absent NTAPI declaration made HalDisplayString cdecl','before':before,'after':sha(p),'failure':'driver001.json; private driver001/build.log'}
subprocess.run(['git','-C',str(B/'fatx'),'add','-f','.'],check=True)
r['trees']['fatx']=subprocess.check_output(['git','-C',str(B/'fatx'),'write-tree'],text=True).strip()
(K/'source002.json').write_text(json.dumps(r,indent=2)+'\n')
(K/'build-driver002.py').write_text((K/'build-driver.py').read_text().replace('driver001','driver002').replace('source001.json','source002.json'))
t=(K/'qualify-driver.py').read_text().replace('driver-host001','driver-host002')
t=t.replace('typedef void VOID,*PVOID;', '#define NTHALAPI\ntypedef char *PCH;typedef void VOID,*PVOID;')
(K/'qualify-driver002.py').write_text(t)
for n in ['build-chain002.py','physical.py','review-driver.py']:
 t=(K/n).read_text().replace('source001.json','source002.json').replace('driver001','driver002').replace('driver-host001','driver-host002')
 (K/n).write_text(t)
print('HAL calling convention corrected; failed build001 retained')
