"""Compare captured reachable paths/sizes; never mount or recollect closed disks."""
import hashlib, json, struct
from pathlib import Path

k = Path(__file__).resolve().parent
sets = []
pins = {}
for case in ['control003', 'candidate003']:
    p = k / case / 'artifacts/directories.bin'
    b = p.read_bytes()
    assert len(b) % 80 == 0
    pins[case] = hashlib.sha256(b).hexdigest()
    dirs, files = {1: ''}, {}
    for o in range(0, len(b), 80):
        kind, parent, cluster, offset = struct.unpack_from('<4I', b, o)
        if kind != 2:
            continue
        e = b[o + 16:o + 80]
        name = e[2:2 + e[0]].decode('latin1')
        path = (dirs[parent] + '/' + name).lstrip('/')
        first, size = struct.unpack_from('<II', e, 44)
        if e[1] & 16:
            dirs[first] = path
        else:
            files[path.lower()] = dict(path=path, size=size)
    sets.append(files)
a, b = sets
r = dict(read_only_existing_captures=True, captures_sha256=pins,
         control_only=[a[n] for n in sorted(a.keys() - b.keys())],
         candidate_only=[b[n] for n in sorted(b.keys() - a.keys())],
         size_differences=[dict(path=a[n]['path'], control=a[n]['size'], candidate=b[n]['size'])
                           for n in sorted(a.keys() & b.keys()) if a[n]['size'] != b[n]['size']],
         limits='Reachable path/size comparison only; not file-content verification, full-hive equality or a new cold collection.')
dest = k / 'directory-comparison003.json'
if dest.exists():
    assert json.loads(dest.read_text(encoding='utf-8')) == r
else:
    dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(capture_comparison_verified=True, candidate_extra=len(r['candidate_only']))))
