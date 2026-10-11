"""Inspect non-relocation instruction differences in the two pinned baselines."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
k=Path(__file__).resolve().parent;summary=json.loads((k/'baseline-comparison001.json').read_text())
pes=[]
for row in summary['inputs']:
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];pes.append(pefile.PE(str(p)))
dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);rows=[]
for group in summary['sections']:
    if not group['first_nonrelocation_offsets']:continue
    sections=[next(s for s in pe.sections if s.Name.rstrip(b'\0').decode()==group['name']) for pe in pes]
    instructions=[list(dis.disasm(s.get_data()[:s.Misc_VirtualSize],pe.OPTIONAL_HEADER.ImageBase+s.VirtualAddress)) for pe,s in zip(pes,sections)]
    seen=set()
    for value in group['first_nonrelocation_offsets']:
        offset=int(value,16);pair=[]
        for pe,sec,ins in zip(pes,sections,instructions):
            address=pe.OPTIONAL_HEADER.ImageBase+sec.VirtualAddress+offset
            v=next(v for v in ins if v.address<=address<v.address+v.size)
            pair.append(dict(offset=hex(v.address-pe.OPTIONAL_HEADER.ImageBase-sec.VirtualAddress),instruction=v.mnemonic+' '+v.op_str,bytes=v.bytes.hex()))
        key=(group['name'],pair[0]['offset'])
        if key not in seen:rows.append(dict(section=group['name'],installed=pair[0],rebuilt=pair[1]));seen.add(key)
dest=k/'baseline-instructions001.json';assert not dest.exists();dest.write_text(json.dumps(dict(scope=__doc__,sampled_instruction_pairs=rows,limits='Addresses and path offsets can change under reconstruction. These samples do not prove complete image equivalence.'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows[:8],indent=2))
