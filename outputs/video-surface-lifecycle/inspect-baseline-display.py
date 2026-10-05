"""Inspect the retained Microsoft display's public DDI callback registration only."""
import json,hashlib,struct,re
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k/'test-compiled.py').read_text();ns={'__file__':str(k/'test-compiled.py')};exec(s[:s.index('results=[]')],ns)
p=k.parent/'native-windows-physical-f/package/F/winnt/system32/framebuf.dll'
pe=ns['pefile'].PE(str(p));ns['pe']=pe;ns['base']=pe.OPTIONAL_HEADER.ImageBase
m=ns['Machine']();sp=ns['STACK']+0xf000;out=ns['STACK']+0x2000
for i,v in enumerate([ns['STOP'],0x20000,12,out]):m.put(sp+4*i,v)
m.u.reg_write(ns['UC_X86_REG_ESP'],sp);m.u.emu_start(ns['base']+pe.OPTIONAL_HEADER.AddressOfEntryPoint,0,count=100000)
assert m.stopped and m.u.reg_read(ns['UC_X86_REG_EAX'])==1 and m.u.reg_read(ns['UC_X86_REG_ESP'])==sp+16
version,count,table=struct.unpack('<3I',m.u.mem_read(out,12));assert 3<count<64
functions=dict(struct.unpack('<2I',m.u.mem_read(table+8*i,8)) for i in range(count))
# Public DDI indices, not an assumed private PDEV layout.
names={0:'DrvEnablePDEV',1:'DrvCompletePDEV',2:'DrvDisablePDEV',3:'DrvEnableSurface',4:'DrvDisableSurface',5:'DrvAssertMode',6:'DrvOffset',8:'DrvDisableDriver',13:'DrvDitherColor',18:'DrvBitBlt',19:'DrvCopyBits',22:'DrvSetPalette',23:'DrvTextOut',29:'DrvSetPointerShape',30:'DrvMovePointer',41:'DrvGetModes'}
r=dict(scope=__doc__,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),version=hex(version),callbacks=[dict(index=i,name=names.get(i),rva=hex(a-ns['base'])) for i,a in functions.items()],render_hooks_registered=any(i in functions for i in [18,19,23]),physical_access=False,private_pdev_not_executed=True)
(k/'baseline-ddi.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
