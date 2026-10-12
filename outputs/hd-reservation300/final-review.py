"""Read-only rehash of the completed reservation build and host evidence."""
import datetime
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'final-review.json'
assert not dest.exists()
build, host, binary, source = [read(k / n) for n in
    ['build001.json', 'host001.json', 'binary-review001.json', 'source-postbuild-review.json']]
assert build['status'] == 'compiled' and host['passed'] and binary['passed'] and source['passed']
checked = {}
for case, record in build['cases'].items():
    for name, pin in record['files'].items():
        p = Path('E:/xwn300/build001') / case / name
        assert p.stat().st_size == pin['bytes'] and sha(p) == pin['sha256']
        checked[str(p)] = pin['sha256']
for name, digest in build['logs'].items():
    p = Path('E:/xwn300/build001') / name
    assert sha(p) == digest
    checked[str(p)] = digest
for name, digest in host['inputs'].items():
    p = Path('E:/xwn300/host001') / name
    assert sha(p) == digest
    checked[str(p)] = digest
assert sha(k / 'xwn_hd_layout.h') == host['inputs']['drivers/xbox/xwn_hd_layout.h']
runtime = read(k.parent / 'hd-reservation301/final-review.json')
trace = read(k.parent / 'hd-reservation301/trace-review.json')
assert runtime['scope_passed'] and not runtime['strict_passed'] and trace['passed']
r = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         passed=True, private_files=checked, source_trees=source['trees'],
         host_scope=host['limits'], ordinary_runtime_scope_passed=True,
         strict_qualification=False, windows_hd_qualified=False, physical_deployment=False,
         evidence={str(p.relative_to(k.parent)): sha(p) for p in
                   [k / 'binary-review001.json', k / 'source-postbuild-review.json',
                    k.parent / 'hd-reservation301/final-review.json',
                    k.parent / 'hd-reservation301/trace-review.json']},
         limits='720x480 reservation-only emulator pair. Full live PFN/cache/alias checks and Windows HD timing remain outstanding.')
dest.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(dict(passed=True, private_files_rehashed=len(checked))))
