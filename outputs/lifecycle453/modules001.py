"""Read-only owned NT5 PSAPI/export identity, not a runtime qualification."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn453/modules001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
sys.path.insert(0,str(W/'work/python-packages'));import pefile
source=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001/hdd.qcow2');expected=json.loads((W/'outputs/install-validation406/emu001/audit.json').read_text())['disk_sha256']
assert sha(source)==expected and not P.exists() and not (K/'modules001.json').exists();P.mkdir(parents=True)
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(source) as io:
 reader=OemReader(io,m.fatx.open_partition(io,source,'E'));data=reader.read('WINNT/system32/psapi.dll');(P/'psapi.dll').write_bytes(data)
pe=pefile.PE(data=data);exports={s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
assert 'GetProcessMemoryInfo' in exports and not exports['GetProcessMemoryInfo'].forwarder
assert sha(source)==expected
(K/'modules001.json').write_text(json.dumps(dict(source_sha256=expected,source_unchanged=True,psapi_sha256=sha(P/'psapi.dll'),exports=list(exports),memory_export_rva=exports['GetProcessMemoryInfo'].address),indent=2)+'\n')
print('Owned NT5 PSAPI exposes GetProcessMemoryInfo; source unchanged.')
