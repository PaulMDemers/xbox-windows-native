"""Pin actual NT5 probe imports and fresh119 observation protocol before launch."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
native=k.parent/'video-upload-accounting210';assert read(native/'build-review.json')['passed'] and read(native/'host-tests001.json')['passed']
assert read(k/'upload-parser-tests.json')['passed']
for n,h in read(k/'upload-parser-tests.json')['source_pins'].items():assert sha(k/n)==h
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32');binaries={};providers={}
for name in ['runner.exe','replay.exe','wizard.exe']:
 p=pefile.PE(str(k/'artifacts'/name));imports={}
 assert p.FILE_HEADER.Machine==0x14c and (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
 for entry in p.DIRECTORY_ENTRY_IMPORT:
  dllname=entry.dll.decode().lower();dll=archive/dllname;exports={v.name for v in pefile.PE(str(dll)).DIRECTORY_ENTRY_EXPORT.symbols if v.name}
  assert all(v.name in exports for v in entry.imports),dllname
  imports[dllname]=[v.name.decode() for v in entry.imports];providers[dllname]=dict(path=str(dll),sha256=sha(dll))
 binaries[name]=dict(sha256=sha(k/'artifacts'/name),imports=imports)
old=k.parent/'video-scalar-runtime209';oldreview=read(old/'build-review.json')
for n in ['runner.exe','wizard.exe']:assert binaries[n]['sha256']==oldreview['binaries'][n]['sha256']
assert binaries['replay.exe']['sha256']==read(k/'probe-build001.json')['binary_sha256']
assert sha(k/'gdi-probe.c')==read(k/'probe-build001.json')['source_sha256']
assert sha(k/'text-cases.c')==sha(old/'text-cases.c')
for name in ['ntdll.dll','setupapi.dll']:providers[name]=dict(path=str(archive/name),sha256=sha(archive/name))
s=(k/'gdi-probe.c').read_text();a=s.index('    for(i=0;i<40;i++) {',s.index('static BOOL windowcase'));b=s.index('        for(phase=0;phase<4;',a)
critical=s[a:b];assert 'record(' not in critical.replace('record("MISMATCH_WINDOW_round_index",i,j,0);','')
assert all('uploadsnapshot(upload[%d])'%i in critical for i in range(4))
assert critical.index('uploadsnapshot(upload[0])')<critical.index('SetWindowPos')<critical.index('uploadsnapshot(upload[1])')<critical.index('InvalidateRect')<critical.index('uploadsnapshot(upload[2])')<critical.index('blit(200+i')<critical.index('uploadsnapshot(upload[3])')
assert 'i<13&&!Failures' in s and 'i<40' in s and 'i<5 && messages()' in s
assert 'static char buffer[16384]' in s and 'sizeof(buffer)-128' in s
assert 'upload_samples' in (k/'audit-emulator.py').read_text()
phy=(k/'audit-physical.py').read_text();assert phy.index('uploads_result=')<phy.index('upload_samples=uploads_result') and "'upload_coverage_passed'" in phy
for p in k.glob('*.py'):ast.parse(p.read_text())
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
compiler_sha=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler]).decode().split()[0]
assert compiler_sha=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
r=dict(passed=True,physical_access=False,guest_launch=False,binaries=binaries,providers=providers,compiler_sha256=compiler_sha,
 source_pins={p.name:sha(p) for p in k.glob('*.c')},only_driver_definition_difference='XWN_UPLOAD_ACCOUNTING',
 expected_body_profile_mode=0,text_bounds_mode=1,scalar_mode=0,packet_words=158,unchanged202_runner=True,unchanged201_helper=True,
 limits='New119 observation and12 probe. Four atomic packets per controlled40 steps; no logging between phase snapshots. Global work includes background. Existing pixels/cold/event/restart gates retained.')
dest.write_text(json.dumps(r,indent=2)+'\n')
pins=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+[dest,k/'probe-build001.json',k/'upload-parser-tests.json']+list((k/'artifacts').glob('*.exe'))
pins+=[native/c/'artifacts/xwnown.dll' for c in ['control001','candidate001']]+[native/'build-review.json',native/'source-review.json',native/'host-tests001.json',k.parent/'video-phase-physical200/package-review.json']
(k/'emulator-frozen.json').write_text(json.dumps({p.relative_to(ws).as_posix():sha(p) for p in pins},indent=2)+'\n')
print('Fresh119/v12 imports, phases, audit gates and frozen inputs PASS')
