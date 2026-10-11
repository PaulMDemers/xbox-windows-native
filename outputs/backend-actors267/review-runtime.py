"""Pin exact renderer child, complete host dependencies and immutable lineage."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'backend-ledger266'
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
assert read(parent/'emu001/host-state.json')['closed'] and read(parent/'emu001/closure.json')['closed']
frozen=read(parent/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
for name in ['common.py','atomic_json.py','kernel-discovery.py','close-host.py','typed-state.py','runtime-dependencies.py','attest.py','attestation-inputs001.json']:
    assert (k/name).read_bytes()==(parent/name).read_bytes()
for name in ['run.py','Invoke.ps1','audit.py','trace.py']:
    expected=(parent/name).read_text().replace('backend-ledger266','backend-actors267').replace('/ledger266/','/actors267/').replace('nt5-ledger266','nt5-actors267').replace('windows-native-ledger266','windows-native-actors267')
    assert (k/name).read_text()==expected,name
b=read(k/'renderer-build001.json');assert b['passed'] and b['borrowed_sources_restored']
assert read(k/'host-tests001.json')['passed'] and read(k/'extra-tests001.json')['passed']
art=Path('E:/Codex-archive/xbox-windows-native/actors267-build001');exe=art/'xemu-actors267.exe'
assert sha(exe)==b['executable_sha256']
pins=read(k/'renderer-source-pins001.json');old=read(k.parent/'backend-ledger265/renderer-source-pins003.json')
changed={n for n in old if old[n]!=pins[n]};assert changed==set(b['changed_sources'])
for n in b['original_sources']:assert sha(art/'source'/n)==pins[n],n
for n,h in b['inputs'].items():assert sha(k/n)==sha(art/'inputs'/n)==h,n
priorlog=(k.parent/'backend-ledger265/renderer-build003.log').read_text(errors='replace')
log=(k/'renderer-build001.log').read_text(errors='replace')
warnings=lambda t:set(re.findall(r'warning: (.*)',t))
assert not (warnings(log)-warnings(priorlog)),warnings(log)-warnings(priorlog)
assert 'error:' not in log
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert f['fixture_sha256']==read(parent/'emu001/fixture.json')['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
for n in ['system','software','default','sam','security']:
    assert sha(k/'emu001/artifacts'/('before-'+n))==sha(parent/'emu001/artifacts'/('before-'+n))
for p in k.glob('*.py'):ast.parse(p.read_text())
sp=importlib.util.spec_from_file_location('deps267',k/'runtime-dependencies.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
host=d.inventory();(k/'host-dependencies.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
r=dict(passed=True,guest_launched=False,physical_access=False,debugger=True,ordinary_qualified=False,
    changed_sources=sorted(changed),host_dependencies=len(host),probe_driver_unchanged=True,
    warning_instances=len(re.findall('warning:',log)),new_warning_messages=[],
    query_scope='GL4.0 uniform/transform-feedback indices, pinned renderer containers and current UI containers',
    actor_ack='Original work-function returned; NOT OS-thread exit/join',
    retirement_ready=False,native_gpu_grant=False)
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.json','.c','.h','.md']:frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('267 runtime preflight PASS;',len(frozen),'frozen inputs')
