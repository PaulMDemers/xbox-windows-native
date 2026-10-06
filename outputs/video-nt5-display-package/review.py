"""Verify the installer imports against owned NT5 exports and pin package inputs."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
sha=lambda b:hashlib.sha256(b).hexdigest()
data=(k/'artifacts/install.exe').read_bytes();pe=pefile.PE(data=data)
assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
imports={};targets={}
def exports(dll):
    p=next(p for p in system.iterdir() if p.name.lower()==dll.lower())
    targets[dll.lower()]=sha(p.read_bytes())
    return {e.name for e in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if e.name}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll=entry.dll.decode();assert all(i.name in exports(dll) for i in entry.imports)
    imports[dll]=[i.name.decode() for i in entry.imports]
assert b'UpdateDriverForPlugAndPlayDevicesA' in exports('newdev.dll')
r=dict(passed=True,installer_sha256=sha(data),source_sha256=sha((k/'install.c').read_bytes()),
       inf_sha256=sha((k/'xboxvnt5.inf').read_bytes()),imports=imports,
       dynamic_exports={'newdev.dll':['UpdateDriverForPlugAndPlayDevicesA']},owned_export_targets=targets,
       note='Static imports and dynamic entry point exist in the owned Windows 2000 binaries; runtime still unqualified.')
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n');print('NT5 import review passed')
