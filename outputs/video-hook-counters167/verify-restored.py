"""Read back restored payloads, startup and SYSTEM; never launch or write console."""
import importlib.util
import json,sys
from pathlib import Path

base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['candidate001'];k=base/case
spec = importlib.util.spec_from_file_location('controller', base/'physical-controller.py')
c = importlib.util.module_from_spec(spec)
sys.argv=['physical-controller.py','inspect',case];spec.loader.exec_module(c)
dest = k/'restored-verification.json'
assert not dest.exists()
r = c.read(c.record)
assert r['baseline_restored'] and not r['startup_enabled']
rows = []
with c.m.connect() as f:
    c.m.owner(f)
    for row in c.capture['files']:
        path = row['path']
        if path.endswith(('/config/software', '/config/sysevent.evt', '/config/appevent.evt', '/xwn-video-trace.bin', '/setupapi.log')):
            continue
        actual = c.sha(c.m.get(f, path))
        rows.append(dict(path=path, sha256=actual, expected=row['sha256'], matched=actual == row['sha256']))
    introduced_absent = c.absence(f, '/F/winnt/system32', 'xwnown.dll')
    rollback_exact = c.sha(c.m.get(f, '/F/'+c.rollback_dir+'/current-rollback167.zip')) == r['rollback_sha256']
result = dict(utc=c.m.utc(), read_only=True, files=rows, introduced_display_dll_absent=introduced_absent,
              console_rollback_exact=rollback_exact,
              passed=all(v['matched'] for v in rows) and introduced_absent and rollback_exact,
              physical_qualified=False, launches_issued=0)
dest.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(restored_verified=result['passed'], files=len(rows))))
