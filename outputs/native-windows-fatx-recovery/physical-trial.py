"""One bounded candidate0088 hardware trial after verified FATX recovery."""
import argparse
import datetime
import ftplib
import hashlib
import io
import json
import os
import pathlib
import socket

k = pathlib.Path(__file__).resolve().parent
physical = k.parent / 'native-windows-physical-f'
record = k / 'physical-trial.json'
artifacts = k / 'artifacts/trial'
startup_path = '/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
sha = lambda data: hashlib.sha256(data).hexdigest()
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
p = argparse.ArgumentParser()
p.add_argument('action', choices=['launch', 'collect'])
p.add_argument('--kind', choices=['short', 'soak'], default='short')
a = p.parse_args()
tag = 'soak' if a.kind == 'soak' else 'trial'
record = k / ('physical-' + tag + '.json')
artifacts = k / 'artifacts' / tag
archive_suffix = '.s88' if a.kind == 'soak' else '.c13r'

class FTP(ftplib.FTP):
    def ntransfercmd(self, *args, **kwargs):
        sock, size = super().ntransfercmd(*args, **kwargs)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock, size

def get(f, path, optional=False):
    data = io.BytesIO()
    try:
        f.retrbinary('RETR ' + path, data.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):
            return None
        raise
    return data.getvalue()

def put(f, path, data):
    # Separate 32 KiB transfers avoid the dashboard's long-transfer stall.
    for offset in range(0, max(1, len(data)), 32768):
        f.storbinary(('STOR ' if offset == 0 else 'APPE ') + path,
                     io.BytesIO(data[offset:offset+32768]), blocksize=1024)
    assert get(f, path) == data, path

def preserve(name, data):
    path = artifacts / name
    if path.exists():
        assert path.read_bytes() == data, 'Evidence changed: ' + name
    else:
        path.write_bytes(data)
    return dict(bytes=len(data), sha256=sha(data))

def save():
    record.write_text(json.dumps(r, indent=2) + '\n')

expected_drivers = {
    '/F/winnt/system32/drivers/xwnfatx.sys': '0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336',
    '/F/winnt/system32/drivers/xboxvnt5.sys': '413098acf0066e48fde515b75d825578c23c17c4094ec2341ebdaa314a2d6b13',
    '/E/Applications/XWNFBoot/loader/halxboxnt5.dll': 'a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648',
}
artifacts.mkdir(exist_ok=True)
with FTP() as f:
    f.connect('192.168.50.242', timeout=15)
    f.login('xbox', os.environ['XWN_FTP_PASSWORD'])
    assert json.loads(get(f, '/F/xwn-deploy-v1.json')) == json.loads(
        (physical / 'physical-cache-preflight.json').read_text())['ownership_marker']
    if a.action == 'launch':
        assert not record.exists(), 'Never blindly repeat a trial'
        for filename, key in [('restored-audit.json', 'passed'),
                              ('physical-restored-allocation.json', 'allocation_consistent')]:
            assert json.loads((k / filename).read_text())[key], filename
        assert json.loads((k / 'preserved-payloads.json').read_text())['passed']
        if a.kind == 'soak':
            assert json.loads((k/'physical-trial-qualification.json').read_text())['passed']
            prior = json.loads((k/'physical-trial.json').read_text())
            assert not prior['startup_restart_enabled']
            assert sha(get(f, '/F/xwn-report-v2.txt')) == prior['report']['sha256']
            for row in prior['payloads']:
                assert sha(get(f, '/F/'+row['path'])) == row['sha256'], row['path']
        for path, expected in expected_drivers.items():
            assert sha(get(f, path)) == expected, path
        initial = json.loads((physical / 'physical-cycle-001.json').read_text())
        for name, key in [('default.xbe', 'launcher_sha256'), ('freeldr.sys', 'loader_sha256')]:
            assert sha(get(f, '/E/Applications/XWNFBoot/' + name)) == initial[key]
        if a.kind == 'soak':
            build = json.loads((physical/'cache-soak-build.json').read_text())
            assert sha((physical/'cache-probe.c').read_bytes()) == build['source_sha256']
            probe = get(f, '/F/xwnsoak.exe')
            assert sha(probe) == build['sha256'] == '74ac7388c381dbb321fa14cbd5afd521f5087e1904b31647d8034452ee9df40b'
        else:
            probe = get(f, '/F/xwncache.exe')
            assert sha(probe) == '833a5756b19db7771b9d96a3e3534781bc848bc440546e8e1acf0197be2a46e3'
        previous = get(f, startup_path)
        assert sha(previous) == json.loads((physical / 'physical-cycle-013.json').read_text())['current_startup_sha256']
        startup = b'@echo off\r\nC:\\xwncache.exe\r\n'
        if a.kind == 'soak':startup = b'@echo off\r\nC:\\xwnsoak.exe\r\n'
        r = dict(scope=__doc__, created_utc=utc(), launch_attempted=False,
                 startup_restart_enabled=False, previous_startup_sha256=sha(previous),
                 startup_sha256=sha(startup), probe_sha256=sha(probe),
                 expected_drivers=expected_drivers, archives=[], checks={})
        r.update(kind=a.kind, mapped_cases_expected=300 if a.kind=='soak' else 30,
                 idle_ms=300000 if a.kind=='soak' else 15000)
        for name in ['xwn-report-v2.txt', 'xwn-cache-append.tmp', 'xwn-cache-map.tmp', 'xwn-cache-pressure.tmp']:
            assert get(f, '/F/' + name + archive_suffix, True) is None, 'Archive already exists'
        for name, path in [('previous-startup.cmd', startup_path),
                           ('previous-trace.bin', '/F/winnt/system32/xwn-video-trace.bin'),
                           ('previous-system.evt', '/F/winnt/system32/config/sysevent.evt')]:
            r['checks'][name] = preserve(name, get(f, path))
        save()
        try:
            for name in ['xwn-report-v2.txt', 'xwn-cache-append.tmp', 'xwn-cache-map.tmp', 'xwn-cache-pressure.tmp']:
                data = get(f, '/F/' + name, True)
                if data is not None:
                    details = preserve('previous-' + name, data)
                    f.rename('/F/' + name, '/F/' + name + archive_suffix)
                    assert get(f, '/F/' + name + archive_suffix) == data
                    r['archives'].append(dict(path='/F/' + name + archive_suffix, **details))
                    save()
            put(f, '/F/xwn-report-v2.txt', b'XWN-CACHE-PENDING\r\n'.ljust(4096, b' '))
            put(f, '/F/winnt/system32/xwn-video-trace.bin', b'XWN-VID-TRACE01\n' + bytes(4080))
            put(f, startup_path, startup)
            r.update(startup_restart_enabled=True, launch_attempted=True, launch_utc=utc(),
                     command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
            save()
            try:
                r['reply'] = f.sendcmd(r['command'])
            except (EOFError, OSError) as e:
                r['uncertain_reply'] = repr(e)
            save()
            print('Launched', a.kind, 'trial:', r.get('reply', r.get('uncertain_reply')), flush=True)
        except Exception as e:
            r['error'] = repr(e)
            if not r['launch_attempted']:
                put(f, startup_path, previous)
                r['startup_restart_enabled'] = False
            save()
            raise
    else:
        r = json.loads(record.read_text())
        assert r.get('kind', 'short') == a.kind
        assert r['launch_attempted'] and not r.get('collected_utc')
        previous = (artifacts / 'previous-startup.cmd').read_bytes()
        assert sha(previous) == r['previous_startup_sha256']
        current = get(f, startup_path)
        assert sha(current) in (r['startup_sha256'], r['previous_startup_sha256'])
        if current != previous:
            put(f, startup_path, previous)
        r.update(startup_restart_enabled=False, current_startup_sha256=sha(previous))
        save()
        report = get(f, '/F/xwn-report-v2.txt')
        r['report'] = dict(**preserve('report.txt', report), text=report.rstrip(b' \0').decode('ascii', errors='replace'))
        r['probe_passed'] = report.startswith(b'XWN-CACHE-START') and b'XWN-CACHE-PASS' in report and b'XWN-CACHE-FAIL' not in report
        if a.kind == 'soak':
            r['mapped_cases_recorded'] = sum(line.startswith(b'map=') for line in report.splitlines())
            r['soak_completed'] = b'five minute background soak completed' in report
            r['probe_passed'] = r['probe_passed'] and r['soak_completed'] and r['mapped_cases_recorded']==300
        r['payloads'] = []
        for name, expected in {
            'xwn-cache-append.tmp': bytes((i*37+(i>>8)+0x65)&255 for i in range(131073)),
            'xwn-cache-map.tmp': b'',
            'xwn-cache-pressure.tmp': bytes((i*37+(i>>8)+0x77)&255 for i in range(65536))*512,
        }.items():
            data = get(f, '/F/' + name, True)
            r['payloads'].append(dict(path=name, present=data is not None,
                                     pattern_match=data == expected,
                                     **(preserve(name, data) if data is not None else {})))
            save()
        r['collected'] = {}
        for name, path in [('trace.bin', '/F/winnt/system32/xwn-video-trace.bin'),
                           ('system.evt', '/F/winnt/system32/config/sysevent.evt'),
                           ('application.evt', '/F/winnt/system32/config/appevent.evt'),
                           ('setupapi.log', '/F/winnt/setupapi.log')]:
            r['collected'][name] = preserve(name, get(f, path))
        r['driver_checks'] = []
        for path, expected in expected_drivers.items():
            data = get(f, path)
            r['driver_checks'].append(dict(path=path, sha256=sha(data), passed=sha(data) == expected))
        r['archive_checks'] = []
        for row in r['archives']:
            data = get(f, row['path'])
            r['archive_checks'].append(dict(path=row['path'], sha256=sha(data),
                                            passed=len(data)==row['bytes'] and sha(data)==row['sha256']))
        r['passed'] = (r['probe_passed'] and all(x['pattern_match'] for x in r['payloads'])
                       and all(x['passed'] for x in r['driver_checks'])
                       and all(x['passed'] for x in r['archive_checks']))
        r.update(collected_utc=utc(), caveat='Bounded trial; event log and post-trial allocation checks are separate.')
        save()
        print('Trial collected; startup disabled; payload/driver checks passed:', r['passed'])
