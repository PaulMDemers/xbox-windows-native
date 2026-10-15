"""Reclaim redundant large extraction files; both immutable disk copies retain them."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/extract004/files')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
r=json.loads((K/'assembly001.json').read_text());disk=Path(r['fixture_path_linux'])
assert r['status']=='assembled-readback-verified' and sha(disk)==r['fixture_sha256']
assert not (K/'cleanup-extraction002.json').exists()
rows=[v for v in r['files'] if v['bytes']>1024**2 and r['sources'][v['path'].lower()]['kind']=='clean404-installed-file' and '/config/' not in v['path'].lower() and (P/v['path']).is_file()]
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    for row in rows:
        p=P/row['path'];assert p.resolve().is_relative_to(P.resolve()) and not p.is_symlink()
        assert sha(p)==row['sha256'] and m.sha(wr.read(row['path']))==row['sha256']
for row in rows:(P/row['path']).unlink()
(K/'cleanup-extraction002.json').write_text(json.dumps(dict(files=rows,bytes=sum(v['bytes'] for v in rows),scope='Only duplicate temporary extraction; unchanged original404 and independent fresh405 images retain exact contents'),indent=2)+'\n')
print('Verified duplicate large files removed',len(rows),sum(v['bytes'] for v in rows))
