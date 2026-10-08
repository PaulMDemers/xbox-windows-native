"""Offline timing qualification; ordinary pixel/event/integrity gates remain strict."""
import hashlib,json
from pathlib import Path
from protocol import validate_log,GEOMETRIES
from timing import isolation,aggregate
k=Path(__file__).resolve().parent;ws=k.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    dest=k/'timing-comparison.json';assert not dest.exists()
    r=dict(passed=False,timing_qualified=False,physical_qualified=False,debugger=False)
    try:
        assert read(k/'verification.json')['ordinary_matched_pair_passed']
        ready=read(k/'fixtures-ready.json');audit=read(k/'audit-start.json');rows=[];parsed=[]
        for case in ['control001','candidate001']:
            out=k/case;run=ws/('work/runs/nt5-vtime156-'+case)
            v=read(out/'verification.json');a=read(out/'audit.json')
            assert v['ordinary_qualified'] and not v['debugger'] and a['strict_qualification_passed']
            assert ready['cases'][case]['fixture_manifest_sha256']==sha(k/('fixture-'+case+'.json'))
            assert ready['cases'][case]['preflight_sha256']==sha(out/'preflight.json')
            assert audit['cleanup_sha256'][case]==sha(run/'cleanup.json')
            assert not list(run.glob('frame*')) and not list(run.glob('state*.json')) and not list(run.glob('*.raw'))
            assert not any((out/n).exists() for n in ['timeout-memory.json','kernel-trace.json','observation.json','live-screen.json'])
            launch=read(out/'launch.json')['cycles'];assert len(launch)==1
            rows.append([read(out/'performance-lease.json'),read(out/'lease-before.json'),read(out/'lease-after.json'),launch[0],read(out/'runner-start.json')])
            p=validate_log((out/'artifacts/result.log').read_bytes())
            assert p['cases']==v['cases'];parsed.append(p)
        isolation(ready,rows,audit)
        assert parsed[0]['clock']['frequency']==parsed[1]['clock']['frequency']
        summaries=[aggregate(p) for p in parsed];comparisons=[]
        for size,g in enumerate(GEOMETRIES):
            w,h,kind,x,y=g;row=dict(size=size,width=w,height=h,kind=kind,x=x,y=y,area=w*h)
            for target in ['primary','memory']:
                c,n=[s[size,target] for s in summaries]
                row[target]=dict(control=c,candidate=n,control_over_candidate=c['median_us']/n['median_us'],candidate_time_change_percent=100*(n['median_us']/c['median_us']-1))
            comparisons.append(row)
        for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
        r.update(passed=True,timing_qualified=True,qualified_cases=45,clock=[p['clock'] for p in parsed],comparisons=comparisons,
            isolation=rows,readiness_sha256=sha(k/'fixtures-ready.json'),audit_start_sha256=sha(k/'audit-start.json'),
            limits='Single control-first pair, three rotated samples per geometry, cooperative build/xemu leases, ordinary background Windows activity unexcluded. Same sparse firmware surface tracing/FTP observer. QPC/coarse-clock/quiet-counter checks passed. Microbenchmark latency, not physical throughput, interactive window dragging or FPS.')
    except (AssertionError,KeyError,ValueError) as exc:r['error']=repr(exc)
    r['verifier_sha256']=sha(Path(__file__));dest.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({n:r[n] for n in ['passed','timing_qualified','physical_qualified']}))
    assert r['passed'],r.get('error')
if __name__=='__main__':main()
