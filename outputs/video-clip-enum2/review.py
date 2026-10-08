"""Review new probe against exact owned NT5 exports; no driver build."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'pe-review.json';assert not dest.exists();path=k/'artifacts/probe.exe';p=pefile.PE(str(path));assert p.FILE_HEADER.Machine==0x14c and p.OPTIONAL_HEADER.Subsystem==3 and p.OPTIONAL_HEADER.MajorSubsystemVersion==5 and p.OPTIONAL_HEADER.MinorSubsystemVersion==0
assert p.OPTIONAL_HEADER.CheckSum==p.generate_checksum()
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32');imports={};targets={}
for entry in p.DIRECTORY_ENTRY_IMPORT:
 dll=entry.dll.decode().lower();target=archive/dll;names={s.name for s in pefile.PE(str(target)).DIRECTORY_ENTRY_EXPORT.symbols};assert all(i.name in names for i in entry.imports)
 imports[dll]=[i.name.decode() for i in entry.imports];targets[dll]=sha(target)
assert {'BitBlt','PatBlt','ExtEscape','GdiFlush'}<=set(imports['gdi32.dll'])
display=k.parent/'video-clip-diagnostic/candidate001/artifacts/xwnown.dll';build=json.loads((k.parent/'video-clip-diagnostic/build-report.json').read_text());assert build['status']=='compiled' and sha(display)==build['builds'][0]['files'][0]['sha256']
driver_pe=pefile.PE(str(display));driver_imports={}
for imp in driver_pe.DIRECTORY_ENTRY_IMPORT:
 target=archive/imp.dll.decode().lower();names={v.name for v in pefile.PE(str(target)).DIRECTORY_ENTRY_EXPORT.symbols}
 assert all(v.name in names for v in imp.imports)
 driver_imports[imp.dll.decode().lower()]=[v.name.decode() for v in imp.imports]
assert {'CLIPOBJ_cEnumStart','CLIPOBJ_bEnum'}<=set(driver_imports['win32k.sys'])
assert p.OPTIONAL_HEADER.ImageBase==0x12000000
r=dict(driver_imports=driver_imports,probe_image_base=p.OPTIONAL_HEADER.ImageBase,build_report_sha256=sha(k.parent/'video-clip-diagnostic/build-report.json'),passed=True,physical_access=False,driver_changed=True,display_sha256=sha(display),probe_source_sha256=sha(k/'probe.c'),probe_sha256=sha(path),build_script_sha256=sha(k/'Build-Probe.ps1'),files=[dict(name='probe.exe',sha256=sha(path),imports=imports,targets=targets)])
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('NT5 import review passed; diagnostic-only111, unchanged upload area')
