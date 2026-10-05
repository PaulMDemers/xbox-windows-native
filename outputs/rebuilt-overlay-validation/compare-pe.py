"""Compare reconstructed PE layout with captured physical baseline; no equivalence claim."""
import json
from pathlib import Path
import sys
import zipfile

k=Path(__file__).resolve().parent
sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile
import capstone
archive=Path('E:/Codex-archive/xbox-windows-native/reconstructed-overlay-20261005/native-overlay.zip')
captured=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files')
result={'scope':__doc__,'files':[]}
with zipfile.ZipFile(archive) as z:
    for name in ['E/Applications/XWNFBoot/loader/halxboxnt5.dll','E/Applications/XWNFBoot/rosload.exe']:
        before=(captured/name).read_bytes();after=z.read(name)
        a=pefile.PE(data=before);b=pefile.PE(data=after)
        row=dict(name=name,image_base=[a.OPTIONAL_HEADER.ImageBase,b.OPTIONAL_HEADER.ImageBase],
                 entry_rva=[a.OPTIONAL_HEADER.AddressOfEntryPoint,b.OPTIONAL_HEADER.AddressOfEntryPoint],
                 sections=[])
        for x,y in zip(a.sections,b.sections):
            assert x.Name==y.Name
            aa=x.get_data();bb=y.get_data()
            diffs=[i for i,(v,w) in enumerate(zip(aa,bb)) if v!=w]
            row['sections'].append(dict(name=x.Name.rstrip(b'\0').decode(),
                rva=[x.VirtualAddress,y.VirtualAddress],sizes=[len(aa),len(bb)],
                differing_byte_positions=len(diffs),first_differences=diffs[:20],
                equal=aa==bb))
            if x.Name.rstrip(b'\0') in (b'.text',b'INIT'):
                pointers=[];covered=set()
                for block in a.DIRECTORY_ENTRY_BASERELOC:
                    for entry in block.entries:
                        off=entry.rva-x.VirtualAddress
                        if entry.type!=3 or not 0<=off<=len(aa)-4:continue
                        av=int.from_bytes(aa[off:off+4],'little');bv=int.from_bytes(bb[off:off+4],'little')
                        if av==bv:continue
                        covered.update(range(off,off+4))
                        def string(pe,v):
                            if not pe.OPTIONAL_HEADER.ImageBase<=v<pe.OPTIONAL_HEADER.ImageBase+pe.OPTIONAL_HEADER.SizeOfImage:return None
                            raw=pe.get_string_at_rva(v-pe.OPTIONAL_HEADER.ImageBase,max_length=512)
                            if not raw or any(c<32 or c>126 for c in raw):return None
                            return raw.decode('ascii')
                        sa=string(a,av);sb=string(b,bv)
                        pointers.append(dict(offset=off,old_target=hex(av),new_target=hex(bv),old_string=sa,new_string=sb,equal_strings=sa is not None and sa==sb))
                row['sections'][-1].update(changed_relocation_pointers=len(pointers),
                    difference_bytes_outside_relocation_slots=len(set(diffs)-covered),
                    relocation_string_samples=pointers[:12])
                residual=sorted(set(diffs)-covered)
                if residual:
                    cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
                    # Start at the known beginning of the section, not an assumed
                    # instruction boundary adjacent to a changed byte.
                    cs.skipdata=True
                    changed=[]
                    bi={i.address:i for i in cs.disasm(bb,y.VirtualAddress)}
                    for ins in cs.disasm(aa,x.VirtualAddress):
                        off=ins.address-x.VirtualAddress
                        if any(off<=d<off+ins.size for d in residual):
                            other=bi.get(ins.address)
                            changed.append(dict(rva=hex(ins.address),old=ins.mnemonic+' '+ins.op_str,
                                                new=(other.mnemonic+' '+other.op_str) if other else None))
                    row['sections'][-1]['non_relocation_instructions']=changed
        result['files'].append(row)
(k/'pe-layout-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([dict(name=r['name'],code=[{key:s.get(key) for key in ['name','differing_byte_positions','changed_relocation_pointers','difference_bytes_outside_relocation_slots']} for s in r['sections'] if s['name'] in ('.text','INIT')]) for r in result['files']],indent=2))
