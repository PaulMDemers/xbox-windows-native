"""Verify the installed adapter checkpoint, then request one fresh launch."""
import datetime
import ftplib
import hashlib
import io
import json
import os
import pathlib

kit = pathlib.Path(__file__).resolve().parent
record = kit / 'physical-cycle-006.json'
assert not record.exists(), 'One-shot launch record already exists'
previous_path = kit / 'physical-cycle-005.json'
previous = json.loads(previous_path.read_text())
previous['user_observation'] = 'Console was BSOD a few minutes earlier; now at dashboard. STOP code not supplied.'
previous['status'] = 'physical_result_unknown_dashboard_confirmed'
previous_path.write_text(json.dumps(previous, indent=2) + '\n')
baseline = json.loads((kit / 'physical-cycle-001.json').read_text())
result = {
    'host': previous['host'],
    'scope': 'Re-launch existing adapter-resource checkpoint after user confirmed dashboard; no upload',
    'launch_attempted': False,
    'previous_cycle': 5,
    'miniport_sha256': previous['miniport_sha256'],
}

def get(ftp, name, optional=False):
    data = io.BytesIO()
    try:
        ftp.retrbinary('RETR ' + name, data.write)
    except ftplib.error_perm as error:
        if optional and str(error).startswith('550'):
            return None
        raise
    return data.getvalue()

with ftplib.FTP() as ftp:
    ftp.connect(result['host'], timeout=15)
    ftp.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    ftp.cwd('/F')
    assert get(ftp, 'xwn-report-v2.txt') == b'XWN-V2-PENDING-20261004\r\n'.ljust(4096, b' '), 'Report changed; inspect before launching'
    assert get(ftp, 'xwn-create-v2.bin', True) is None, 'Probe output exists; inspect before launching'
    result['probe_report_seed_unchanged'] = True
    ftp.cwd('/F/winnt/system32/drivers')
    assert hashlib.sha256(get(ftp, 'xboxvnt5.sys')).hexdigest() == result['miniport_sha256']
    ftp.cwd('/E/Applications/XWNFBoot')
    for name, key in [('default.xbe', 'launcher_sha256'), ('freeldr.sys', 'loader_sha256')]:
        assert hashlib.sha256(get(ftp, name)).hexdigest() == baseline[key]
        result[key] = baseline[key]
    result.update(launch_attempted=True,
                  launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  command=baseline['command'],
                  status='launch_requested_screen_result_pending')
    record.write_text(json.dumps(result, indent=2) + '\n')
    try:
        result['reply'] = ftp.sendcmd(result['command'])
    except (EOFError, OSError, ftplib.Error) as error:
        result['uncertain_reply'] = repr(error)
    record.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
