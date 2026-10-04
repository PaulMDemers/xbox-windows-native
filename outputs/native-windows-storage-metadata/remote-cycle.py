"""Explicitly authorized launch/retrieve cycle for this bounded rebooting probe."""
import argparse, datetime, ftplib, hashlib, io, json, os, pathlib

kit = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('phase', choices=['launch', 'retrieve'])
p.add_argument('--run', required=True)
a = p.parse_args()
assert a.run.isascii() and all(c.isalnum() or c == '-' for c in a.run)
record_path = kit / (a.run + '.json')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def read(f, name, optional=False):
    stream = io.BytesIO()
    try: f.retrbinary('RETR ' + name, stream.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'): return None
        raise
    return stream.getvalue()

if a.phase == 'launch':
    assert not record_path.exists(), 'Use a new run ID; never repeat an uncertain launch'
    r = dict(started_utc=now(), host='192.168.50.242', directory='/F/Applications/XWNMetadata',
             command=r'SITE EXEC F:\Applications\XWNMetadata\default.xbe', launch_attempted=False)
else:
    r = json.loads(record_path.read_text())
    assert r['launch_attempted']
f = ftplib.FTP()
try:
    f.connect(r['host'], 21, timeout=12)
    f.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    f.cwd(r['directory'])
    if a.phase == 'launch':
        expected = json.loads((kit/'validation.json').read_text())['xbe_sha256']
        r['remote_xbe_sha256'] = sha(read(f, 'default.xbe'))
        assert r['remote_xbe_sha256'] == expected, 'Unexpected executable; do not launch'
        prior = read(f, 'xwn-storage-metadata.txt', optional=True)
        if prior is not None:
            backup = 'metadata-before-' + a.run + '.txt'
            assert read(f, backup, optional=True) is None
            (kit / backup).write_bytes(prior)
            f.rename('xwn-storage-metadata.txt', backup)
            r.update(prior_report_sha256=sha(prior), prior_report_remote_backup=backup)
        assert read(f, 'xwn-storage-metadata.txt', optional=True) is None
        r.update(fresh_report_required=True, launch_attempted=True, launch_utc=now())
        record_path.write_text(json.dumps(r, indent=2)+'\n')
        try: r['launch_reply'] = f.sendcmd(r['command'])
        except (EOFError, OSError) as e:
            r['launch_reply_uncertain'] = type(e).__name__ + ': ' + str(e)
        print('Launch attempted:', r.get('launch_reply', r.get('launch_reply_uncertain')))
    else:
        data = read(f, 'xwn-storage-metadata.txt')
        (kit / ('physical-metadata-' + a.run + '.txt')).write_bytes(data)
        text = data.decode('ascii')
        assert text.startswith('XWN storage metadata v1')
        assert 'METADATA_COMPLETE success=1 log_ok=1' in text, 'Probe incomplete'
        r.update(retrieved_utc=now(), fresh_report_retrieved=True, report_sha256=sha(data),
                 probe_completed=True, dashboard_ftp_available=True)
        print(text)
finally:
    f.close()
    record_path.write_text(json.dumps(r, indent=2)+'\n')
