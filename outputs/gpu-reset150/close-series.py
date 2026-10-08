"""Seal two overlap runs and the successful/failed reset cases without reruns."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
target=k/'series-closure.json';assert not target.exists();series={}
assert read(k/'verification.json')['evidence_verified']
assert not read(k/'verification.json')['matched_pair_passed']
assert read(ws/'outputs/gpu-overlap149/verification.json')['passed']
for kit in ['gpu-overlap149','gpu-reset150']:
    root=ws/'outputs'/kit;assert read(root/'verifier-tests.json')['passed'];results={}
    for name,digest in read(root/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    for p in root.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in root.rglob('*.json'):read(p)
    for row in read(root/'build-inputs.json')['sdk_inputs']:assert sha(Path(row['path']))==row['sha256']
    for case in ['control001','candidate001']:
        out=root/case;run=ws/'work/runs'/(kit+'-'+case);a=read(out/'audit.json');inst=read(run/'instance.json')
        cleanup=read(run/'cleanup.json')
        subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {int(inst['processId'])} -ErrorAction SilentlyContinue){{exit 3}}"],check=True)
        expected=not (kit=='gpu-reset150' and case=='control001');assert a['cold_passed']==expected
        assert a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files']
        private={str(p.relative_to(ws)):sha(p) for p in sorted(run.iterdir()) if p.is_file()}
        private.update({str(p.relative_to(ws)):sha(p) for p in sorted((out/'artifacts').iterdir()) if p.is_file()})
        results[case]=dict(cold_passed=expected,cleanup=cleanup,audit_sha256=sha(out/'audit.json'),private_artifact_sha256=private)
    series[kit]=results
build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json');source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
raw=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',*[source+p for p in build['original_sources']]],text=True)
restored={r.split()[1].removeprefix(source):r.split()[0] for r in raw.splitlines()};assert restored==build['original_sources']
target.write_text(json.dumps(dict(all_owned_sessions_closed=True,series=series,shared_sdk_unchanged=True,
    borrowed_sources_restored=restored,physical_access=False,windows_qualified=False,performance_qualified=False,
    control_reset_failure_preserved=True,closer_sha256=sha(Path(__file__))),indent=2)+'\n')
print('Four unique native runs closed; reset control failure preserved')
