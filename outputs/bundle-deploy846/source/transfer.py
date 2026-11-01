"""One-shot Xbox 1.0 E transfer or audited journal-linked continuation; no launch/delete."""
import argparse
import datetime
import io
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle as bundle
from common import deployment_lease, retrieve, sha, verify_f_owner
from preflight import MANAGED_ROOTS, _list_dir, _scan_relevant_tree, _read_identity

ARCHIVE = 'e1837395ac915fd1446bf115fc713a9e267df9c79667a2cff018f11cb8415915'
LAUNCHER = '/E/Applications/XWNEBoot/default.xbe'
EXPECTED_OLD_LAUNCHER = '6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expected_scan_dirs(pre, created, receipt_sha):
    managed = tuple('/' + x.casefold() for x in MANAGED_ROOTS)
    root_rows = [v for p, v in pre['directories'].items() if p.casefold() == '/e']
    require(len(root_rows) == 1, 'Ambiguous E root receipt')
    if not root_rows[0]['exists']:
        require(receipt_sha == '37838d4a1d9a180bb1609b49dc3945d5efe942b4a7b1ba83a202e0cf0e3fde63',
                'Unexpected absent E root in preflight')
    expected = {'/e'} | {p.casefold() for p, d in pre['directories'].items() if d['exists'] and
               (p.casefold() in ('/e', '/e/applications') or any(p.casefold() == root or p.casefold().startswith(root + '/') for root in managed))}
    expected |= {p.casefold() for p in created if any(p.casefold() == root or p.casefold().startswith(root + '/') for root in managed)}
    return expected


def run(a):
    receipt_dir = a.receipt.resolve()
    first_journal = receipt_dir / 'transfer001.jsonl'
    continuation_journal = receipt_dir / 'transfer002.jsonl'
    if a.previous:
        require(a.previous.resolve() == first_journal and a.journal.resolve() == continuation_journal,
                'Continuation must link the fixed original and successor journals')
    else:
        require(a.journal.resolve() == first_journal and not first_journal.exists() and not continuation_journal.exists(),
                'First attempt already exists; never replay it')
    record_bytes = (a.receipt / 'preflight.json').read_bytes()
    require(sha(record_bytes) == a.preflight_sha256, 'Preflight receipt hash mismatch')
    pre = json.loads(record_bytes)
    require(pre['completed'] and not pre['physical_writes'] and not pre['launch_requested'], 'Incomplete preflight')
    require(pre['archive']['profile'] == 'e-720p' and pre['archive']['sha256'] == ARCHIVE, 'Wrong package')
    require(a.dashboard_ip == '192.168.50.242' and pre['target']['console_revision'] == '1.0' and pre['target']['dashboard_ip'] == a.dashboard_ip,
            'Wrong console revision or endpoint')
    require(sha(a.archive.read_bytes()) == ARCHIVE, 'Archive hash mismatch')
    manifest = bundle.verify(a.archive)
    require(manifest['kind'] == 'windows-e-preview' and manifest['profile'] == 'e-720p', 'Wrong manifest profile')
    rows = {'/' + x['path']: x for x in manifest['files'] if x['path'].startswith('E/')}
    targets = {path: row for path, row in pre['archive_targets'].items() if row['kind'] == 'file'}
    require(set(rows) == set(targets), 'Incomplete archive target map')
    for path, row in rows.items():
        target = targets[path]
        require(target['expected_sha256'] == row['sha256'] and target['expected_bytes'] == row['bytes'], 'Target map mismatch')
        require(target['target_path'].casefold() == path.casefold(), 'Unsafe target alias')
    old_launcher = targets[LAUNCHER]
    require(old_launcher['exists'] and old_launcher['before_sha256'] == EXPECTED_OLD_LAUNCHER,
            'Expected 1.0 launcher was not captured')
    saved = {path.casefold(): row for path, row in pre['files'].items()}
    require(len(saved) == len(pre['files']), 'Duplicate case-insensitive preimages')
    for path, target in targets.items():
        if target['exists']:
            captured = saved.get(target['target_path'].casefold())
            require(captured is not None and captured['bytes'] == target['before_bytes']
                    and captured['sha256'] == target['before_sha256'], 'Archive target preimage was not captured: ' + path)
        else:
            require(target['target_path'].casefold() not in saved, 'Absent target conflicts with a captured file')
    for path, row in pre['files'].items():
        backup = (a.receipt / row['backup_path']).resolve()
        require(backup.is_relative_to((a.receipt / 'before').resolve()), 'Backup outside private capture')
        require(type(row['bytes']) is int and 0 <= row['bytes'] <= 256 * 1024**2,
                'Captured preimage exceeds transfer audit limit: ' + path)
        data = backup.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Backup changed: ' + path)
    cap_bytes = a.capacity.read_bytes()
    require(sha(cap_bytes) == a.capacity_sha256, 'Capacity observation hash mismatch')
    cap = json.loads(cap_bytes)
    require(cap['schema'] == 1 and cap['source'] == 'user-dashboard-observation' and cap['dashboard_ip'] == a.dashboard_ip
            and cap['volume'] == 'E' and cap['cluster_bytes'] == 16384, 'Wrong capacity observation')
    observed = datetime.datetime.fromisoformat(cap['observed_utc'].replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    age = (now - observed).total_seconds()
    require(0 <= age <= 1200, 'Capacity observation must be recent')
    require(type(cap['displayed_bytes']) is int and cap['displayed_bytes'] >= 0 and type(cap['rounding_bytes']) is int
            and type(cap['lower_bound_bytes']) is int
            and cap['rounding_bytes'] > 0 and cap['lower_bound_bytes'] == max(0, cap['displayed_bytes'] - cap['rounding_bytes']),
            'Invalid conservative rounding bound')
    alloc = lambda n: ((n + 16383) // 16384) * 16384
    growth = sum(max(0, alloc(row['bytes']) - alloc(targets[path]['before_bytes'] or 0)) for path, row in rows.items())
    growth += 16384 * sum(not d['exists'] for d in pre['directories'].values())
    require(growth + 256 * 1024**2 <= cap['lower_bound_bytes'], 'Insufficient observed E capacity plus reserve')
    identity_sha = pre['target'].get('identity_receipt_sha256') or pre['target'].get('identity_evidence_sha256')
    require(identity_sha and pre['target'].get('identity_evidence_sha256', identity_sha) == identity_sha,
            'Identity receipt hashes disagree')
    identity, identity_data = _read_identity(a.identity, identity_sha, a.dashboard_ip)
    require(sha(identity_data) == identity_sha, 'Identity changed')
    done = set()
    created = set()
    old_hash = None
    if a.previous:
        old_bytes = a.previous.read_bytes()
        require(sha(old_bytes) == a.previous_sha256, 'Previous journal hash mismatch')
        old_hash = sha(old_bytes)
        old = [json.loads(x) for x in old_bytes.splitlines()]
        require(old and old[0]['kind'] == 'start' and old[0]['archive_sha256'] == ARCHIVE, 'Wrong prior journal')
        require(old[0].get('previous_journal_sha256') is None, 'Further continuation requires manual review')
        require(old[0]['preflight_sha256'] == a.preflight_sha256, 'Prior journal/preflight mismatch')
        require(not any(x['kind'] == 'complete' for x in old), 'Prior transaction already complete')
        wi = [x for x in old if x['kind'] == 'write_intent']
        wv = [x for x in old if x['kind'] == 'write_verified']
        mi = [x for x in old if x['kind'] == 'mkdir_intent']
        mv = [x for x in old if x['kind'] == 'mkdir_verified']
        done = {x['path'] for x in wv}
        created = {x['path'] for x in mv}
        require(len(wi) == len(wv) == len(done) and {x['path'] for x in wi} == done, 'Uncertain write: manual recovery required')
        require(len(mi) == len(mv) == len(created) and {x['path'] for x in mi} == created, 'Uncertain mkdir: manual recovery required')
        require(all(path in rows for path in done) and LAUNCHER not in done, 'Invalid or launched prior transfer')
        require(all(x['target_sha256'] == rows[x['path']]['sha256'] for x in wi + wv), 'Prior digest mismatch')
    else:
        require(not a.previous_sha256, 'Unexpected previous journal hash')
    require(not a.journal.exists(), 'Fresh journal required; never replay a failed attempt')
    with deployment_lease(a.config, a.dashboard_ip, timeout=20) as (ftp, host):
        require(host == pre['target']['dashboard_ip'], 'Endpoint changed')
        require(verify_f_owner(ftp)['sha256'] == pre['f_owner_marker']['sha256'], 'F owner changed')
        for marker in identity['markers']:
            require(sha(retrieve(ftp, marker['path'], 256 * 1024**2)) == marker['sha256'], 'Identity marker changed')
        with a.journal.open('xb', buffering=0) as journal, zipfile.ZipFile(a.archive) as z:
            def log(kind, path, **fields):
                journal.write((json.dumps({'kind': kind, 'path': path, **fields}) + '\n').encode())
                os.fsync(journal.fileno())
            log('start', 'E', archive_sha256=ARCHIVE, preflight_sha256=a.preflight_sha256,
                capacity_sha256=a.capacity_sha256, previous_journal_sha256=old_hash,
                projected_growth_bytes=growth, conservative_free_bytes=cap['lower_bound_bytes'])
            archive_files = {path.lstrip('/'): row for path, row in rows.items()}
            archive_dirs = [x for x in manifest['directories'] if x == 'E' or x.startswith('E/')]
            current, current_dirs, _ = _scan_relevant_tree(ftp, identity['markers'], archive_files, archive_dirs)
            expected_existing = set(saved) | {p.casefold() for p in done if not targets[p]['exists']}
            require(set(current) == expected_existing, 'Managed tree file set changed')
            expected_dirs = expected_scan_dirs(pre, created, a.preflight_sha256)
            require({p.casefold() for p, d in current_dirs.items() if d['exists']} == expected_dirs, 'Managed tree directory set changed')
            done_keys = {p.casefold(): p for p in done}
            for index, (key, row) in enumerate(current.items(), 1):
                actual_path = row['path']
                target_path = done_keys.get(key)
                expected = rows[target_path]['sha256'] if target_path else saved[key]['sha256']
                require(sha(retrieve(ftp, actual_path, row['bytes'])) == expected, 'Managed file changed: ' + actual_path)
                if index % 100 == 0:
                    log('audit_progress', 'E', files=index)
            log('audit_complete', 'E', files=len(current))
            dirs = sorted((x for x in manifest['directories'] if x.startswith('E/')), key=lambda x: (x.count('/'), x))
            for directory in dirs:
                remote = '/' + directory
                parent, leaf = remote.rsplit('/', 1)
                current_entry = _list_dir(ftp, parent).get(leaf.casefold())
                if current_entry:
                    require(current_entry['directory'], 'Directory collision: ' + remote)
                    continue
                require(remote.casefold() not in {p.casefold() for p in created}, 'Previously created directory vanished')
                log('mkdir_intent', remote)
                ftp.mkd(remote)
                require(_list_dir(ftp, parent)[leaf.casefold()]['directory'], 'Directory creation readback failed')
                log('mkdir_verified', remote)
            for path in sorted(set(rows) - {LAUNCHER}) + [LAUNCHER]:
                row, old_target = rows[path], targets[path]
                if path in done:
                    continue
                # Unchanged targets need no write; the launcher still receives a fresh final check.
                if old_target['exists'] and old_target['before_sha256'] == row['sha256']:
                    if path == LAUNCHER:
                        require(sha(retrieve(ftp, old_target['target_path'], row['bytes'])) == EXPECTED_OLD_LAUNCHER,
                                'Existing launcher changed immediately before completion')
                        log('launcher_verified_unchanged', path, target_sha256=row['sha256'])
                    continue
                parent, leaf = path.rsplit('/', 1)
                entry = _list_dir(ftp, parent).get(leaf.casefold())
                if old_target['exists']:
                    require(entry and not entry['directory'] and entry['bytes'] == old_target['before_bytes'], 'Preimage missing')
                    require(sha(retrieve(ftp, old_target['target_path'], entry['bytes'])) == old_target['before_sha256'], 'Preimage changed')
                else:
                    require(entry is None, 'Previously absent target appeared')
                data = z.read(row['path'])
                require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Package member mismatch')
                log('write_intent', path, target_sha256=row['sha256'])
                for offset in range(0, max(1, len(data)), 32768):
                    ftp.storbinary(('STOR ' if offset == 0 else 'APPE ') + old_target['target_path'],
                                   io.BytesIO(data[offset:offset + 32768]), 1024)
                require(sha(retrieve(ftp, old_target['target_path'], len(data))) == row['sha256'], 'Write readback mismatch')
                log('write_verified', path, target_sha256=row['sha256'])
            for index, (path, row) in enumerate(rows.items(), 1):
                require(sha(retrieve(ftp, targets[path]['target_path'], row['bytes'])) == row['sha256'], 'Final readback mismatch: ' + path)
                if index % 100 == 0:
                    log('readback_progress', 'E', files=index)
            target_keys = {p.casefold() for p in rows}
            for key, old_file in saved.items():
                if key not in target_keys:
                    require(sha(retrieve(ftp, old_file['path'], old_file['bytes'])) == old_file['sha256'],
                            'Unrelated preserved file changed: ' + old_file['path'])
            log('complete', 'E', files=len(rows), launcher_last=True, launch_requested=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('archive', 'receipt', 'capacity', 'identity', 'config', 'journal'):
        p.add_argument('--' + arg, type=Path, required=True)
    for arg in ('preflight-sha256', 'capacity-sha256', 'dashboard-ip'):
        p.add_argument('--' + arg, required=True)
    p.add_argument('--previous', type=Path)
    p.add_argument('--previous-sha256')
    run(p.parse_args())


if __name__ == '__main__':
    main()
