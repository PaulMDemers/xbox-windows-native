"""Reject missing transfers, wrong eviction behavior and changed geometry."""
import copy,hashlib,json
from pathlib import Path
from verify import verify,parse
k=Path(__file__).resolve().parent;ws=k.parents[1];checks=[]
for case in ['control001','candidate001']:
    a=json.loads((k/case/'audit.json').read_text());l=json.loads((k/case/'launch.json').read_text())
    events=[e for e in parse((ws/('work/runs/gpu-draw147-'+case+'/cpu-trace.log')).read_bytes()) if e['offset']>=l['trace_before_launch']]
    candidate=case.startswith('candidate');base=a['surface_base'];verify(events,base,candidate)
    for kind in ['create','upload','download','invalidated']+(['evict_reason'] if candidate else []):
        e=copy.deepcopy(events);i=next(i for i,r in enumerate(e) if r['base']==base and r['kind']==kind);del e[i]
        try:verify(e,base,candidate)
        except AssertionError:checks.append(dict(case=case,missing=kind))
        else:raise AssertionError(('Missing accepted',case,kind))
    e=copy.deepcopy(events);r=next(r for r in e if r['base']==base and r['kind']=='download');r['pitch']=1280
    try:verify(e,base,candidate)
    except AssertionError:checks.append(dict(case=case,corrupted='pitch'))
    else:raise AssertionError('Bad geometry accepted')
p=k/'verifier-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,rejected=checks,test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print(len(checks),'draw-lifecycle mutation checks passed')
