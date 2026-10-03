import pathlib,sys,struct
r=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(r/'work/python-packages'))
import pefile
from capstone import *
d=Cs(CS_ARCH_X86,CS_MODE_32);d.detail=True;d.skipdata=True
for file in ['ntoskrnl.exe','hal.dll']:
 p=pefile.PE(str(r/'outputs/native-windows-nt5/installed-files/WINNT/system32'/file));b=p.OPTIONAL_HEADER.ImageBase
 print('\nFILE',file,hex(b))
 ex={s.name.decode():s.address for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 if file=='ntoskrnl.exe':
  for n in ['KeUpdateSystemTime','Kei386EoiHelper','KeUpdateRunTime','KiDispatchInterrupt','KiDeliverApc']:
   print('\nEXPORT',n)
   for i in d.disasm(p.get_data(ex[n],640 if n=='KeUpdateSystemTime' else 96),b+ex[n]):print(hex(i.address),i.mnemonic,i.op_str)
 else:
  targets={s.address:s.name.decode() for m in p.DIRECTORY_ENTRY_IMPORT for s in m.imports if s.name and s.name.decode() in ['KeUpdateSystemTime','Kei386EoiHelper','KeUpdateRunTime','KiDeliverApc','KiDispatchInterrupt']}
  for sec in p.sections:
   if not sec.Characteristics&0x20000000:continue
   ins=list(d.disasm(sec.get_data(),b+sec.VirtualAddress))
   for j,i in enumerate(ins):
    if i.mnemonic in ['call','jmp'] and len(i.operands)==1 and i.operands[0].type==CS_OP_MEM and (i.operands[0].mem.disp & 0xffffffff) in targets:
     print('\nREFERENCE',targets[i.operands[0].mem.disp & 0xffffffff])
     for x in ins[max(0,j-22):j+4]:print(hex(x.address),x.mnemonic,x.op_str)



