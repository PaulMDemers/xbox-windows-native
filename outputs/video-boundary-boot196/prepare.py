"""Fresh standalone byte-equivalent pending diagnostic; original chains stay immutable."""
import subprocess
from common import *

dest = k / 'fixture-pending002.json'
assert not dest.exists()
prior = k.parent / 'video-measurement-boundary194'
f = read(prior / 'fixture-pending001.json')
base = ws / 'outputs/native-windows-fatx-forensics/artifacts' / f['fixture_name']
assert sha(base) == f['fixture_sha256']
assert read(prior / 'pending001/closure.json')['closed']
out = k / 'pending002'
out.mkdir(exist_ok=False)
target = Path('/mnt/e/Codex-archive/xbox-windows-native/video-boundary196/pending002.qcow2')
assert not target.exists()
target.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['qemu-img', 'convert', '-c', '-O', 'qcow2', str(base), str(target)], check=True)
subprocess.run(['qemu-img', 'compare', '-f', 'qcow2', '-F', 'qcow2', str(base), str(target)], check=True)
info = json.loads(subprocess.check_output(['qemu-img', 'info', '--output=json', str(target)]))
assert not info.get('backing-filename') and info['virtual-size'] == 250059350016
with ColdIO(target) as io:
    rr = readers(io, target)
    for name, digest in f['files'].items():
        volume, path = name.split('/', 1)
        assert m.sha(rr[volume].read(path)) == digest, name
    for name in HIVES:
        p = out / 'artifacts' / ('before-' + name)
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(rr['F'].read('winnt/system32/config/' + name))
        hive(p)
scan(target, out / 'before/artifacts')
a = read(out / 'before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
for row in f['parents']:
    assert sha(Path(row['path'])) == row['sha256']
assert sha(base) == f['fixture_sha256']
record = dict(f, case='pending002', guest_launch=False, physical_access=False,
              fixture_path_linux=str(target),
              fixture_path_windows='E:/Codex-archive/xbox-windows-native/video-boundary196/pending002.qcow2',
              fixture_sha256=sha(target), seed_sha256=sha(target),
              standalone_compressed=True, virtual_compare_equal=True,
              original_prelaunch_sha256=f['fixture_sha256'],
              prior_failed_closure_sha256=sha(prior / 'pending001/closure.json'),
              original_chains_unchanged=True,
              debugger_observations_planned=True, ordinary_qualified=False,
              limits='New standalone/compressed host fixture is a diagnostic discriminator, '
                     'not a kernel/driver/registry fix or relaunch of closed194. Exact same helper/startup/core bytes.')
save(dest, record)
print('New196 standalone byte-equivalent fixture, protected/hives/allocation and original chains verified')
