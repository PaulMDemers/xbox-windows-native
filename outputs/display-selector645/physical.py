"""Fresh watched selector cycle. No startup hook; one launch, then 720p restoration."""
import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('C:/xwn645/physical001')
s = importlib.util.spec_from_file_location('helper642', K.parent/'windows480p642/physical.py')
b = importlib.util.module_from_spec(s); s.loader.exec_module(b)
m = b.m
session = b.session
read = b.read
s = importlib.util.spec_from_file_location('selector645', W/'tools/configure-e-display.py')
selector = importlib.util.module_from_spec(s); s.loader.exec_module(selector)
POLICY = read(W/'tools/e-display-policy.json')
ARCHIVE = Path('C:/xwn644/xwn-display-selector644-002.zip')
COMMAND = r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
RECEIPT = P/'rollback480p'
SAVED = '/E/xwn480p642/input.txt'


def verify():
    m.ticket()
    assert shutil.disk_usage('C:/').free - 128*1024**2 >= 20*1024**3
    assert m.sha(ARCHIVE.read_bytes()) == '249a270ab9c7254b36cd24f15203acf42140dc1b26bf323f579df730411ba420'
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in ('tools/configure-e-display.py', 'tools/e-display-policy.json'):
            assert z.read(name) == (W/name).read_bytes()
        data = z.read('resolution/480p/default.xbe')
    assert m.sha(data) == POLICY['profiles']['480p']['sha256']
    return data


def source_pins():
    return {str(p.relative_to(W)): m.sha(p.read_bytes()) for p in
            list(K.glob('*.py')) + [W/'tools/configure-e-display.py', W/'tools/e-display-policy.json']}


def check(f, mode):
    m.baseline(f, mode)
    b.startup(f)


def prepare():
    verify()
    assert not P.exists() and not (K/'preparation001.json').exists()
    assert read(K/'host001.json')['controller_sha256'] == m.sha(Path(__file__).read_bytes())
    P.mkdir(parents=True)
    out = K/'preparation001.json'
    r = dict(utc=m.utc(), completed=False, before={}, test_hook=False, remote_file_writes=False,
             source_pins=source_pins(), console_C_accessed=False)
    m.write_json(out, r)
    try:
        with m.connect(timeout=15) as f:
            check(f, '720p')
            for n in b.protected() + m.MUTABLE + [SAVED]:
                data = m.get(f,n); assert data == m.get(f,n)
                r['before'][n] = m.keep(P/'before', n, data); m.write_json(out,r)
            assert m.get(f,SAVED) in (b'XBOX480',b'XBOX480\r\n')
        r['completed'] = True
    except BaseException as e:
        r['failure_type'] = type(e).__name__; raise
    finally:
        m.write_json(out,r)


def apply():
    data = verify(); p = read(K/'preparation001.json'); assert p['completed']
    assert p['source_pins'] == source_pins()
    out = K/'selection001.json'; assert not out.exists()
    r = dict(utc=m.utc(), completed=False, test_hook=False, only_remote_write=selector.TARGET)
    m.write_json(out,r)
    try:
        with m.connect(timeout=15) as f:
            check(f,'720p')
            for n,v in p['before'].items(): assert m.sha(m.get(f,n)) == v['sha256'],n
            r['selector'] = selector.apply(f,POLICY,'480p',data,RECEIPT)
            check(f,'480p')
            r['readback_sha256'] = m.sha(m.get(f,selector.TARGET))
        r['completed'] = True
    except BaseException as e:
        r['failure_type'] = type(e).__name__; raise
    finally:
        m.write_json(out,r)


def request_once(f,out):
    r = dict(utc=m.utc(), requested=True, command=COMMAND, automatic_retry=False,
             test_hook=False, manual_normal_restart_required=True, selected_mode='480p')
    with out.open('x') as stream: json.dump(r,stream,indent=2)
    f.sock.settimeout(20)
    try: r['reply'] = f.sendcmd(COMMAND)
    except Exception as e: r['reply_uncertain'] = type(e).__name__
    m.write_json(out,r)


def launch():
    verify(); assert read(K/'selection001.json')['completed']
    p = read(K/'preparation001.json'); assert p['source_pins'] == source_pins()
    assert read(K/'host001.json')['controller_sha256'] == m.sha(Path(__file__).read_bytes())
    with m.connect(timeout=15) as f:
        check(f,'480p')
        for n,v in p['before'].items():
            if n != selector.TARGET: assert m.sha(m.get(f,n)) == v['sha256'],n
        request_once(f,K/'launch001.json')


def collect():
    assert read(K/'launch001.json')['requested']
    out = K/'collection001.json'; assert not out.exists()
    p = read(K/'preparation001.json')
    r = dict(utc=m.utc(), completed=False, after={}, test_hook=False, restored720p=False,
             console_C_accessed=False, dashboard_returned=True)
    m.write_json(out,r)
    try:
        with m.connect(timeout=15) as f:
            # No hook exists. Restore the captured default before bulk collection.
            check(f,'480p')
            r['return_launcher_sha256'] = m.sha(m.get(f,selector.TARGET))
            m.write_json(out,r)
            r['restore'] = selector.restore(f,POLICY,RECEIPT)
            check(f,'720p'); r['restored720p'] = True; m.write_json(out,r)
            for n in p['before']:
                data = m.get(f,n); assert data == m.get(f,n)
                r['after'][n] = m.keep(P/'after',n,data); m.write_json(out,r)
            r['protected_unchanged'] = all(r['after'][n]['sha256']==p['before'][n]['sha256']
                                           for n in b.protected()+[SAVED])
        r.update(completed=True,ended_utc=m.utc())
    except BaseException as e:
        r['failure_type'] = type(e).__name__; raise
    finally:
        m.write_json(out,r)


if __name__ == '__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('prepare','apply','launch','collect')
    session(); globals()[sys.argv[1]]()
