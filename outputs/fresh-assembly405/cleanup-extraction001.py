"""Remove only redundant extracted dllcache after exact independent image readback."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
r=json.loads((K/'assembly001.json').read_text());assert r['status']=='assembled-readback-verified'
disk=Path(r['fixture_path_linux']);assert sha(disk)==r['fixture_sha256']
root=Path('/mnt/c/xwn405/extract004/files/WINNT/system32/dllcache');assert root.resolve()==root and root.is_dir()
selected=[v for v in r['files'] if v['path'].lower().startswith('winnt/system32/dllcache/')]
assert len(selected)==1760 and not (K/'cleanup-extraction001.json').exists()
actual={p.name.lower():p for p in root.iterdir() if p.is_file()};assert len(actual)==1760
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    for row in selected:
        p=actual[Path(row['path']).name.lower()]
        assert p.resolve().parent==root.resolve() and sha(p)==row['sha256'] and m.sha(wr.read(row['path']))==row['sha256']
record=dict(scope='Redundant temporary extracted dllcache only; unchanged source404 disk and independent fresh Xbox copy retain exact contents',files=selected,deleted=[])
dest=K/'cleanup-extraction001.json'
for row in selected:
    p=actual[Path(row['path']).name.lower()];p.unlink();record['deleted'].append(row['path'])
dest.write_text(json.dumps(record,indent=2)+'\n');print('Verified duplicate extraction removed',len(selected),sum(v['bytes'] for v in selected))
