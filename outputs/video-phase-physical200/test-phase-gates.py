"""Host replay of actual199 packets and NEW200 production gates; no console operations."""
import ast
import hashlib
import json
from pathlib import Path
from sample_analysis import analyze
from dib_analysis import analyze as rows_analyze
from timing_analysis import timing
from window_analysis import window

k=Path(__file__).resolve().parent
ws=k.parents[1]
dest=k/'phase-gate-tests.json'
assert not dest.exists()
source=(k/'audit-physical.py').read_text(encoding='utf-8')
parse=compile(ast.parse(source[source.index('samples=[analyze'):source.index("attempt=''",source.index('samples=[analyze'))]),'actual200-parser-block','exec')
tree=ast.parse(source)
gate=next(n for n in tree.body if isinstance(n,ast.Assign) and any(
    isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value=='workload_passed' for t in n.targets))
code=compile(ast.Module(body=[gate],type_ignores=[]),'actual200-workload-gate','exec')
checks=[]
pins={}
for case in ['control001','candidate001']:
    logs=[]
    for i in range(5):
        p=k.parent/('video-phase-runtime199/'+case+'/artifacts/sample%d/gdi-baseline.txt'%i)
        pins[p.relative_to(ws).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        logs.append(p.read_bytes().decode('ascii'))
    for label,selected,expected in [
        ('actual199-packets',logs,True),
        ('missing-window', [v.replace('WINDOW_CASE_pass 1 40 0','WINDOW_CASE_missing 1 40 0') for v in logs],False),
        ('missing-phase', [v.replace('PROFILE_CALL_kind_phase_result','PROFILE_CALL_missing') for v in logs],False),
        ('wrong-window-output', [v.replace('WINDOW_CASE_pass 1 40 0','WINDOW_CASE_pass 0 40 0') for v in logs],False)]:
        env=dict(logs=selected,case=case,analyze=analyze,rows_analyze=rows_analyze,timing=timing,window=window)
        exec(parse,env)
        s,d,t,w=[env[n] for n in ['samples','dib','phases','windows']]
        result=dict(caps_consistent=True,matched_emulator_geometry=True,
            probe_passed=all(v['probe_passed'] for v in s),
            pixel_checks_passed=all(v['copy_checks_passed'] for v in s) and all(v['passed'] for v in d),
            counters_passed=all(v['counters_passed'] for v in s) and all(v['passed'] for v in d),
            loop_coverage=all(v['loop_coverage'] for v in s),
            phase_coverage_passed=all(v['passed'] for v in t),window_coverage_passed=all(v['passed'] for v in w),
            normal_restart_requested=True,dashboard_return=True,normal_shutdown_count=1)
        exec(code,dict(result=result));assert result['workload_passed']==expected,(case,label)
        checks.append(dict(case=case,name=label,expected=expected,actual=result['workload_passed']))
dest.write_text(json.dumps(dict(passed=True,physical_access=False,real_launches=0,
    production_source_sha256=hashlib.sha256((k/'audit-physical.py').read_bytes()).hexdigest(),
    raw_actual199_pins=pins,checks=checks),indent=2)+'\n',encoding='utf-8')
print('NEW200 production parser/workload gate: eight actual packet/adversarial replays passed')
