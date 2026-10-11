"""Fresh244 byte/source/actor review before its sole owned guest run."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
b=read(k/'build004.json');assert b['passed'] and b['borrowed_sources_restored']
assert read(k/'build001.json')['borrowed_sources_restored'] and not read(k/'build001.json')['passed']
assert read(k/'build002.json')['borrowed_sources_restored'] and not read(k/'build002.json')['passed']
assert read(k/'build003.json')['passed'] and read(k/'build003.json')['borrowed_sources_restored']
assert not (k/'build003.json').is_relative_to(k/'preserve001')
src=k/'artifacts/build004/source';old=k.parent/'gpu-reference-pair242/artifacts/build004/source'
for name in ['hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h']:assert sha(src/name)==sha(old/name)
expected=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/display.c','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/pgraph.c','hw/xbox/nv2a/trace-events','system/physmem.c','system/trace-events','ui/xemu.c']
assert sorted(b['changed_sources'])==sorted(expected)
phy=(src/'system/physmem.c').read_text();a=phy.index('static void do_mem_access_callback_remove_by_ref');z=phy.index('void mem_access_callback_remove_by_ref',a+10);body=phy[a:z]
assert body.index('QTAILQ_REMOVE')<body.index('trace_xwn_mem_callback244(4,')<body.index('g_free(cb)')<body.index('trace_xwn_mem_callback244(5,')
assert body[body.index('g_free(cb)'):].count('cb->')==0 and 'qatomic_read(&cpu->stopped)' in body
assert body.count('QTAILQ_REMOVE')==body.count('g_free(cb)')==1
ui=(src/'ui/xemu.c').read_text();a=ui.index('static void gl_render_frame');z=ui.index('static bool event_watch_callback',a);body=ui[a:z]
assert body.index('glFinish()')<body.index('trace_nv2a_lifecycle244(31,')<body.index('nv2a_release_framebuffer_surface()')<body.index('trace_nv2a_lifecycle244(32,')
assert body.count('glFinish()')==1 and body.count('nv2a_release_framebuffer_surface()')==1
for name in ['pair-test001','guard-test003','connection-test001','host-close-test001','lifecycle-test001']:assert read(k/(name+'.json'))['passed']
assert read(k/'lifecycle-test001.json')['parser_sha256']==sha(k/'lifecycle.py')
assert read(k/'pair-test001.json')['actual_trace_source_sha256']==sha(k/'trace.py')
trace=(k/'trace.py').read_text();assert trace.count('xwn-lifecycle244-mark true')==2 and trace.count('SITE EXEC')==1
assert trace.count("qom-set '+path+' xwn-preserve227 true")==1 and "capture('after-preservation')" not in trace and "Qqemu.PhyMemMode:1" not in trace
assert 'time.sleep(.2)' in trace and "'trace-event '+event+' off'" in trace
f=read(k/'fixture-preserve001.json');prior=read(k.parent/'gpu-reference-pair243/fixture-preserve001.json')
assert f['files']==prior['files'] and f['protected']==prior['protected'] and not f['inherited_null_policy']
assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']==prior['seed_sha256']
assert sha(k/'artifacts/build004/xemu-lifecycle244.exe')==b['executable_sha256']
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase244-runs/nt5-phase244-preserve001')
assert not run.exists() and not (k/'preserve001/runner-start.json').exists() and not (k/'preserve001/host-state.json').exists()
assert shutil.disk_usage('C:/').free-b['executable_bytes']-32*1024**2>=20*1024**3
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
dest.write_text(json.dumps(dict(passed=True,fresh_case='preserve001',executable_sha256=b['executable_sha256'],source_sha256=sha(Path(__file__)),frozen_pins=len(read(k/'emulator-frozen.json')),observation_only=True,physical_access=False,guest_launch=False,native_gpu_ownership=False),indent=2)+'\n')
print('244 actual compiled observation/unchanged driver/actor and fresh-ID review PASS')
