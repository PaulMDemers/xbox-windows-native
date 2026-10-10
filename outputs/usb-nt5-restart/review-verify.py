import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'artifacts/verify001'
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages');import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((k/'build001-review.json').read_text());pe=pefile.PE(str(out/'verify.exe'))
assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==3
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
imports={}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    n=e.dll.decode();provider=base['providers'][n.lower()];p=Path(provider['path']);assert sha(p)==provider['sha256']
    exports={s.name.decode() for s in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    imports[n]=[s.name.decode() for s in e.imports];assert set(imports[n])<=exports
assert not any(n in ['CreateProcessA','UpdateDriverForPlugAndPlayDevicesA'] for group in imports.values() for n in group)
source=(out/'verify.c').read_text();assert 'VERIFY_EXISTING_DRIVER' in source and 'update(' not in source and 'finish_known_setup' not in source
inputs={}
for n in ['verify.c','setup_gate201.h','restart_gate201.h']:
    assert sha(k/n)==sha(out/n);inputs[n]=sha(k/n)
r=dict(passed=True,binary_sha256=sha(out/'verify.exe'),inputs=inputs,imports=imports,driver_rebuilt=False,physical_access=False)
(k/'verify001-review.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS verify-only probe source and actual NT5 imports')
