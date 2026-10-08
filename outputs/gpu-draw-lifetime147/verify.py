"""Whole-draw retention and exact transfer sequence for the primitive-aware fix."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def verify(events,base,candidate):
    rows=[e for e in events if e['base']==base]
    first=next(i for i,e in enumerate(rows) if e['kind']=='create')
    C,U,D,I,E='create','upload','download','invalidated','evict_reason:cpu-write'
    # Case0: initial upload/draw/read. Case1: download before CPU write, then
    # evict+recreate (candidate) or upload original (control), draw/read.
    expected=[C,U,D,D]+([E,I,C,U] if candidate else [U])+[D]
    # Cases2/3 retain the binding through BEGIN/END. CPU reads force download;
    # the pending upload from case2 is consumed by the next clear's update.
    expected += [D,D,U,D,D,I]
    life=rows[first:first+len(expected)]
    tokens=[e['kind']+(':'+e['reason'] if e['kind']=='evict_reason' else '') for e in life]
    assert tokens==expected,(tokens,expected)
    for e in life:
        if e['kind'] in [C,U,D]:
            assert (e['width'],e['height'],e['pitch'],e['normalized_layout'])==(640,480,2560,'linear')
            assert e['binding'].lower()=='color'
            if e['kind']!=C:assert e['bytes_per_pixel']==4
    return dict(events=life,expected=expected,cpu_write_evictions=expected.count(E))
if __name__=='__main__':
    target=k/'verification.json';assert not target.exists()
    r={}
    build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        a=read(k/case/'audit.json');assert a['cold_passed']
        launch=read(k/case/'launch.json');run=ws/('work/runs/gpu-draw147-'+case)
        assert (run/'cleanup.json').exists()
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
        assert read(run/'instance.json')['sourceSha256'].lower()==digest
        data=(run/'cpu-trace.log').read_bytes();es=[e for e in parse(data) if e['offset']>=launch['trace_before_launch']]
        r[case]=dict(lifecycle=verify(es,a['surface_base'],case.startswith('candidate')),
            trace_sha256=sha(run/'cpu-trace.log'),audit_sha256=sha(k/case/'audit.json'),emulator_sha256=digest)
    a=read(k/'control001/audit.json');b=read(k/'candidate001/audit.json');assert a['files']==b['files'] and a['log']==b['log']
    for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    target.write_text(json.dumps(dict(passed=True,results=r,verifier_sha256=sha(Path(__file__)),
        parser_sha256=sha(ws/'outputs/video-surface-history/lifecycle.py'),performance_qualified=False,
        limits='Native same-value disjoint store, four legal command sequences. Does not force the request-to-worker BEGIN race, reset or overlap.'),indent=2)+'\n')
    print('Matched draws and primitive-aware surface lifecycle PASS')
