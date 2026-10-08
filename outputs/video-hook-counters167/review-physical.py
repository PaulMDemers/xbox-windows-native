"""Review fresh candidate-only rollback protocol after complete emulator closure."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'physical-ready.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(k/'candidate001/audit.json');assert a['workload_passed'] and a['integrity_passed']
assert len(a['samples'])==5 and all(v['counters_passed'] for v in a['samples'])
assert read(k/'emulator-counters.json')['counter_coverage_passed']
assert read(k/'candidate001/closure.json')['closed'] and not a['strict_qualification_passed']
fields=['source','event_id','type','strings','data_hex'];expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
assert len(a['warnings_errors'])==len(expected)==1 and all(a['warnings_errors'][0][f]==expected[0][f] for f in fields)
sys.argv=['physical-controller.py','inspect','candidate001'];spec=importlib.util.spec_from_file_location('controller167',k/'physical-controller.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
assert len(c.changes)==3 and c.namespace=='xwnvh167' and c.rollback_dir=='xwn-display167'
assert c.test_startup==b'@echo off\r\nC:\\xwnvh167\\runner.exe\r\nexit\r\n'
assert c.record==k/'candidate001/physical.json' and not c.record.exists()
assert read(k/'candidate001/launch.json')['cycles'][0]['dashboard_return']
paths=['physical-controller.py','audit-physical.py','audit-physical-hives.py','verify-restored.py','watch-physical.py','sample_analysis.py','review-physical.py','summarize-counters.py']
for name in paths:ast.parse((k/name).read_text(encoding='utf-8'))
dest.write_text(json.dumps(dict(prepared=True,physical_launch_performed=False,strict_release_qualified=False,
    source_pins={n:sha(k/n) for n in paths},no_second_launch_per_case=True,baseline_restored_after_case=True,
    scope='One candidate-only unchanged RAM0112 physical counter diagnostic; global counters and full-scan latency, no engine/upload split or performance promotion',
    source_review=['New v4 user probe and unchanged qualified166 helper','Driver hashes unchanged from158/166',
    'Actual typed physical159 bindings only; emulator hives never deployed','Fresh rollback verified before changes; startup LAST/FIRST',
    'Eligibility requires closed complete emulator/counter/cold audit and exact sole inherited Ft49; strict remains false',
    'Historical166 control gates are baseline evidence, not a newly paired v4 control; original framebuf lacks these escapes']),indent=2)+'\n',encoding='utf-8')
print('New hardware counters diagnostic reviewed; no console access')
