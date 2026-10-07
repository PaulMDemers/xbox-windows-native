"""Review pinned candidate0101 write entry and cache-call boundaries, no guest edit."""
from pathlib import Path
import json,sys,hashlib
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
binary=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/fatx-directory-order-001/build-fatx/drivers/filesystems/vfatfs/vfatfs.sys')
raw=binary.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;assert base==0x10000
assert [(i.address-base) for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name==b'CcCopyWrite']==[0x1a260]
m=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
code=pe.get_data(0x12930,0x53d);ins=list(m.disasm(code,0x12930));assert sum(i.size for i in ins)==len(code)
bounds={i.address:i for i in ins};assert bounds[0x12e4a].mnemonic=='call' and bounds[0x12e50].bytes.hex()=='83ec14'
nt=json.loads((k.parent/'fatx-target-buffer/sites.json').read_text())
r=dict(scope=__doc__,source_sha256=sha(Path(__file__).read_bytes()),driver_sha256=sha(raw),preferred_base=base,
       ntdll_sha256=nt['ntdll_sha256'],ntwrite_gate=nt['sites'][0],kernel_base_expected=0x823df000,kernel_timestamp=0x4b7a1bd5,
       sites=[dict(name='write_entry',rva=0x12930,bytes=pe.get_data(0x12930,14).hex()),
              dict(name='cache_call',rva=0x12e4a,bytes=pe.get_data(0x12e4a,6).hex(),relocation_offset=2,iat_rva=0x1a260),
              dict(name='cache_return',rva=0x12e50,bytes='83ec14')],
       cache_setup_instructions=[dict(rva=i.address,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins if 0x12e22<=i.address<=0x12e64],
       layouts_sha256=sha((k.parent/'fatx-install-buffer/write-layouts.json').read_bytes()),
       limits='VfatWrite takes a pointer to context pointer. CcCopyWrite arguments at ESP are FileObject,Offset pointer,Length,Wait,Buffer. AL is Boolean on return. Entry MDL reads use an existing mapped address only, without mapping guest pages. Entry file EOF is a snapshot, not a locked final append offset.')
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Reviewed cache-write call and argument setup')
