"""Owned172 packets + explicit synthetic v9 completion labels test phase parser only."""
import hashlib,json
from pathlib import Path
from timing_analysis import timing
k=Path(__file__).resolve().parent;dest=k/'timing-tests.json';assert not dest.exists()
checks=0;pins={}
for mode,case in enumerate(['control001','candidate001']):
    p=k.parent/'video-body-runtime172'/case/'audit.json';a=json.loads(p.read_text());pins[str(p.relative_to(k.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
    log=a['sample0/gdi-baseline.txt'].rstrip()+'\n'+'\n'.join('POST_TIMING_kind_pass %d 1 0'%i for i in range(3))
    assert timing(log,mode)['passed'];checks+=1
    lines=log.splitlines()
    assert not timing(log,1-mode)['passed'];checks+=1
    for field in [4,6,11,12,26,27]:
        q=list(lines);i=next(i for i,v in enumerate(q) if v.startswith('PROFILE_AFTER_kind_index_value 0 %d '%field));parts=q[i].split();parts[3]=str(0 if field in [4,6,26] else 1);q[i]=' '.join(parts)
        assert not timing('\n'.join(q),mode)['passed'];checks+=1
    i=next(i for i,v in enumerate(lines) if v.startswith('PROFILE_AFTER_kind_index_value 0 0 '))
    assert not timing('\n'.join(lines[:i]+lines[i+1:]),mode)['passed'];checks+=1
    assert not timing('\n'.join(lines+[lines[i]]),mode)['passed'];checks+=1
dest.write_text(json.dumps(dict(passed=True,checks=checks,host_only=True,adapted_completion_markers_are_synthetic=True,source_packets_owned172=True,guest_launch=False,physical_access=False,pins=pins,parser_sha256=hashlib.sha256((k/'timing_analysis.py').read_bytes()).hexdigest()),indent=2)+'\n')
print(checks,'phase parser coverage and refusal checks')
