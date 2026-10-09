"""Observe and collect ONE already launched trial; never launch a guest or candidate."""
import datetime
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
case = sys.argv[1]
assert case in ['control001', 'candidate001']
out = k / case
dest = out / 'finish-state.json'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
assert not dest.exists() and read(out / 'physical.json')['launch_requested']
assert not read(out / 'physical.json').get('collected_utc')
assert not (out / 'physical-return.json').exists()
sys.argv = ['physical-controller.py', 'inspect', case]
spec = importlib.util.spec_from_file_location('finish_controller', k / 'physical-controller.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
c.ready()
r = dict(case=case, launch_requested_by_this_process=False, steps=[], closed=False)
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

def save():
    tmp = dest.with_suffix('.tmp')
    tmp.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    tmp.replace(dest)

def step(label, argv):
    row = dict(name=label, started_utc=utc())
    r['steps'].append(row)
    save()
    log = out / (label + '-console.txt')
    with log.open('x', encoding='utf-8') as stream:
        completed = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT)
    row.update(exit_code=completed.returncode, closed_utc=utc())
    save()
    assert completed.returncode == 0, label

def host(script):
    return [sys.executable, str(k / script), case]

def linux(script):
    path = '/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/video-text-oracle206/' + script
    return ['wsl', '-d', 'Ubuntu', '--', 'env',
            'LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu',
            'python3', path, case]

try:
    step('observer', host('watch-physical.py'))
    if not read(out / 'physical-return.json')['dashboard_return']:
        r['status'] = 'observer_closed_manual_screen_needed'
    else:
        step('collect', [sys.executable, str(k / 'physical-controller.py'), 'collect', case])
        step('restored', host('verify-restored.py'))
        step('hives', linux('audit-physical-hives.py'))
        step('audit', host('audit-physical.py'))
        step('closure', host('close-case.py'))
        r['status'] = 'collected_restored_audited_closed'
        r['scoped_display_passed'] = read(out / 'physical-audit.json')['scoped_display_passed']
        r['strict_events_passed'] = read(out / 'physical-audit.json')['strict_events_passed']
except Exception as exc:
    r['status'] = 'preserved_failure_requires_review'
    r['error'] = repr(exc)
    state = read(out / 'physical.json')
    returned = read(out / 'physical-return.json').get('dashboard_return') if (out / 'physical-return.json').exists() else False
    if returned and not state.get('baseline_restored'):
        try:
            step('fallback-rollback', [sys.executable, str(k / 'physical-controller.py'), 'rollback', case])
        except Exception as rollback_error:
            r['rollback_error'] = repr(rollback_error)
finally:
    r.update(closed=True, closed_utc=utc(), baseline_restored=read(out / 'physical.json').get('baseline_restored', False))
    save()
print(json.dumps({name:r.get(name) for name in ['status', 'baseline_restored', 'scoped_display_passed', 'strict_events_passed']}, indent=2))
