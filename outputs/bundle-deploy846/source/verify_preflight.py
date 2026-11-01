"""Offline audit of captured Xbox 1.0 managed-root preimages and archive mapping."""
import argparse
import json
from pathlib import Path
import transfer
from common import sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('receipt', type=Path)
p.add_argument('archive', type=Path)
a = p.parse_args()
raw = (a.receipt / 'preflight.json').read_bytes()
d = json.loads(raw)
assert d['completed'] and not d['physical_writes'] and not d['launch_requested']
assert d['target']['dashboard_ip'] == '192.168.50.242' and d['target']['console_revision'] == '1.0'
assert len(d['target']['identity_marker_readbacks']) >= 2
assert all(x['matched'] for x in d['target']['identity_marker_readbacks'])
assert d['archive']['sha256'] == transfer.ARCHIVE == sha(a.archive.read_bytes())
manifest = transfer.bundle.verify(a.archive)
rows = {'/' + x['path']: x for x in manifest['files'] if x['path'].startswith('E/')}
targets = {p: v for p, v in d['archive_targets'].items() if v['kind'] == 'file'}
assert set(rows) == set(targets)
files = {p.casefold(): x for p, x in d['files'].items()}
assert len(files) == len(d['files']) and len(files) > 1
total = 0
for path, item in d['files'].items():
    backup = (a.receipt / item['backup_path']).resolve()
    assert backup.is_relative_to((a.receipt / 'before').resolve())
    data = backup.read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256']
    total += len(data)
assert total == d['preserved_bytes']
for path, row in rows.items():
    target = targets[path]
    assert target['expected_sha256'] == row['sha256'] and target['expected_bytes'] == row['bytes']
    assert target['target_path'].casefold() == path.casefold()
    if target['exists']:
        previous = files[target['target_path'].casefold()]
        assert previous['sha256'] == target['before_sha256'] and previous['bytes'] == target['before_bytes']
    else:
        assert target['target_path'].casefold() not in files
launcher = targets[transfer.LAUNCHER]
assert launcher['exists'] and launcher['before_sha256'] == transfer.EXPECTED_OLD_LAUNCHER
assert max(x['bytes'] for x in files.values()) <= 256 * 1024**2
alloc = lambda n: ((n + 16383) // 16384) * 16384
growth = sum(max(0, alloc(row['bytes']) - alloc(targets[path]['before_bytes'] or 0)) for path, row in rows.items())
growth += 16384 * sum(not x['exists'] for x in d['directories'].values())
assert growth + 256 * 1024**2 <= 480000000
print(json.dumps({'preflight_sha256': sha(raw), 'archive_targets': len(rows), 'captured_files': len(files),
                  'captured_bytes': total, 'identity_markers': len(d['target']['identity_marker_readbacks']),
                  'existing_launcher_sha256': launcher['before_sha256'], 'projected_positive_growth': growth,
                  'conservative_e_free': 480000000, 'required_reserve': 256 * 1024**2}, indent=2))
