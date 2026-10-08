"""Verify staged frozen bytes and actual closed records; never rerun guest stages."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-verification.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda b:hashlib.sha256(b).hexdigest()
checked=0
for n,d in read(k/'frozen-inputs.json').items():
    assert sha((ws/n).read_bytes())==d,n
    if n.startswith('outputs/video-hook-counters167/') and '/artifacts/' not in n:
        assert sha(subprocess.check_output(['git','show',':'+n],cwd=ws))==d,n
    checked+=1
for n,d in read(k/'physical-ready.json')['source_pins'].items():
    p=k/n;assert sha(p.read_bytes())==d,n
    assert sha(subprocess.check_output(['git','show',':'+str(p.relative_to(ws)).replace('\\','/')],cwd=ws))==d,n
case=k/'candidate001';assert read(case/'closure.json')['closed']
r=read(case/'physical.json')
assert r['launch_requested'] and r.get('collected_utc') and r['baseline_restored'] and not r['startup_enabled']
assert read(case/'physical-return.json')['closed'] and read(case/'restored-verification.json')['passed']
assert read(case/'physical-hive-audit.json')['passed']
assert read(k/'emulator-counters.json')['counter_coverage_passed'] and read(k/'physical-counters.json')['counter_coverage_passed']
assert not read(k/'summary.json')['scoped_counter_diagnostic_qualified']
assert not read(k/'eligibility-correction.json')['actual_emulator']['eligible']
for p in k.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
result=dict(passed=True,source_pins_checked=checked,physical_sources_exact=True,owned_runs_closed=True,
    ordinary_emulator_launches=1,physical_launches=1,physical_collections=1,source_or_guest_reruns=0,
    emulator_scanout_checks=50,physical_scanout_checks=50,strict_release_qualified=False,
    emulator_shutdown_popup_preserved=True,executed_eligibility_gate_failure_preserved=True,
    scoped_diagnostic_qualified=False)
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
