"""Fresh read-only physical capture; no upload, rename, launch or configuration edit."""
import hashlib
import importlib.util
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'capture001.json'
assert not dest.exists(), 'Capture already recorded; use a new reviewed attempt'
state = ws / 'outputs/device-hardware220/state'
for claim in state.glob('*-claimed.json'):
    closed = claim.with_name(claim.name.replace('-claimed.json', '-closed.json'))
    assert closed.exists() and json.loads(closed.read_text())['baseline_restored'], claim

spec = importlib.util.spec_from_file_location('physical_helpers', ws / 'outputs/fatx0098-soak3/physical.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
base = json.loads((ws / 'outputs/fatx0101-physical/installed-state.json').read_text())
art = Path('E:/Codex-private-artifacts/xbox-windows-feasibility/demo251/incoming001')
art.mkdir(parents=True, exist_ok=False)
sha = lambda b: hashlib.sha256(b).hexdigest()
paths = list(base['checks']) + [
    m.startup, '/F/xwn-deploy-v1.json',
    '/E/Applications/XWNFBoot/loader/xboxbvid.dll',
    '/E/Applications/XWNFBoot/boot.cfg',
    '/F/winnt/system32/ntoskrnl.exe', '/F/winnt/system32/win32k.sys',
    '/F/winnt/system32/drivers/atapi.sys', '/F/winnt/system32/drivers/nvnetnt5.sys',
    '/F/winnt/system32/drivers/videoprt.sys', '/F/winnt/system32/xwn-video-trace.bin',
    '/F/winnt/setupapi.log',
] + ['/F/winnt/system32/config/' + n for n in
     ('system', 'software', 'default', 'sam', 'security', 'sysevent.evt', 'appevent.evt')]
optional = {'/E/Applications/XWNFBoot/boot.cfg'}
r = dict(scope=__doc__, utc=m.utc(), physical_access=True, physical_writes=False,
         launch_attempted=False, files=[], private_root=str(art), passed=False)
def save():
    m.save(r, dest)
save()
try:
    with m.connect() as f:
        m.owner(f)
        r['ownership_verified'] = True
        r['dashboard_reply'] = f.getwelcome()
        save()
        for path in dict.fromkeys(paths):
            data = m.get(f, path, optional=path in optional)
            again = m.get(f, path, optional=path in optional)
            assert data == again, 'Read changed: ' + path
            if data is None:
                r['files'].append(dict(path=path, absent=True, second_read_exact=True))
            else:
                p = art / path.lstrip('/')
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
                expected = base['checks'].get(path, {}).get('sha256')
                r['files'].append(dict(path=path, bytes=len(data), sha256=sha(data),
                    second_read_exact=True, historical_expected=expected,
                    historical_match=None if expected is None else sha(data) == expected))
            save()
    r.update(passed=True, completed_utc=m.utc(),
             meaning='Stable double-read capture only; historical differences are reported, not overwritten.')
    save()
    print(json.dumps(dict(passed=True, files=len(r['files']),
                         historical_differences=[x['path'] for x in r['files'] if x.get('historical_match') is False])))
except BaseException as exc:
    r.update(error=repr(exc), failed_utc=m.utc())
    save()
    raise
