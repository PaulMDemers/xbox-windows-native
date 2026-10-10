"""Pinned NT5 provider/export and nondiscardable section review before launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review005.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build005.json');assert b['status']=='compiled_host_tests_passed' and all(r['passed'] for r in b['host_runs'])
for name,digest in b['source_pins'].items():assert sha(k/name)==digest,name
bridge=read(k/'bridge001.json');assert bridge['passed']
for name,digest in bridge['inputs'].items():assert sha(k/name)==digest,name
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
    p=k/'artifacts/build005'/name;assert sha(p)==row['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
    assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
    imports={}
    for d in pe.DIRECTORY_ENTRY_IMPORT:
        dll=d.dll.decode().lower();symbols=[s.name.decode() for s in d.imports]
        assert set(symbols)<=exports[dll],(dll,symbols);imports[dll]=symbols
    sections=[dict(name=s.Name.rstrip(b'\0').decode(),flags=s.Characteristics,rva=s.VirtualAddress,bytes=s.Misc_VirtualSize) for s in pe.sections]
    if name=='resident.sys':
        assert pe.OPTIONAL_HEADER.Subsystem==1
        assert not any(s['name'].startswith(('PAGE','INIT')) for s in sections)
        assert all(not s['flags']&0x02000000 for s in sections if s['name'] in ['.text','.rdata','.bss','.idata'])
        assert set(imports)=={'ntoskrnl.exe','hal.dll'}
    bins[name]=dict(**row,imports=imports,sections=sections,entry_rva=pe.OPTIONAL_HEADER.AddressOfEntryPoint)
for old in ['001','002','003']:
    record=read(k/('build'+old+'.json'))
    for name,digest in record['source_pins'].items():assert sha(k/('prior-build'+old)/name)==digest,(old,name)
r=dict(passed=True,physical_access=False,guest_launch=False,gpu_access=False,native_runtime_qualified=False,
       source_sha256=sha(Path(__file__)),build_sha256=sha(k/'build005.json'),bridge_sha256=sha(k/'bridge001.json'),
       providers=providers,binaries=bins,limits='Actual intended211 providers/export names and on-disk sections; not executed NT5 ABI, actual page residency, kernel worker timing, GPU ownership or physical qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Native222 imports/sections/source preservation PASS')
