"""Reparse ordinary cold pixels and prelaunch surface lifetimes; no guest actions."""
import hashlib,json
from pathlib import Path
from lifecycle import parse
from pixels import reference,observed
from protocol import fnv
k=Path(__file__).resolve().parent;ws=k.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def lifetime(events,launch):
    # Reconstruct surfaces actually alive at the launch request, not historical
    # creations that were invalidated before Windows began.
    live={}
    for e in events:
        if e['end_offset']>launch:break
        if e['kind']=='create':live[e['base']]=[e]
        elif e['kind']=='invalidated':live.pop(e['base'],None)
        elif e['base'] in live:live[e['base']].append(e)
    rows=[]
    for base,history in live.items():
        c=history[0];uploads=[e for e in history if e['kind']=='upload']
        if (c.get('binding'),c.get('width'),c.get('height'),c.get('pitch'))!=('zeta',640,480,1280):continue
        assert uploads and uploads[-1]['bytes_per_pixel']==2 and c['normalized_layout']=='linear'
        after=[e for e in events if e['base']==base and e['offset']>=launch]
        rows.append(dict(base=base,extent=[base,base+1280*480],prelaunch=history,after_launch=after,
            first_download=next((e for e in after if e['kind']=='download'),None),
            first_cpu_write_eviction=next((e for e in after if e['kind']=='evict_reason' and e['reason']=='cpu-write'),None),
            first_invalidation=next((e for e in after if e['kind']=='invalidated'),None)))
    assert len(rows)==1,'Require exactly one actual prelaunch640x480Z16 watch'
    assert rows[0]['first_download']
    return rows[0]
def main():
    target=k/'verification.json';assert not target.exists();results={}
    assert read(k/'pair-input-review.json')['passed']
    build=read(k.parent/'xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        out=k/case;run=ws/('work/runs/nt5-vwin155-'+case)
        a=read(out/'audit.json');v=read(out/'verification.json');f=read(k/('fixture-'+case+'.json'))
        assert a['strict_qualification_passed'] and v['passed'] and v['ordinary_qualified']
        assert not v['debugger'] and not v['timing_qualified'] and not a['warnings_errors']
        assert v['compared_pixels']==13271040 and len(v['observed_readbacks'])==45
        assert v['pagefile_unchanged'] and v['trace_records']<=254 and not v['dropped']
        assert (run/'cleanup.json').exists()
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
        assert read(out/'preflight.json')['emulator_sha256']==digest
        assert read(run/'instance.json')['sourceSha256'].lower()==digest
        for i in range(45):
            ref=(out/'artifacts'/f'ref{i:02d}.rgb').read_bytes()
            got=(out/'artifacts'/f'got{i:02d}.rgb').read_bytes()
            assert reference(ref,i) and observed(got,i)
            assert fnv(ref)==v['cases'][i]['reference_hash']
        raw=(run/'cpu-trace.log').read_bytes();events=parse(raw)
        assert b'nv2a_pgraph_surface_access_write ' not in raw and b'nv2a_pgraph_surface_access_read ' not in raw
        launch=read(out/'launch.json')['cycles'];assert len(launch)==1 and launch[0]['dashboard_return']
        watched=lifetime(events,launch[0]['trace_before_launch_offset'])
        assert watched['extent']==[0x03c64000,0x03cfa000]
        if case=='candidate001':
            ev=watched['first_cpu_write_eviction'];invalid=watched['first_invalidation']
            assert ev and invalid and watched['first_download']['offset']<ev['offset']<invalid['offset']
        else:assert not watched['first_cpu_write_eviction']
        results[case]=dict(ordinary_passed=True,emulator_sha256=digest,
            prelaunch_watch=watched,trace_sha256=sha(run/'cpu-trace.log'),
            cold_verification_sha256=sha(out/'verification.json'),fixture_sha256=f['fixture_sha256'],
            actual_bitblt_calls=v['callback_totals']['BitBlt'])
    for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    for n in ['oracle-tests.json','protocol-tests.json','pixel-tests.json']:assert read(k/n)['passed']
    target.write_text(json.dumps(dict(passed=True,ordinary_matched_pair_passed=True,results=results,
        debugger=False,physical_qualified=False,timing_qualified=False,
        limits='Postlaunch lifecycle covers handoff, Windows and normal dashboard return; no per-store/phase pairing. RGB readback uses the guest display path, not independent physical scanout. No speed claim.',
        verifier_sha256=sha(Path(__file__))),indent=2)+'\n')
    print('Matched ordinary Windows pixels, cold gates and prelaunch watch evidence passed')
if __name__=='__main__':main()
