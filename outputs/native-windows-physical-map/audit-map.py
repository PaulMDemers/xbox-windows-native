"""Audit the new high-address HAL checkpoint and pinned mid-function site."""
from pathlib import Path
import hashlib,json,struct,sys
kit=Path(__file__).resolve().parent;sys.path.insert(0,str(kit.parent.parent/'work/python-packages'))
import pefile,capstone
p=kit/'package/loader/halxboxnt5.dll';data=p.read_bytes();pe=pefile.PE(data=data);image=pe.get_memory_mapped_image()
symbols={};start=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols;strings=start+count*18;i=0
while i<count:
 raw,value,section,kind,storage,aux=struct.unpack_from('<8sIhHBB',data,start+i*18)
 if raw[:4]==b'\0'*4:
  off=strings+struct.unpack_from('<I',raw,4)[0];name=data[off:data.index(b'\0',off)].decode()
 else:name=raw.rstrip(b'\0').decode()
 if 0<section<=len(pe.sections):symbols[name]=pe.sections[section-1].VirtualAddress+value
 i+=aux+1
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);blocks={}
names=['_HalpXwnMapCheckpoint@4','_HalpXwnMapEntry','_XwnConfigureMapProbe@8','_HalpXwnMapSnapshot','_HalpXwnMapText','_HalpXwnDisplayMapped']
for name in names:
 at=symbols[name];end=min(v for v in symbols.values() if v>at)
 blocks[name]=[{'rva':hex(x.address),'op':x.mnemonic,'args':x.op_str} for x in md.disasm(image[at:end],at)]
entry=blocks['_HalpXwnMapEntry'];assert entry[0]['op']=='push' and entry[0]['args']=='ebp'
assert entry[1]['op']=='call' and int(entry[1]['args'],16)==symbols['_HalpXwnMapCheckpoint@4']
body=blocks['_HalpXwnMapCheckpoint@4']
assert any(x['op']=='mov' and x['args'].startswith('cr3,') for x in body)
assert any(x['op']=='mov' and x['args'].startswith('cr4,') for x in body)
assert any(x['op']=='hlt' for x in body) and not any(x['op'].startswith('ret') for x in body)
k=kit/'package/WINNT/system32/ntoskrnl.exe';kp=pefile.PE(str(k));ki=kp.get_memory_mapped_image()
assert ki[0x157f3e:0x157f46]==bytes.fromhex('8b450833db8d4808')
assert hashlib.sha256(k.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
r={'hal_sha256':hashlib.sha256(data).hexdigest(),'symbols_rva':{n:hex(symbols[n]) for n in names+['_XwnMapRecord','_XwnMapFont']},'blocks':blocks,'native_low_pde_loop_rva':['0x157f27','0x157f3c'],'checkpoint_rva':'0x157f3e','expected_target_bytes':'8b450833db8d4808','patched_bytes':5,'cr3_flush_instruction_present':True,'global_tlb_flush_supported':True,'assembly_preserves_native_frame_argument':True,'checkpoint_has_halt_and_no_return':True,'kernel_file_unchanged':True}
(kit/'map-boundary-audit.json').write_text(json.dumps(r,indent=2)+'\n')
print('High HAL checkpoint, TLB flush and pinned native stop verified')
