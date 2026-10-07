"""Pin exact scripts, source, helper, seed and all parents before a unique launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','candidate001']
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def hostpath(p):
    return Path(p[5]+':'+p[6:]) if sys.platform=='win32' and p.startswith('/mnt/') else Path(p)
f=read(k/('fixture-'+case+'.json'));review=read(k/'build-review.json')
assert not (ws/('work/runs/nt5-hal-dump-path-'+case)).exists()
assert not (k/case/'preflight.json').exists()
if case=='candidate001':
    control=read(k/'control001/audit.json')
    assert control['workload_and_persistence_passed'] and control['integrity_passed']
    # This permits a diagnostic comparison only. Strict event failure is retained.
    assert (k/'control001/closure.json').exists()
assert sha(k/'build-review.json')==f['build_review_sha256']
assert sha(k/'hal-review.json')==f['hal_review_sha256']
hal=read(k/'hal-review.json')[case]
assert sha(k/'artifacts'/hal['name'])==f['hal_after_sha256']==hal['sha256']
assert sha(k/'probe.c')==review['source_sha256'] and sha(k/'artifacts/probe.exe')==review['probe_sha256']
assert sha(k/'Build.ps1')==review['build_script_sha256']
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/('work/hal-dump-path-'+case+'-seed.qcow2'))==f['seed_sha256']
for row in f['parents']:assert sha(hostpath(row['path']))==row['sha256']
allocation=read(k/case/'before/allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert read(k/case/'before-configuration.json')['expected_configuration']
oracle=read(k/'oracle-review.json');assert oracle['helper_sha256']==review['probe_sha256'] and all(oracle['validator_negative_checks'].values())
paths=['probe.c','Build.ps1','build-review.json','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','oracle-review.json','fixture-'+case+'.json']
paths+=['hal-review.json','inputs.json','control-inputs.json','manifest.json','0102-hal-root-dump-path-accounting.patch','counter-tests.json','test-counts.py','build.py','build-control.py','prepare-source.py','review-hal.py','hal-build-candidate001.json','hal-build-control001.json','atomic_json.py']
r=dict(passed=True,case=case,physical_access=False,debugger=False,sources={n:sha(k/n) for n in paths},helper_sha256=review['probe_sha256'],fixture_sha256=f['fixture_sha256'],seed_sha256=f['seed_sha256'],parents_verified=len(f['parents']))
snapshot=k/case/'source';assert not snapshot.exists();snapshot.mkdir()
for name in paths:
    target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((k/name).read_bytes())
(k/case/'preflight.json').write_text(json.dumps(r,indent=2)+'\n');print('Pinned fresh ordinary '+case)
