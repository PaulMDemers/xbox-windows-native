"""Single explicit fixed-profile launch after a completed 847 delta transfer."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'outputs/bundle-deploy846/source'))
from common import deployment_lease, retrieve, sha, sha_file, verify_f_owner
from profiles import expected_delta, verify_archive, verify_source_profile
from compat import preflight846, preflight847

_base = preflight846()
_switch_preflight = preflight847()
_read_identity = _base._read_identity
attempt_lock = _switch_preflight.attempt_lock
require = _switch_preflight.require

COMMAND = r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'


def _journal(data: bytes):
    rows = [json.loads(line) for line in data.decode('utf-8').splitlines()]
    require(rows and rows[0]['kind'] == 'start' and rows[-1]['kind'] == 'complete',
            'Transfer journal is not complete')
    require(rows[-1]['launcher_last'] is True and rows[-1]['launch_requested'] is False,
            'Launcher transfer order/result invalid')
    require(not any(row['kind'] in ('error', 'uncertain') for row in rows), 'Transfer journal contains an unresolved result')
    return rows


def run(archive: Path, receipt: Path, preflight_sha256: str, transfer_sha256: str,
        identity: Path, identity_sha256: str, config: Path, dashboard_ip: str,
        attempt: str, *, ftp_factory=None, ticket_check=None, lock_path=None):
    if ftp_factory is None:
        import ftplib
        ftp_factory = ftplib.FTP
    receipt = Path(receipt)
    pre_raw = (receipt / 'preflight.json').read_bytes()
    require(sha(pre_raw) == preflight_sha256.lower(), 'Preflight receipt changed')
    pre = json.loads(pre_raw.decode('utf-8'))
    require(pre.get('completed') is True and pre.get('physical_writes') is False
            and pre.get('launch_requested') is False, 'Preflight is incomplete')
    require(pre.get('attempt_id') == attempt and pre['target']['dashboard_ip'] == dashboard_ip == '192.168.50.242',
            'Attempt or target mismatch')
    profile = pre['target_profile']
    manifest, profile_pin, _ = verify_archive(archive, profile)
    require(sha_file(archive) == profile_pin['sha256'] == pre['archive']['sha256'], 'Wrong profile/archive')
    transfer_data = (receipt / 'transfer.jsonl').read_bytes()
    require(sha(transfer_data) == transfer_sha256.lower(), 'Transfer journal hash mismatch')
    events = _journal(transfer_data)
    require(events[0]['attempt_id'] == attempt and events[0]['target_profile'] == profile
            and events[0]['preflight_sha256'] == preflight_sha256.lower()
            and events[0]['archive_sha256'] == profile_pin['sha256'], 'Transfer journal lineage mismatch')
    identity_obj, identity_raw = _read_identity(identity, pre['target']['identity_evidence_sha256'], dashboard_ip)
    require(sha(identity_raw) == identity_sha256.lower() == pre['target']['identity_evidence_sha256'],
            'Identity evidence changed')
    launcher = profile_pin['launcher']
    require(pre['launcher_change']['after_sha256'] == launcher['sha256'], 'Launcher target pin mismatch')
    delta = expected_delta(pre['source_profile'], profile, manifest)
    intents = [(row['path'].casefold(), row['target_sha256']) for row in events if row['kind'] == 'write_intent']
    verified = [(row['path'].casefold(), row['target_sha256']) for row in events if row['kind'] == 'write_verified']
    required = [(('/' + row['path']).casefold(), row['after_sha256']) for row in delta]
    require(intents == verified == required, 'Transfer journal does not prove the exact profile delta')
    complete = events[-1]
    require(complete.get('files') == len(delta)
            and complete.get('changed_paths') == [row['path'] for row in delta],
            'Transfer completion record does not match the selected profile delta')
    launch_log = receipt / 'launch.jsonl'
    require(not launch_log.exists(), 'Launch intent already exists; never retry')
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
            final = verify_source_profile(ftp, profile, retrieve=retrieve,
                                          list_dir=_base._list_dir)
            require(final['files']['/E/Applications/XWNEBoot/default.xbe']['sha256'] == launcher['sha256'],
                    'Fixed-profile launcher mismatch')
            # Exclusive, durable intent is created before the one command can leave the host.
            with launch_log.open('xb', buffering=0) as stream:
                intent = {'kind': 'intent', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          'attempt_id': attempt, 'source_profile': pre['source_profile'],
                          'target_profile': profile, 'dashboard_ip': dashboard_ip,
                          'command': COMMAND, 'archive_sha256': profile_pin['sha256'],
                          'transfer_journal_sha256': transfer_sha256.lower(),
                          'launcher_sha256': launcher['sha256'], 'checked': final['files'],
                          'automatic_retry': False, 'expected_return': 'Windows boots in the selected fixed mode; dashboard return is not assumed'}
                stream.write((json.dumps(intent, sort_keys=True) + '\n').encode('utf-8'))
                os.fsync(stream.fileno())
                ftp.sock.settimeout(20)
                try:
                    reply = ftp.sendcmd(COMMAND)
                    stream.write((json.dumps({'kind': 'reply', 'reply': reply}, sort_keys=True) + '\n').encode('utf-8'))
                    os.fsync(stream.fileno())
                except Exception as exc:
                    stream.write((json.dumps({'kind': 'reply_uncertain', 'error_type': type(exc).__name__}, sort_keys=True) + '\n').encode('utf-8'))
                    os.fsync(stream.fileno())
    return {'intent_recorded': True, 'command_sent_once': True, 'profile': profile,
            'automatic_retry': False, 'physical_result': 'not observed by this host operation'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('archive', 'receipt', 'identity', 'config'):
        p.add_argument('--' + arg, type=Path, required=True)
    for arg in ('preflight-sha256', 'transfer-sha256', 'identity-sha256', 'dashboard-ip', 'attempt'):
        p.add_argument('--' + arg, required=True)
    a = p.parse_args()
    result = run(a.archive, a.receipt, a.preflight_sha256, a.transfer_sha256,
                 a.identity, a.identity_sha256, a.config, a.dashboard_ip, a.attempt)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
