"""Review the closed diagnostic, frozen inputs and exact staged evidence."""
import ast, datetime, hashlib, json, subprocess
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'review001.json'
assert not dest.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
for kit in ['xemu-backend-dashboard229', 'xemu-backend-dashboard230']:
    for name, digest in read(k.parent / kit / 'emulator-frozen.json').items():
        assert sha(ws / name) == digest, name
for name, digest in read(k / 'author.json')['actual_compiled_model_stub_pins'].items():
    assert sha(k / 'source' / name) == digest
h = read(k / 'trace001/host-state.json')
a = read(k / 'trace001/audit.json')
t = read(k / 'trace001/trace.json')
c = read(k / 'trace001/closure.json')
raw = read(k / 'trace-observation-review001.json')
assert h['closed'] and h['cleanup_record_exists']
assert all(h[n] == 0 for n in ['observer_exit_code', 'runner_exit_code', 'tracer_exit_code', 'audit_exit_code'])
assert c['closed'] and c['never_relaunch_or_recollect']
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed']
assert a['normal_shutdown_count'] == 1 and a['dashboard_return']
assert len(a['warnings_errors']) == 1
assert a['warnings_errors'][0]['source'] == 'Ftdisk' and a['warnings_errors'][0]['event_id'] == 49
assert a['warnings_errors'][0]['data_hex'].startswith('000000000100560000000000310004c003')
assert not a['strict_qualification_passed'] and not a['backend_preservation_qualified']
assert not a['publication_contract_qualified'] and not a['ordinary_qualified'] and not a['physical_qualified']
assert raw['passed'] and raw['raw_read_bytes'] == 212992
assert raw['trace_sha256'] == sha(k / 'trace001/trace.json')
assert t['closed'] and t['physical_mode_restored'] and t['guest_resumed']
assert t['preserve_result']['state'] == 4 and t['preserve_result']['reason'] == 1
assert not t['passed'] and not t['dirty_surface_coverage'] and t['preserve_result']['bytes'] == 0
for phase in ['before', 'after']:
    for row in t[phase]:
        p = ws / row['path']
        assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
for p in k.glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
staged = {}
for name in subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ws).decode().strip('\0').split('\0'):
    if name.startswith(('outputs/xemu-backend-dashboard229/', 'outputs/xemu-backend-dashboard230/')):
        data = subprocess.check_output(['git', 'show', ':' + name], cwd=ws)
        assert data == (ws / name).read_bytes(), name
        staged[name] = hashlib.sha256(data).hexdigest()
assert staged
subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ws, check=True)
subprocess.run(['C:/Python314/python.exe', '-B', str(ws / 'tools/check-repository.py')], cwd=ws, check=True)
dest.write_text(json.dumps(dict(passed=True,
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    source_sha256=sha(Path(__file__)), staged_byte_pins=staged,
    scopes='Closed debugger refusal, safe mode restoration, unchanged reserved bytes and normal CPU/cold scopes; strict/backend/native/ordinary/physical remain false',
    frozen_inputs_unchanged=True, owned_root_sessions_closed=True,
    physical_access=False), indent=2) + '\n')
print('230 closed diagnostic / frozen inputs / staged exact bytes PASS')
