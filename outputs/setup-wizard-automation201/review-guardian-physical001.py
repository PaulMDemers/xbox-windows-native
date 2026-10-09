"""Check actual NT5 imports and pinned tool/source. Not a runtime qualification."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'guardian-physical-review001.json';assert not dest.exists()
p=k/'artifacts/guardian-physical001/guardian.exe';exe=pefile.PE(str(p));providers={};imports={}
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
for name,symbol in [('setupapi.dll','CMP_WaitNoPendingInstallEvents')]:
    assert symbol in provider(name)
assert (exe.OPTIONAL_HEADER.MajorSubsystemVersion,exe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
names={n for ns in imports.values() for n in ns}
assert not names.intersection({'SendInput','mouse_event','keybd_event','SetForegroundWindow','SetupDiCallClassInstaller','SetupDiSetDeviceRegistryPropertyA','RegSetValueExA','DeleteFileA','WriteProcessMemory','TerminateProcess'})
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
tool=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler],text=True).split()[0]
assert (k/'restart_gate201.h').read_bytes()==(k.parent/'video-measurement-boundary194/restart_gate.h').read_bytes()
assert (k/'setup_gate201.h').read_bytes()==(k.parent/'video-measurement-boundary194/setup_gate.h').read_bytes()
source=(k/'guardian-physical001.c').read_text();assert source.count('ExitWindowsEx(')==1 and 'EWX_FORCE' not in source and 'TerminateProcess' not in source
assert source.index('HELPER_JOIN_RESULT')<source.index('HELPER_EXIT')<source.index('xwn_wait_setup_idle(NULL')<source.index('xwn_guarded_restart(NULL')
assert json.loads((k/'guardian-physical-build001.json').read_text())['binary_sha256']==sha(p)
r=dict(passed=True,binary_sha256=sha(p),source_sha256=sha(k/'guardian-physical001.c'),compiler=compiler,compiler_sha256=tool,
    imports=imports,providers=providers,physical_access=False,runtime_qualified=False,
    write_scope='Own CREATE_NEW guardian201.log. One compiled201 helper,150sec join; refusal if helper nonzero or unjoined. Real idle and exact194 normal restart gate.',
    policy_sha256=sha(k/'policy.h'),review='Eight restart/8011 setup actual-header host assertion cases ASan/UBSan pass; exact unchanged194 guard bytes. No UI messages in guardian, no kill/forced restart. Guest runtime unverified.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Actual NT5 import/static observation review passed')
