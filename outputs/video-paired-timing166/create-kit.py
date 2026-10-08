"""Create a fresh five-sample helper kit; do not mutate previous attempts."""
import ast
import hashlib
import json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-helper-runtime165'
assert not (k/'Run.ps1').exists()
for name in ['common.py','preflight.py','audit.py','supervise.py','check-leases.ps1','Run.ps1']:
    text=(old/name).read_text(encoding='utf-8').replace('vphys165','vperf166').replace('video-helper-runtime165','video-paired-timing166').replace('windows-native-vtrial165','windows-native-vperf166').replace('xwnv164','xwnvt166')
    if name=='Run.ps1':
        text=text.replace("ValidateSet('candidate001')","ValidateSet('control001','candidate001')")
    if name=='audit.py':
        text=text.replace("for name in ['attempt.log','gdi-baseline.txt']:","for name in ['attempt.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]:")
        text=text.replace("if data is not None:(art/name).write_bytes(data)","if data is not None:\n            (art/name).parent.mkdir(parents=True,exist_ok=True);(art/name).write_bytes(data)")
        start=text.index("log=(r['gdi-baseline.txt']")
        end=text.index("r['warnings_errors']",start)
        text=text[:start]+'''r['samples']=[analyze(r.get('sample%d/gdi-baseline.txt'%i)) for i in range(5)]
r['probe_passed']=all(v['probe_passed'] for v in r['samples'])
r['copy_checks_passed']=all(v['copy_checks_passed'] for v in r['samples'])
r['loop_coverage']=all(v['loop_coverage'] for v in r['samples'])
r['actual_caps']=r['samples'][0]['actual_caps']
r['actual_modes']=r['samples'][0]['actual_modes']
r['caps_consistent']=all(v['actual_caps']==r['actual_caps'] and v['actual_modes']==r['actual_modes'] for v in r['samples'])
r['runner_normal_restart']=(r['attempt.log'] or '').splitlines()==['ATTEMPT_ONCE']+['SAMPLE_EXIT_ZERO %d'%i for i in range(5)]+['NORMAL_RESTART_REQUEST']
''' + text[end:]
        text=text.replace('from common import *','from common import *\nfrom sample_analysis import analyze')
        text=text.replace("r['probe_passed'] and r['copy_checks_passed']","r['caps_consistent'] and r['probe_passed'] and r['copy_checks_passed']")
    (k/name).write_bytes(text.encode('utf-8'))
text=(k.parent/'video-hardware-trial164/Build-Runner.ps1').read_text(encoding='utf-8').replace('video-hardware-trial164','video-paired-timing166')
(k/'Build-Runner.ps1').write_bytes(text.encode('utf-8'));(k/'artifacts').mkdir(exist_ok=False)
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
print('Fresh matched five-sample helper sources created')
