"""Host-only transfer guard tests; no network calls or real Xbox data."""
import datetime
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import transfer

root_bug = {'directories': {'/E': {'exists': False}, '/E/Applications': {'exists': True},
                            '/E/WINNT': {'exists': True}, '/E/WINNT/new': {'exists': False}}}
pin = '37838d4a1d9a180bb1609b49dc3945d5efe942b4a7b1ba83a202e0cf0e3fde63'
assert transfer.expected_scan_dirs(root_bug, set(), pin) == {'/e', '/e/applications', '/e/winnt'}
try:
    transfer.expected_scan_dirs(root_bug, set(), '0' * 64)
except ValueError:
    pass
else:
    raise AssertionError('Unpinned absent-root receipt accepted')


def encode(value):
    return (json.dumps(value) + '\n').encode()


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    archive = root / 'fixture.zip'
    archive.write_bytes(b'fixture archive')
    original_archive = transfer.ARCHIVE
    original_launcher = transfer.EXPECTED_OLD_LAUNCHER
    transfer.ARCHIVE = transfer.sha(archive.read_bytes())
    before = b'original launcher'
    transfer.EXPECTED_OLD_LAUNCHER = transfer.sha(before)
    receipt = root / 'receipt'
    backup = receipt / 'before/E/Applications/XWNEBoot/default.xbe'
    backup.parent.mkdir(parents=True)
    backup.write_bytes(before)
    lp = transfer.LAUNCHER
    row = {'path': lp.lstrip('/'), 'bytes': len(before), 'sha256': transfer.sha(before)}
    target = {'kind': 'file', 'archive_path': row['path'], 'expected_bytes': row['bytes'],
              'expected_sha256': row['sha256'], 'exists': True, 'target_path': lp,
              'before_bytes': len(before), 'before_sha256': transfer.sha(before)}
    pre = {'completed': True, 'physical_writes': False, 'launch_requested': False,
           'archive': {'profile': 'e-720p', 'sha256': transfer.ARCHIVE},
           'target': {'console_revision': '1.0', 'dashboard_ip': '192.168.50.242', 'identity_receipt_sha256': transfer.sha(b'identity')},
           'archive_targets': {lp: target, '/E': {'kind': 'directory'}},
           'files': {lp: {'path': lp, 'bytes': len(before), 'sha256': transfer.sha(before),
                          'backup_path': 'before/E/Applications/XWNEBoot/default.xbe'}},
           'directories': {'/E': {'exists': True}}}
    pre_bytes = encode(pre)
    (receipt / 'preflight.json').write_bytes(pre_bytes)
    cap = {'schema': 1, 'source': 'user-dashboard-observation', 'dashboard_ip': '192.168.50.242',
           'volume': 'E', 'cluster_bytes': 16384, 'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'displayed_bytes': 2 * 1024**3, 'rounding_bytes': 1024**2,
           'lower_bound_bytes': 2 * 1024**3 - 1024**2}
    cap_path = root / 'capacity.json'
    cap_path.write_bytes(encode(cap))
    args = SimpleNamespace(receipt=receipt, preflight_sha256=transfer.sha(pre_bytes), archive=archive,
                           dashboard_ip='192.168.50.242', capacity=cap_path,
                           capacity_sha256=transfer.sha(cap_path.read_bytes()), identity=root / 'identity',
                           config=root / 'config', journal=receipt / 'transfer001.jsonl', previous=None, previous_sha256=None)
    manifest = {'kind': 'windows-e-preview', 'profile': 'e-720p', 'files': [row]}
    class LeaseReached(Exception):
        pass
    with patch.object(transfer.bundle, 'verify', return_value=manifest), \
         patch.object(transfer, '_read_identity', return_value=({'markers': []}, b'identity')), \
         patch.object(transfer, 'deployment_lease', side_effect=LeaseReached):
        try:
            transfer.run(args)
        except LeaseReached:
            pass
        else:
            raise AssertionError('Valid fixture did not reach the lease gate')
        backup.write_bytes(b'changed')
        try:
            transfer.run(args)
        except ValueError as exc:
            assert 'Backup changed' in str(exc)
        else:
            raise AssertionError('Changed backup was accepted')
        backup.write_bytes(before)
        cap['lower_bound_bytes'] = 1
        cap_path.write_bytes(encode(cap))
        args.capacity_sha256 = transfer.sha(cap_path.read_bytes())
        try:
            transfer.run(args)
        except ValueError as exc:
            assert 'rounding' in str(exc)
        else:
            raise AssertionError('Invalid capacity bound was accepted')
        cap['lower_bound_bytes'] = cap['displayed_bytes'] - cap['rounding_bytes']
        cap_path.write_bytes(encode(cap))
        args.capacity_sha256 = transfer.sha(cap_path.read_bytes())
        previous = receipt / 'transfer001.jsonl'
        previous.write_bytes(encode({'kind': 'start', 'archive_sha256': transfer.ARCHIVE,
                                     'preflight_sha256': args.preflight_sha256, 'previous_journal_sha256': None}) +
                             encode({'kind': 'write_intent', 'path': lp, 'target_sha256': row['sha256']}))
        args.previous, args.previous_sha256 = previous, transfer.sha(previous.read_bytes())
        args.journal = receipt / 'transfer002.jsonl'
        try:
            transfer.run(args)
        except ValueError as exc:
            assert 'Uncertain write' in str(exc)
        else:
            raise AssertionError('Unmatched write intent was accepted for continuation')
    transfer.ARCHIVE = original_archive
    transfer.EXPECTED_OLD_LAUNCHER = original_launcher
print('846 host-only archive, preimage and capacity gates passed')
