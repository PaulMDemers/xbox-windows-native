"""Seal both completed ordinary Windows cases; never launch or recollect."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
target=k/'series-closure.json';assert not target.exists();results={}
assert read(k/'verification.json')['ordinary_matched_pair_passed']
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
for n in ['oracle-tests.json','protocol-tests.json','pixel-tests.json','lifetime-tests.json']:
    t=read(k/n);assert t['passed']
    for name,digest in t['pins'].items():assert sha(k/name)==digest,name
for case in ['control001','candidate001']:
    out=k/case;run=ws/('work/runs/nt5-vwin155-'+case);cl=read(out/'closure.json')
    assert read(out/'verification.json')['ordinary_qualified'] and read(out/'audit.json')['strict_qualification_passed']
    assert sha(run/'hdd.qcow2')==cl['private_disk_sha256']
    for n,digest in cl['run_metadata_sha256'].items():assert sha(run/n)==digest,n
    for n,digest in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==digest,n
    for pid in {int(cl['instance']['processId']),int(read(out/'runner-start.json')['pid'])}:
        subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 3}}"],check=True)
    private={str(p.relative_to(ws)):sha(p) for p in sorted(run.iterdir()) if p.is_file()}
    private.update({str(p.relative_to(ws)):sha(p) for p in sorted((out/'artifacts').iterdir()) if p.is_file()})
    for p in out.glob('live-screen.*'):private[str(p.relative_to(ws))]=sha(p)
    results[case]=dict(ordinary_passed=True,cleanup=cl['cleanup'],audit_sha256=sha(out/'audit.json'),
        cold_verification_sha256=sha(out/'verification.json'),private_artifact_sha256=private)
build=read(k.parent/'xemu-cpu-surface-evict/build003/build.json');source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
raw=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',*[source+n for n in build['original_sources']]],text=True)
restored={r.split()[1].removeprefix(source):r.split()[0] for r in raw.splitlines()};assert restored==build['original_sources']
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
for p in k.rglob('*.json'):read(p)
target.write_text(json.dumps(dict(all_owned_sessions_closed=True,results=results,
    borrowed_sources_restored=restored,physical_access=False,debugger_intervention=False,
    timing_qualified=False,failed_host_verifier_preserved=True,
    closer_sha256=sha(Path(__file__))),indent=2)+'\n',encoding='utf-8')
print('Two ordinary Windows cases closed; inputs/source unchanged; no timing/physical claim')
