"""Matched-binary evidence for fixed cleanup status and the PnP token argument."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
root=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);result={}
for name,blocks in [('advapi32.dll',[(0x27015,0x27042),(0x124d8,0x12567)]),('umpnpmgr.dll',[(0x5989,0x59c7),(0x662b,0x66e0)])]:
    f=root/name;pe=pefile.PE(str(f));base=pe.OPTIONAL_HEADER.ImageBase
    imports={hex(i.address):i.name.decode() for dll in pe.DIRECTORY_ENTRY_IMPORT for i in dll.imports if i.name}
    result[name]=dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),preferred_base=hex(base),blocks=[])
    for first,end in blocks:
        result[name]['blocks'].append(dict(start_rva=hex(first),end_rva=hex(end),instructions=[dict(rva=hex(i.address-base),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(pe.get_data(first,end-first),base+first)]))
    result[name]['relevant_imports']={a:n for a,n in imports.items() if n in ['NtTerminateProcess','CloseHandle','CreateProcessAsUserW','ReleaseMutex','WaitForMultipleObjects']}
r=dict(scope=__doc__,binaries=result,
       conclusions=['advapi32 cleanup explicitly pushes constant5 before NtTerminateProcess; it is not the original failure code.','umpnpmgr creation call at RVA66d8 supplies the saved handle at RVA15b64 to CreateProcessAsUserW.','A separate cleanup block closes that saved handle and later clears its storage. Static order alone does not establish which close caused the observed invalid handle or a race.'],
       limits='Private owned binary inspection, not redistributed binaries, source provenance or a patch. Runtime handle lifetime and popup cause require separate evidence.')
(k/'unwind-review.json').write_text(json.dumps(r,indent=2)+'\n')
