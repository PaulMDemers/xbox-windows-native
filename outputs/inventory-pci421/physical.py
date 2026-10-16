"""One staged ordinary scanner, one authorized launch, bounded collection."""
import importlib.util
import json
import sys
import time
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
TARGET = '/E/Applications/XWNInfo421/default.xbe'
SHA = 'f9163c73c3baa556c80138e122dbc81fe9aec77bd7ec3d951ec9fd9ad0778d5d'
TRACE = '/E/xwn-trace420.bin'
TRACE_SHA = 'e5dfb1121b8cb35987cf4b5fc207d53cda0dd9b4dd7fa2965ce7a5cea1eac968'

def protected(f, expected):
    actual = m.protected(f, expected)
    assert m.sha(m.get(f, m.TARGET)) == m.EXPECTED
    old = m.read(W / 'outputs/inventory-startup420/stage001.json')
    assert m.sha(m.get(f, old['target'])) == old['xbe_sha256']
    assert m.sha(m.get(f, TRACE)) == TRACE_SHA
    return actual

def reports(f):
    return {n: m.sha(m.get(f, '/E/' + n)) for n in m.names(f, '/E') if m.REPORT.fullmatch(n)}

def stage():
    out = K / 'stage001.json'; assert not out.exists()
    assert m.read(K / 'smoke001.json')['report_scope_passed']
    assert m.read(K / 'closure001.json')['exit'] == 0
    assert m.read(K / 'policy-tests001.json')['result']['passed']
    build = m.read(K / 'build001.json'); assert build['compiled'] and build['sdk_unchanged']
    data = Path('E:/xwn421/build001/bin/default.xbe').read_bytes(); assert m.sha(data) == SHA
    baseline = m.read(W / 'outputs/inventory-startup420/physical-collection001.json')
    assert baseline['completed'] and baseline['protected_unchanged']
    r = dict(started_utc=m.utc(), completed=False, writes=[], target=TARGET,
             xbe_sha256=SHA, console_C_accessed=False, launch_sent=False,
             inputs={p.name:m.sha(p.read_bytes()) for p in K.iterdir() if p.is_file()})
    m.write_json(out, r)
    try:
        with m.connect() as f:
            r['protected'] = protected(f, baseline['protected_actual'])
            assert 'xwninfo421' not in {n.lower() for n in m.names(f, '/E/Applications')}
            r['reports_before'] = reports(f)
            r['writes'].append('/E/Applications/XWNInfo421'); m.write_json(out, r)
            f.mkd('/E/Applications/XWNInfo421')
            r['writes'].append(TARGET); m.write_json(out, r)
            m.put(f, TARGET, data)
            assert m.get(f, TARGET) == data
            protected(f, r['protected'])
            r.update(completed=True, ended_utc=m.utc(), protected_unchanged=True)
    except BaseException as exc:
        r['error'] = repr(exc)
        raise
    finally:
        m.write_json(out, r)
    print('421 staged and readback verified; selected Windows/old diagnostics unchanged')

def launch():
    out = K / 'physical-launch001.json'; assert not out.exists()
    stage = m.read(K / 'stage001.json'); assert stage['completed']
    for n, h in stage['inputs'].items(): assert m.sha((K / n).read_bytes()) == h, n
    with m.connect() as f:
        protected(f, stage['protected'])
        assert m.sha(m.get(f, TARGET)) == SHA
        assert reports(f) == stage['reports_before']
        r = dict(utc=m.utc(), launch_requested=True, route='FTP SITE EXEC',
                 command=r'SITE EXEC E:\Applications\XWNInfo421\default.xbe', target_sha256=SHA)
        m.write_json(out, r)
        f.sock.settimeout(15)
        try: r['reply'] = f.sendcmd(r['command'])
        except Exception as exc: r['reply_uncertain'] = type(exc).__name__
        m.write_json(out, r)
    print(json.dumps(r))

def observe():
    out = K / 'physical-return001.json'; assert not out.exists()
    assert m.read(K / 'physical-launch001.json')['launch_requested']
    stage = m.read(K / 'stage001.json')
    r = dict(started_utc=m.utc(), returned=False, observations=[], launch_sent=False)
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            with m.connect(timeout=3) as f:
                current = reports(f)
                fresh = set(current) - set(stage['reports_before'])
                r['observations'].append(dict(utc=m.utc(), ftp=True, fresh=sorted(fresh)))
                if fresh:
                    r.update(returned=True, reports=current)
                    break
        except Exception as exc:
            r['observations'].append(dict(utc=m.utc(), error=type(exc).__name__))
        m.write_json(out, r)
        time.sleep(5)
    r.update(closed=True, ended_utc=m.utc()); m.write_json(out, r)
    print(json.dumps(r))

def collect():
    out = K / 'physical-collection001.json'; assert not out.exists()
    assert m.read(K / 'physical-launch001.json')['launch_requested']
    stage = m.read(K / 'stage001.json')
    r = dict(started_utc=m.utc(), completed=False, console_C_accessed=False,
             whole_disk_audited=False, windows_ran=False, physical_writes=False)
    private = Path('E:/xwn421/physical001'); private.mkdir(exist_ok=False)
    m.write_json(out, r)
    try:
        with m.connect() as f:
            current = reports(f)
            for n, h in stage['reports_before'].items(): assert current[n] == h
            fresh = set(current) - set(stage['reports_before']); assert len(fresh) == 1, fresh
            name = fresh.pop(); data = m.get(f, '/E/' + name)
            dest = private / name; dest.write_bytes(data)
            r.update(report_path=str(dest), report_bytes=len(data), report_sha256=m.sha(data))
            m.write_json(out, r)
            assert data == m.get(f, '/E/' + name)
            report = m.load(dest)
            assert report['schema'] == 2 and report['pci_scan_policy'] == 'xbox-safe-v1'
            protected(f, stage['protected'])
            assert m.sha(m.get(f, TARGET)) == SHA
            r.update(completed=True, report=report, repeated_readback_exact=True,
                     protected_unchanged=True, old_trace_and_utilities_unchanged=True,
                     dashboard_ftp_returned=True, ended_utc=m.utc())
    except BaseException as exc:
        r['error'] = repr(exc)
        raise
    finally:
        m.write_json(out, r)
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('stage', 'launch', 'observe', 'collect')
    globals()[sys.argv[1]]()
