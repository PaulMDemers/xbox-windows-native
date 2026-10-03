from pathlib import Path
import hashlib,json,struct,sys
kit=Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
import pefile,capstone
p=kit/'package/loader/halxboxnt5.dll';data=p.read_bytes();pe=pefile.PE(data=data)
symbols={};start=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols;strings=start+count*18;i=0
while i<count:
 raw,value,section,kind,storage,aux=struct.unpack_from('<8sIhHBB',data,start+i*18)
 if raw[:4]==b'\0'*4:
  off=strings+struct.unpack_from('<I',raw,4)[0];name=data[off:data.index(b'\0',off)].decode()
 else:name=raw.rstrip(b'\0').decode()
 if 0<section<=len(pe.sections):symbols[name]=pe.sections[section-1].VirtualAddress+value
 i+=1+aux
names=['_HalInitSystem@8','_HalInitializeProcessor@8','_HalpXwnPhase0','_HalpXwnProcessorBoundary','_HalpInitPhase0','_HalpXboxInitPartIo']
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);image=pe.get_memory_mapped_image();blocks={}
for name in names:
 rva=symbols[name];end=min([v for v in symbols.values() if v>rva]+[rva+512])
 blocks[name]=[{'rva':hex(x.address),'mnemonic':x.mnemonic,'operands':x.op_str} for x in md.disasm(image[rva:end],rva)]
phase=blocks['_HalInitSystem@8'];calls=[x for x in phase if x['mnemonic']=='call']
assert len(calls)==1 and int(calls[0]['operands'],16)==symbols['_HalpXwnPhase0'],calls
assert not any(x['mnemonic'].startswith('ret') for x in phase)
processor=blocks['_HalInitializeProcessor@8'];targets=[int(x['operands'],16) for x in processor if x['mnemonic']=='call' and x['operands'].startswith('0x')]
assert targets.count(symbols['_HalpXwnProcessorBoundary'])==2
assert any(x['mnemonic'].startswith('ret') for x in processor)
r={'sha256':hashlib.sha256(data).hexdigest(),'symbols_rva':{n:hex(symbols[n]) for n in names},'blocks':blocks,'hal_phase0_original_body_unreachable':True,'processor_has_before_after_calls_and_return':True}
(kit/'hal-boundary-audit.json').write_text(json.dumps(r,indent=2)+'\n')
print('HAL processor boundaries and no-return phase-0 redirect verified.')
