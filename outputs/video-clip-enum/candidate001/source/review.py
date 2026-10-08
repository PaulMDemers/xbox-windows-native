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
display=k.parent/'video-line-upload/candidate001/artifacts/xwnown.dll';assert sha(display)=='a1d5cf1eea27729a23c06e177f89f862eedcff0a1d0aa002815f4456279b4e98'
r=dict(passed=True,physical_access=False,driver_changed=False,display_sha256=sha(display),probe_source_sha256=sha(k/'probe.c'),probe_sha256=sha(path),build_script_sha256=sha(k/'Build-Probe.ps1'),files=[dict(name='probe.exe',sha256=sha(path),imports=imports,targets=targets)])
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Exact NT5 import review passed; no driver/settings change')
