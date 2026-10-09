"""Prepare an independent unobserved pending child only after closed196 functional integrity."""
import subprocess
from common import *

prior = k.parent / 'video-boundary-boot196'
closed = read(prior / 'pending002/closure.json')
audit = read(prior / 'pending002/audit.json')
assert closed['closed'] and sha(prior / 'pending002/audit.json') == closed['audit_sha256']
assert audit['diagnostic_usable'] and audit['pending_branch_passed'] and audit['integrity_passed']
assert audit['debugger'] and audit['ordinary_qualified'] is False
assert read(prior / 'pending002/live-observation.json')['closed']
dest = k / 'fixture-pending001.json'
assert not dest.exists()
out = k / 'pending001'
assert not out.exists()
f = read(prior / 'fixture-pending002.json')
base = Path(f['fixture_path_linux'])
assert sha(base) == f['fixture_sha256']
info = json.loads(subprocess.check_output(['qemu-img', 'info', '--output=json', str(base)]))
assert not info.get('backing-filename') and info['virtual-size'] == 250059350016
out.mkdir()
with ColdIO(base) as io:
    rr = readers(io, base)
    for name, digest in f['files'].items():
        volume, path = name.split('/', 1)
        assert m.sha(rr[volume].read(path)) == digest, name
    for name in HIVES:
        p = out / 'artifacts' / ('before-' + name)
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(rr['F'].read('winnt/system32/config/' + name))
        hive(p)
scan(base, out / 'before/artifacts')
a = read(out / 'before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
for row in f['parents']:
    assert sha(Path(row['path'])) == row['sha256']
assert sha(base) == f['fixture_sha256']
save(dest, dict(f, case='pending001', guest_launch=False, debugger_observations_planned=False,
                prerequisite196_closure_sha256=sha(prior / 'pending002/closure.json'),
                prerequisite196_audit_sha256=sha(prior / 'pending002/audit.json'),
                retained194_failure_sha256=sha(k.parent / 'video-measurement-boundary194/pending001/closure.json'),
                limits='Fresh unobserved run from the immutable byte-equivalent standalone source; '
                'no driver/helper/device/registry change, not an ordinary whole-boot or physical qualification.'))
print('197 standalone source reverified, closed196 prerequisite pinned, no launch')
