"""Compiled247 source, exact parent, frozen fresh fixture and once-only guards."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
b=read(k/'build004.json');assert b['passed'] and b['borrowed_sources_restored']
src=k/'artifacts/build004/source';parent=k.parent/'frontend-close246/artifacts/build001/source'
changed=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/nv2a.h','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c','ui/xemu.c'];assert sorted(b['changed_sources'])==sorted(changed)
for n in ['hw/xbox/nv2a/pgraph/gl/display.c','hw/xbox/nv2a/pgraph/pgraph.c','system/physmem.c','hw/xbox/nv2a/pgraph/gl/renderer.h']:assert sha(src/n)==sha(parent/n),n
assert (k.parent/'worker-barrier247/worker.c').read_text() in (src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
assert 'G_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);' in (src/'hw/xbox/nv2a/nv2a_int.h').read_text()
for name in ['pair-test002','guard-test004','connection-test001','host-close-test001','lifecycle-test002','closed-test001']:assert read(k/(name+'.json'))['passed']
assert read(k.parent/'worker-barrier247/worker-test003.json')['renderer_sha256']==sha(src/'hw/xbox/nv2a/pgraph/gl/renderer.c')
trace=(k/'trace.py').read_text();assert trace.count('SITE EXEC')==1 and trace.count('xwn-worker247-close true')==1 and trace.count('xwn-worker247-close false')==2
assert "assert r['frontend_closed_reread']==r['frontend_closed_report']" in trace and "assert r['frontend_closed_reread']==reply" not in trace
assert read(k/'worker-proof001.json')['passed'] and read(k.parent/'worker-barrier247/worker-test003.json')['passed']
assert trace.index("r['worker_scope_passed']=True")<trace.index("reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close false')")
assert 'worker_failure_released_or_refused' in trace and 'Qqemu.PhyMemMode:1' not in trace
f=read(k/'fixture-preserve001.json');old=read(k.parent/'frontend-close246/fixture-preserve001.json');assert f['files']==old['files'] and f['protected']==old['protected'] and not f['inherited_null_policy']
assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
for row in read(k/'baseline-inputs001.json')['files']:assert sha(ws/row['path'])==row['sha256']
assert sha(src.parent/'xemu-worker247.exe')==b['executable_sha256']
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase248-runs/nt5-phase248-preserve001');assert not run.exists() and not (k/'preserve001/runner-start.json').exists()
assert shutil.disk_usage('C:/').free-b['executable_bytes']-32*1024**2>=20*1024**3
for p in k.glob('*.py'):ast.parse(p.read_text())
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),frozen_pins=len(read(k/'emulator-frozen.json')),executable_sha256=b['executable_sha256'],physical_access=False,guest_launch=False,scope='One-shot finite worker/UI barrier, retained references, no native permit'),indent=2)+'\n')
print('247 compiled source/fresh fixture/capacity/once-only review PASS')
