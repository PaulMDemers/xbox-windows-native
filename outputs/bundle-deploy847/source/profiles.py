"""Pinned Xbox 1.0 fixed-profile archives and mode-delta checks for 847."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle as bundle
from common import sha, sha_file

PINS_PATH = Path(__file__).resolve().with_name('profile-pins.json')
PINS_SHA256 = 'd81420b8297d72953caf9e2794b7e8874243c867af7fc2100585fd8d91487a81'
PROFILE_PATHS = {
    'launcher': 'E/Applications/XWNEBoot/default.xbe',
    'xwnfatx': 'E/winnt/system32/drivers/xwnfatx.sys',
    'freeldr': 'E/Applications/XWNEBoot/freeldr.sys',
    'rosload': 'E/Applications/XWNEBoot/rosload.exe',
    'startup': 'E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd',
}


def pins():
    data = PINS_PATH.read_bytes()
    if sha(data) != PINS_SHA256:
        raise ValueError('847 profile pins file changed')
    return json.loads(data.decode('utf-8'))


def verify_source_evidence(table=None):
    table = table or pins()
    for source in table['sources']:
        path = ROOT / source['path']
        if path.is_symlink() or not path.is_file() or sha_file(path) != source['sha256']:
            raise ValueError('Profile evidence source changed: ' + source['path'])


def common_tree_digest(manifest):
    mode = {p.casefold() for p in pins()['shared_tree']['profile_changing_paths']}
    rows = sorted(({'path': row['path'].casefold(), 'bytes': row['bytes'], 'sha256': row['sha256']}
                   for row in manifest['files'] if row['path'].startswith('E/')
                   and row['path'].casefold() not in mode), key=lambda row: row['path'])
    raw = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return len(rows), hashlib.sha256(raw).hexdigest()


def verify_archive(path: Path, profile: str):
    table = pins()
    if profile not in table['profiles'] or profile not in table['rotation_profiles']:
        raise ValueError('Only fixed 480p or 1080i target profiles are supported here')
    verify_source_evidence(table)
    entry = table['profiles'][profile]
    path = Path(path)
    if path.stat().st_size != entry['bytes'] or sha_file(path) != entry['sha256']:
        raise ValueError('Selected profile archive hash/size mismatch')
    manifest = bundle.verify(path)
    if manifest['kind'] != 'windows-e-preview' or manifest['profile'] != profile:
        raise ValueError('Selected archive manifest/profile mismatch')
    common_count, common_sha = common_tree_digest(manifest)
    shared = table['shared_tree']
    if common_count != shared['file_count'] or common_sha != shared['sha256']:
        raise ValueError('Archive common E tree differs from reviewed profile set')
    rows = {row['path'].casefold(): row for row in manifest['files'] if row['path'].startswith('E/')}
    for key in ('launcher', 'xwnfatx'):
        expected = entry[key]
        row = rows.get(expected['path'].casefold())
        if row is None or row['bytes'] != expected['bytes'] or row['sha256'] != expected['sha256']:
            raise ValueError('Profile-specific ' + key + ' pin mismatch')
    shared_boot = table['shared_boot_and_startup']
    for path, expected in shared_boot.items():
        row = rows.get(path.casefold())
        if row is None or row['bytes'] != expected['bytes'] or row['sha256'] != expected['sha256']:
            raise ValueError('Shared boot/startup pin mismatch: ' + path)
    return manifest, entry, table


def verify_source_profile(ftp, source_profile: str, *, retrieve, list_dir):
    table = pins()
    if source_profile not in table['current_baseline_profiles']:
        raise ValueError('Unsupported current profile')
    source = table['profiles'][source_profile]
    expected = [source['launcher'], source['xwnfatx']]
    expected.extend({'path': path, **item} for path, item in table['shared_boot_and_startup'].items())
    observed = {}
    for item in expected:
        remote = '/' + item['path']
        data = retrieve(ftp, remote, item['bytes'])
        digest = sha(data)
        if len(data) != item['bytes'] or digest != item['sha256']:
            raise ValueError('Current profile pin mismatch: ' + remote)
        observed[remote] = {'bytes': len(data), 'sha256': digest}
    startup = '/' + PROFILE_PATHS['startup']
    startup_dir = startup.rsplit('/', 1)[0]
    listing = list_dir(ftp, startup_dir)
    cmd_files = [row['name'].casefold() for row in listing.values()
                 if not row['directory'] and row['name'].casefold().endswith('.cmd')]
    if sorted(cmd_files) != ['xwnsetup.cmd']:
        raise ValueError('Unexpected startup command/hook; preserve and inspect before switching')
    return {'profile': source_profile, 'files': observed, 'startup_command_files': cmd_files}


def expected_delta(source_profile: str, target_profile: str, manifest):
    table = pins()
    if source_profile not in table['current_baseline_profiles']:
        raise ValueError('Unsupported source profile')
    if target_profile not in table['rotation_profiles'] or source_profile == target_profile:
        raise ValueError('Switch must name one different supported fixed profile')
    target = table['profiles'][target_profile]
    source = table['profiles'][source_profile]
    rows = {row['path'].casefold(): row for row in manifest['files'] if row['path'].startswith('E/')}
    delta = []
    for key in ('xwnfatx', 'launcher'):
        before = source[key]
        after = target[key]
        if before['sha256'] != after['sha256']:
            row = rows.get(after['path'].casefold())
            if row is None or row['sha256'] != after['sha256'] or row['bytes'] != after['bytes']:
                raise ValueError('Target delta does not match package manifest')
            delta.append({'path': after['path'], 'kind': key, 'before_bytes': before['bytes'],
                          'before_sha256': before['sha256'], 'after_bytes': after['bytes'],
                          'after_sha256': after['sha256'], 'write_order': 2 if key == 'launcher' else 1})
    if not any(row['kind'] == 'launcher' for row in delta):
        raise ValueError('Profile switch must change the fixed-mode launcher')
    if sum(row['kind'] == 'launcher' for row in delta) != 1:
        raise ValueError('Exactly one mode launcher change is allowed')
    return sorted(delta, key=lambda row: row['write_order'])
