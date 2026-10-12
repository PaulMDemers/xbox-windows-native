"""Freeze exact actual source hooks; compile original functions in explicit models."""
import hashlib,json,subprocess,sys,traceback
from pathlib import Path
import instrument
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt.isdecimal()
dest=k/('host'+attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/hooks286-host'+attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/source/hw/xbox/nv2a/pgraph/gl/texture.c')
assert sha(source) in json.loads((k.parent/'release-runtime281/source-review.json').read_text())['files'].values()
for n in ['adapter.h','instrument.py','test-tail.c','test-host.py']:(out/n).write_bytes((k/n).read_bytes())
for n,kit in [('publication.h','owner-publication285'),('lifetime.h','replacement-life284')]:
 (out/n).write_bytes((k.parent/kit/n).read_bytes())
old=Path('E:/Codex-archive/xbox-windows-native/cache283-host003');prior=json.loads((k.parent/'cache-disposal283/host003.json').read_text())['files']
for n in ['qemu/lru.h','qemu/queue.h','release.h','fixture.h','admission.h','proposed-release.c','test.c']:
 assert sha(old/n)==prior[n]
 if n=='test.c':continue
 p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((old/n).read_bytes())
r=dict(passed=False,host_only=True,renderer_built=False,guest_launched=False,shared_source_changed=False,
 source_sha256=sha(source),models=['GL operations/source registers/generate_texture upload','owner identity and active observer lookup','arm/proof/worker context are test fixtures, not actual runtime providers'])
try:
 text=source.read_text();patched,changes=instrument.instrument(text)
 (out/'original-texture.c').write_bytes(source.read_bytes());(out/'instrumented-texture.c').write_bytes(patched.encode())
 names=['texture_binding_destroy','texture_cache_entry_init','texture_cache_entry_post_evict','texture_cache_entry_compare','pgraph_gl_bind_textures']
 (out/'actual-functions.h').write_bytes((text[:text.index('#include')]+'\n\n'.join(instrument.function(patched,n) for n in names)+'\n').encode())
 model=(old/'test.c').read_text().split('\n#include "boundary.h"')[0]
 model=model.replace('#include "actual-functions.h"','''static unsigned thread286=123;
static unsigned qemu_get_thread_id(void){return thread286;}
#include "adapter.h"
static P285 *active285;
static P285 *x286_active(void){return active285;}
#include "actual-functions.h"''')
 # Assert before the actual host free that no completed-free event was emitted.
 model=model.replace('static void g_free(void *p) {assert(p);frees++;free(p);}',
  'static void before_free286(void *p);\nstatic void g_free(void *p) {assert(p);before_free286(p);frees++;free(p);}')
 model+='''
static void before_free286(void *p) {
 if(!active285 || atomic_load(&active285->terminal))return;
 for(unsigned i=0;i<4;i++)if(active285->core.unit[i].old_identity==(uint64_t)(uintptr_t)p && active285->core.unit[i].old_refs)
  assert(!active285->core.unit[i].old_free);
}
'''+(k/'test-tail.c').read_text()
 (out/'test.c').write_bytes(model.encode());base='/mnt/e/Codex-archive/xbox-windows-native/hooks286-host'+attempt
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+base,base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 r.update(passed=True,original_source_reconstructed=True,hook_replacement_sites=len(changes),actual_original_functions=names)
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
r['files']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
