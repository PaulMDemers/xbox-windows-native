"""Check actual NT5 imports and pinned tool/source. Not a runtime qualification."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review001.json';assert not dest.exists()
p=Path('D:/xwn313/build001/wizard.exe');exe=pefile.PE(str(p));providers={};imports={}
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
assert not names.intersection({'ExitWindowsEx','SendInput','mouse_event','keybd_event','SetupDiCallClassInstaller','SetupDiSetDeviceRegistryPropertyA','RegSetValueExA','DeleteFileA','WriteProcessMemory','TerminateProcess'})
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
tool=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler],text=True).split()[0]
source=(k/'wizard313.c').read_text();assert 'SendMessageTimeoutA((HWND)w.button,BM_CLICK,0,0,' in source
assert 'GetForegroundWindow()!=h' in source and 'info.hwndActive!=h' in source and '||!welcome(h)' in source
assert 'PSM_PRESSBUTTON' not in source
assert 'SetForegroundWindow' in names
assert 'AttachThreadInput' not in names
assert sha(k/'policy.h')==sha(k.parent/'setup-wizard-automation201/policy.h')
assert source.replace('#include \"activation.inc\"\n','').replace('    activate313(h,w.tid);\n','')==(k.parent/'setup-wizard-automation201/wizard006.c').read_text()
r=dict(passed=True,binary_sha256=sha(p),source_sha256=sha(k/'wizard313.c'),compiler=compiler,compiler_sha256=tool,
    imports=imports,providers=providers,physical_access=False,runtime_qualified=False,
    write_scope='Exclusive wizard201.log in own folder only,1MiB bound. Observe or explicit verified Cancel BM_CLICK; new compiled emulator-only activation opt-in. No device/registry/restart.',
    policy_sha256=sha(k/'policy.h'),review='Singlethreaded, bounded remoteASCIIcommand/read/window waits, exactinstances andliveprocesscreation pairing. Up to8unique processowner Cancelactions,120sec total. Only verified active/foreground welcome page allows BM_CLICK to its actual enabled Cancel button. Read-only GUI context retained. One emulator-only SetForegroundWindow attempt per held PID/creation,8owner bound; unchanged actual Cancel guard. New adapter Win32 calls host modeled; runtime still unverified.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Actual NT5 import/static observation review passed')
