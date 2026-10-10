"""Review closed guard evidence, source pins and exact staged owned text bytes."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'checkpoint-review.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = {}
for manifest in ('frozen.json', 'frozen002.json'):
    values = read(k / manifest)
    for name, digest in values.items():
        assert sha(ws / name) == digest, name
    pins[manifest] = {'sha256': sha(k / manifest), 'checked': len(values)}
v = read(k / 'pair-verification003.json')
assert v['passed'] and not v['ordinary_qualified'] and not v['gpu_context_qualified']
assert v['source_sha256'] == sha(k / 'verify003.py')
for name, digest in v['pins'].items():
    assert sha(k / name) == digest, name
for case in ('control002', 'candidate002'):
    audit = read(k / case / 'audit.json')
    host = read(k / case / 'host-state.json')
    closure = read(k / case / 'closure.json')
    assert closure['audit_sha256'] == sha(k / case / 'audit.json')
    assert host['closed'] and audit['guard_scope_passed'] and audit['integrity_passed']
    assert all(host[n] == 0 for n in ('runner_exit', 'tracer_exit', 'supervisor_exit', 'audit_exit'))
    assert not audit['ordinary_qualified'] and not audit['physical_qualified'] and not audit['dump_qualified']
    errors = [e for e in audit['new_events']['system'] if e['type'] in (1, 2)]
    assert len(errors) == 1 and errors[0]['source'] == 'Ftdisk' and errors[0]['event_id'] == 49
    assert not audit['new_events']['application'] and audit['normal_shutdown_count'] == 0
for case in ('control001',):
    assert read(k / case / 'host-state.json')['closed']
    assert not read(k / case / 'trace.json')['passed']
assert not (k / 'candidate001' / 'runner-start.json').exists()
q = ws / 'outputs/device-hardware220'
assert read(q / 'queue-review001.json')['passed']
assert read(q / 'queue-review001.json')['source_sha256'] == sha(q / 'queue.py')
syntax = []
for folder in (k, q):
    for p in folder.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
        syntax.append(str(p.relative_to(ws)))
staged = subprocess.check_output(['git', '-C', str(ws), 'ls-files', '-z',
                                 'outputs/video-reset-guard221', 'outputs/device-hardware220'], text=True).split('\0')
exact = {}
for name in filter(None, staged):
    assert '/artifacts/' not in name and '/state/' not in name, name
    data = subprocess.check_output(['git', '-C', str(ws), 'show', ':' + name])
    assert data == (ws / name).read_bytes(), name
    exact[name] = hashlib.sha256(data).hexdigest()
for record in read(ws / 'outputs/task-storage-offload/manifest-kernel032035-20261010.json')['records']:
    assert record['status'] == 'complete'
dest.write_text(json.dumps({'passed': True, 'physical_access': False, 'frozen': pins,
                           'pair_review_sha256': sha(k / 'pair-verification003.json'),
                           'python_syntax': syntax, 'exact_staged_owned_text': exact,
                           'strict_event_passed': False, 'ordinary_qualified': False,
                           'limits': 'Owned staged text and closed evidence review only; no exhaustive file-content audit, early boot guard, GPU command or physical qualification.'}, indent=2) + '\n', encoding='utf-8')
print('Closed scope, frozen inputs, Python syntax and exact staged text PASS')
