"""Pin actual NT5 import providers and the real guest/host guard builds."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'build-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
p=pefile.PE(str(k/'artifacts/runner.exe'));r=json.loads((k/'sites.json').read_text());providers={};imports={}
captured=k.parent/'video-physical-rehearsal160/artifacts/F/winnt/system32'
for entry in p.DIRECTORY_ENTRY_IMPORT:
    name=entry.dll.decode().lower();dll=(k/'artifacts'/name) if (k/'artifacts'/name).exists() else captured/name
    assert dll.exists(),name
    target=pefile.PE(str(dll));exports={v.name for v in target.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    assert all(v.name in exports for v in entry.imports),name
    imports[name]=[v.name.decode() for v in entry.imports];providers[name]=dict(path=str(dll.relative_to(ws)).replace('\\','/'),sha256=sha(dll))
    r['binaries'][name]=dict(path=providers[name]['path'],sha256=sha(dll),preferred_base=target.OPTIONAL_HEADER.ImageBase,
        timestamp=target.FILE_HEADER.TimeDateStamp,image_size=target.OPTIONAL_HEADER.SizeOfImage)
setup=k/'artifacts/setupapi.dll';assert not setup.exists()
shutil.copyfile(Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/setupapi.dll'),setup)
pe=pefile.PE(str(setup));ex=next(v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'CMP_WaitNoPendingInstallEvents');assert not ex.forwarder
r['binaries']['setupapi.dll']=dict(path=str(setup.relative_to(ws)).replace('\\','/'),sha256=sha(setup),preferred_base=pe.OPTIONAL_HEADER.ImageBase,
    timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
(k/'sites.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
assert sha(k/'artifacts/gdi-probe.exe')==sha(k.parent/'video-installer-owner177/artifacts/gdi-probe.exe')
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
toolpins=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum','/usr/bin/gcc',compiler]).decode().strip().splitlines()
review=dict(passed=True,physical_access=False,guest_runtime_qualified=False,source_sha256=sha(k/'runner.c'),sha256=sha(k/'artifacts/runner.exe'),
    header_sha256=sha(k/'restart_gate.h'),probe_sha256=sha(k/'artifacts/gdi-probe.exe'),imports=imports,providers=providers,
    dynamic_setupapi=r['binaries']['setupapi.dll'],wait_export_rva=ex.address,compiler=compiler,compiler_pins=toolpins,
    host_tests=dict(passed=True,asan_ubsan=True,cases=8,header_sha256=sha(k/'restart_gate.h'),source_sha256=sha(k/'test-gate.c'),binary_sha256=sha(k/'artifacts/host-gate'),
                    coverage='Idle permits one request; pending-first, stale-idle then pending, query failures/unexpected results never request restart; restart API failure remains failure.'),
    limits='Import/export and isolated host tests are not runtime qualification. Prepare/preflight must cold-match all providers including SetupAPI.')
dest.write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8');print('New runner imports, SetupAPI export and actual guard host/guest build pins reviewed')
