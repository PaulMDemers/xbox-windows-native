"""Preserve linked HAL terminal/ABI disassembly and non-discardable ownership."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
k=Path(__file__).resolve().parent;p=k/'artifacts/build001/halxboxnt5.dll';raw=p.read_bytes()
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
symbols=[];ptr=pe.FILE_HEADER.PointerToSymbolTable;n=pe.FILE_HEADER.NumberOfSymbols;strings=ptr+18*n;i=0
while i<n:
    name,value,section,typ,storage,aux=struct.unpack_from('<8sIhHBB',raw,ptr+18*i)
    if name[:4]==b'\0'*4:
        off=struct.unpack_from('<I',name,4)[0];start=strings+off;name=raw[start:raw.index(b'\0',start)]
    else:name=name.rstrip(b'\0')
    if section>0:symbols.append(dict(name=name.decode('ascii',errors='replace'),rva=pe.sections[section-1].VirtualAddress+value,section=section,kind=typ))
    i+=1+aux
dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
result=dict(scope=__doc__,sha256=hashlib.sha256(raw).hexdigest(),symbols=[],disassembly={})
for token in ('HalpXboxPowerAction','HalpSmbusOwner','HalpSmbusTerminalResult','XwnSmbusReadV1'):
    matches=[v for v in symbols if token in v['name']];assert matches,token
    for sym in matches:
        sec=pe.sections[sym['section']-1];assert not sec.Characteristics&0x02000000
        result['symbols'].append(dict(**sym,section_name=sec.Name.decode().rstrip('\0'),non_discardable=True))
        if sym['kind']&0x20:
            following=[v['rva'] for v in symbols if v['kind']&0x20 and v['rva']>sym['rva'] and v['section']==sym['section']]
            length=min(following,default=sym['rva']+1024)-sym['rva']
            ins=list(dis.disasm(pe.get_data(sym['rva'],length),base+sym['rva']))
            result['disassembly'][sym['name']]=[dict(address=hex(v.address),bytes=v.bytes.hex(),instruction=v.mnemonic+' '+v.op_str) for v in ins]
            if token=='HalpXboxPowerAction':
                cli=next(j for j,v in enumerate(ins) if v.mnemonic=='cli')
                assert not any(v.mnemonic in ('call','in','out','xchg','cmpxchg') for v in ins[:cli])
                assert any(v.mnemonic=='hlt' for v in ins)
                result['terminal_disables_interrupts_before_calls_or_io']=True
dest=k/'linked-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Linked ownership/entry symbols resident; CLI precedes terminal calls/I/O')
