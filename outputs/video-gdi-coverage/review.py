"""Review actual NT5 imports, entrypoint and source pins before preparing guests."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'pe-review.json';assert not dest.exists()
build=read(k/'build-report.json');assert build['status']=='compiled'
patch=read(k/'patch-review.json');assert sha(k/'0109-ram-ownership.patch')==patch['patch_sha256']==build['patch_sha256']
for n,h in patch['source_files'].items():assert sha(k/'display'/n)==h
host=read(k/'host-tests.json');assert host['passed']
for n,h in host['pins'].items():assert sha(k/n)==h
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
reports=[]
for path in [k/'candidate001/artifacts/xwnown.dll',k/'artifacts/probe.exe']:
 pe=pefile.PE(str(path));assert pe.FILE_HEADER.Machine==0x14c
 assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
 imports={};targets={}
 for entry in pe.DIRECTORY_ENTRY_IMPORT:
  dll=entry.dll.decode().lower();target=next(p for base in [archive,archive/'drivers'] for p in base.iterdir() if p.name.lower()==dll)
  names={s.name for s in pefile.PE(str(target)).DIRECTORY_ENTRY_EXPORT.symbols}
  assert all(i.name and i.name in names for i in entry.imports),(path.name,dll)
  imports[dll]=[i.name.decode() for i in entry.imports];targets[dll]=sha(target)
 if path.name=='xwnown.dll':
  assert set(imports)=={'win32k.sys'}
  assert pe.OPTIONAL_HEADER.Subsystem==1
 reports.append(dict(name=path.name,sha256=sha(path),bytes=path.stat().st_size,
  subsystem=pe.OPTIONAL_HEADER.Subsystem,subsystem_version=[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion],
  entrypoint=pe.OPTIONAL_HEADER.AddressOfEntryPoint,imports=imports,targets=targets))
assert reports[0]['sha256']==read(k/'candidate001/build.json')['files'][0]['sha256']
r=dict(passed=True,physical_access=False,source_tree=build['source_tree'],build_sha256=sha(k/'build-report.json'),
 display_sha256=reports[0]['sha256'],probe_sha256=reports[1]['sha256'],probe_source_sha256=sha(k/'probe.c'),
 host_tests_sha256=sha(k/'host-tests.json'),files=reports,
 limits='Import/export and exact source fault tests only. RAM-primary identity/coherence and functional compatibility still require guest evidence; host engine is a shim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Direct display and probe import review PASS')
