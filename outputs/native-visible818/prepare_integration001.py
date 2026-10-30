"""Create a fresh relocated bridge plus complete transaction model."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'model001.py').read_text().replace("K/'model001.json'","K/'integration001.json'")
s=s.replace("def run(label,expected=1,", "def run(label,layout='dual',expected=1,")
start=s.index(' c=u.Uc(',s.index('def run('));end=s.index(' rng=random.Random',start)
s=s[:start]+''' h=Path('C:/xwn818/host007'); hb=json.loads((K/'host007.json').read_text());assert hb['passed']
 for n,v in hb['files'].items():assert sha((h/n).read_bytes())==v
 page=(h/layout/'page.bin').read_bytes(); base=struct.unpack_from('<I',page,0x844)[0]
 global FB,RP,OP,SP,END
 FB=0x3000000;RP=base+0x77c0;OP=base+0x7800;SP=base+0xa000;END=base+hb['bridge_symbols']['bridge_hold']
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(base-4096,49152);c.mem_write(base-4096,b'G'*49152);c.mem_write(base,page)
 c.mem_map(BASE,0x800000);c.mem_map(FB-4096,ALLOC+8192)
 c.mem_write(FB-4096,b'G'*4096);c.mem_write(FB,b'Z'*(ALLOC+4096))
 req=list(struct.unpack('<15I',page[0x77c0:0x77fc])); original=bytes(c.mem_read(base,40960))
 c.reg_write(x.UC_X86_REG_GDTR,(0,base+0x800,31,0));c.reg_write(x.UC_X86_REG_CR0,0x40000011);c.reg_write(x.UC_X86_REG_CR4,0)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,base);c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci=dict(zip([0x80010000,0x80010004,0x80010010,0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884],[0x02a010de,2,0xfd000000,0x01b410de,1,0xc001,0x01b210de,1,0,0x8001]))
 pci_sel=[0x12345678]; low_stack=[SP]
 def stack_watch(c,address,size,data):low_stack[0]=min(low_stack[0],c.reg_read(x.UC_X86_REG_ESP))
 c.hook_add(u.UC_HOOK_CODE,stack_watch)
'''+s[end:]
s=s.replace('  if port==0x8008:', '''  if (port,width)==(0xcf8,4):return pci_sel[0]
  if (port,width)==(0xcfc,4):return pci[pci_sel[0]]
  if port==0x8008:''')
s=s.replace("  ph=phase();ports.append([ph,port,width,v])", "  if (port,width)==(0xcf8,4):pci_sel[0]=v;return\n  ph=phase();ports.append([ph,port,width,v])")
s=s.replace("c.emu_start(syms['native_transaction704'],END", "c.emu_start(base+hb['bridge_symbols']['bridge_post'],END")
s=s.replace("ret=c.reg_read(x.UC_X86_REG_EAX);", "ret=struct.unpack('<I',c.mem_read(base+0x8d4,4))[0];")
start=s.index(" assert c.mem_read(OP-16,16)");end=s.index(" assert c.mem_read(FB-4096",start)
s=s[:start]+''' assert c.mem_read(base-4096,4096)==b'G'*4096 and c.mem_read(base+40960,4096)==b'G'*4096
 assert c.mem_read(OP+160,0x8700-0x7800-160)==original[0x7800+160:0x8700]
 assert c.mem_read(base+0x8700,0x804)==original[0x8700:0x8f04]
 assert c.mem_read(RP,60)==pack(*req) and c.mem_read(base+0x900,28352)==original[0x900:0x77c0]
 assert base+0x8f04<=low_stack[0] and c.reg_read(x.UC_X86_REG_ESP)==SP
 assert pci_sel[0]==0x12345678 and c.reg_read(x.UC_X86_REG_CR3)==0
'''+s[end:]
start=s.index('try:\n run(');end=s.index('except BaseException',start)
s=s[:start]+'''try:
 for layout in ['dual','identity','relocated','scatter']:
  run('complete-'+layout,layout=layout,ext_lock=True)
  run('encoder-error-'+layout,layout=layout,fail_bus=147,bus_kind='error',expected=10)
  run('VGA-drop-'+layout,layout=layout,drop=('gr',5),drop_phase=7,expected=11)
  run('enable-drop-'+layout,layout=layout,enable_drop=True,expected=14)
 R['passed']=True
'''+s[end:]
with (K/'integration001.py').open('x',newline='\n') as f:f.write(s)
print('Prepared relocated bridge/complete transaction model')
