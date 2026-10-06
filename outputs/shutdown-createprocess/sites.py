"""Pin user-mode creation/unwind sites from matching owned NT5 binaries."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
root=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
sites=[];binaries={};disassembly={}
for name in ['kernel32.dll','advapi32.dll','ntdll.dll']:
    file=root/name;pe=pefile.PE(str(file));base=pe.OPTIONAL_HEADER.ImageBase
    binaries[name]=dict(sha256=hashlib.sha256(file.read_bytes()).hexdigest(),preferred_base=hex(base))
    exports={e.name.decode():e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
    specs={'kernel32.dll':[('CreateProcessInternalW',11,'create'),('CreateProcess_CsrReply',0,'csr')],
           'advapi32.dll':[('CreateProcessAsUserW',11,'create')],
           'ntdll.dll':[('NtTerminateProcess',2,'terminate'),('NtSetInformationProcess_return',4,'setinfo_return'),('NtRaiseHardError',6,'harderror'),('NtQueryInformationToken_return',5,'token_return'),('NtDuplicateToken_return',6,'duplicate_return')]}[name]
    for symbol,argc,kind in specs:
        rva=0x2663c if kind=='csr' else exports[symbol.removesuffix('_return')]+11 if kind.endswith('_return') else exports[symbol]
        raw=pe.get_data(rva,3)
        if kind=='csr':assert raw.hex()=='399d50'
        if kind=='setinfo_return':assert raw.hex()=='c21000'
        sites.append(dict(name=symbol,module=name,rva=rva,address=base+rva,bytes=raw.hex(),argc=argc,kind=kind))
    if name=='kernel32.dll':
        md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
        rows=list(md.disasm(pe.get_data(exports['CreateProcessInternalW'],0x26981-exports['CreateProcessInternalW']),base+exports['CreateProcessInternalW']))
        disassembly[name]=[dict(rva=hex(i.address-base),bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in rows if 0x26627<=i.address-base<0x2667f]
src=ws/'outputs/native-windows-nt5-kernel';pubs=json.loads((src/'kernel-publics.json').read_text())['symbols']
prior=json.loads((k.parent/'shutdown-installer-trace/site-review.json').read_text())
for s in prior['sites']:
    if 'HardError' in s['name'] or s['name']=='_NtShutdownSystem@4':sites.append(dict(s,module='ntoskrnl.exe',kind='shutdown' if 'Shutdown' in s['name'] else 'harderror'))
r=dict(scope=__doc__,binaries=binaries,kernel_sha256=prior['kernel_sha256'],sites=sites,disassembly=disassembly,
       thread_owner_offset=prior['thread_owner_offset'],teb_offset=32,
       limits='User-mode sites use preferred image bases and verify bytes when hit. Dynamic return sites are tied to the originating ETHREAD and exact saved return address. No changed return values or guest data.')
(k/'site-review.json').write_text(json.dumps(r,indent=2)+'\n')
