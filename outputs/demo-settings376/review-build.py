"""Review actual compiled372 PE against owned NT5 import providers."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review001.json';assert not dest.exists()
b=json.loads((k/'build001.json').read_text());binary=Path(b['output_windows'])
assert b['compiled'] and not b['warnings'] and sha(binary)==b['binary_sha256']
for name,digest in b['source_pins'].items():assert sha(k/name)==sha(binary.parent/name)==digest
p=pefile.PE(str(binary));assert p.FILE_HEADER.Machine==0x14c
assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
providers={};imports={};archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
for entry in p.DIRECTORY_ENTRY_IMPORT:
    name=entry.dll.decode().lower();assert name in ['kernel32.dll','user32.dll','advapi32.dll']
    dll=archive/name;d=pefile.PE(str(dll));exports={v.name for v in d.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    assert all(v.name and v.name in exports for v in entry.imports),name
    imports[name]=[v.name.decode() for v in entry.imports];providers[name]=dict(path=str(dll),sha256=sha(dll))
assert set(imports)=={'kernel32.dll','user32.dll','advapi32.dll'}
r=dict(passed=True,binary=str(binary),binary_sha256=sha(binary),binary_bytes=binary.stat().st_size,
       subsystem=[5,0],machine=p.FILE_HEADER.Machine,imports=imports,providers=providers,
       source_pins=b['source_pins'],compiler_sha256=b['compiler_sha256'],runtime_qualified=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
