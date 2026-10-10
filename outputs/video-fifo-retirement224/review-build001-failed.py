"""Once-only review of actual224 import providers, preserved failure and native sections."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review002.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build002.json');assert b['passed'] and not b['guest_launch']
for name,digest in b['input_pins'].items():assert sha(k/name)==digest,name
for name,digest in read(k/'build001.json')['input_pins'].items():assert sha(k/'prior-build001'/name)==digest,name
f=read(k.parent/'video-upload-runtime211/fixture-candidate001.json');base=k.parent/'video-upload-runtime211/artifacts'
names={'ntoskrnl.exe':'F/winnt/system32/ntoskrnl.exe','hal.dll':'E/Applications/XWNFBoot/loader/halxboxnt5.dll',
       'kernel32.dll':'F/winnt/system32/kernel32.dll','advapi32.dll':'F/winnt/system32/advapi32.dll','user32.dll':'F/winnt/system32/user32.dll',
       'setupapi.dll':'F/winnt/system32/setupapi.dll'}
providers={};exports={}
for dll,path in names.items():
    p=base/path;expected=(f['files']|f['protected'])[path];assert sha(p)==expected
    pe=pefile.PE(str(p));exports[dll]={s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    providers[dll]=dict(path=str(p.relative_to(ws)),sha256=expected)
assert 'CMP_WaitNoPendingInstallEvents' in exports['setupapi.dll']
bins={}
for name,row in b['native'].items():
    p=k/'artifacts/build002'/('probe.exe' if name=='probe.exe' else name+'/resident.sys')
    assert sha(p)==row['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
    assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
    imports={}
    for d in pe.DIRECTORY_ENTRY_IMPORT:
        dll=d.dll.decode().lower();symbols=[s.name.decode() for s in d.imports]
        assert set(symbols)<=exports[dll],(dll,symbols);imports[dll]=symbols
    sections=[dict(name=s.Name.rstrip(b'\0').decode(),flags=s.Characteristics,rva=s.VirtualAddress,bytes=s.Misc_VirtualSize) for s in pe.sections]
    if name!='probe.exe':
        assert pe.OPTIONAL_HEADER.Subsystem==1 and not any(s['name'].startswith(('PAGE','INIT')) for s in sections)
        assert all(not s['flags']&0x02000000 for s in sections if s['name'] in ['.text','.rdata','.bss','.idata'])
        assert set(imports)=={'ntoskrnl.exe','hal.dll'}
    bins[name]=dict(**row,imports=imports,sections=sections,entry_rva=pe.OPTIONAL_HEADER.AddressOfEntryPoint)
assert {'MmMapIoSpace','MmUnmapIoSpace'}<=set(bins['candidate001']['imports']['ntoskrnl.exe'])
assert 'READ_REGISTER_ULONG' in bins['candidate001']['imports']['hal.dll']
assert 'MmMapIoSpace' not in bins['control001']['imports']['ntoskrnl.exe']
assert sha(k/'context.c')==sha(k.parent/'video-resident-context222/context.c')
assert sha(k/'context.h')==sha(k.parent/'video-resident-context222/context.h')
r=dict(passed=True,physical_access=False,guest_launch=False,gpu_writes=False,gpu_ownership_qualified=False,
       source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build002.json'),providers=providers,binaries=bins,
       limits='Pinned provider export names and on-disk resident sections; not executed ABI, runtime PTE residency, GPU drain or physical qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Native224 imports/sections/source preservation PASS')
