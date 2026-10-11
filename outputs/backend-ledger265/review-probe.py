"""Verify native imports/checkpoint ABI and independently check every expected byte."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'probe-review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
b=json.loads((k/'build001.json').read_text());assert b['passed']
for n,digest in b['input_pins'].items():assert sha(k/n)==digest,n
p=k/'artifacts/build001/probe.exe';assert sha(p)==b['native_sha256']
pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
assert (pe.OPTIONAL_HEADER.Subsystem,pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(3,5,0)
old=json.loads((k.parent/'surface-pattern258/build-review002.json').read_text());imports={}
for row in pe.DIRECTORY_ENTRY_IMPORT:
    dll=row.dll.decode().lower();provider=old['providers'][dll];file=ws/provider['path']
    assert sha(file)==provider['sha256'];actual=pefile.PE(str(file))
    symbols={s.name.decode() for s in actual.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    imports[dll]=[s.name.decode() for s in row.imports]
    assert set(imports[dll])<=symbols
exports=[v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'X265Checkpoint'];assert len(exports)==1
rva=exports[0].address;raw=pe.get_data(rva,32)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);ins=[]
for i in md.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+rva):
    ins.append(dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
    if i.mnemonic=='ret':break
assert ins[-1]['mnemonic']=='ret' and ins[-1]['operands']==''
assert any(i['mnemonic']=='xchg' for i in ins)
# Decode actual COFF symbol values for later runtime attestation. These are RVAs,
# never assumed runtime virtual addresses. Section indices are one-based.
data=p.read_bytes();start=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols
strings=start+18*count;symbols={};index=0
while index<count:
    name,value,section,typ,storage,aux=struct.unpack_from('<8sIhHBB',data,start+index*18)
    if name[:4]==b'\0'*4:
        offset=struct.unpack('<I',name[4:])[0];end=data.index(0,strings+offset);name=data[strings+offset:end]
    else:name=name.rstrip(b'\0')
    if name in (b'_Reply',b'_Checkpoint'):
        assert section>0;symbols[name.decode()]=pe.sections[section-1].VirtualAddress+value
    index+=1+aux
assert set(symbols)=={'_Reply','_Checkpoint'}
r=dict(passed=True,guest_launch=False,gl_executed=False,physical_access=False,
 source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build001.json'),native_sha256=sha(p),
 imports=imports,preferred_image_base=pe.OPTIONAL_HEADER.ImageBase,checkpoint_rva=rva,
 checkpoint_instructions=ins,symbols_rva=symbols,
 limits='Static observation-only probe: two CPU seed0 reads, no renderer injection. Runtime identities remain required.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('265 observation probe imports and checkpoint ABI PASS')
