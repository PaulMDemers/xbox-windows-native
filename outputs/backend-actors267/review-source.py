"""Post-build exact source check, independent of successful guest observation."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
art=Path('E:/Codex-archive/xbox-windows-native/actors267-build001')
parent=Path('E:/Codex-archive/xbox-windows-native/retirement264-source001')
n='hw/xbox/nv2a/pgraph/gl/shaders.c'
sha=lambda b:hashlib.sha256(b).hexdigest()
base=(parent/n).read_text();new=(art/'source'/n).read_text()
# Exact original full source is reconstructed by undoing only the three
# instrumented sites and the appended wrapper, never matching function names alone.
restored=new.replace((art/'inputs/actors.c').read_text()+'\n','',1)
restored=restored.replace('    binding->actor267 = NULL;\n','',1)
restored=restored.replace('    x267_create(binding->save_thread,name,shader_write_to_disk,binding,1,&binding->actor267);',
 '    qemu_thread_create(binding->save_thread, name, shader_write_to_disk, binding, QEMU_THREAD_JOINABLE);',1)
restored=restored.replace('    x267_create(&r->shader_disk_thread,"pgraph.renderer_state->shader_cache",\n                shader_reload_lru_from_disk,pg,2,&r->loader267);',
 '    qemu_thread_create(&r->shader_disk_thread, "pgraph.renderer_state->shader_cache",\n                       shader_reload_lru_from_disk, pg, QEMU_THREAD_JOINABLE);',1)
assert restored==base
assert new.count('qemu_thread_join(')==base.count('qemu_thread_join(')
for name in ['actor-core.h','actors.c','context-extra.c']:
    assert (k/name).read_bytes()==(art/'inputs'/name).read_bytes()
source=(art/'source/hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
ui=(art/'source/ui/xemu.c').read_text()
extra=(art/'inputs/context-extra.c').read_text()
assert extra in source and extra in ui
assert not any(call in extra for call in ['glDelete','glGen','glBufferData','glTexImage','glDraw','glClear','glFinish','glFlush'])
r=dict(passed=True,original_shader_source_reconstructed_exactly=True,
    normalized_original_shader_sha256=sha(base.encode()),normal_join_sites_unchanged=base.count('qemu_thread_join('),
    borrowed_sources_restored=json.loads((k/'renderer-build001.json').read_text())['borrowed_sources_restored'],
    gl_selection_only=True,scope='Original shader work functions, joins and disposal logic unchanged; instrumentation wraps exactly two creation sites',
    limitation='UI VGA owner read uses existing main-loop/BQL locking. The one-second query budget does not independently time out lock acquisition; the outer owned-run watchdog bounds the entire process.',
    physical_access=False,guest_result_not_assumed=True)
dest=k/'source-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
