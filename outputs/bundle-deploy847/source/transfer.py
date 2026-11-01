"""Transfer only the reviewed fixed-profile delta; never delete, launch or retry."""
from __future__ import annotations

import argparse
import datetime
import io
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'outputs/bundle-deploy846/source'))
from common import deployment_lease, retrieve, sha, sha_file, verify_f_owner
from profiles import expected_delta, verify_archive, verify_source_profile
from compat import preflight846, preflight847

_base = preflight846()
_switch_preflight = preflight847()
attempt_lock = _switch_preflight.attempt_lock
require = _switch_preflight.require
_read_identity = _base._read_identity

RESERVE_BYTES = 256 * 1024**2
LAUNCHER = '/E/Applications/XWNEBoot/default.xbe'
STARTUP = '/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'


def load_capacity(path: Path, expected_sha: str, dashboard_ip: str):
    raw = Path(path).read_bytes()
    require(sha(raw) == expected_sha.lower(), 'Capacity receipt hash mismatch')
    obj = json.loads(raw.decode('utf-8'))
    require(obj.get('schema') == 1 and obj.get('source') == 'user-dashboard-observation'
            and obj.get('dashboard_ip') == dashboard_ip and obj.get('volume') == 'E'
            and obj.get('cluster_bytes') == 16384, 'Invalid or wrong-console E capacity receipt')
    observed = datetime.datetime.fromisoformat(obj['observed_utc'].replace('Z', '+00:00'))
    age = (datetime.datetime.now(datetime.timezone.utc) - observed).total_seconds()
    require(0 <= age <= 1200, 'E capacity receipt must be from the last 20 minutes')
    shown = obj.get('displayed_bytes'); rounding = obj.get('rounding_bytes'); lower = obj.get('lower_bound_bytes')
    require(type(shown) is int and shown >= 0 and type(rounding) is int and rounding > 0
            and type(lower) is int and lower == max(0, shown - rounding), 'Invalid conservative capacity bound')
    return obj, raw


def _save_journal_line(stream, row):
    stream.write((json.dumps(row, sort_keys=True) + '\n').encode('utf-8'))
    os.fsync(stream.fileno())


def index_archive_targets(manifest_files, archive_targets):
    """Index manifest paths in the same absolute form used by preflight receipts."""
    rows = {}
    for row in manifest_files:
        path = row['path']
        if not path.startswith('E/'):
            continue
        key = ('/' + path).casefold()
        require(key not in rows, 'Duplicate case-insensitive path in archive manifest')
        rows[key] = row
    targets = {}
    for path, row in archive_targets.items():
        if row.get('kind') != 'file':
            continue
        require(path.startswith('/') and not path.startswith('//'), 'Archive target path is not absolute')
        key = path.casefold()
        require(key not in targets, 'Duplicate case-insensitive file target in preflight receipt')
        targets[key] = row
    require(set(rows) == set(targets), 'Incomplete archive target inventory')
    for key, item in rows.items():
        target = targets[key]
        require(target.get('archive_path', '').casefold() == item['path'].casefold(),
                'Archive target path differs from manifest')
        require(target.get('expected_sha256') == item['sha256']
                and target.get('expected_bytes') == item['bytes'],
                'Archive target content pin differs from manifest')
    return rows, targets


def run(archive: Path, receipt: Path, preflight_sha256: str, capacity: Path, capacity_sha256: str,
        identity: Path, identity_sha256: str, config: Path, dashboard_ip: str,
        attempt: str, *, ftp_factory=None, ticket_check=None, lock_path=None):
    if ftp_factory is None:
        import ftplib
        ftp_factory = ftplib.FTP
    receipt = Path(receipt)
    pre_bytes = (receipt / 'preflight.json').read_bytes()
    require(sha(pre_bytes) == preflight_sha256.lower(), 'Preflight receipt hash mismatch')
    pre = json.loads(pre_bytes.decode('utf-8'))
    require(pre.get('completed') is True and pre.get('physical_writes') is False
            and pre.get('launch_requested') is False, 'Incomplete or unsafe preflight receipt')
    require(pre.get('attempt_id') == attempt, 'Attempt ID mismatch')
    profile = pre.get('target_profile'); source_profile = pre.get('source_profile')
    manifest, target_pin, table = verify_archive(archive, profile)
    require(pre['archive']['sha256'] == target_pin['sha256'] and sha_file(archive) == target_pin['sha256'],
            'Archive changed since preflight')
    require(pre['target']['console_revision'] == '1.0' and pre['target']['dashboard_ip'] == dashboard_ip == '192.168.50.242',
            'Wrong target identity')
    identity_obj, identity_raw = _read_identity(identity, pre['target']['identity_evidence_sha256'], dashboard_ip)
    require(sha(identity_raw) == identity_sha256.lower() == pre['target']['identity_evidence_sha256'], 'Identity evidence changed')
    base_delta = expected_delta(source_profile, profile, manifest)
    require(base_delta == pre['mode_delta'], 'Mode delta changed since preflight')
    capacity_obj, capacity_raw = load_capacity(capacity, capacity_sha256, dashboard_ip)
    rows, targets = index_archive_targets(manifest['files'], pre['archive_targets'])
    # The only mutable targets are the mode launcher and, when needed, the HDTV FATX driver.
    delta_paths = {('/' + row['path']).casefold(): row for row in base_delta}
    require(set(delta_paths) == {('/' + row['path']).casefold() for row in pre['mode_delta']}, 'Invalid write set')
    old_launcher = targets[LAUNCHER.casefold()]
    require(old_launcher['exists'] and old_launcher['before_sha256'] == table['profiles'][source_profile]['launcher']['sha256'],
            'Current launcher preimage is not the selected source profile')
    startup_target = targets[STARTUP.casefold()]
    startup_pin = table['shared_boot_and_startup'][STARTUP[1:].lower()]
    require(startup_target['exists'] and startup_target['before_sha256'] == startup_pin['sha256'],
            'Normal startup script changed; refusing to touch it')
    for path, row in pre['files'].items():
        backup = (receipt / row['backup_path']).resolve()
        require(backup.is_relative_to((receipt / 'before').resolve()), 'Backup path escapes preflight receipt')
        require(backup.is_file() and backup.stat().st_size == row['bytes'] and sha_file(backup) == row['sha256'],
                'Preserved preimage changed: ' + path)
    alloc = lambda size: ((size + 16383) // 16384) * 16384
    growth = 0
    for item in base_delta:
        path = ('/' + item['path']).casefold()
        target = targets[path]
        growth += max(0, alloc(item['after_bytes']) - alloc(target['before_bytes'] or 0))
    require(growth + RESERVE_BYTES <= capacity_obj['lower_bound_bytes'], 'Insufficient conservative E capacity')
    journal = receipt / 'transfer.jsonl'
    require(not journal.exists(), 'Transfer journal exists; never repeat an uncertain write')
    options = {'ftp_factory': ftp_factory, 'timeout': 20}
    if ticket_check is not None:
        options['ticket_check'] = ticket_check
    if lock_path is not None:
        options['lock_path'] = lock_path
    with attempt_lock(profile, attempt):
        with deployment_lease(config, dashboard_ip, **options) as (ftp, host):
            require(host == dashboard_ip, 'FTP endpoint changed')
            require(verify_f_owner(ftp)['sha256'] == pre['f_owner_marker']['sha256'], 'F owner marker changed')
            for marker in identity_obj['markers']:
                require(sha(retrieve(ftp, marker['path'], 16 * 1024**2)) == marker['sha256'],
                        'Preserved 1.0 identity marker changed')
            current = verify_source_profile(ftp, source_profile, retrieve=retrieve,
                                             list_dir=_base._list_dir)
            journal_created = False
            with zipfile.ZipFile(archive) as z:
                # Recheck every changed preimage immediately before any write.
                for path, item in delta_paths.items():
                    target = targets[path]
                    remote = target['target_path']
                    data = retrieve(ftp, remote, target['before_bytes'])
                    require(len(data) == target['before_bytes'] and sha(data) == target['before_sha256'],
                            'Profile file changed since preflight: ' + remote)
                with journal.open('xb', buffering=0) as log:
                    journal_created = True
                    _save_journal_line(log, {'kind': 'start', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                             'attempt_id': attempt, 'source_profile': source_profile,
                                             'target_profile': profile, 'archive_sha256': target_pin['sha256'],
                                             'preflight_sha256': preflight_sha256.lower(),
                                             'capacity_sha256': capacity_sha256.lower(), 'projected_growth_bytes': growth,
                                             'remaining_reserve_bytes': capacity_obj['lower_bound_bytes'] - growth,
                                             'launcher_change': pre['launcher_change'], 'normal_startup_unchanged': True,
                                             'automatic_retry': False})
                    # Driver delta first; fixed-mode launcher always changes last.
                    for delta in base_delta:
                        remote = '/' + delta['path']
                        if delta['kind'] == 'launcher':
                            require(remote.casefold() == LAUNCHER.casefold(), 'Unexpected launcher path')
                        archive_path = delta['path']
                        data = z.read(archive_path)
                        require(len(data) == delta['after_bytes'] and sha(data) == delta['after_sha256'],
                                'Archive delta bytes mismatch')
                        before = targets[remote.casefold()]
                        _save_journal_line(log, {'kind': 'write_intent', 'path': remote,
                                                 'before_sha256': before['before_sha256'],
                                                 'target_sha256': delta['after_sha256'],
                                                 'bytes': delta['after_bytes'],
                                                 'launcher': delta['kind'] == 'launcher'})
                        for offset in range(0, max(1, len(data)), 32768):
                            ftp.storbinary(('STOR ' if offset == 0 else 'APPE ') + before['target_path'],
                                           io.BytesIO(data[offset:offset + 32768]), 1024)
                        readback = retrieve(ftp, before['target_path'], len(data))
                        require(len(readback) == len(data) and sha(readback) == delta['after_sha256'],
                                'Changed file readback mismatch: ' + remote)
                        _save_journal_line(log, {'kind': 'write_verified', 'path': remote,
                                                 'target_sha256': delta['after_sha256'],
                                                 'bytes': len(data), 'launcher': delta['kind'] == 'launcher'})
                    # Keep the shared startup command byte-identical and confirm final profile pins.
                    final = verify_source_profile(ftp, profile, retrieve=retrieve,
                                                  list_dir=_base._list_dir)
                    _save_journal_line(log, {'kind': 'complete', 'files': len(base_delta),
                                             'changed_paths': [row['path'] for row in base_delta],
                                             'launcher_last': True, 'launch_requested': False,
                                             'final_profile': final['profile'],
                                             'final_files': final['files']})
    return {'completed': True, 'profile': profile, 'attempt_id': attempt,
            'archive_sha256': target_pin['sha256'], 'mode_delta': base_delta,
            'journal_sha256': sha(journal.read_bytes()), 'physical_writes': True,
            'launch_requested': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('archive', 'receipt', 'capacity', 'identity', 'config'):
        p.add_argument('--' + arg, type=Path, required=True)
    for arg in ('preflight-sha256', 'capacity-sha256', 'identity-sha256', 'dashboard-ip', 'attempt'):
        p.add_argument('--' + arg, required=True)
    a = p.parse_args()
    result = run(a.archive, a.receipt, a.preflight_sha256, a.capacity, a.capacity_sha256,
                 a.identity, a.identity_sha256, a.config, a.dashboard_ip, a.attempt)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
