"""Reject missing transfers, stale watch lifetimes and wrong surface geometry."""
import copy,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
spec=importlib.util.spec_from_file_location('verify_native_lifecycle',k/'verify-lifecycle.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
checks=[]
for number in [143,144]:
    kit=k.parent/f'gpu-cpu-coherence{number}'
    a=json.loads((kit/'control001/audit.json').read_text())
    events=v.parse((ws/f'work/runs/gpu-coherence{number}-control001/cpu-trace.log').read_bytes())
    lower=json.loads((kit/'control001/launch.json').read_text())['trace_before_launch']
    events=[e for e in events if e['offset']>=lower]
    assert v.verify(events,a['surfaces'],number==144)
    base=a['surfaces'][0]['base']
    picked=[i for i,e in enumerate(events) if e['base']==base]
    for kind in ['download','upload','invalidated']:
        i=next(i for i in picked if events[i]['kind']==kind)
        bad=events[:i]+events[i+1:]
        try:v.verify(bad,a['surfaces'],number==144)
        except (AssertionError,StopIteration):pass
        else:raise AssertionError('Missing '+kind+' accepted')
        checks.append(dict(case=number,rejected='missing_'+kind))
    for field,value in [('pitch',1280),('binding','ZETA'),('bytes_per_pixel',2)]:
        bad=copy.deepcopy(events);i=next(i for i in picked if events[i]['kind']=='download');bad[i][field]=value
        try:v.verify(bad,a['surfaces'],number==144)
        except AssertionError:pass
        else:raise AssertionError('Wrong '+field+' accepted')
        checks.append(dict(case=number,rejected='wrong_'+field))
    try:v.verify(events,a['surfaces'],number!=144)
    except AssertionError:pass
    else:raise AssertionError('Wrong unread-write protocol accepted')
    checks.append(dict(case=number,rejected='wrong_workload'))
p=k/'recorded-lifecycle-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,checks=checks),indent=2)+'\n')
print('Fourteen recorded lifecycle corruption gates rejected as expected')
