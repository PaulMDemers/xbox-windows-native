"""Review actual190 helper/host tests against owned NT5 providers; no guest/physical access."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
build=read(k/'build002.json');exe=k/'artifacts/build002/runner.exe'
assert build['built'] and build['host_tests'] and build['binary_sha256']==sha(exe) and build['source_sha256']==sha(k/'runner.c')
old=k.parent/'video-word-order186'
assert (k/'restart_gate.h').read_bytes()==(old/'restart_gate.h').read_bytes()
assert (k/'test-restart.c').read_bytes()==(old/'test-gate.c').read_bytes()
pe=pefile.PE(str(exe));assert pe.FILE_HEADER.Machine==0x14c
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
providers={};imports={}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    name=entry.dll.decode().lower();path=archive/name;dll=pefile.PE(str(path))
    exported={v.name for v in dll.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    assert all(v.name in exported for v in entry.imports),name
    imports[name]=[v.name.decode() for v in entry.imports]
    providers[name]=dict(path=str(path),sha256=sha(path),image_base=dll.OPTIONAL_HEADER.ImageBase,timestamp=dll.FILE_HEADER.TimeDateStamp)
assert 'Sleep' in imports['kernel32.dll'] and 'GetTickCount' in imports['kernel32.dll']
assert not any(name.startswith(('SetupDi','CM_')) for values in imports.values() for name in values)
setup=archive/'setupapi.dll';sp=pefile.PE(str(setup))
wait=next(v for v in sp.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'CMP_WaitNoPendingInstallEvents');assert not wait.forwarder
providers['setupapi.dll']=dict(path=str(setup),sha256=sha(setup),wait_export_rva=wait.address)
source=(k/'runner.c').read_text(encoding='utf-8')
assert source.index('xwn_wait_setup_idle(NULL')<source.index('for(i=0;i<5;i++)')<source.index('CreateProcessA(')
assert source.index('INSTALL_BEFORE_SAMPLE')<source.index('CreateProcessA(')<source.index('INSTALL_AFTER_SAMPLE')<source.index('xwn_guarded_restart(NULL')
assert source.count('ExitWindowsEx(')==1 and '300000,5000,250' in source
assert 'SetupDi' not in source and 'SendMessage' not in source and 'TerminateProcess' not in source
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
toolpins=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum','/usr/bin/gcc',compiler]).decode().strip().splitlines()
rows={p.name:sha(p) for p in [k/'runner.c',k/'setup_gate.h',k/'restart_gate.h',k/'test-setup.c',k/'test-restart.c',k/'Build002.ps1']}
r=dict(passed=True,physical_access=False,guest_runtime_qualified=False,binary_sha256=sha(exe),sources=rows,compiler=compiler,compiler_pins=toolpins,imports=imports,providers=providers,
    unchanged_restart_gate=True,unchanged_probe_path=str(old/'artifacts/gdi-probe.exe'),unchanged_probe_sha256=sha(old/'artifacts/gdi-probe.exe'),
    host_tests=dict(asan_ubsan=True,setup_cases=8001,restart_cases=8,test_setup_sha256=sha(k/'artifacts/build002/test-setup'),test_restart_sha256=sha(k/'artifacts/build002/test-restart')),
    limits='Pinned owned archive providers/export checks and host shared-function tests only. Fresh guest preflight must match actual providers. No runtime, physical display or setup qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('190 host cases/NT5 imports/subsystem/unchanged restart guard reviewed; no guest launch')
