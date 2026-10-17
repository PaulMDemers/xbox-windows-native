import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn425/modules001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
source=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001/hdd.qcow2');expected=json.loads((W/'outputs/install-validation406/emu001/audit.json').read_text())['disk_sha256']
assert sha(source)==expected and not P.exists();P.mkdir(parents=True)
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512);rows={}
with ColdIO(source) as io:
 reader=OemReader(io,m.fatx.open_partition(io,source,'E'))
 for name in ['ntdll.dll','ntoskrnl.exe','kernel32.dll','advapi32.dll','user32.dll','gdi32.dll','crypt32.dll','rpcrt4.dll']:
  (P/name).write_bytes(reader.read('WINNT/system32/'+name));rows[name]=sha(P/name)
assert sha(source)==expected
(K/'modules001.json').write_text(json.dumps({'source_sha256':expected,'modules':rows,'source_unchanged':True},indent=2)+'\n')
print('Owned modules extracted read-only:',len(rows))
