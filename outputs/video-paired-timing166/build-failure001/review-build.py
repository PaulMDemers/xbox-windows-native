"""Pin the new NT5 launcher against actual target exports before guest use."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
dest=k/'build-review.json';assert not dest.exists()
p=pefile.PE(str(k/'artifacts/runner.exe'));imports={}
source=k.parent/'video-physical-rehearsal160/artifacts/F/winnt/system32'
for entry in p.DIRECTORY_ENTRY_IMPORT:
    name=entry.dll.decode();dll=next(v for v in source.iterdir() if v.name.lower()==name.lower())
    target=pefile.PE(str(dll));exports={v.name for v in target.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    assert all(v.name in exports for v in entry.imports),name
    imports[name]=[v.name.decode() for v in entry.imports]
assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
probe=k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe'
assert sha(probe)==json.loads((k.parent/'video-next/probe-v3/build-review.json').read_text())['sha256']
dest.write_bytes((json.dumps(dict(passed=True,source_sha256=sha(k/'runner.c'),sha256=sha(k/'artifacts/runner.exe'),
    probe_sha256=sha(probe),imports=imports,physical_access=False,guest_runtime_qualified=False),indent=2)+'\n').encode('utf-8'))
print('Actual NT5 exports and unchanged probe verified')
