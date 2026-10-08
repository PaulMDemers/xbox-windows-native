"""Seal all closed draw attempts, including failed instrumentation and regression."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
target=k/'series-closure.json';assert not target.exists()
assert read(k/'verification.json')['passed']
assert read(ws/'outputs/gpu-evict-regression148/verification.json')['passed']
assert read(k/'verifier-tests.json')['passed']
assert read(ws/'outputs/gpu-draw-lifetime146/oracle-tests.json')['passed']
series={}
for kit,run_prefix,cases in [
    ('gpu-draw-lifetime145','gpu-draw145-',['control001']),
    ('gpu-draw-lifetime146','gpu-draw146-',['control001','candidate001']),
    ('gpu-draw-lifetime147','gpu-draw147-',['control001','candidate001']),
    ('gpu-evict-regression148','gpu-regression148-',['control001','candidate001'])]:
    root=ws/'outputs'/kit;results={}
    for name,digest in read(root/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    for p in root.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in root.rglob('*.json'):read(p)
    for case in cases:
        out=root/case;run=ws/'work/runs'/(run_prefix+case)
        cleanup=read(run/'cleanup.json');inst=read(run/'instance.json');a=read(out/'audit.json')
        subprocess.run(['powershell','-NoProfile','-Command',f"if(Get-Process -Id {int(inst['processId'])} -ErrorAction SilentlyContinue){{exit 3}}"],check=True)
        passed=not (kit=='gpu-draw-lifetime145' or (kit=='gpu-draw-lifetime146' and case=='candidate001'))
        assert a['cold_passed']==passed
        assert a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files']
        if kit!='gpu-draw-lifetime145':assert read(run/'completion.json')['reason']=='external_capture_complete'
        private={str(p.relative_to(ws)):sha(p) for p in sorted(run.iterdir()) if p.is_file()}
        private.update({str(p.relative_to(ws)):sha(p) for p in sorted((out/'artifacts').iterdir()) if p.is_file()})
        results[case]=dict(cold_passed=passed,launch=read(out/'launch.json'),cleanup=cleanup,
            audit_sha256=sha(out/'audit.json'),private_artifact_sha256=private)
    series[kit]=results
build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
raw=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',*[source+p for p in build['original_sources']]],text=True)
restored={r.split()[1].removeprefix(source):r.split()[0] for r in raw.splitlines()};assert restored==build['original_sources']
old=read(ws/'outputs/xemu-cpu-surface-evict/build002/candidate-source-pins.json')
new=read(ws/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json')
delta=[p for p in old if old[p]!=new[p]];assert delta==['hw/xbox/nv2a/pgraph/gl/surface.c']
for row in read(ws/'outputs/gpu-draw-lifetime145/build-inputs.json')['sdk_inputs']:assert sha(Path(row['path']))==row['sha256']
r=dict(all_owned_sessions_closed=True,borrowed_sources_restored=restored,shared_sdk_unchanged=True,
       build002_to_build003_source_changes=delta,series=series,
       corrected_draw_pair_passed=True,corrected_color_depth_pair_passed=True,
       physical_access=False,windows_qualified=False,performance_qualified=False,
       failed_trace_and_failed_candidate_preserved=True,closer_sha256=sha(Path(__file__)))
target.write_text(json.dumps(r,indent=2)+'\n')
print('Seven unique native runs sealed; two strict failures preserved, corrected pairs pass')
