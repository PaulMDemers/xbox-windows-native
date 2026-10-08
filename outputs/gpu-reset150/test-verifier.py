"""Reject missing reset, invalid ordering and removed surface invalidation."""
import copy,json
from pathlib import Path
from verify import reset_evidence,read,sha,ws
k=Path(__file__).resolve().parent;checks=[]
for case in ['control001','candidate001']:
    r=read(k/case/'reset.json');data=(ws/('work/runs/gpu-reset150-'+case+'/cpu-trace.log')).read_bytes()
    for name in ['no_reset','duplicate_reset','wrong_order','missing_cpu_reset','missing_marker_invalidation']:
        x=copy.deepcopy(r);d=data
        if name=='no_reset':x['reset_count']=0
        elif name=='duplicate_reset':x['reset_count']=2
        elif name=='wrong_order':x['reset_requested_utc']=x['before_reset']['requested_utc']
        elif name=='missing_cpu_reset':
            start=x['reset_trace_offset'];d=d[:start]+d[start:].replace(b'CPU Reset (CPU 0)',b'CPU Resex (CPU 0)',1)
        else:
            start=x['reset_trace_offset'];needle=f"nv2a_pgraph_surface_invalidated 0x{x['marker']['base']:08x}".encode()
            at=d.index(needle,start);d=d[:at]+b'X'+d[at+1:]
        try:reset_evidence(x,d)
        except AssertionError:checks.append(case+':'+name)
        else:raise AssertionError('Bad reset accepted: '+name)
p=k/'verifier-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,checks=checks,test_sha256=sha(Path(__file__))),indent=2)+'\n')
print(len(checks),'reset evidence mutation checks passed')
