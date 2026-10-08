"""Verify frozen inputs and close all three single-attempt native test records."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
for number in [142,143,144]:
    kit=k.parent/f'gpu-cpu-coherence{number}';run=ws/f'work/runs/gpu-coherence{number}-control001'
    dest=kit/'closure.json';assert not dest.exists()
    assert (run/'cleanup.json').exists() and read(run/'disk-retention.json')['retained']
    frozen=read(kit/'frozen-inputs.json')
    for name,digest in frozen.items():assert sha(Path(name))==digest,name
    build=read(kit/'build-inputs.json')
    assert sha(kit/'main.c')==build['source_sha256']
    assert sha(kit/'Makefile')==build['makefile_sha256']
    assert sha(Path(build['build'])/'pbkit-private/pbkit.c')==build['private_core_sha256']
    for row in build['sdk_inputs']:assert sha(Path(row['path']))==row['sha256']
    for row in read(kit/'build.json')['files']:assert sha(kit/'artifacts'/row['name'])==row['sha256']
    oracle=json.loads(subprocess.check_output(['C:/Python314/python.exe',str(kit/'test-oracle.py')],text=True))
    audit=read(kit/'control001/audit.json');assert audit['cold_passed']==(number!=142)
    if number!=142:assert read(kit/'lifecycle-verification.json')['passed']
    expected={'applications/xwngpu'+str(number)+'/bootstrap.log','xwngpu'+str(number)+'/result.log'} | {'xwngpu'+str(number)+'/'+r['name'] for r in audit['files']}
    new_files_exact=set(audit['new_e_files'])==(expected if number!=142 else set())
    assert new_files_exact
    private=[run/'hdd.qcow2',run/'cpu-trace.log',run/'input-hashes.json',run/'instance.json',run/'cleanup.json']
    private+=list((kit/'control001/artifacts').glob('*'))
    r=dict(closed=True,one_launch=True,physical_access=False,windows_launched=False,debugger=False,
      emulator_sha256=read(run/'instance.json')['sourceSha256'].lower(),native_cold_passed=audit['cold_passed'],
      lifecycle_passed=number!=142,performance_qualified=False,hardware_qualified=False,
      all_frozen_inputs_unchanged=True,shared_sdk_inputs_unchanged=True,new_files_exact=True,
      oracle_tests=oracle,launch=read(kit/'control001/launch.json'),cleanup=read(run/'cleanup.json'),
      private_artifacts={str(p.relative_to(ws)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in private},
      audit_sha256=sha(kit/'control001/audit.json'),frozen_inputs_sha256=sha(kit/'frozen-inputs.json'))
    dest.write_text(json.dumps(r,indent=2)+'\n')
    print(number,'closed; cold',r['native_cold_passed'],'lifecycle',r['lifecycle_passed'])
