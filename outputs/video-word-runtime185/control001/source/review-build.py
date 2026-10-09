"""Pin probe/unchanged launcher against owned actual NT5 export tables."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
source=k.parent/'video-physical-rehearsal160/artifacts/F/winnt/system32';binaries={}
for name in ['runner.exe','gdi-probe.exe']:
    p=pefile.PE(str(k/'artifacts'/name));imports={};providers={}
    for entry in p.DIRECTORY_ENTRY_IMPORT:
        dllname=entry.dll.decode();dll=next((v for v in source.iterdir() if v.name.lower()==dllname.lower()),None)
        if dll is None:
            assert dllname.lower()=='advapi32.dll';dll=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/advapi32.dll')
        target=pefile.PE(str(dll));exports={v.name for v in target.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
        assert all(v.name in exports for v in entry.imports),dllname
        imports[dllname]=[v.name.decode() for v in entry.imports];providers[dllname]=dict(path=str(dll),sha256=sha(dll))
    assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    binaries[name]=dict(sha256=sha(k/'artifacts'/name),imports=imports,providers=providers)
assert binaries['runner.exe']['sha256']==sha(k.parent/'device-settled-reboot181/artifacts/runner.exe')
assert 'ExtEscape' in binaries['gdi-probe.exe']['imports']['GDI32.dll']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(k/'gdi-probe.c'),binaries=binaries,physical_access=False,
    guest_runtime_qualified=False,driver_changed=True,compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc',
    compiler_flags='-Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin; entry mainCRTStartup@0; console5.0'),indent=2)+'\n',encoding='utf-8')
print('Unchanged launcher and v7 ExtEscape imports reviewed against actual NT5')
