"""Review actual204 PE imports, same guards/helper and new text source before freezing."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-unattended202'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
assert read(k.parent/'video-text-clip205/build-review.json')['passed']
binaries={};providers={};archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
for name in ['runner.exe','replay.exe','wizard.exe']:
 p=pefile.PE(str(k/'artifacts'/name));imports={}
 assert p.FILE_HEADER.Machine==0x14c and (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
 for entry in p.DIRECTORY_ENTRY_IMPORT:
  dllname=entry.dll.decode().lower();dll=archive/dllname;d=pefile.PE(str(dll));exports={v.name for v in d.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
  assert all(v.name in exports for v in entry.imports),dllname
  imports[dllname]=[v.name.decode() for v in entry.imports];providers[dllname]=dict(path=str(dll),sha256=sha(dll))
 binaries[name]=dict(sha256=sha(k/'artifacts'/name),imports=imports)
for name in ['runner.exe','wizard.exe']:assert binaries[name]['sha256']==read(old/'build-review.json')['binaries'][name]['sha256']
assert binaries['replay.exe']['sha256']==read(k/'probe-build001.json')['binary_sha256']
assert sha(k/'gdi-probe.c')==read(k/'probe-build001.json')['source_sha256']
for name in ['ntdll.dll','setupapi.dll']:
 dll=archive/name;providers[name]=dict(path=str(dll),sha256=sha(dll))
s=(k/'text-cases.c').read_text();base=(k/'gdi-probe.c').read_text()
assert s.index('textsnapshot(before)')<s.index('drawok=textdraw(Screen,stage)')<s.index('packetok=textsnapshot(after)')<s.index('record("TEXT_DRAW')
assert 'if(after[37])inside=' in s
assert 'if(delta!=1&&!(stage==3&&delta==0))' in s and 'coherence[19]' in s and 'for(i=0;i<W*H;i++)' in s
assert 'i<13&&!Failures' in base and 'i<40' in base and 'i<5 && messages()' in base
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
compiler_sha=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',compiler]).decode().split()[0]
assert compiler_sha=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
result=dict(passed=True,physical_access=False,runtime_qualified=False,binaries=binaries,providers=providers,compiler_sha256=compiler_sha,
 source_pins={p.name:sha(p) for p in [k/'gdi-probe.c',k/'text-cases.c']},unchanged202_runner=True,unchanged201_helper=True,
 expected_body_profile_mode=0,only_driver_definition_difference='XWN_TEXT_BOUNDS',
 limits='New font/opaque/clipping/readback suite and owned neutral backdrop; prior copy/DIB/timing/window checks remain. Same202 joinedhelper194 idle/bookend/restart gates; no device-policy change.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
pins=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+[k/'build-review.json',k/'probe-build001.json']+list((k/'artifacts').glob('*.exe'))
pins += [k.parent/'video-text-clip205'/c/'artifacts/xwnown.dll' for c in ['control001','candidate001']]
pins += [k.parent/'video-text-clip205/build-review.json',k.parent/'video-phase-physical200/package-review.json']
(k/'emulator-frozen.json').write_text(json.dumps({p.relative_to(ws).as_posix():sha(p) for p in pins},indent=2)+'\n',encoding='utf-8')
print('Actual204 imports/source/new117 pair and unchanged202 runner/201helper reviewed and frozen')
