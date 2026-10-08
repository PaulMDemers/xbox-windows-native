"""Require preservation on overlap replacement and candidate CPU-write eviction."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(events,surfaces,candidate):
    results=[]
    for s in surfaces:
        a=s['base'];b=a+s['offset']
        rows=[e for e in events if e['base'] in (a,b)][:14]
        kinds=['create','upload','evict_overlapping','download','invalidated','create','upload','download',
               'evict_reason' if candidate else 'evict_overlapping','invalidated','create','upload','download','invalidated']
        bases=[a,a,a,a,a,b,b,b,b,b,a,a,a,a]
        assert len(rows)==14
        for e,kind,base in zip(rows,kinds,bases):
            assert e['kind']==kind and e['base']==base,(e,kind,base)
            if 'width' in e:assert (e['width'],e['height'],e['pitch'])==(64,64,s['pitch_a'] if base==a else s['pitch_b'])
            if 'bytes_per_pixel' in e:assert e['bytes_per_pixel']==s['bpp']
            if 'normalized_layout' in e:assert e['normalized_layout']=='linear'
            if kind=='evict_reason':assert e['reason']=='cpu-write'
        results.append(dict(depth=s['depth'],events=rows))
    return results
def main():
    target=k/'verification.json';assert not target.exists();results={}
    build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        a=read(k/case/'audit.json');assert a['cold_passed']
        run=ws/('work/runs/gpu-overlap149-'+case);launch=read(k/case/'launch.json');assert (run/'cleanup.json').exists()
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
        assert read(run/'instance.json')['sourceSha256'].lower()==digest
        es=[e for e in parse((run/'cpu-trace.log').read_bytes()) if e['offset']>=launch['trace_before_launch']]
        results[case]=dict(lifecycle=verify(es,a['surfaces'],case.startswith('candidate')),emulator_sha256=digest,
                           trace_sha256=sha(run/'cpu-trace.log'),audit_sha256=sha(k/case/'audit.json'))
    assert read(k/'control001/audit.json')['files']==read(k/'candidate001/audit.json')['files']
    for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    target.write_text(json.dumps(dict(passed=True,results=results,verifier_sha256=sha(Path(__file__)),
        simultaneous_overlapping_watches_proven=False,performance_qualified=False,physical_qualified=False),indent=2)+'\n')
    print('Exact overlap replacement and CPU-write lifecycle PASS')
if __name__=='__main__':main()
