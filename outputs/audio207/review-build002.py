"""Pin actual binaries, compiler and imports against copied actual NT5 providers."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
providers=k/'artifacts/inventory001';rows=[]
for path in [k/'artifacts/build002/ac97xnt5.sys',k/'artifacts/probe001/probe.exe',k/'artifacts/probe001/runner.exe']:
    p=pefile.PE(str(path));imports=[]
    assert p.FILE_HEADER.Machine==0x14c
    for lib in p.DIRECTORY_ENTRY_IMPORT:
        name=lib.dll.decode().lower();provider=providers/name;assert provider.exists(),name
        exported=pefile.PE(str(provider));names={v.name for v in exported.DIRECTORY_ENTRY_EXPORT.symbols}
        missing=[v.name.decode() if v.name else v.ordinal for v in lib.imports if v.name not in names]
        assert not missing,(path,name,missing)
        imports.append(dict(library=name,provider_sha256=sha(provider),names=[v.name.decode() for v in lib.imports],missing=missing))
    if path.suffix=='.exe':assert p.OPTIONAL_HEADER.MajorSubsystemVersion==5 and p.OPTIONAL_HEADER.MinorSubsystemVersion==0
    rows.append(dict(path=str(path.relative_to(k)),sha256=sha(path),imports=imports))
report=dict(passed=True,binaries=rows,physical_qualified=False,runtime_qualified=False)
(k/'build-review002.json').write_text(json.dumps(report,indent=2)+'\n')
print('Three PE import reviews passed against actual fixture providers')
