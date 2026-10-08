"""Verify explicit reset evidence without converting the control timeout to a pass."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
s=importlib.util.spec_from_file_location('overlap',ws/'outputs/gpu-overlap149/verify.py');overlap=importlib.util.module_from_spec(s);s.loader.exec_module(overlap)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset_evidence(r,data):
    assert r['reset_count']==1 and not r['physical_access'] and not r['debugger']
    assert r['before_reset']['status']=='accepted'
    assert 'system_reset' in r['reset_reply'] and '(qemu)' in r['reset_reply']
    assert r['before_reset']['requested_utc']<r['marker_utc']<r['reset_requested_utc']<r['reset_command_completed_utc']
    start=r['reset_trace_offset'];end=r.get('after_reset',{}).get('trace_offset',len(data))
    assert r['before_reset']['trace_offset']<r['marker']['offset']<start<end
    assert data[start:end].count(b'CPU Reset (CPU 0)')==1
    es=parse(data);marker=[e for e in es if e['offset']==r['marker']['offset']];assert marker==[r['marker']]
    assert marker[0]['kind']=='upload' and marker[0]['binding']=='COLOR'
    assert (marker[0]['width'],marker[0]['height'],marker[0]['pitch'],marker[0]['bytes_per_pixel'])==(80,40,320,4)
    transitions=[e for e in es if start<=e['offset']<end and e['base']==marker[0]['base']]
    assert [e['kind'] for e in transitions]==['invalidated','create','upload','evict_overlapping','invalidated']
    return transitions
def main():
    target=k/'verification.json';assert not target.exists();results={}
    build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        out=k/case;run=ws/('work/runs/gpu-reset150-'+case);assert (run/'cleanup.json').exists()
        a=read(out/'audit.json');r=read(out/'reset.json');data=(run/'cpu-trace.log').read_bytes()
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
        assert read(run/'instance.json')['sourceSha256'].lower()==digest
        before=(out/'before-reset-trace.log').read_bytes();assert data[:len(before)]==before
        assert sha(out/'before-reset-trace.log')==r['before_reset_trace_sha256']
        assert a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files']
        assert a['phases']['150']['protocol_passed']
        assert all(f['matched'] for f in a['files'] if f['phase']==150)
        result=dict(reset_lifecycle=reset_evidence(r,data),cold_passed=a['cold_passed'],emulator_sha256=digest,
                    trace_sha256=sha(run/'cpu-trace.log'),audit_sha256=sha(out/'audit.json'))
        if case=='candidate001':
            assert a['cold_passed'] and r['dashboard_return'] and r['offline_after_second_launch'] and not r.get('failed')
            assert r['reset_command_completed_utc']<r['reset_dashboard_utc']<=r['after_reset']['requested_utc']<r['returned_utc']
            events=[e for e in parse(data) if e['offset']>=r['after_reset']['trace_offset']]
            result['post_reset_lifecycle']=overlap.verify(events,a['phases']['149']['surfaces'],True)
        else:
            assert not a['cold_passed'] and r['failed'] and 'after_reset' not in r
            assert r['error']=="RuntimeError('No dashboard return; no repeat')"
            assert not a['phases']['149']['protocol_passed']
            assert all(f['sha256'] is None for f in a['files'] if f['phase']==149)
            result['screen_sha256']=sha(out/'reset-screen.png')
        results[case]=result
    for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    target.write_text(json.dumps(dict(evidence_verified=True,matched_pair_passed=False,candidate_reset_passed=True,
        control_reset_passed=False,network_difference_cause_proven=False,results=results,
        verifier_sha256=sha(Path(__file__)),overlap_verifier_sha256=sha(Path(overlap.__file__)),
        physical_qualified=False,windows_qualified=False,performance_qualified=False),indent=2)+'\n')
    print('Reset candidate PASS; control timeout preserved, pair NOT qualified')
if __name__=='__main__':main()
