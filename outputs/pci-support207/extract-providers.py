"""Read-only cold extraction from immutable201 standalone seed; no fixture mutation."""
import hashlib, importlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
k = Path(__file__).resolve().parent
repo = k.parents[1]
canonical = Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,str(repo/'outputs/fatx-mapped-eof'))
from coldio import ColdIO
sys.path.insert(0,str(repo/'outputs/native-windows-paint-save'))
m = importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
manifest=canonical/'outputs/setup-wizard-automation201/fixture-observe002.json'
f=json.loads(manifest.read_text()); seed=Path(f['fixture_path_linux'])
assert sha(seed)==f['fixture_sha256']
out=k/'artifacts/providers001'; assert not out.exists(); out.mkdir()
report={'scope':__doc__,'seed':str(seed),'seed_sha256':sha(seed),'manifest_sha256':sha(manifest),'files':{}}
with ColdIO(seed) as io:
    readers={v:m.Writer(io,m.fatx.open_partition(io,seed,v)) for v in ('E','F')}
    files=['F/winnt/inf/machine.inf','F/winnt/inf/oem1.inf','F/winnt/system32/drivers/pci.sys',
           'F/winnt/system32/ntoskrnl.exe','E/Applications/XWNFBoot/loader/halxboxnt5.dll',
           'F/winnt/system32/kernel32.dll','F/winnt/system32/setupapi.dll',
           'F/winnt/system32/cfgmgr32.dll','F/winnt/system32/newdev.dll']
    for file in files:
        v,path=file.split('/',1); data=readers[v].read(path); digest=hashlib.sha256(data).hexdigest()
        if file in f['files']: assert digest==f['files'][file]
        dest=out/Path(path).name; dest.write_bytes(data)
        report['files'][file]={'sha256':digest,'bytes':len(data),'output':dest.name,'seed_manifest_pin':f['files'].get(file)}
assert sha(seed)==report['seed_sha256']
(k/'providers001.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
