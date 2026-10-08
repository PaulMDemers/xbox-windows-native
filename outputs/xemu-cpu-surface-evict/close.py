"""Seal the completed native pair without reopening or rerunning either guest."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
target=k/'closure.json';assert not target.exists()
pair=read(k/'pair-verification.json');assert pair['native_pair_passed']
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
build=read(k/'build002/build.json')
c=read(k/'build002/control-source-pins.json');d=read(k/'build002/candidate-source-pins.json')
assert c.keys()==d.keys()
changed=sorted(x for x in c if c[x]!=d[x]);assert changed==build['changed_sources']
assert sha(k/'build002/cpu-surface-evict.patch')==build['patch_sha256']
oracle=json.loads(subprocess.check_output([sys.executable,str(k/'test-oracle.py')]))
assert oracle['passed'] and read(k/'recorded-pair-tests.json')['passed']
source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
output=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',*[source+p for p in build['original_sources']]],text=True)
restored={line.split()[1].removeprefix(source):line.split()[0] for line in output.splitlines()}
assert restored==build['original_sources']
cases={}
for case in ['control002','candidate002']:
    run=ws/('work/runs/gpu-evict-'+case);out=k/case
    assert read(run/'completion.json')['reason']=='external_capture_complete'
    assert read(out/'audit.json')['cold_passed']
    inst=read(run/'instance.json')
    # Require each owned process to have terminated; never terminate by name.
    ps=subprocess.check_output(['powershell','-NoProfile','-Command',
       f"if(Get-Process -Id {int(inst['processId'])} -ErrorAction SilentlyContinue){{exit 3}}"],text=True)
    private={str(p.relative_to(ws)):sha(p) for p in sorted(run.iterdir()) if p.is_file()}
    private.update({str(p.relative_to(ws)):sha(p) for p in sorted((out/'artifacts').iterdir()) if p.is_file()})
    cases[case]=dict(launch=read(out/'launch.json'),cleanup=read(run/'cleanup.json'),private_artifact_sha256=private)
for p in k.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in k.rglob('*.json'):read(p)
r=dict(closed=True,native_pair_passed=True,all_owned_sessions_closed=True,
    debugger=False,windows_qualified=False,hardware_qualified=False,performance_qualified=False,
    physical_access=False,borrowed_sources_restored=restored,frozen_inputs_unchanged=True,
    matched_source_differences=changed,oracle_tests=oracle,cases=cases,
    pair_verification_sha256=sha(k/'pair-verification.json'),recorded_tests_sha256=sha(k/'recorded-pair-tests.json'),
    preserved=dict(failed_build001='Git ownership failure before compilation; restored',
        build001='Compiled unguarded candidate NEVER launched',control001='Prepared NEVER launched'),
    closer_sha256=sha(Path(__file__)))
target.write_text(json.dumps(r,indent=2)+'\n')
print('Both runs closed, source/input/artifact pins verified; native-only qualification sealed')
