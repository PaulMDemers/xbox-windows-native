"""Read-only preflight for one Xbox 1.0 fixed-profile transition (480p or 1080i)."""
from __future__ import annotations

import argparse
import contextlib
import ipaddress
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'outputs/bundle-deploy846/source'))
from common import deployment_lease, retrieve, retrieve_to_file, sha, sha_file, verify_f_owner
from compat import preflight846
from profiles import expected_delta, pins, verify_archive, verify_source_profile

_base = preflight846()
MANAGED_ROOTS = _base.MANAGED_ROOTS
_read_identity = _base._read_identity
_scan_relevant_tree = _base._scan_relevant_tree
_write_receipt = _base._write_receipt

STATE = SOURCE.parent / 'state'
MAX_PREIMAGE_FILE_BYTES = 8 * 1024**3
MIN_HEADROOM = 128 * 1024**2
HOST_RESERVE = 20 * 1024**3
ATTEMPT_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{1,31}$')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def lookup_directory(directories, remote):
    """Find a scanned FATX directory case-insensitively, including '/E'."""
    folded = remote.casefold()
    direct = directories.get(folded)
    if direct is not None:
        return direct
    return next((value for key, value in directories.items() if key.casefold() == folded), None)


@contextlib.contextmanager
def attempt_lock(profile: str, attempt: str):
    require(profile in ('e-720p', 'e-720x480', 'e-1080i'), 'Invalid target profile')
    require(ATTEMPT_RE.fullmatch(attempt) is not None, 'Attempt ID must be a short lowercase token')
    STATE.mkdir(parents=True, exist_ok=True)
    lock = STATE / f'{profile}-{attempt}.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, json.dumps({'profile': profile, 'attempt_id': attempt, 'pid': os.getpid()}).encode())
        os.fsync(fd)
        yield lock
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def read_base_receipt(path: Path, expected_sha256: str, identity: dict, identity_sha256: str):
    raw = Path(path).read_bytes()
    require(sha(raw) == expected_sha256.lower(), '846 base receipt SHA-256 mismatch')
    base = json.loads(raw.decode('utf-8'))
    require(base.get('completed') is True and base.get('physical_writes') is False,
            '846 read-only baseline receipt is incomplete')
    target = base.get('target', {})
    require(base.get('archive', {}).get('profile') == 'e-720p'
            and base.get('archive', {}).get('sha256') == pins()['profiles']['e-720p']['sha256']
            and target.get('console_revision') == '1.0' and target.get('dashboard_ip') == '192.168.50.242',
            '846 receipt is not from the reviewed 1.0 target')
    require(target.get('identity_evidence_sha256', target.get('identity_receipt_sha256')) == identity_sha256.lower(),
            '846 receipt does not pin the supplied preserved identity')
    expected_records = {(x['path'].casefold(), x['sha256'].lower()) for x in identity['markers']}
    recorded = {(x.get('path', '').casefold(), x.get('sha256', '').lower())
                for x in target.get('identity_markers', [])}
    require(expected_records <= recorded, '846 receipt identity markers differ from the supplied 1.0 identity')
    required = {x['path'].casefold(): x['sha256'].lower() for x in identity['markers']}
    captured = {p.casefold(): row for p, row in base.get('files', {}).items()}
    for path, digest in required.items():
        row = captured.get(path)
        require(row and row.get('sha256') == digest and row.get('identity_marker') is True,
                'Identity marker was not preserved in the 846 receipt: ' + path)
    f_marker = base.get('f_owner_marker', {})
    require(f_marker.get('path') == '/F/xwn-deploy-v1.json' and isinstance(f_marker.get('sha256'), str),
            '846 F ownership marker receipt missing')
    return base, raw


def _validate_base_preimages(receipt_dir: Path, base: dict, identity: dict):
    for marker in identity['markers']:
        row = next((r for p, r in base['files'].items() if p.casefold() == marker['path'].casefold()), None)
        require(row is not None, 'Preserved identity marker not in base receipt')
        backup = (receipt_dir / row['backup_path']).resolve()
        require(backup.is_relative_to((receipt_dir / 'before').resolve()), 'Base marker backup escapes receipt')
        require(backup.is_file() and sha_file(backup) == marker['sha256'].lower(),
                'Preserved identity marker backup mismatch')


def run(profile: str, source_profile: str, attempt: str, archive: Path, archive_sha256: str,
        identity_path: Path, identity_sha256: str, base_receipt_path: Path, base_receipt_sha256: str,
        config_path: Path, dashboard_ip: str, destination: Path, *, ftp_factory=None,
        ticket_check=None, lock_path=None, disk_usage_fn=None):
    if ftp_factory is None:
        import ftplib
        ftp_factory = ftplib.FTP
    if disk_usage_fn is None:
        disk_usage_fn = shutil.disk_usage
    target_ip = str(ipaddress.ip_address(dashboard_ip))
    require(target_ip == '192.168.50.242', '847 is restricted to the reviewed 1.0 dashboard')
    require(profile in ('e-720p', 'e-720x480', 'e-1080i') and source_profile != profile,
            'Select one different fixed profile; no live profile switching')
    require(ATTEMPT_RE.fullmatch(attempt) is not None, 'Invalid unique attempt ID')
    manifest, target_pin, profile_table = verify_archive(archive, profile)
    require(sha_file(archive) == archive_sha256.lower() == target_pin['sha256'], 'Archive hash pin mismatch')
    identity, identity_raw = _read_identity(identity_path, identity_sha256, target_ip)
    base, base_raw = read_base_receipt(base_receipt_path, base_receipt_sha256, identity, identity_sha256)
    _validate_base_preimages(Path(base_receipt_path).parent, base, identity)
    files_in_package = {row['path']: row for row in manifest['files'] if row['path'].startswith('E/')}
    dirs_in_package = [p for p in manifest['directories'] if p == 'E' or p.startswith('E/')]
    delta = expected_delta(source_profile, profile, manifest)
    destination = Path(destination)
    require(destination.is_absolute() and not destination.exists(), 'Use a new private receipt directory per attempt')
    require(destination.parent.is_dir() and not destination.parent.is_symlink(), 'Receipt parent must be a regular directory')
    require(not destination.resolve().is_relative_to(ROOT), 'Keep private profile preimages outside the repository')
    record = {
        'schema': 1, 'attempt_id': attempt, 'completed': False, 'physical_writes': False,
        'launch_requested': False, 'source_profile': source_profile, 'target_profile': profile,
        'archive': {'profile': profile, 'sha256': target_pin['sha256'], 'bytes': target_pin['bytes']},
        'target': {'dashboard_ip': target_ip, 'console_revision': '1.0',
                   'identity_receipt_sha256': identity_sha256.lower(),
                   'identity_evidence_sha256': identity_sha256.lower(),
                   'identity_markers': [{'path': x['path'], 'sha256': x['sha256'].lower()} for x in identity['markers']]},
        'base_receipt': {'sha256': base_receipt_sha256.lower(), 'archive_sha256': base['archive']['sha256'],
                         'path_hint': Path(base_receipt_path).name},
        'f_owner_marker': None, 'source_profile_state': None,
        'launcher_change': next(row for row in delta if row['kind'] == 'launcher'),
        'mode_delta': delta,
        'capacity': {'status': 'insufficient-evidence',
                     'reason': 'No recent live FATX allocation/free-cluster measurement is present; transfer requires a separate current capacity receipt.'},
        'directories': {}, 'files': {}, 'archive_targets': {}, 'preserved_bytes': 0,
    }
    with attempt_lock(profile, attempt):
        lease = {'ftp_factory': ftp_factory}
        if ticket_check is not None:
            lease['ticket_check'] = ticket_check
        if lock_path is not None:
            lease['lock_path'] = lock_path
        with deployment_lease(config_path, target_ip, **lease) as (ftp, host):
            require(host == target_ip, 'Private FTP config/dashboard address mismatch')
            record['f_owner_marker'] = verify_f_owner(ftp)
            require(record['f_owner_marker']['sha256'] == base['f_owner_marker']['sha256'],
                    'F ownership marker changed since the 846 identity preflight')
            record['source_profile_state'] = verify_source_profile(ftp, source_profile, retrieve=retrieve,
                                                                   list_dir=_base._list_dir)
            for marker in identity['markers']:
                data = retrieve(ftp, marker['path'], 16 * 1024**2)
                require(sha(data) == marker['sha256'].lower(), 'Preserved 1.0 marker mismatch: ' + marker['path'])
            scanned, dirs, total_bytes = _scan_relevant_tree(ftp, identity['markers'], files_in_package, dirs_in_package)
            free = disk_usage_fn(destination.parent).free
            required = total_bytes + MIN_HEADROOM + HOST_RESERVE
            require(free >= required, 'Host 20 GiB reserve would be consumed by profile preimages')
            destination.mkdir()
            record['capacity'].update({'measured_host_preimage_bytes': total_bytes,
                                       'host_free_before_capture_bytes': free,
                                       'host_free_after_capture_floor_bytes': free - total_bytes,
                                       'required_host_free_bytes': required,
                                       'minimum_host_reserve_bytes': HOST_RESERVE})
            record['directories'] = {row.get('path', key): row for key, row in dirs.items()}
            for path, row in files_in_package.items():
                remote = '/' + path
                current = scanned.get(remote.casefold())
                record['archive_targets'][remote] = {
                    'kind': 'file', 'archive_path': path, 'expected_bytes': row['bytes'],
                    'expected_sha256': row['sha256'], 'exists': current is not None,
                    'target_path': current['path'] if current else remote,
                    'before_bytes': current['bytes'] if current else None,
                    'before_sha256': None,
                }
            for directory in dirs_in_package:
                remote = '/' + directory
                current = lookup_directory(dirs, remote)
                record['archive_targets'][remote] = {'kind': 'directory', 'archive_path': directory,
                                                     'exists': current is not None,
                                                     'target_path': current.get('path', remote) if current else remote}
            record['target']['identity_marker_readbacks'] = [
                {'path': m['path'], 'sha256': m['sha256'].lower(), 'matched': True} for m in identity['markers']]
            _write_receipt(destination, record)
            try:
                for remote_key, row in scanned.items():
                    remote = row['path']
                    require(row['bytes'] <= MAX_PREIMAGE_FILE_BYTES, 'Selected preimage exceeds per-file bound')
                    rel = remote.lstrip('/')
                    local = destination / 'before' / Path(*rel.split('/'))
                    local.parent.mkdir(parents=True, exist_ok=True)
                    captured = retrieve_to_file(ftp, remote, local, row['bytes'], MAX_PREIMAGE_FILE_BYTES)
                    require(sha_file(local) == captured['sha256'], 'Preimage readback hash mismatch: ' + remote)
                    entry = {'path': remote, 'bytes': captured['bytes'], 'sha256': captured['sha256'],
                             'backup_path': local.relative_to(destination).as_posix(),
                             'archive_paths': row['archive_paths'], 'identity_marker': row['identity_marker']}
                    record['files'][remote] = entry
                    record['preserved_bytes'] += captured['bytes']
                    for archive_path in row['archive_paths']:
                        key = '/' + archive_path
                        target = record['archive_targets'][key]
                        target['exists'] = True
                        target['target_path'] = remote
                        target['before_bytes'] = captured['bytes']
                        target['before_sha256'] = captured['sha256']
                    if len(record['files']) % 200 == 0:
                        _write_receipt(destination, record)
            except BaseException as exc:
                record['error_type'] = type(exc).__name__
                record['error'] = str(exc)
                _write_receipt(destination, record)
                raise
    record['completed'] = True
    _write_receipt(destination, record)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=('e-720p', 'e-720x480', 'e-1080i'), required=True)
    p.add_argument('--source-profile', choices=('e-720p', 'e-720x480', 'e-1080i'), required=True)
    p.add_argument('--attempt', required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--archive-sha256', required=True)
    p.add_argument('--identity', type=Path, required=True)
    p.add_argument('--identity-sha256', required=True)
    p.add_argument('--base-receipt', type=Path, required=True)
    p.add_argument('--base-receipt-sha256', required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--dashboard-ip', required=True)
    p.add_argument('--destination', type=Path, required=True)
    a = p.parse_args()
    result = run(a.profile, a.source_profile, a.attempt, a.archive, a.archive_sha256,
                 a.identity, a.identity_sha256, a.base_receipt, a.base_receipt_sha256,
                 a.config, a.dashboard_ip, a.destination)
    print(json.dumps({'completed': result['completed'], 'profile': a.profile, 'attempt': a.attempt,
                      'archive_sha256': result['archive']['sha256'], 'preserved_files': len(result['files']),
                      'physical_writes': False, 'launch_requested': False,
                      'capacity': result['capacity']['status']}, sort_keys=True))


if __name__ == '__main__':
    main()
