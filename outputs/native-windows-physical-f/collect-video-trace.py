"""Read a completed physical cycle's trace; never launch, reset, or seed it."""
import argparse, datetime, ftplib, hashlib, importlib.util, io, json, os, pathlib
k = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser(); p.add_argument('--cycle', type=int, required=True); a = p.parse_args()
assert 1 <= a.cycle <= 999
record = k / f'physical-cycle-{a.cycle:03d}.json'
r = json.loads(record.read_text()); assert r['launch_attempted'] and 'trace_seed_sha256' in r
spec = importlib.util.spec_from_file_location('decoder', k / 'decode-video-trace.py')
decoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder)
def get(ftp, name):
    data = io.BytesIO(); ftp.retrbinary('RETR ' + name, data.write); return data.getvalue()
with ftplib.FTP() as ftp:
    ftp.connect(r['host'], timeout=15); ftp.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    if 'hal_sha256' in r:
        ftp.cwd('/E/Applications/XWNFBoot/loader')
        assert hashlib.sha256(get(ftp, 'halxboxnt5.dll')).hexdigest() == r['hal_sha256']
    ftp.cwd('/F/winnt/system32/drivers')
    digest = hashlib.sha256(get(ftp, 'xboxvnt5.sys')).hexdigest()
    assert digest == r['miniport_sha256'], 'Installed miniport changed; investigate attribution'
    ftp.cwd('/F/winnt/system32'); data = get(ftp, 'xwn-video-trace.bin')
    decoded = decoder.decode(data)
    destination = k / 'artifacts' / f'physical-video-trace-{a.cycle:03d}.bin'
    if destination.exists(): assert destination.read_bytes() == data, 'Refusing to replace earlier trace'
    else: destination.write_bytes(data)
    ftp.cwd('/F'); probe = get(ftp, 'xwn-report-v2.txt')
decoded.update(cycle=a.cycle, scope='Physical persisted trace read after dashboard return',
               miniport_sha256=digest, collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(k / f'physical-video-trace-{a.cycle:03d}.json').write_text(json.dumps(decoded, indent=2) + '\n')
r.update(trace_collected=True, trace_records=decoded['records'], trace_sha256=decoded['sha256'],
         probe_report_sha256=hashlib.sha256(probe).hexdigest(),
         probe_pending_seed_present=probe == b'XWN-V2-PENDING-20261004\r\n'.ljust(4096,b' '))
record.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(decoded, indent=2))
