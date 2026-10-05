"""Collect cycle012 once the dashboard returns; never launch the console."""
import argparse, datetime, ftplib, hashlib, io, json, os, pathlib

p = argparse.ArgumentParser()
p.add_argument('--cycle', type=int, choices=[12, 13], default=12)
a = p.parse_args()
tag = f'{a.cycle:03d}'

k = pathlib.Path(__file__).resolve().parent
record = k / f'physical-cycle-{tag}.json'
r = json.loads(record.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()

def get(f, name, optional=False):
    b = io.BytesIO()
    try:
        f.retrbinary('RETR ' + name, b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):
            return None
        raise
    return b.getvalue()

def preserve(name, data):
    p = k / 'artifacts' / ('physical-' + tag + '-' + name)
    if p.exists():
        assert p.read_bytes() == data, 'Evidence changed: ' + name
    else:
        p.write_bytes(data)
    return {'bytes': len(data), 'sha256': sha(data)}

def save():
    record.write_text(json.dumps(r, indent=2) + '\n')

assert r['launch_attempted'] and not r.get('evidence_collected_utc')
with ftplib.FTP() as f:
    f.connect(r['host'], timeout=10)
    f.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F')
    assert json.loads(get(f, 'xwn-deploy-v1.json')) == json.loads((k / 'physical-cache-preflight.json').read_text())['ownership_marker']
    prior = get(f, r['prior_report_backup'])
    previous = json.loads((k / f"physical-cycle-{r.get('prior_cycle', 9):03d}.json").read_text())
    assert sha(prior) == (previous['cache_report']['sha256'] if 'cache_report' in previous else previous['report_sha256'])
    old_startup = get(f, r.get('startup_backup', '/F/xwn-startup-c11.bak'))
    assert sha(old_startup) == json.loads((k / 'physical-cycle-010.json').read_text())['startup_sha256']
    f.cwd('/F/documents and settings/all users/start menu/programs/startup')
    current = get(f, 'xwnsetup.cmd')
    assert sha(current) in [r['startup_sha256'], sha(old_startup)]
    if current != old_startup:
        f.storbinary('STOR xwnsetup.cmd', io.BytesIO(old_startup), blocksize=1024)
    assert get(f, 'xwnsetup.cmd') == old_startup
    r.update(startup_restart_enabled=False, current_startup_sha256=sha(old_startup))
    save()
    f.cwd('/F')
    report = get(f, 'xwn-report-v2.txt')
    r['cache_report'] = preserve('report.txt', report)
    r['cache_report']['text'] = report.rstrip(b' \0').decode('ascii', errors='replace')
    r['cache_probe_started'] = report.startswith(b'XWN-CACHE-START')
    r['cache_probe_passed'] = r['cache_probe_started'] and b'XWN-CACHE-PASS' in report and b'XWN-CACHE-FAIL' not in report
    if a.cycle == 13:
        r['soak_completed'] = b'five minute background soak completed' in report
        r['mapped_cases_recorded'] = sum(line.startswith(b'map=') for line in report.splitlines())
        r['cache_probe_passed'] = r['cache_probe_passed'] and r['soak_completed'] and r['mapped_cases_recorded'] == 300
    r['test_files'] = {}
    expected = {
        'xwn-cache-append.tmp': bytes((i*37+(i>>8)+0x65)&255 for i in range(131073)),
        'xwn-cache-map.tmp': b'',
        'xwn-cache-pressure.tmp': bytes((i*37+(i>>8)+0x77)&255 for i in range(65536)) * 512,
    }
    for name, wanted in expected.items():
        data = get(f, name, True)
        r['test_files'][name] = None if data is None else {
            'bytes': len(data), 'sha256': sha(data), 'pattern_match': data == wanted}
    r['payload_readback_passed'] = all(x is not None and x['pattern_match'] for x in r['test_files'].values())
    save()
    for directory, names in [('/F/winnt/system32', ['xwn-video-trace.bin']),
                             ('/F/winnt/system32/config', ['sysevent.evt', 'appevent.evt']),
                             ('/F/winnt', ['setupapi.log'])]:
        f.cwd(directory)
        for name in names:
            r.setdefault('collected', {})[name] = preserve(name, get(f, name))
    f.cwd('/F/winnt/system32/drivers')
    r['driver_checks'] = []
    def check(name, expected):
        row = {'path': name, 'expected_sha256': expected, 'passed': False}
        try:
            data = get(f, name)
            row.update(bytes=len(data), sha256=sha(data), passed=sha(data)==expected)
        except ftplib.all_errors as e:
            row['error'] = repr(e)
        r['driver_checks'].append(row)
    check('xwnfatx.sys', r['filesystem_sha256'])
    check('xwnfatx.xwn-c11', r['previous_filesystem_sha256'])
    check('xboxvnt5.sys', r['miniport_sha256'])
    f.cwd('/E/Applications/XWNFBoot/loader')
    check('halxboxnt5.dll', r['hal_sha256'])
    r['physical_cache_trial_passed'] = r['cache_probe_passed'] and r['payload_readback_passed'] and all(row['passed'] for row in r['driver_checks'])
    r['status'] = 'physical_cache_trial_passed' if r['physical_cache_trial_passed'] else 'physical_cache_trial_incomplete_or_failed'
    r['evidence_collected_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print(json.dumps(r, indent=2))
