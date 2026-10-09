"""Read-only owned-console baseline check; no staging, startup write or launch."""
import importlib.util
import json
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
dest = k / 'dashboard-preflight.json'
assert not dest.exists()
sys.argv = ['physical-controller.py', 'inspect', 'control001']
spec = importlib.util.spec_from_file_location('controller_read_only', k / 'physical-controller.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
r = dict(scope=__doc__, utc=c.m.utc(), writes=0, launch_requested=False, passed=False,
         source_sha256=c.sha(Path(__file__).read_bytes()), controller_sha256=c.sha((k / 'physical-controller.py').read_bytes()))
try:
    with c.m.connect() as f:
        c.m.owner(f)
        r['fixed_checks'] = c.fixed_checks(f)
        r['normal_startup_exact'] = c.sha(c.m.get(f, c.startup)) == next(v['sha256'] for v in c.capture['files'] if v['path'] == c.startup)
        r['introduced_display_absent'] = c.absence(f, '/F/winnt/system32', 'xwnown.dll')
        r['control_namespace_absent'] = c.absence(f, '/F', 'xwnpre200a')
        r['passed'] = all(r[name] for name in ['normal_startup_exact', 'introduced_display_absent', 'control_namespace_absent'])
except Exception as exc:
    r['error'] = repr(exc)
finally:
    r['closed_utc'] = c.m.utc()
    dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(passed=r['passed'], writes=0, launch_requested=False, error=r.get('error')), indent=2))
