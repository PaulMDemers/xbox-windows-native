"""New child with byte-exact host transport; guest/renderer remain identical265."""
import ast,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'backend-ledger265'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
assert read(parent/'emu001/host-state.json')['closed']
assert read(parent/'emu001/closure.json')['closed']
frozen=read(parent/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
for name in ['common.py','atomic_json.py','kernel-discovery.py','close-host.py','typed-state.py','runtime-dependencies.py','attest.py','attestation-inputs001.json','analyze-ledger.py']:
    assert (k/name).read_bytes()==(parent/name).read_bytes()
for name in ['run.py','Run.ps1','Invoke.ps1','audit.py','trace.py']:
    expected=(parent/name).read_text().replace('backend-ledger265','backend-ledger266').replace('/ledger265/runs','/ledger266/runs').replace('/ledger265/scratch','/ledger266/scratch').replace('nt5-ledger265','nt5-ledger266').replace('windows-native-ledger265','windows-native-ledger266')
    if name=='trace.py':
        expected=expected.replace("file.write_text(reply,encoding='utf-8')","file.write_bytes(reply.encode('utf-8'))").replace("command(4594,'qom-get '+path+' '+prop)==(out/manifest[0]['file']).read_text(encoding='utf-8')","command(4594,'qom-get '+path+' '+prop).encode('utf-8')==(out/manifest[0]['file']).read_bytes()")
    assert (k/name).read_text()==expected,name
assert read(k/'transport-tests001.json')['passed']
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert f['fixture_sha256']==read(parent/'emu001/fixture.json')['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
for n in ['system','software','default','sam','security']:
    assert sha(k/'emu001/artifacts'/('before-'+n))==sha(parent/'emu001/artifacts'/('before-'+n))
exe=Path('E:/Codex-archive/xbox-windows-native/ledger265-build003/xemu-ledger265.exe')
assert sha(exe)==read(parent/'renderer-build003.json')['executable_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text())
sp=importlib.util.spec_from_file_location('deps266',k/'runtime-dependencies.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
host=d.inventory();(k/'host-dependencies.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
r=dict(passed=True,guest_launched=False,physical_access=False,debugger=True,ordinary_qualified=False,
    parent_failed_attempt_preserved=True,renderer_unchanged=True,probe_driver_unchanged=True,
    host_dependencies=len(host),change='Byte-exact UTF8 page writes/rereads; new unique attempt paths only',
    retirement_ready=False,native_gpu_grant=False)
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.json']:frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('266 fresh child preflight PASS;',len(frozen),'frozen inputs')
