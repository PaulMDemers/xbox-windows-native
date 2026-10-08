"""Require real swizzled lifecycles and retain153's incorrect Z-depth expectation."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'));from lifecycle import parse
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(events,surfaces,candidate):
    result=[]
    ck=['create','upload','download','upload','download','evict_reason','invalidated','create','upload','download','upload','download','invalidated']
    nk=['create','upload','download','evict_reason','invalidated','create','upload','download','evict_reason','invalidated','create','upload','download','evict_reason','invalidated','create','upload','download','invalidated']
    for s in surfaces:
        kinds=nk if candidate else ck;rows=[e for e in events if e['base']==s['base']][:len(kinds)];assert len(rows)==len(kinds)
        for i,(e,kind) in enumerate(zip(rows,kinds)):
            assert e['kind']==kind,(i,e,kind)
            shape=int(i>= (10 if candidate else 7));w,h=(32,64) if shape else (64,32)
            if 'width' in e:assert (e['width'],e['height'],e['pitch'])==(w,h,w*s['bpp'])
            if 'normalized_layout' in e:assert e['normalized_layout']=='swizzled'
            if 'bytes_per_pixel' in e:assert e['bytes_per_pixel']==s['bpp']
            if kind=='evict_reason':assert e['reason']==('cpu-write' if candidate else 'incompatible')
        result.append(dict(depth=s['depth'],events=rows))
    return result
def main(root):
    target=root/'verification.json';assert not target.exists();results={};qualified=root.name=='gpu-swizzle154'
    spec=importlib.util.spec_from_file_location('local_oracle',root/'oracle.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        out=root/case;run=ws/'work/runs'/(root.name+'-'+case);assert (run/'cleanup.json').exists();a=read(out/'audit.json');l=read(out/'launch.json')
        assert a['cold_passed']==qualified and a['protocol_passed'] and a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files'] and a['dashboard_return'] and a['new_files_exact']
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3]);assert read(run/'instance.json')['sourceSha256'].lower()==digest
        events=[e for e in parse((run/'cpu-trace.log').read_bytes()) if e['offset']>=l['trace_before_launch']]
        rows=verify(events,a['surfaces'],case.startswith('candidate'))
        if qualified:assert a['exact_pixels_passed']
        else:
            # Source-derived W-buffer reference is forensic evidence, not a waiver
            # of the original frozen oracle requiring Z=0.
            for q in range(2):
                for d in range(2):
                    for stage in range(3):
                        ref=bytearray(oracle.expected(q,d,stage))
                        if d:
                            for at in range(0,len(ref),2):
                                if ref[at:at+2]==b'\0\0':ref[at:at+2]=b'\1\0'
                        assert (out/'artifacts'/f'q{q}-d{d}-s{stage}.raw').read_bytes()==ref
            assert not a['exact_pixels_passed']
        results[case]=dict(cold_passed=qualified,lifecycle=rows,emulator_sha256=digest,
                          audit_sha256=sha(out/'audit.json'),trace_sha256=sha(run/'cpu-trace.log'))
    assert read(root/'control001/audit.json')['files']==read(root/'candidate001/audit.json')['files']
    for name,digest in read(root/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    target.write_text(json.dumps(dict(evidence_verified=True,matched_pair_passed=qualified,results=results,
        failed153_original_oracle_preserved=not qualified,verifier_sha256=sha(Path(__file__)),
        physical_qualified=False,windows_qualified=False,performance_qualified=False),indent=2)+'\n')
    print(root.name,'swizzled evidence verified; strict matched pair',qualified)
if __name__=='__main__':main(k if len(sys.argv)==1 else Path(sys.argv[1]).resolve())
