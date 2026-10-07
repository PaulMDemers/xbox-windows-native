"""Pin owned NT5 syscall stubs and breakpoint instruction boundaries."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntdll.dll')
data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha=='ed276d6a3ae93c71a6cef73672b82e3808211da1c63bf7d3e23d93294e54813a'
pe=pefile.PE(data=data);md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);sites=[]
for name,argc in [('NtWriteFile',9),('NtFlushBuffersFile',2),('NtClose',1)]:
 e=next(e for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==name.encode());raw=pe.get_data(e.address,14);ins=list(md.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+e.address))
 assert [i.mnemonic for i in ins]==['mov','lea','int','ret'] and ins[2].op_str=='0x2e' and int(ins[-1].op_str,0)==argc*4
 sites.append(dict(name=name,address=pe.OPTIONAL_HEADER.ImageBase+e.address,rva=e.address,argc=argc,bytes=raw.hex(),instructions=[dict(address=i.address,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins]))
 if name=='NtWriteFile':sites.append(dict(name='NtWriteFile_return',address=ins[-1].address,rva=ins[-1].address-pe.OPTIONAL_HEADER.ImageBase,argc=0,bytes=ins[-1].bytes.hex()))
r=dict(scope=__doc__,ntdll_sha256=sha,preferred_base=pe.OPTIONAL_HEADER.ImageBase,sites=sites,physical_access=False,limits='Preferred addresses are verified against live instruction bytes on each hit. Breakpoint pauses alter timing. Return stub is before RET after INT2E; status pending is not completion.')
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
