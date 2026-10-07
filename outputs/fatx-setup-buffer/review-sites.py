"""Review the exact owned SetupAPI seek/write/flush routine and capture sites."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile,capstone
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/setupapi.dll');data=p.read_bytes();sha=hashlib.sha256(data).hexdigest()
assert sha=='1d0a6e9d062a51e71eaae93d776746823834f5c518096d340f2b332fc059a23d'
pe=pefile.PE(data=data);base=pe.OPTIONAL_HEADER.ImageBase;assert base==0x77880000
imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
assert imports[0x7788124c]=='SetFilePointer' and imports[0x77881290]=='WriteFile' and imports[0x778811b0]=='FlushFileBuffers' and imports[0x77881250]=='lstrlenA'
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);raw=pe.get_data(0x4c5a8,101);ins=list(md.disasm(raw,base+0x4c5a8));bounds={i.address:i for i in ins}
assert sum(i.size for i in ins)==len(raw)
spec=[('seek_return',0x778cc5bb,3),('write_call',0x778cc5e8,6),('write_return',0x778cc5ee,3),('flush_call',0x778cc5fd,6),('flush_return',0x778cc603,2)]
sites=[]
for name,a,n in spec:
 assert a in bounds
 sites.append(dict(name=name,address=a,rva=a-base,bytes=pe.get_data(a-base,n).hex()))
r=dict(scope=__doc__,setupapi_sha256=sha,preferred_base=base,routine_rva=0x4c5a8,routine_bytes=raw.hex(),instructions=[dict(address=i.address,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins],sites=sites,imports={hex(a):imports[a] for a in [0x7788124c,0x77881290,0x778811b0,0x77881250]},interpretation='Routine calls SetFilePointer(handle,0,NULL,FILE_END), converts its string, passes lstrlenA bytes to WriteFile with no OVERLAPPED, frees temporary string, and calls FlushFileBuffers only when WriteFile returned true. Capture post-flush EAX before MOV EAX,EDI replaces it with WriteFile BOOL.',limits='Preferred addresses verified live; bytes/disassembly establish this routine only. Runtime file identity and actual written bytes require independent evidence.')
dest=k/'sites.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Reviewed SetupAPI seek/write/flush instruction boundaries')
