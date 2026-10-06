"""Run existing read-only FATX allocation analyzer on closed owned fixtures."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from allocation import scan
case=sys.argv[1];assert case in ['001']
f=json.loads((k/('fixture-'+case+'.json')).read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
with base.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest()==f['fixture_sha256']
disk=ws/('work/runs/nt5-fatx-shutdown-concurrency-'+case+'/hdd.qcow2')
assert (disk.parent/'cleanup.json').exists()
assert not (k/case/'allocation.json').exists(),'Preserve an existing completed scan'
scan(disk,k/case/'artifacts')
