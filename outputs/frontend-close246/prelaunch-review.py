"""Fresh246 actual source/capacity/one-shot protocol review before launch."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored']
src=k/'artifacts/build001/source';prior=k.parent/'gpu-lifecycle244/artifacts/build005/source'
changed=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a.h','hw/xbox/nv2a/pgraph/pgraph.c','ui/xemu.c'];assert sorted(b['changed_sources'])==sorted(changed)
for n in ['hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/display.c','system/physmem.c','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h']:assert sha(src/n)==sha(prior/n),n
ui=(src/'ui/xemu.c').read_text();assert (k/'frontend.c').read_text() in ui
assert ui.index('if (frontend246_gate(scon))')<ui.index('GLuint tex = nv2a_get_framebuffer_surface();')
assert 'G_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);' in (src/'hw/xbox/nv2a/nv2a_int.h').read_text()
for name in ['frontend-test002','pair-test002','guard-test004','connection-test001','host-close-test001','lifecycle-test002','closed-test001']:assert read(k/(name+'.json'))['passed']
assert read(k/'frontend-test002.json')['actual_ui_sha256']==sha(src/'ui/xemu.c')
trace=(k/'trace.py').read_text();assert trace.count('SITE EXEC')==1 and trace.count('xwn-frontend246-close true')==1 and trace.count('xwn-frontend246-close false')==2
assert 'Qqemu.PhyMemMode:1' not in trace and 'frontend_failure_reopen_reply' in trace
f=read(k/'fixture-preserve001.json');old=read(k.parent/'gpu-lifecycle245/fixture-preserve001.json');assert f['files']==old['files'] and f['protected']==old['protected'] and not f['inherited_null_policy']
assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
for row in read(k/'baseline-inputs001.json')['files']:assert sha(ws/row['path'])==row['sha256']
assert sha(src.parent/'xemu-frontend246.exe')==b['executable_sha256']
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase246-runs/nt5-phase246-preserve001');assert not run.exists() and not (k/'preserve001/runner-start.json').exists()
assert shutil.disk_usage('C:/').free-b['executable_bytes']-32*1024**2>=20*1024**3
for p in k.glob('*.py'):ast.parse(p.read_text())
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),frozen_pins=len(read(k/'emulator-frozen.json')),executable_sha256=b['executable_sha256'],frontend_scope='One-shot UI close/reopen, no shared-context disposal or native ownership',physical_access=False,guest_launch=False),indent=2)+'\n')
print('246 actual compiled one-shot UI gate/fresh inputs/capacity review PASS')
