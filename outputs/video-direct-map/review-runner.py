"""Check the private-path runner and unchanged probe against captured NT5 exports."""
import hashlib,json
from pathlib import Path
import sys
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
system=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
sha=lambda data:hashlib.sha256(data).hexdigest()
result=dict(scope=__doc__,files=[])
for name,path,src in [('runner.exe',k/'artifacts/runner.exe',k/'runner.c'),('replay.exe',ws/'outputs/video-next/probe-v3/artifacts/gdi-probe.exe',ws/'outputs/video-next/probe-v3/gdi-probe.c')]:
    data=path.read_bytes();pe=pefile.PE(data=data)
    assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
    imports={}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll=entry.dll.decode();target=next(p for p in system.iterdir() if p.name.lower()==dll.lower())
        exp=pefile.PE(str(target)).DIRECTORY_ENTRY_EXPORT.symbols
        exports={e.name for e in exp if e.name}
        assert all(i.name in exports for i in entry.imports)
        imports[dll]=[i.name.decode() for i in entry.imports]
    result['files'].append(dict(name=name,sha256=sha(data),source_sha256=sha(src.read_bytes()),bytes=len(data),imports=imports))
original=json.loads((ws/'outputs/video-next/probe-v3/build-review.json').read_text())
assert result['files'][1]['sha256']==original['sha256']
result['passed']=True
(k/'build-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,files=[v['name'] for v in result['files']])))
