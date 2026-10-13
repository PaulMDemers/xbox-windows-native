"""Full E/F file-content and directory metadata comparison for new reconstruction."""
import json
import struct
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'))
from common import ColdIO, readers, sha, m, save
f=json.loads((K/'seed001/fixture.json').read_text())
dest=K/'seed001/content-review002.json';assert not dest.exists()
private=Path('/mnt/e/xwn329/seed001')
def inventory(path):
    entries={}
    with ColdIO(path) as io:
        for volume,r in readers(io,path).items():
            pending=[('',1)];seen=set()
            for prefix,cluster in pending:
                if cluster==0: continue
                assert cluster not in seen
                seen.add(cluster)
                for name,(_,__,e) in r.directory(cluster)['entries'].items():
                    relative=prefix+'/'+name if prefix else name
                    key=volume+'/'+relative
                    row=dict(directory=bool(e[1]&16),metadata=(e[:44]+e[52:64]).hex())
                    if row['directory']:
                        pending.append((relative,struct.unpack_from('<I',e,44)[0]))
                    else:
                        data=r.read(relative);row.update(bytes=len(data),sha256=m.sha(data))
                    assert key not in entries
                    entries[key]=row
    return entries
base=Path(f['parent']);source=Path(f['fixture_path_linux'])
assert sha(base)==f['parent_sha256'] and sha(source)==f['fixture_sha256']
a=inventory(base);b=inventory(source)
assert a.keys()==b.keys(), 'Namespace changed'
expected={n.lower():h for n,h in f['replacement_files'].items()}
changes=[]
for name,left in a.items():
    right=b[name]
    assert left['directory']==right['directory'] and left['metadata']==right['metadata'],name
    if left!=right:
        assert not left['directory'] and right['sha256']==expected[name.lower()],name
        changes.append(name)
assert {x.lower() for x in changes}==set(expected)
save(private/'content-before.json',a);save(private/'content-after.json',b)
assert sha(base)==f['parent_sha256'] and sha(source)==f['fixture_sha256']
save(dest,dict(passed=True,namespace_and_entry_metadata_unchanged=True,
    file_count=sum(not r['directory'] for r in a.values()),directory_count=sum(r['directory'] for r in a.values()),
    changed_files=changes,exact_expected_replacement_count=7,
    all_other_file_bytes_unchanged=True,source_sha256=f['fixture_sha256'],
    original317_container_match=False,guest_launched=False,physical_access=False,
    manifests={p.name:sha(p) for p in [private/'content-before.json',private/'content-after.json']}))
print(dest.read_text())
