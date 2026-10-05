"""Resolve combined rename candidate imports against the owned native NT5 binaries."""
from pathlib import Path
import argparse,hashlib,json,sys
ws=Path(__file__).resolve().parents[2];kit=Path(__file__).resolve().parent
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--unlinked',action='store_true');g.add_argument('--cleanup',action='store_true');g.add_argument('--deleted-write',action='store_true');a=p.parse_args()
driver=kit/('artifacts/xwnfatx-retired-write.sys' if a.unlinked else 'artifacts/xwnfatx-deleted-write.sys' if a.deleted_write else 'artifacts/xwnfatx-delete-cache.sys' if a.cleanup else 'artifacts/xwnfatx-rename-integration.sys')
root=ws/'outputs/native-windows-physical-mmcomplete/package'
targets={'ntoskrnl.exe':root/'WINNT/system32/ntoskrnl.exe','hal.dll':root/'loader/halxboxnt5.dll'}
exports={lib:{s.name.decode() if s.name else s.ordinal for s in pefile.PE(str(path)).DIRECTORY_ENTRY_EXPORT.symbols} for lib,path in targets.items()}
imports=[]
for group in pefile.PE(str(driver)).DIRECTORY_ENTRY_IMPORT:
    lib=group.dll.decode().lower()
    for sym in group.imports:
        name=sym.name.decode() if sym.name else sym.ordinal
        imports.append(dict(library=lib,name=name,resolved=name in exports.get(lib,set())))
r=dict(scope=__doc__,driver_sha256=hashlib.sha256(driver.read_bytes()).hexdigest(),imports=imports,
       all_resolved=all(i['resolved'] for i in imports),runtime_compatibility_established=False)
(kit/('retired-import-audit.json' if a.unlinked else 'deleted-write-import-audit.json' if a.deleted_write else 'cleanup-import-audit.json' if a.cleanup else 'rename-import-audit.json')).write_text(json.dumps(r,indent=2)+'\n')
assert r['all_resolved']
print(len(imports),'imports resolved',r['driver_sha256'])
