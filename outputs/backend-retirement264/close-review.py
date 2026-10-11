"""Verify the new review artifacts and record the closed host-only state."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

inventory = json.loads((HERE/'inventory-review.json').read_text())
test = json.loads((HERE/'texture-lifetime-test001.json').read_text())
assert test['passed'] and test['compile_exit'] == test['test_exit'] == 0
assert 'PASS 28 host lifetime cases' in test['test_output']
assert len(inventory['source_files_verified']) == 26
assert inventory['same_reference_sets_all_stages']
assert [s['stage'] for s in inventory['stages']] == [1, 2, 3, 4]
assert sum(len(s['negative_controls']) for s in inventory['stages']) == 40
assert sha(Path(inventory['trace'])) == inventory['trace_sha256']
for manifest in ['source-review.json', 'source-review002.json']:
    data = json.loads((HERE/manifest).read_text())
    for row in data['files']:
        assert sha(Path(data['destination'])/row['path']) == row['sha256']
for name, digest in test['files'].items():
    assert sha(Path('E:/Codex-archive/xbox-windows-native/retirement264-host001')/name) == digest
for script in HERE.glob('*.py'):
    ast.parse(script.read_text(encoding='utf-8'), filename=str(script))

def wsl(*args):
    return subprocess.check_output(['wsl','-d','Ubuntu','-u','root','--',*args],timeout=30).decode().strip()

result = dict(closed=True, closed_utc=datetime.now(timezone.utc).isoformat(),
              scope='source review and host ownership accounting, no runtime retirement',
              source_files=26, additional_queue_header_verified=True,
              guest_launches=0, physical_access=False, renderer_modified=False,
              owned_running_sessions=[], actual_inventory_stages=4,
              unchanged_references_per_stage=118, rejected_actual_report_mutations=40,
              host_exact_function_cases=28, asan_ubsan_harness_passed=True,
              gl_calls='counted stubs; no GL context or real deletion tested',
              full_backend_retirement_proved=False, native_gpu_ownership=False,
              strict_qualification_passed=False, inherited_strict_failure='Ftdisk49',
              compiler_version=wsl('gcc','--version'),
              compiler_sha256=wsl('sha256sum','/usr/bin/gcc').split()[0],
              evidence={str(p.relative_to(HERE)):sha(p) for p in HERE.iterdir()
                        if p.is_file() and p.name != 'final-review.json'})
with (HERE/'final-review.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2); f.write('\n')
print(json.dumps({k:result[k] for k in ['closed','source_files','host_exact_function_cases','guest_launches','physical_access']}))
