"""Verify the new helper uses the already-tested NT5 imports and new private paths."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
path=k/'artifacts/runner.exe';data=path.read_bytes();p=pefile.PE(data=data)
old=pefile.PE(str(ws/'outputs/video-trace-reuse-settled/artifacts/runner.exe'))
def imports(p):return {e.dll.decode():[i.name.decode() for i in e.imports] for e in p.DIRECTORY_ENTRY_IMPORT}
assert imports(p)==imports(old)
assert (p.OPTIONAL_HEADER.MajorSubsystemVersion,p.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
assert b'C:\\xwnv164\\attempt.log\0' in data and b'C:\\xwnv164\\replay.exe\0' in data and b'xwnrps01' not in data
r=dict(passed=True,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),imports=imports(p),
       source_sha256=hashlib.sha256((k/'runner.c').read_bytes()).hexdigest(),old_runner_sha256=hashlib.sha256((ws/'outputs/video-trace-reuse-settled/artifacts/runner.exe').read_bytes()).hexdigest(),
       physical_access=False,limits='Import/path/source review only; new namespace still requires one emulator runtime before physical launch.')
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('NT5 imports unchanged; unique one-shot helper reviewed')
