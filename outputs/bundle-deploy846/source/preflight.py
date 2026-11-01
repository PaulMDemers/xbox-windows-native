"""Read-only 1.0 fixed-720p package preflight and full managed-root preimage capture.

This utility never calls FTP STOR/APPE/MKD/DELE/SITE and never launches XBE.
It is intentionally limited to the Xbox 1.0, fixed 720p archive. It is not a
hardware qualification or permission to install. Do not run against hardware
until the parent review and operator staging gates are complete.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle as bundle
import fatx_names
from common import deployment_lease, retrieve, retrieve_to_file, sha, sha_file, verify_f_owner

PROFILE = 'e-720p'
REVISION = '1.0'
MANAGED_ROOTS = (
    'E/WINNT', 'E/Documents and Settings', 'E/Program Files',
    'E/Applications/XWNEBoot', 'E/xwndemo372',
)
MAX_MARKER_BYTES = 16 * 1024**2
MAX_PREIMAGE_FILE_BYTES = 8 * 1024**3
MAX_CAPTURE_BYTES = 128 * 1024**3
MAX_ENTRIES = 50000
MIN_HOST_HEADROOM = 128 * 1024**2
HOST_FREE_RESERVE = 20 * 1024**3


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _valid_hash(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in '0123456789abcdef' for c in value.lower()))


def _remote_path(parts):
    path = '/'.join(parts)
    fatx_names.check_path(path, 437)
    return '/' + path


def _list_dir(ftp, remote):
    _require(remote == '/E' or remote.startswith('/E/') or remote == '/F',
             'Preflight LIST is restricted to E roots and the pinned F owner marker')
    ftp.cwd(remote)
    actual = ftp.pwd().replace('\\', '/').rstrip('/')
    _require(actual.casefold() == remote.rstrip('/').casefold(), 'FTP CWD/PWD mismatch')
    rows = []
    ftp.retrlines('LIST', rows.append)
    result = {}
    for row in rows:
        fields = row.split(None, 8)
        _require(len(fields) == 9, 'Unsupported FTP LIST format')
        name = fields[8]
        if name in ('.', '..'):
            continue
        _require('/' not in name and '\\' not in name, 'Unsafe FTP name')
        _require(name not in ('', '.', '..') and not any(ord(c) < 32 or ord(c) == 127 for c in name),
                 'Unsafe FTP name')
        key = name.casefold()
        _require(key not in result, 'Case-insensitive FTP name collision')
        is_dir = fields[0].startswith('d')
        try:
            size = int(fields[4])
        except ValueError as exc:
            raise ValueError('Unsupported FTP LIST size') from exc
        _require(0 <= size <= 2**63 - 1, 'FTP entry size bound')
        result[key] = {'name': name, 'directory': is_dir, 'bytes': size}
    return result


def _read_identity(identity_path: Path, expected_sha256: str, dashboard_ip: str):
    data = Path(identity_path).read_bytes()
    _require(sha(data) == expected_sha256.lower(), 'Identity receipt hash mismatch')
    obj = json.loads(data.decode('utf-8'))
    _require(isinstance(obj, dict) and obj.get('schema') == 1, 'Unknown identity receipt schema')
    _require(obj.get('console_revision') == REVISION, 'Refusing target revision other than Xbox 1.0')
    _require(obj.get('profile') == PROFILE, 'Identity receipt is not for the selected fixed 720p profile')
    _require(obj.get('dashboard_ip') == dashboard_ip, 'Identity receipt/dashboard IP mismatch')
    markers = obj.get('markers')
    _require(isinstance(markers, list) and len(markers) >= 2, 'At least two historic identity markers are required')
    seen = set()
    for marker in markers:
        _require(isinstance(marker, dict), 'Invalid identity marker record')
        path = marker.get('path')
        _require(isinstance(path, str) and path.startswith('/E/') and '\r' not in path and '\n' not in path,
                 'Identity markers must be exact E paths')
        fatx_names.check_path(path.lstrip('/'), 437)
        key = path.casefold()
        _require(key not in seen, 'Duplicate identity marker path')
        seen.add(key)
        _require(_valid_hash(marker.get('sha256')), 'Invalid identity marker hash')
        evidence_path = marker.get('evidence_path')
        evidence_sha = marker.get('evidence_sha256')
        _require(isinstance(evidence_path, str) and _valid_hash(evidence_sha),
                 'Each identity marker must cite a pinned evidence receipt')
        evidence_file = (ROOT / evidence_path).resolve()
        _require(evidence_file.is_relative_to(ROOT) and evidence_file.is_file() and not evidence_file.is_symlink(),
                 'Identity evidence must be a local repository file')
        evidence_data = evidence_file.read_bytes()
        _require(sha(evidence_data) == evidence_sha.lower(), 'Identity evidence file hash mismatch')
        record = json.loads(evidence_data.decode('utf-8-sig'))
        expected = marker['sha256'].lower()
        row = None
        for table in ('staged', 'before'):
            candidate = record.get(table, {}).get(path)
            if candidate:
                row = candidate
                break
        _require(isinstance(row, dict) and row.get('sha256') == expected,
                 'Marker hash is not present at the cited historic path')
    return obj, data


def _write_receipt(destination: Path, record: dict):
    path = destination / 'preflight.json'
    tmp = destination / 'preflight.json.tmp'
    with tmp.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _scan_relevant_tree(ftp, identity_markers, archive_files, archive_dirs):
    root_listing = _list_dir(ftp, '/E')
    files = {}
    # Keep all inventory keys casefolded, including the volume root. Consumers
    # use normalized manifest paths such as '/E' -> '/e'.
    directories = {'/e': {'path': '/E', 'exists': True, 'archive_paths': []}}
    total_bytes = 0
    count = 1
    archive_file_names = {('/' + p).casefold(): p for p in archive_files}
    archive_dir_names = {('/' + p).casefold(): p for p in archive_dirs}

    def add_file(remote, entry, archive_path=None, marker=False):
        nonlocal total_bytes, count
        key = remote.casefold()
        if key in files:
            existing = files[key]
            if archive_path:
                existing['archive_paths'].append(archive_path)
            existing['identity_marker'] = existing.get('identity_marker', False) or marker
            return
        archive_path = archive_path or archive_file_names.get(key)
        files[key] = {'path': remote, 'bytes': entry['bytes'], 'archive_paths': [archive_path] if archive_path else [],
                      'identity_marker': marker, 'expected_archive_sha256': None}
        _require(entry['bytes'] <= MAX_PREIMAGE_FILE_BYTES, 'Selected preimage file exceeds per-file bound')
        total_bytes += entry['bytes']
        _require(total_bytes <= MAX_CAPTURE_BYTES, 'Managed-root preimage exceeds total capture bound')
        count += 1
        _require(count <= MAX_ENTRIES, 'Managed-root entry count bound exceeded')

    def descend(remote, listing, archive_path=None):
        nonlocal count
        key = remote.casefold()
        archive_path = archive_path or archive_dir_names.get(key)
        directories.setdefault(key, {'path': remote, 'exists': True, 'archive_paths': []})
        if archive_path:
            directories[key]['archive_paths'].append(archive_path)
        for item in listing.values():
            child = remote.rstrip('/') + '/' + item['name']
            if item['directory']:
                count += 1
                _require(count <= MAX_ENTRIES, 'Managed-root entry count bound exceeded')
                child_key = child.casefold()
                child_archive = archive_dir_names.get(child_key)
                directories[child_key] = {'path': child, 'exists': True,
                                          'archive_paths': [child_archive] if child_archive else []}
                descend(child, _list_dir(ftp, child))
            else:
                add_file(child, item)

    for archive_root in MANAGED_ROOTS:
        parts = archive_root.split('/')
        parent = '/E'
        listing = root_listing
        actual_parts = ['E']
        missing = False
        for index, component in enumerate(parts[1:], 1):
            found = listing.get(component.casefold())
            expected_path = '/'.join(parts[:index + 1])
            if found is None:
                directories[('/' + expected_path).casefold()] = {
                    'path': '/' + expected_path, 'exists': False,
                    'archive_paths': [expected_path] if ('/' + expected_path).casefold() in archive_dir_names else []}
                missing = True
                break
            _require(found['directory'], 'Managed directory collides with a file: ' + expected_path)
            actual_parts.append(found['name'])
            parent = '/' + '/'.join(actual_parts)
            actual_key = parent.casefold()
            archive_path = archive_dir_names.get(actual_key)
            directories[actual_key] = {'path': parent, 'exists': True,
                                       'archive_paths': [archive_path] if archive_path else []}
            listing = _list_dir(ftp, parent)
        if not missing:
            descend(parent, listing, archive_root)

    # Identity markers may live in the private, isolated historical test namespace.
    # Capture the marker preimage too, but do not inventory unrelated siblings.
    for marker in identity_markers:
        remote = marker['path']
        parent, leaf = remote.rsplit('/', 1)
        listing = _list_dir(ftp, parent)
        entry = listing.get(leaf.casefold())
        _require(entry is not None and not entry['directory'], 'Required 1.0 identity marker missing: ' + remote)
        actual = parent.rstrip('/') + '/' + entry['name']
        add_file(actual, entry, marker=True)
    return files, directories, total_bytes


def run(archive: Path, archive_sha256: str, identity_path: Path, identity_sha256: str,
        config_path: Path, dashboard_ip: str, destination: Path, *, ftp_factory=None,
        lock_path=None, ticket_check=None, disk_usage_fn=None):
    """Perform local package checks, then read-only FTP checks and local capture."""
    if ftp_factory is None:
        import ftplib
        ftp_factory = ftplib.FTP
    if disk_usage_fn is None:
        disk_usage_fn = shutil.disk_usage
    _require(_valid_hash(archive_sha256), 'Invalid pinned archive hash')
    actual_archive_sha = sha_file(Path(archive))
    _require(actual_archive_sha == archive_sha256.lower(), 'Archive SHA-256 mismatch')
    manifest = bundle.verify(Path(archive))
    _require(manifest['kind'] == 'windows-e-preview' and manifest['profile'] == PROFILE,
             'Only the pinned 1.0 fixed 720p package is accepted')
    try:
        dashboard_ip = str(ipaddress.ip_address(dashboard_ip))
    except ValueError as exc:
        raise ValueError('Dashboard IP must be a literal address') from exc
    _require(ipaddress.ip_address(dashboard_ip).version == 4, 'Only IPv4 dashboard addresses are supported')
    identity, identity_data = _read_identity(identity_path, identity_sha256, dashboard_ip)
    target_files = {x['path']: x for x in manifest['files'] if x['path'].startswith('E/')}
    target_dirs = [x for x in manifest['directories'] if x == 'E' or x.startswith('E/')]
    _require(all(any(p.casefold().startswith(root.casefold() + '/') for root in MANAGED_ROOTS)
                 for p in target_files), 'Archive contains a file outside the five managed roots')
    destination = Path(destination)
    _require(destination.is_absolute() and not destination.exists(), 'Receipt destination must be a new absolute path')
    _require(destination.parent.is_dir() and not destination.parent.is_symlink(),
             'Receipt parent must be an existing regular directory')
    _require(not destination.resolve().is_relative_to(ROOT), 'Keep private console preimages outside the repository')

    record = {
        'schema': 1, 'completed': False, 'physical_writes': False, 'launch_requested': False,
        'archive': {'profile': PROFILE, 'sha256': actual_archive_sha, 'bytes': Path(archive).stat().st_size},
        'target': {'dashboard_ip': dashboard_ip, 'console_revision': REVISION, 'profile': PROFILE,
                   'identity_receipt_sha256': identity_sha256.lower(),
                   'identity_evidence_sha256': identity_sha256.lower(),
                   'identity_markers': [{'path': x['path'], 'sha256': x['sha256'].lower()} for x in identity['markers']]},
        'f_owner_marker': None, 'capacity': {
            'status': 'insufficient-evidence',
            'reason': 'FTP LIST reports logical file sizes, not Xbox FATX free clusters/allocation; no pinned live E capacity counter is available. No write stage may proceed until capacity is independently measured and receipted.'},
        'directories': {}, 'files': {}, 'archive_targets': {}, 'preserved_bytes': 0,
    }
    lease_options = {'ftp_factory': ftp_factory}
    if lock_path is not None:
        lease_options['lock_path'] = lock_path
    if ticket_check is not None:
        lease_options['ticket_check'] = ticket_check
    with deployment_lease(config_path, dashboard_ip, **lease_options) as (ftp, host):
        record['target']['dashboard_ip'] = host
        record['f_owner_marker'] = verify_f_owner(ftp)
        for marker in identity['markers']:
            data = retrieve(ftp, marker['path'], MAX_MARKER_BYTES)
            _require(sha(data) == marker['sha256'].lower(), 'Xbox 1.0 identity marker hash mismatch: ' + marker['path'])
        files, directories, total_bytes = _scan_relevant_tree(ftp, identity['markers'], target_files, target_dirs)
        free = disk_usage_fn(destination.parent).free
        required = total_bytes + MIN_HOST_HEADROOM + HOST_FREE_RESERVE
        _require(free >= required,
                 'Host free-space preflight would consume the required 20 GiB reserve')
        destination.mkdir()
        record['target']['identity_marker_readbacks'] = [
            {'path': m['path'], 'sha256': m['sha256'].lower(), 'matched': True} for m in identity['markers']]
        record['capacity']['measured_preimage_logical_bytes'] = total_bytes
        record['capacity']['host_free_before_capture_bytes'] = free
        record['capacity']['required_host_free_bytes'] = required
        record['capacity']['projected_host_free_after_capture_bytes'] = free - total_bytes
        record['capacity']['minimum_host_reserve_bytes'] = HOST_FREE_RESERVE
        record['directories'] = {d['path'] if d.get('path') else k: d for k, d in directories.items()}
        # Every package E file path is explicit even when absent; this is the rollback absent-path journal.
        for path, item in target_files.items():
            remote = '/' + path
            actual = files.get(remote.casefold())
            record['archive_targets'][remote] = {
                'kind': 'file',
                'archive_path': path, 'expected_bytes': item['bytes'], 'expected_sha256': item['sha256'],
                'exists': actual is not None,
                'target_path': actual['path'] if actual else remote,
                'before_bytes': actual['bytes'] if actual else None,
                'before_sha256': None,
            }
        # Include every archive directory before any preimage transfer begins.
        for archive_dir in target_dirs:
            remote = '/' + archive_dir
            prior = directories.get(remote.casefold())
            if prior is None:
                record['directories'][remote] = {'path': remote, 'exists': False, 'archive_paths': [archive_dir]}
                record['archive_targets'][remote] = {'kind': 'directory', 'archive_path': archive_dir,
                                                     'exists': False, 'target_path': remote}
            else:
                actual_path = prior.get('path', remote)
                record['directories'][actual_path] = dict(prior, archive_paths=list(set(prior.get('archive_paths', [])) | {archive_dir}))
                record['archive_targets'][remote] = {'kind': 'directory', 'archive_path': archive_dir,
                                                     'exists': prior.get('exists', True), 'target_path': actual_path}
        _write_receipt(destination, record)
        # Preserve every file in the five managed roots, including non-package extras, and identity markers.
        try:
            for key, row in files.items():
                remote = row['path']
                _require(row['bytes'] <= MAX_PREIMAGE_FILE_BYTES, 'Selected file exceeds streaming preimage bound')
                rel = remote.lstrip('/')
                fatx_names.check_path(rel, 437)
                backup = destination / 'before' / Path(*rel.split('/'))
                backup.parent.mkdir(parents=True, exist_ok=True)
                capture = retrieve_to_file(ftp, remote, backup, row['bytes'], MAX_PREIMAGE_FILE_BYTES)
                digest = capture['sha256']
                _require(sha_file(backup) == digest, 'Local preimage readback mismatch: ' + remote)
                saved = {'path': remote, 'bytes': capture['bytes'], 'sha256': digest,
                         'backup_path': str(backup.relative_to(destination)).replace('\\', '/'),
                         'archive_paths': row['archive_paths'], 'identity_marker': row['identity_marker']}
                record['files'][remote] = saved
                record['preserved_bytes'] += capture['bytes']
                for target in row['archive_paths']:
                    target_key = '/' + target
                    record['archive_targets'][target_key] = {
                        'kind': 'file',
                        'archive_path': target, 'expected_bytes': target_files[target]['bytes'],
                        'expected_sha256': target_files[target]['sha256'], 'exists': True,
                        'target_path': remote, 'before_bytes': capture['bytes'], 'before_sha256': digest,
                    }
                if len(record['files']) % 200 == 0:
                    _write_receipt(destination, record)
        except BaseException as exc:
            record['error_type'] = type(exc).__name__
            record['error'] = str(exc)
            _write_receipt(destination, record)
            raise
    # Keep archive targets in manifest spelling, including case aliases to current FATX names.
    for path, item in target_files.items():
        remote = '/' + path
        record['archive_targets'].setdefault(remote, {
            'kind': 'file', 'archive_path': path, 'expected_bytes': item['bytes'], 'expected_sha256': item['sha256'],
            'exists': False, 'target_path': remote, 'before_bytes': None, 'before_sha256': None,
        })
    record['completed'] = True
    _write_receipt(destination, record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    parser.add_argument('--identity', type=Path, required=True,
                        help='local operator-prepared identity JSON; pins revision/profile/markers/evidence')
    parser.add_argument('--identity-sha256', required=True)
    parser.add_argument('--config', type=Path, required=True,
                        help='private JSON config or literal session.py; never copied into receipt')
    parser.add_argument('--dashboard-ip', required=True)
    parser.add_argument('--destination', type=Path, required=True,
                        help='new private local directory for complete managed-root preimages')
    args = parser.parse_args(argv)
    result = run(args.archive, args.archive_sha256, args.identity, args.identity_sha256,
                 args.config, args.dashboard_ip, args.destination)
    print(json.dumps({'completed': result['completed'], 'archive_sha256': result['archive']['sha256'],
                      'profile': PROFILE, 'preserved_files': len(result['files']),
                      'preserved_bytes': result['preserved_bytes'], 'physical_writes': False,
                      'launch_requested': False, 'capacity': result['capacity']['status']}, sort_keys=True))


if __name__ == '__main__':
    main()
