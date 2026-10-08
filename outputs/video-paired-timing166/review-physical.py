"""Review derived one-shot controller paths and freeze physical source packet."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent
dest=k/'physical-ready.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
fields=['source','event_id','type','strings','data_hex']
expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
for case in ['control001','candidate001']:
    a=read(k/case/'audit.json');assert a['workload_passed'] and a['integrity_passed']
    assert len(a['samples'])==5 and not a['strict_qualification_passed']
    assert len(a['warnings_errors'])==len(expected)==1 and all(a['warnings_errors'][0][f]==expected[0][f] for f in fields)
    sys.argv=['physical-controller.py','inspect',case]
    spec=importlib.util.spec_from_file_location('controller_'+case,k/'physical-controller.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    assert len(c.changes)==(0 if case=='control001' else 3)
    assert c.namespace==('xwnvt166a' if case=='control001' else 'xwnvt166b')
    assert c.test_startup==('@echo off\r\nC:\\'+c.namespace+'\\runner.exe\r\nexit\r\n').encode('ascii')
    assert c.record==k/case/'physical.json' and not c.record.exists()
    assert read(k/case/'launch.json')['cycles'][0]['dashboard_return']
paths=['physical-controller.py','audit-physical.py','audit-physical-hives.py','verify-restored.py','watch-physical.py','sample_analysis.py','review-physical.py']
for name in paths:ast.parse((k/name).read_text(encoding='utf-8'))
pins={name:hashlib.sha256((k/name).read_bytes()).hexdigest() for name in paths}
result=dict(prepared=True,physical_launch_performed=False,strict_release_qualified=False,
    source_pins=pins,scope='One fresh baseline and one candidate, same five-sample helper/probe; nonpromoting paired timing diagnostic',
    no_second_launch_per_case=True,baseline_restored_after_each_case=True,
    source_review=['No driver or binding change in control','Only3displayfiles/2typedphysicalbindings in candidate',
    'Immutable core/SYSTEM/startup guards; mutable logs/SOFTWARE captured fresh per case',
    'Unique namespace/rollback folders, readback before staging, startup LAST/FIRST',
    'Candidate requires clean complete control except exact inherited Ft49 signature'])
dest.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
print('Fresh paired console protocol reviewed and frozen; no console access')
