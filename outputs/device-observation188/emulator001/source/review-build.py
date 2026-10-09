"""Check actual NT5 imports and pinned tool/source. Not a runtime qualification."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
p=k/'artifacts/build003/observer.exe';exe=pefile.PE(str(p));providers={};imports={}
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
capture=k.parent/'video-word-physical187/artifacts/F/winnt/system32'
def provider(name):
    root=capture if (capture/name.lower()).exists() else base
    path=next(v for v in root.iterdir() if v.name.lower()==name.lower())
    pe=pefile.PE(str(path));exports={v.name.decode():v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    providers[name.lower()]=dict(path=str(path),sha256=sha(path))
    return exports
for entry in exe.DIRECTORY_ENTRY_IMPORT:
    name=entry.dll.decode();exports=provider(name)
    names=[v.name.decode() for v in entry.imports];assert all(n in exports for n in names),name
    imports[name]=names
    for n in names:
        f=exports[n].forwarder
        if f:
            module,symbol=f.decode().rsplit('.',1);assert symbol in provider(module+'.dll')
for name,symbol in [('ntdll.dll','NtQueryInformationProcess'),('setupapi.dll','CMP_WaitNoPendingInstallEvents')]:
    assert symbol in provider(name)
assert (exe.OPTIONAL_HEADER.MajorSubsystemVersion,exe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
names={n for ns in imports.values() for n in ns}
assert not names.intersection({'ExitWindowsEx','SendInput','mouse_event','keybd_event','SetForegroundWindow','SetupDiCallClassInstaller','SetupDiSetDeviceRegistryPropertyA','RegSetValueExA','DeleteFileA','WriteProcessMemory','TerminateProcess'})
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
tool=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler],text=True).split()[0]
r=dict(passed=True,binary_sha256=sha(p),source_sha256=sha(k/'probe003.c'),compiler=compiler,compiler_sha256=tool,
    imports=imports,providers=providers,physical_access=False,runtime_qualified=False,
    write_scope='Exclusive observer.log in own folder only; bounded 4 MiB. Read-only PnP/UI/volume queries. No restart.',
    review='Single-threaded static 8193/4096-byte scratch arrays avoid CRT stack helper; counted blobs at most4096 bytes, hex batched. Query buffers and WM_GETTEXT waits bounded. Missing/error fields retained.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Actual NT5 import/static observation review passed')
