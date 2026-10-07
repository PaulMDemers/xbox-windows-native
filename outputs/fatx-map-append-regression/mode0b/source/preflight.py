"""Pin exact scripts, source, helper, seed and all parents before a unique launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['mode0b','mode1']
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def hostpath(p):
    return Path(p[5]+':'+p[6:]) if sys.platform=='win32' and p.startswith('/mnt/') else Path(p)
f=read(k/('fixture-'+case+'.json'));review=read(k/'build-review.json')
assert not (ws/('work/runs/nt5-fatx-map-append-'+case)).exists()
assert not (k/case/'preflight.json').exists()
assert sha(k/'build-review.json')==f['build_review_sha256']
assert sha(k/'probe.c')==review['source_sha256'] and sha(k/'artifacts/probe.exe')==review['probe_sha256']
assert sha(k/'Build.ps1')==review['build_script_sha256']
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/('work/fatx-map-append-'+case+'-seed.qcow2'))==f['seed_sha256']
for row in f['parents']:assert sha(hostpath(row['path']))==row['sha256']
allocation=read(k/case/'before/allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
paths=['probe.c','Build.ps1','build-review.json','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','fixture-'+case+'.json']
r=dict(passed=True,case=case,physical_access=False,debugger=False,sources={n:sha(k/n) for n in paths},helper_sha256=review['probe_sha256'],fixture_sha256=f['fixture_sha256'],seed_sha256=f['seed_sha256'],parents_verified=len(f['parents']))
(k/case/'preflight.json').write_text(json.dumps(r,indent=2)+'\n');print('Pinned fresh ordinary '+case)
