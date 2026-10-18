"""New runtime/controller namespace; no old runtime execution or physical access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'pre-c-stop541';rows={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['controller.py','supervise.py','host001.py','stage-host001.py','audit.py','decode_actual.py',
 'primary_decode.py','witness_decode.py','decode.py','receipts.py','legacy_refusal_decode.py','failure_marker.py','stack_host.py']:
 src=S/name;t=src.read_text(encoding='utf-8')
 if name in ['controller.py','supervise.py','host001.py','stage-host001.py','audit.py','decode_actual.py']:
  t=t.replace('pre-c-stop541','pre-pci-stop542').replace('xwn541','xwn542').replace('XWNBoot541','XWNBoot542')
  t=t.replace('audit541','audit542').replace('completed541','completed542')
  t=t.replace('stack-stop540/after1.json','pre-c-stop541/after1.json')
 if name=='controller.py':t=t.replace('pre-C halt','pre-PCI halt')
 if name=='stack_host.py':
  t=t.replace('0x2600200','0x26004f8').replace('else 0x5f','else 0xf5')
  t=t.replace('u.mem_map(0x27ff000,4096);u.mem_write(0x27ff000,b\'\\xa5\'*4096)',"u.mem_map(0x27fc000,0x4000);u.mem_write(0x27fc000,b'\\xa5'*0x4000)")
  t=t.replace("u.reg_write(x.UC_X86_REG_ESP,0xdead0000)","u.reg_write(x.UC_X86_REG_ESP,0xdead0000 if name=='a' else 0x27fdf84)")
  t=t.replace('0x27ff000<=address and address+size<=0x2800000',"0x27fc000<=address and address+size<=(0x2800000 if name=='a' else 0x27fdf84)")
  t=t.replace("assert u.reg_read(x.UC_X86_REG_ESP)==0x2800000","assert u.reg_read(x.UC_X86_REG_ESP)==(0x2800000 if name=='a' else 0x27fdf84)\n     if name=='b':assert bytes(u.mem_read(0x27fdf84,0x207c))==b'\\xa5'*0x207c")
 p=K/name;assert not p.exists();p.write_text(t,encoding='utf-8',newline='\n')
 rows[name]=dict(source=str(src),source_sha256=sha(src),sha256=sha(p))
(K/'workflow-copy001.json').write_text(json.dumps(dict(files=rows,physical_access=False),indent=2)+'\n',encoding='utf-8',newline='\n')
