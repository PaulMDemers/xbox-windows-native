"""Review actual guest helper/source/build/181 policy inputs before freezing."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'input-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in k.glob('*.py'):ast.parse(p.read_text())
assert read(k/'run-interface-review.json')['passed'] and read(k/'build-review.json')['passed']
old=k.parent/'device-settled-reboot181'
for n in ['runner.c','restart_gate.h','test-gate.c','xwnunused179.inf','artifacts/runner.exe']:assert (k/n).read_bytes()==(old/n).read_bytes(),n
assert read(old/'candidate001/closure.json')['closed'] and read(old/'candidate001/package-verification.json')['configuration_observed']
driver=k.parent/'video-dib-copy182'
assert read(driver/'driver-review.json')['passed'] and read(driver/'copy-review.json')['passed']
for name in ['control001','candidate001']:
 f=read(k/('fixture-'+name+'.json'));assert f['prepared'] and not f['launched']
 assert f['display_build_sha256']==sha(driver/name/'artifacts/xwnown.dll')
 assert read(k/name/'before/allocation.json')['allocation_consistent']
run=(k/'Run.ps1').read_text();assert '-GdbPort' not in run and '-Seconds 300' in run
assert sha(k/'Run.ps1')==read(k/'run-interface-review.json')['source_sha256']
assert 'CMP_WaitNoPendingInstallEvents' in (k/'runner.c').read_text()
dest.write_text(json.dumps(dict(passed=True,same_compiled_guard_sha256=sha(k/'artifacts/runner.exe'),probe_sha256=sha(k/'artifacts/gdi-probe.exe'),probe_source_sha256=sha(k/'gdi-probe.c'),matched_driver_source_tree=read(driver/'driver-review.json')['source_tree'],prior_closure_sha256=sha(old/'candidate001/closure.json'),prior_configuration_sha256=sha(old/'candidate001/package-verification.json'),run_interface_sha256=sha(k/'Run.ps1'),ordinary_no_debugger=True,physical_access=False,unchanged_null_policy=True,strict_event_gates_unchanged=True),indent=2)+'\n')
print('183 inputs, matched drivers and181 policy reviewed; still not launched')
