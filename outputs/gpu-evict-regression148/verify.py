"""Unchanged native144 pixel oracle and lifecycle expectations against build003."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'))
from lifecycle import parse
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
control=load('control_verifier',ws/'outputs/gpu-cpu-coherence144/verify-lifecycle.py')
candidate=load('candidate_verifier',ws/'outputs/xemu-cpu-surface-evict/verify-pair.py')
target=k/'verification.json';assert not target.exists();results={}
build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
for case in ['control001','candidate001']:
    a=read(k/case/'audit.json');assert a['cold_passed']
    run=ws/('work/runs/gpu-regression148-'+case);launch=read(k/case/'launch.json');assert (run/'cleanup.json').exists()
    digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
    assert read(run/'instance.json')['sourceSha256'].lower()==digest
    es=[e for e in parse((run/'cpu-trace.log').read_bytes()) if e['offset']>=launch['trace_before_launch']]
    lifecycle=control.verify(es,a['surfaces'],True) if case.startswith('control') else candidate.verify_candidate(es,a['surfaces'])
    results[case]=dict(lifecycle=lifecycle,emulator_sha256=digest,trace_sha256=sha(run/'cpu-trace.log'),audit_sha256=sha(k/case/'audit.json'))
assert read(k/'control001/audit.json')['files']==read(k/'candidate001/audit.json')['files']
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
target.write_text(json.dumps(dict(passed=True,results=results,verifier_sha256=sha(Path(__file__)),
    control_verifier_sha256=sha(Path(control.__file__)),candidate_verifier_sha256=sha(Path(candidate.__file__)),
    performance_qualified=False,physical_qualified=False),indent=2)+'\n')
print('Build003 color/depth coherence and preserved CPU-write eviction PASS')
