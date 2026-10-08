"""Check the native protocol's complete transfer order and guarded build identity."""
import hashlib, importlib.util, json, sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(rows):
    return [e['kind']+(':'+e['reason'] if e['kind']=='evict_reason' else '') for e in rows]

def verify_candidate(events,surfaces):
    result=[]
    for depth in [False,True]:
        group=[s for s in surfaces if s['depth']==depth]
        assert len(group)==2 and group[0]['base']==group[1]['base']
        base=group[0]['base'];rows=[e for e in events if e['base']==base]
        first=next(i for i,e in enumerate(rows) if e['kind']=='create')
        # Each CPU write into unread GPU data must first download, then evict.
        # Subsequent partial GPU clear must recreate/upload the CPU-modified RAM.
        create=['create','upload'];downloads=['download','download']
        evict=['evict_reason:cpu-write','invalidated']
        expected=create+downloads+evict+create+downloads
        # pbkit's second initialization clears depth through CPU stores; color
        # is not CPU-cleared there. Both epochs then repeat the unread-write case.
        expected+=(evict+create if depth else [])+downloads+evict+create+downloads
        expected+=['invalidated'] # later handoff, after both measured epochs
        life=rows[first:first+len(expected)]
        assert tokens(life)==expected,(depth,tokens(life),expected)
        for e in life:
            if e['kind'] in ['create','upload','download']:
                assert (e['width'],e['height'],e['pitch'],e['normalized_layout'])==(640,480,2560,'linear')
                assert e['binding'].lower()==('zeta' if depth else 'color')
                if e['kind']!='create':assert e['bytes_per_pixel']==4
        assert any(e['kind']=='create' for e in rows[first+len(expected):]),'No handoff replacement'
        result.append(dict(depth=depth,base=base,expected_order=expected,events=life,
            creates=expected.count('create'),uploads=expected.count('upload'),
            downloads=expected.count('download'),cpu_write_evictions=expected.count('evict_reason:cpu-write')))
    return result

def load_case(case):
    out=k/case;run=ws/('work/runs/gpu-evict-'+case)
    a=read(out/'audit.json');launch=read(out/'launch.json')
    assert a['cold_passed'] and launch['dashboard_return'] and launch['status']=='accepted'
    assert (run/'cleanup.json').exists()
    events=[e for e in parse((run/'cpu-trace.log').read_bytes()) if e['offset']>=launch['trace_before_launch']]
    return a,events,run

def main():
    target=k/'pair-verification.json';assert not target.exists()
    spec=importlib.util.spec_from_file_location('old',ws/'outputs/gpu-cpu-coherence144/verify-lifecycle.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    builds=read(k/'build002/build.json');assert builds['passed'] and builds['borrowed_sources_restored']
    results={}
    for case in ['control002','candidate002']:
        a,events,run=load_case(case);role=case.replace('002','')
        expected=next(b['sha256'] for b in builds['builds'] if b['case']==role)
        assert sha(k/('build002/artifacts/xemu-'+role+'.exe'))==expected
        assert read(run/'instance.json')['sourceSha256'].lower()==expected
        lifecycle=old.verify(events,a['surfaces'],unread=True) if role=='control' else verify_candidate(events,a['surfaces'])
        results[case]=dict(lifecycle=lifecycle,emulator_sha256=expected,trace_sha256=sha(run/'cpu-trace.log'),
            trace_bytes=(run/'cpu-trace.log').stat().st_size,audit_sha256=sha(k/case/'audit.json'))
    for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    a=read(k/'control002/audit.json');b=read(k/'candidate002/audit.json')
    assert a['files']==b['files'] and a['log']==b['log']
    report=dict(native_pair_passed=True,results=results,frozen_inputs_unchanged=True,
        exact_readback_bytes_per_run=19660800,volatile_cpu_stores_per_run=120292,
        debugger=False,windows_qualified=False,physical_qualified=False,performance_qualified=False,
        limits='Clear/read/CPU-store/partial-clear and pbkit lifetime coverage only. No explicit reset, overlap, Z16, swizzled or draw-batch coherence qualification.',
        verifier_sha256=sha(Path(__file__)),parser_sha256=sha(ws/'outputs/video-surface-history/lifecycle.py'),
        control_verifier_sha256=sha(ws/'outputs/gpu-cpu-coherence144/verify-lifecycle.py'))
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('Matched native pixels, protocol, cold state and exact surface lifecycle PASS')
if __name__=='__main__':main()
