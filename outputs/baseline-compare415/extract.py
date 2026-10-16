"""Read selected comparison bytes from the audited clean installation; no boot."""
import json
import shutil
import sys
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
P=Path('/mnt/e/xwn415/fresh')
out=K/'fresh001.json'
assert not out.exists() and not P.exists()
assert shutil.disk_usage('/mnt/e').free-40*1024**2>=20*1024**3
sys.path.insert(0,str(W/'outputs/video-text-oracle206'))
from common import ColdIO,m,sha
sys.path.insert(0,str(W/'outputs/install-validation406'))
from oem_reader import OemReader
disk=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001/hdd.qcow2')
audit=json.loads((W/'outputs/install-validation406/emu001/audit.json').read_text())
assert sha(disk)==audit['disk_sha256']
manifest=Path('/mnt/e/xwn406/cold001/after/files.json')
files=json.loads(manifest.read_text())
physical=json.loads((K/'physical001.json').read_text())
assert physical['completed'] and physical['baseline_code_and_startup_exact']
paths={p[3:] for p in physical['files']}
paths.update(v['path'] for v in json.loads((W/'outputs/fresh-assembly405/installed-final001.json').read_text())['fresh403_components'])
P.mkdir()
r=dict(physical_access=False,guest_launched=False,source_disk_sha256=audit['disk_sha256'],
       source_inventory_sha256=sha(manifest),files={},absent=[],source='Closed normal-restarted406 installation, read-only comparison only')
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(disk) as io:
    rd=OemReader(io,m.fatx.open_partition(io,disk,'E'))
    for path in sorted(paths,key=str.casefold):
        name=path.lower()
        if name not in files:
            r['absent'].append(path)
            continue
        data=rd.read(path)
        assert m.sha(data)==files[name],path
        target=P/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        r['files'][name]=dict(bytes=len(data),sha256=m.sha(data),local_path=str(target))
assert sha(disk)==audit['disk_sha256']
r.update(completed=True,source_unchanged=True)
with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(dict(completed=True,files=len(r['files']),absent=r['absent'],source_unchanged=True)))
