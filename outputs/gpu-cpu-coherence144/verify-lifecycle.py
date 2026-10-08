"""Verify complete surface transfer sequences, not merely a screenshot or count."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(events,surfaces,unread=False):
    result=[]
    for depth in [False,True]:
        group=[s for s in surfaces if s['depth']==depth]
        assert len(group)==2 and group[0]['base']==group[1]['base'],'Expected measured address reuse'
        base=group[0]['base'];rows=[e for e in events if e['base']==base]
        first=next(i for i,e in enumerate(rows) if e['kind']=='create')
        end=next(i for i in range(first+1,len(rows)) if rows[i]['kind']=='invalidated')
        life=rows[first:end+1]
        for e in life:
            if e['kind'] in ['create','upload','download']:
                assert (e['width'],e['height'],e['pitch'],e['normalized_layout'])==(640,480,2560,'linear')
                assert e['binding'].lower()==('zeta' if depth else 'color')
                if e['kind']!='create':assert e['bytes_per_pixel']==4
        # One coherent read per GPU clear. The unread variant forces a second
        # download on the first CPU store, before the partial-clear upload.
        epoch=['download']+(['download'] if unread else [])+['upload','download','download']
        expected=['create','upload']+epoch+(['upload'] if depth else [])+epoch+['invalidated']
        observed=[e['kind'] for e in life if e['kind'] not in ['evict_reason','evict_overlapping']]
        assert observed==expected,(depth,observed,expected)
        assert any(e['kind']=='create' for e in rows[end+1:]),'No later surface replacement'
        result.append(dict(depth=depth,base=base,first_lifetime=life,expected_order=expected,
                           uploads=observed.count('upload'),downloads=observed.count('download'),
                           retained_across_pbkit_reinit=True,later_invalidation_and_recreation=True))
    return result

if __name__=='__main__':
    out=k/'control001';a=json.loads((out/'audit.json').read_text());assert a['cold_passed']
    launch=json.loads((out/'launch.json').read_text())
    run=ws/'work/runs/gpu-coherence144-control001';assert (run/'cleanup.json').exists()
    data=(run/'cpu-trace.log').read_bytes();events=parse(data)
    events=[e for e in events if e['offset']>=launch['trace_before_launch']]
    result=verify(events,a['surfaces'],unread=True)
    target=k/'lifecycle-verification.json';assert not target.exists()
    target.write_text(json.dumps(dict(passed=True,surfaces=result,trace_sha256=sha(run/'cpu-trace.log'),trace_bytes=len(data),
       audit_sha256=sha(out/'audit.json'),parser_sha256=sha(ws/'outputs/video-surface-history/lifecycle.py'),verifier_sha256=sha(Path(__file__)),
       debugger=False,performance_qualified=False,physical_qualified=False,
       limits='Same surfaces survive both pbkit epochs; later invalidation/recreation is during handoff. No explicit device-reset contract, overlapping watch or Z16/swizzled coverage claimed.'),indent=2)+'\n')
    print('Exact transfer order verified for color and depth; no performance claim')
