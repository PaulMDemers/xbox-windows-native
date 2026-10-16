"""One inventory deployment/launch and bounded readback; never changes Windows."""
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'outputs/demo-audio-level256'))
from common001 import connect, get, names, put, sha, ticket, utc
sys.path.insert(0, str(W / 'outputs/surface-bridge260'))
from atomic_json import write_json
sys.path.insert(0, str(W / 'tools'))
from hardware_report import load

TARGET = '/E/Applications/XWNInfo/default.xbe'
EXPECTED = 'dd7fb7777d1806e478571f2680db771ea0ec3d13acba0e679e9077fb420074c7'
REPORT = re.compile(r'xwn-report-[0-9]{2}\.json', re.I)

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def protected(f, expected=None):
    baseline = read(W / 'outputs/loader-correspondence416/stage002.json')['protected']
    # Registry and event contents can legitimately change during the user's boot.
    paths = [p for p in baseline if '/config/' not in p.lower()]
    result = {p: sha(get(f, p)) for p in paths}
    assert result == (expected if expected is not None else {p: baseline[p] for p in paths})
    return result

def stage():
    out = K / 'stage002.json'
    assert not out.exists(), 'Consumed stage; inspect journal'
    data = Path('E:/xwn417/build002/bin/default.xbe').read_bytes()
    assert sha(data) == EXPECTED
    ticket()
    r = dict(started_utc=utc(), completed=False, console_C_accessed=False,
             target=TARGET, writes=[], launch_requested=False)
    write_json(out, r)
    try:
        with connect() as f:
            r['protected'] = protected(f)
            r['reports_before'] = {n: sha(get(f, '/E/' + n)) for n in names(f, '/E') if REPORT.fullmatch(n)}
            entries = names(f, '/E/Applications')
            assert 'xwninfo' not in {n.lower() for n in entries}, 'Existing utility directory; inspect before changing'
            r['writes'].append('/E/Applications/XWNInfo'); write_json(out, r)
            f.mkd('/E/Applications/XWNInfo')
            r['writes'].append(TARGET); write_json(out, r)
            put(f, TARGET, data)
            assert get(f, TARGET) == data
            r['xbe_sha256'] = EXPECTED
            protected(f, r['protected'])
        r.update(completed=True, ended_utc=utc())
    except BaseException as exc:
        r['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        write_json(out, r)
    print('Inventory uploaded and readback verified; Windows baseline unchanged')

def launch():
    out = K / 'launch001.json'
    assert not out.exists(), 'Never repeat recorded launch'
    s = read(K / 'stage002.json'); assert s['completed']
    with connect() as f:
        assert sha(get(f, TARGET)) == EXPECTED
        protected(f, s['protected'])
        r = dict(utc=utc(), launch_requested=True, command=r'SITE EXEC E:\Applications\XWNInfo\default.xbe')
        write_json(out, r)
        f.sock.settimeout(15)
        try:
            r['reply'] = f.sendcmd(r['command'])
        except Exception as exc:
            r['reply_uncertain'] = type(exc).__name__
        write_json(out, r)
    print(json.dumps(r))

def collect():
    out = K / 'collection001.json'
    assert not out.exists(), 'Already collected; inspect existing record'
    s = read(K / 'stage002.json'); assert read(K / 'launch001.json')['launch_requested']
    with connect() as f:
        current = {n for n in names(f, '/E') if REPORT.fullmatch(n)}
        fresh = current - set(s['reports_before'])
        assert len(fresh) == 1, f'Expected one new report, found {sorted(fresh)}'
        for n, h in s['reports_before'].items(): assert sha(get(f, '/E/' + n)) == h
        n = next(iter(fresh)); data = get(f, '/E/' + n)
        assert data == get(f, '/E/' + n), 'Repeated readback differs'
        private = Path('E:/xwn418'); private.mkdir(exist_ok=False)
        dest = private / n; dest.write_bytes(data)
        report = load(dest)
        protected(f, s['protected'])
        assert sha(get(f, TARGET)) == EXPECTED
        r = dict(completed=True, utc=utc(), report_path=str(dest), report_sha256=sha(data),
                 report_bytes=len(data), report=report, repeated_readback_exact=True,
                 protected_unchanged=True, dashboard_ftp_returned=True,
                 windows_ran=False, whole_disk_audited=False, console_C_accessed=False)
        write_json(out, r)
    print(json.dumps(r, indent=2))

if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('stage', 'launch', 'collect')
    globals()[sys.argv[1]]()

