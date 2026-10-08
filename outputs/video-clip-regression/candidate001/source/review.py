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
display=k.parent/'video-clip-upload/candidate001/artifacts/xwnown.dll';control=k.parent/'video-line-upload/candidate001/artifacts/xwnown.dll'
build=json.loads((k.parent/'video-clip-upload/build-report.json').read_text());assert build['status']=='compiled' and sha(display)==build['builds'][0]['files'][0]['sha256']
assert sha(control)=='a1d5cf1eea27729a23c06e177f89f862eedcff0a1d0aa002815f4456279b4e98'
host=json.loads((k.parent/'video-clip-upload/host-tests.json').read_text());assert host['passed']
d=pefile.PE(str(display));assert d.OPTIONAL_HEADER.CheckSum==d.generate_checksum() and d.OPTIONAL_HEADER.Subsystem==1
for item in d.DIRECTORY_ENTRY_IMPORT:
 assert item.dll.lower()==b'win32k.sys';owned=pefile.PE(str(archive/'win32k.sys'));exports={x.name for x in owned.DIRECTORY_ENTRY_EXPORT.symbols};assert all(x.name in exports for x in item.imports)
r=dict(passed=True,physical_access=False,driver_changed=True,display_sha256=sha(display),control_display_sha256=sha(control),build_report_sha256=sha(k.parent/'video-clip-upload/build-report.json'),host_tests_sha256=sha(k.parent/'video-clip-upload/host-tests.json'),probe_source_sha256=sha(k/'probe.c'),probe_sha256=sha(path),build_script_sha256=sha(k/'Build-Probe.ps1'),files=[dict(name='probe.exe',sha256=sha(path),imports=imports,targets=targets)])
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Candidate112 and shared probe NT5 import review passed')
