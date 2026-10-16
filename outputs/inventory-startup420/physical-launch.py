"""One authorized FTP launch of420; never repeat an uncertain request."""
import importlib.util
import json
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
out = K / 'physical-launch001.json'
assert not out.exists(), 'Consumed physical launch'
stage = m.read(K / 'stage001.json'); assert stage['completed']
for name, digest in stage['inputs'].items():
    assert m.sha((K / name).read_bytes()) == digest, name
with m.connect() as f:
    m.protected(f, stage['protected'])
    assert m.sha(m.get(f, stage['target'])) == stage['xbe_sha256']
    assert m.sha(m.get(f, m.TARGET)) == m.EXPECTED
    root = m.names(f, '/E')
    assert 'xwn-trace420.bin' not in {n.lower() for n in root}, 'Trace exists; do not relaunch'
    reports = {n: m.sha(m.get(f, '/E/' + n)) for n in root if m.REPORT.fullmatch(n)}
    assert reports == stage['reports_before']
    r = dict(utc=m.utc(), route='FTP SITE EXEC', launch_requested=True,
             manual_launch_superseded_by_explicit_user_authorization=True,
             command=r'SITE EXEC E:\Applications\XWNInfo420\default.xbe',
             target_sha256=stage['xbe_sha256'], protected_before_exact=True,
             script_sha256=m.sha(Path(__file__).read_bytes()))
    m.write_json(out, r)
    f.sock.settimeout(15)
    try: r['reply'] = f.sendcmd(r['command'])
    except Exception as exc: r['reply_uncertain'] = type(exc).__name__
    m.write_json(out, r)
print(json.dumps(r))
