"""One bounded Xbox 1.0 packaged boot after verified transfer; never retry SITE."""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle as bundle
from common import STATE, deployment_lease, retrieve, sha, verify_f_owner
from preflight import _read_identity
from transfer import ARCHIVE, LAUNCHER, EXPECTED_OLD_LAUNCHER, require

COMMAND = r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
LAUNCH_GUARD = STATE / 'launch846-once.jsonl'
PINS = {
    'E/Applications/XWNEBoot/default.xbe': EXPECTED_OLD_LAUNCHER,
    'E/Applications/XWNEBoot/freeldr.ini': '5d003852c683031a90b8ab7de21077e0ee9133501fa847cf18a9544212e5124c',
    'E/Applications/XWNEBoot/freeldr.sys': '8723fc175cc490f0c3cd1650e9c91ab97e9ed04108734ad6202e6f0653804697',
    'E/Applications/XWNEBoot/rosload.exe': '62f3620183cb2c7b1aa575d9908df3e54e043cd5bf62c1c8a291954e9876f4b1',
    'E/Applications/XWNEBoot/loader/halxboxnt5.dll': 'a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648',
    'E/Applications/XWNEBoot/loader/xboxbvid.dll': '0c8f5d494016a72e098134072d340aa83252fada2739b538b9be5a633d20623f',
    'E/winnt/system32/drivers/xwnfatx.sys': '41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126',
    'E/winnt/system32/drivers/xboxvnt5.sys': '74ccdc9fc7b26fe76919941fe978822b1fb538c7814343b0f0755d99e661c1dd',
    'E/winnt/system32/ntoskrnl.exe': '84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152',
    'E/winnt/system32/xwnown.dll': 'b23b94ac12c9f507e3d905d9de905dcff9a8fd53c2fba4336fb830e97666101d',
    'E/winnt/system32/config/system': '1fd47f2de4ca1aa8c9a285321ce81e285c4a417aff5de136c9812c8359b12a44',
    'E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd': '257ec9b4c77199f0ac046289912c41acdaba3a30750bf81dfb4c09cbb003af2d',
    'E/xwndemo372/display-settings.exe': '7ff648f3e41cff123ca6659482e94a2575ec8a081ffbfbbd2387e97e605ac470',
    'E/xwndemo372/outline-applied.txt': '31172c0f9d516939ee90b07e3d27190cebcdfb68aad1ce4e86a9d89326d92955',
}


def pairs(journal, rows):
    intent = [(x['path'], x['target_sha256']) for x in journal if x['kind'] == 'write_intent']
    verified = [(x['path'], x['target_sha256']) for x in journal if x['kind'] == 'write_verified']
    require(intent == verified and len({p for p, _ in intent}) == len(intent), 'Uncertain/duplicate write')
    require(all(p in rows and rows[p]['sha256'] == h for p, h in intent), 'Journal target mismatch')
    return intent


def validate(a):
    require(not LAUNCH_GUARD.exists() and not (a.receipt / 'launch846.jsonl').exists(), 'Launch intent already exists; never retry')
    pre_bytes = (a.receipt / 'preflight.json').read_bytes()
    require(sha(pre_bytes) == a.preflight_sha256, 'Preflight hash mismatch')
    pre = json.loads(pre_bytes)
    require(pre['completed'] and not pre['physical_writes'] and not pre['launch_requested'], 'Incomplete preflight')
    require(pre['target']['dashboard_ip'] == a.dashboard_ip == '192.168.50.242' and pre['target']['console_revision'] == '1.0', 'Wrong target')
    require(pre['archive']['sha256'] == sha(a.archive.read_bytes()) == ARCHIVE, 'Wrong archive')
    manifest = bundle.verify(a.archive)
    require(manifest['kind'] == 'windows-e-preview' and manifest['profile'] == 'e-720p', 'Wrong profile')
    rows = {'/' + x['path']: x for x in manifest['files'] if x['path'].startswith('E/')}
    targets = {p: x for p, x in pre['archive_targets'].items() if x['kind'] == 'file'}
    require(set(rows) == set(targets), 'Incomplete target map')
    require(all('/' + p in rows and rows['/' + p]['sha256'] == h == targets['/' + p]['expected_sha256']
                for p, h in PINS.items()), 'Pinned boot dependency mismatch')
    data = a.journal.read_bytes()
    require(sha(data) == a.journal_sha256, 'Journal hash mismatch')
    j = [json.loads(line) for line in data.splitlines()]
    require(j and j[0]['kind'] == 'start' and j[0]['archive_sha256'] == ARCHIVE and j[0]['preflight_sha256'] == a.preflight_sha256, 'Wrong journal')
    require(j[-1]['kind'] == 'complete' and j[-1]['files'] == len(rows) and j[-1]['launcher_last'] is True
            and j[-1]['launch_requested'] is False and sum(x['kind'] == 'complete' for x in j) == 1, 'Full readback incomplete')
    require(sum(x['kind'] == 'audit_complete' for x in j) == 1, 'Mixed-state audit missing')
    writes = pairs(j, rows)
    prior_hash = j[0].get('previous_journal_sha256')
    if prior_hash:
        require(a.previous is not None and sha(a.previous.read_bytes()) == prior_hash == a.previous_sha256, 'Prior journal link mismatch')
        old = [json.loads(line) for line in a.previous.read_bytes().splitlines()]
        require(old and old[0]['kind'] == 'start' and old[0]['archive_sha256'] == ARCHIVE and old[0]['preflight_sha256'] == a.preflight_sha256, 'Wrong original journal')
        require(not any(x['kind'] == 'complete' for x in old), 'Original journal already complete')
        writes = pairs(old, rows) + writes
    else:
        require(a.previous is None and a.previous_sha256 is None, 'Unexpected prior journal')
    require(len({p for p, _ in writes}) == len(writes), 'Write replay detected')
    expected = {p for p, x in targets.items() if not x['exists'] or x['before_sha256'] != x['expected_sha256']}
    require({p for p, _ in writes} == expected, 'Incomplete target writes')
    require(any(x['kind'] == 'launcher_verified_unchanged' and x['path'] == LAUNCHER
                and x['target_sha256'] == EXPECTED_OLD_LAUNCHER for x in j), 'Final launcher check missing')
    identity_sha = pre['target'].get('identity_receipt_sha256') or pre['target'].get('identity_evidence_sha256')
    require(identity_sha and pre['target'].get('identity_evidence_sha256', identity_sha) == identity_sha,
            'Identity receipt hashes disagree')
    identity, raw = _read_identity(a.identity, identity_sha, a.dashboard_ip)
    require(sha(raw) == identity_sha, 'Identity changed')
    return pre, rows, targets, identity


def run(a):
    pre, rows, targets, identity = validate(a)
    with deployment_lease(a.config, a.dashboard_ip, timeout=20) as (ftp, host):
        require(host == '192.168.50.242', 'Endpoint changed')
        require(verify_f_owner(ftp)['sha256'] == pre['f_owner_marker']['sha256'], 'F owner changed')
        for marker in identity['markers']:
            require(sha(retrieve(ftp, marker['path'], 256 * 1024**2)) == marker['sha256'], 'Identity marker changed')
        checked = {}
        for path, expected in PINS.items():
            key = '/' + path
            data = retrieve(ftp, targets[key]['target_path'], rows[key]['bytes'])
            require(len(data) == rows[key]['bytes'] and sha(data) == expected, 'Boot dependency changed: ' + path)
            checked[path] = expected
        # Exclusive durable intent precedes the one command. An uncertain reply is never retried.
        with LAUNCH_GUARD.open('xb', buffering=0) as guard, (a.receipt / 'launch846.jsonl').open('xb', buffering=0) as log:
            def record(row):
                line = (json.dumps(row, sort_keys=True) + '\n').encode()
                guard.write(line)
                os.fsync(guard.fileno())
                log.write(line)
                os.fsync(log.fileno())
            record({'kind': 'intent', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'command': COMMAND, 'archive_sha256': ARCHIVE, 'journal_sha256': a.journal_sha256,
                    'checked': checked, 'automatic_retry': False})
            ftp.sock.settimeout(20)
            try:
                record({'kind': 'reply', 'reply': ftp.sendcmd(COMMAND)})
            except Exception as exc:
                record({'kind': 'reply_uncertain', 'error_type': type(exc).__name__})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('archive', 'receipt', 'identity', 'config', 'journal'):
        p.add_argument('--' + arg, type=Path, required=True)
    for arg in ('preflight-sha256', 'journal-sha256', 'dashboard-ip'):
        p.add_argument('--' + arg, required=True)
    p.add_argument('--previous', type=Path)
    p.add_argument('--previous-sha256')
    run(p.parse_args())


if __name__ == '__main__':
    main()
