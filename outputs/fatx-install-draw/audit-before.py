"""Audit padded immutable fixture allocation before launch, once."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
f=json.loads((k/('fixture-'+case+'.json')).read_text());disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
with disk.open('rb') as h:assert hashlib.file_digest(h,'sha256').hexdigest()==f['fixture_sha256']
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from allocation import scan
out=k/case;out.mkdir(exist_ok=True)
assert not (out/'before-allocation.json').exists()
raw=out/'before';assert not (raw/'allocation.json').exists()
scan(disk,raw/'artifacts')
a=json.loads((raw/'allocation.json').read_text())
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
(out/'before-allocation.json').write_bytes((raw/'allocation.json').read_bytes())
