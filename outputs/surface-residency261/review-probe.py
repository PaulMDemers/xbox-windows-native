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
exports=[v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'X259Checkpoint'];assert len(exports)==1
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
native=(k/'artifacts/build001/expected.bin').read_bytes();assert len(native)==4*16384
oracle=[]
for mode in range(4):
    # Different expression/layout than the compiled C generator.
    buf=bytearray((((i*37)+(i>>4)*19+(i>>8)*7)^(83 if mode==3 else 0))%256 for i in range(16384))
    if mode<3:
        for y in range(11):
            for x in range(13):
                buf[4096+y*64+x*4:4100+y*64+x*4]=bytes(((x*17+y*29+3+mode*31)%256,(x*71+y*11+19+mode*47)%256,(x*5+y*97+101+mode*67)%256,255))
    assert native[mode*16384:(mode+1)*16384]==buf
    oracle.append(bytes(buf))
oldoracle=json.loads((k.parent/'surface-pattern258/pixel-oracle-review.json').read_text())
assert hashlib.sha256(oracle[0]).hexdigest()==oldoracle['expected_read_sha256']
assert hashlib.sha256(oracle[3]).hexdigest()==oldoracle['expected_post_cpu_store_sha256']
negative={}
cpu0=bytes((((i*37)+(i>>4)*19+(i>>8)*7))%256 for i in range(16384))
negative['no_renderer_injection']=cpu0!=oracle[0]
negative['stale_gpu_after_cpu_store']=oracle[2]!=oracle[3]
negative['old_texture_at_read']=oracle[0]!=oracle[1]
for pos,name in [(4095,'prefix'),(4096+52,'row_padding'),(4096+64*11,'suffix'),(4096+17,'pixel')]:
    bad=bytearray(oracle[1]);bad[pos]^=1;negative[name]=bad!=oracle[1]
for name in ['flipped_rows','wrong_pitch','red_blue_swap']:
    bad=bytearray(cpu0)
    for y in range(11):
        for x in range(13):
            src=4096+(10-y if name=='flipped_rows' else y)*64+x*4
            pixel=oracle[1][src:src+4]
            if name=='red_blue_swap':pixel=pixel[2:3]+pixel[1:2]+pixel[0:1]+pixel[3:4]
            dst=4096+y*(52 if name=='wrong_pitch' else 64)+x*4;bad[dst:dst+4]=pixel
    negative[name]=bad!=oracle[1]
assert all(negative.values())
r=dict(passed=True,guest_launch=False,gl_executed=False,pixel_preservation_proved=False,physical_access=False,
    source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build001.json'),native_sha256=sha(p),
    imports=imports,preferred_image_base=pe.OPTIONAL_HEADER.ImageBase,checkpoint_rva=rva,
    checkpoint_instructions=ins,checkpoint_abi='cdecl: stage, Reply pointer, File HANDLE at stopped entry; verify actual process and resident code',
    symbols_rva=symbols,exact_independent_bytes=len(native),expected_sha256=[hashlib.sha256(v).hexdigest() for v in oracle],
    negative_controls=negative,limits='Compiled probe/host oracle only. No renderer hook, runtime ownership attestation or GL execution yet.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('259 probe/import/checkpoint/oracle review PASS; no guest or GL execution')
