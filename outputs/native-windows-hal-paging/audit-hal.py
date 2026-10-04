"""Check the ordinary HAL's imports and disabled diagnostic entry points."""
from pathlib import Path
import sys, json, hashlib
kit = Path(__file__).resolve().parent
root = kit.parents[1]
sys.path.insert(0, str(root / 'work/python-packages'))
import pefile
p = kit / 'artifacts/halxboxnt5.dll'
pe = pefile.PE(str(p))
k = root / 'outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'
kp = pefile.PE(str(k))
exports = {s.name for s in kp.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
imports = [{'dll': d.dll.decode(), 'name': s.name.decode() if s.name else s.ordinal,
            'resolved': d.dll.lower() == b'ntoskrnl.exe' and s.name in exports}
           for d in pe.DIRECTORY_ENTRY_IMPORT for s in d.imports]
assert all(i['resolved'] for i in imports)
probes = {}
for name in ('XwnConfigureEntryProbe', 'XwnConfigureMapProbe'):
    rva = next(s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name == name.encode())
    assert pe.get_data(rva, 5) == bytes.fromhex('31c0c20800')
    probes[name] = hex(rva)
r = {'hal_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
     'kernel_sha256': hashlib.sha256(k.read_bytes()).hexdigest(),
     'imports': imports, 'disabled_probe_exports': probes,
     'sections': [{'name': s.Name.rstrip(b'\0').decode(), 'rva': hex(s.VirtualAddress),
                   'size': s.Misc_VirtualSize, 'discardable': bool(s.Characteristics & 0x02000000)}
                  for s in pe.sections]}
(kit / 'hal-audit.json').write_text(json.dumps(r, indent=2) + '\n')
print(r['hal_sha256'], len(imports))
