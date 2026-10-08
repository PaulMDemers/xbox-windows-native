"""Seal eight unique cases without rerunning or changing a qualification gate."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

target=k/'series-closure.json';assert not target.exists();series={}
kits=['gpu-reset-network151','gpu-reset-banner152','gpu-swizzle153','gpu-swizzle154']
for kit in kits:
    root=ws/'outputs'/kit;v=read(root/'verification.json')
    assert v['evidence_verified'] and v['matched_pair_passed']==(kit in ['gpu-reset-banner152','gpu-swizzle154'])
    for name,digest in read(root/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    for p in root.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    for p in root.rglob('*.json'):read(p)
    if (root/'build-inputs.json').exists():
        for row in read(root/'build-inputs.json')['sdk_inputs']:assert sha(Path(row['path']))==row['sha256']
        assert read(root/'build.json')['shared_sdk_unchanged']
    results={}
    for case in ['control001','candidate001']:
        out=root/case;run=ws/'work/runs'/(kit+'-'+case)
        a=read(out/'audit.json');inst=read(run/'instance.json');cleanup=read(run/'cleanup.json')
        ids={int(inst['processId']),int(read(out/'runner-start.json')['pid'])}
        for pid in ids:
            subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 3}}"],check=True)
        expected=kit!='gpu-swizzle153' and not (kit=='gpu-reset-network151' and case=='candidate001')
        assert a['cold_passed']==expected
        assert a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files']
        private={str(p.relative_to(ws)):sha(p) for p in sorted(run.iterdir()) if p.is_file()}
        private.update({str(p.relative_to(ws)):sha(p) for p in sorted((out/'artifacts').iterdir()) if p.is_file()})
        results[case]=dict(cold_passed=expected,cleanup=cleanup,audit_sha256=sha(out/'audit.json'),private_artifact_sha256=private)
    series[kit]=results
assert read(k/'evidence-tests.json')['passed'] and len(read(k/'evidence-tests.json')['checks'])==18
assert read(ws/'outputs/gpu-reset-banner152/deadline-tests.json')['passed']
assert read(ws/'outputs/gpu-swizzle153/lifecycle-tests.json')['passed']
assert len(read(ws/'outputs/gpu-swizzle153/lifecycle-tests.json')['checks'])==10
for kit in ['gpu-swizzle153','gpu-swizzle154']:
    t=read(ws/'outputs'/kit/'oracle-tests.json');assert t['passed'] and t['checks']==67
assert not read(ws/'outputs/gpu-reset150/control001/audit.json')['cold_passed']
build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
raw=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',*[source+p for p in build['original_sources']]],text=True)
restored={r.split()[1].removeprefix(source):r.split()[0] for r in raw.splitlines()};assert restored==build['original_sources']
target.write_text(json.dumps(dict(all_owned_sessions_closed=True,series=series,
    shared_sdk_unchanged=True,borrowed_sources_restored=restored,physical_access=False,
    windows_qualified=False,performance_qualified=False,old150_failure_preserved=True,
    candidate151_return_failure_preserved=True,original153_depth_failures_preserved=True,
    closer_sha256=sha(Path(__file__))),indent=2)+'\n',encoding='utf-8')
print('Eight unique cases closed; 150/151/153 failures preserved')
