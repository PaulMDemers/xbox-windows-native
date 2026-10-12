"""Freeze exact278 binder/destructor plus proposed279 helper in explicit GL model."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host003.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/unbound279-host003');out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=k.parent/'texture-boundary278';pins=json.loads((parent/'source-review.json').read_text())['files']
src=Path('E:/Codex-archive/xbox-windows-native/boundary278-build002/source/hw/xbox/nv2a/pgraph/gl/texture.c')
assert sha(src)==pins[str(src).replace('/','\\')] if str(src).replace('/','\\') in pins else sha(src) in pins.values()
text=src.read_text()
def function(name):
 m=re.search(r'(?m)^(?:static )?(?:void|bool) '+name+r'\([^)]*\)\s*\{',text);assert m,name
 depth=1;end=m.end()
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[m.start():end]
names=['texture_binding_destroy','texture_cache_entry_init','texture_cache_entry_post_evict','texture_cache_entry_compare','pgraph_gl_bind_textures']
(out/'actual-functions.h').write_text(text[:text.index('#include')]+'\n\n'.join(function(n) for n in names)+'\n')
(out/'qemu').mkdir()
old=Path('E:/Codex-archive/xbox-windows-native/unit-release268-host003')
prior={n.replace('\\','/'):v for n,v in json.loads((k.parent/'unit-release268/host-test003.json').read_text())['files'].items()}
for n in ['qemu/lru.h','qemu/queue.h']:
 assert sha(old/n)==prior[n];(out/n).write_bytes((old/n).read_bytes())
for n in ['release.h','proposed-release.c','test-tail.c','test-host.py']:(out/n).write_bytes((k/n).read_bytes())
(out/'admission.h').write_bytes((parent/'admission.h').read_bytes())
(out/'fixture.h').write_bytes(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/fixture.h').read_bytes())
model=(k.parent/'unit-release268/test-rebind.c').read_text().split('static unsigned scenarios,negative;')[0]
model=model.replace('#include "release-core.h"','#include "release.h"\n#include "fixture.h"')
start=model.index('static X268Edge edges[4];');end=model.index('static void setup(',start);model=model[:start]+model[end:]
model=model.replace('uint8_t bytes[64]','uint8_t bytes[512]').replace('return 64;','return 512;').replace('return 4096;','return 67108864;')
model=model.replace('i<64;i++','i<512;i++').replace('i<4096;i++','i<65536;i++').replace('offset[i]=i*256','offset[i]=i*4096+256')
model=model.replace('TextureShape){indexed,2,false,4,4}','TextureShape){indexed,2,false,16,8}')
hooks='''static unsigned event_count,inject_event,inject_gl,inject_observer,observer_error;
static unsigned pgraph_gl_reuse269_error(void){return observer_error;}
static void x269_destroying(TextureBinding *b){assert(b->refcnt);event_count++;if(event_count==inject_event){if(inject_gl)gl_error=0x502;if(inject_observer)observer_error=7;}}
static void x269_bound(NV2AState *d,unsigned unit,TextureBinding *b,unsigned path){(void)d;(void)unit;(void)b;(void)path;}
'''
model=model.replace('#include "actual-functions.h"',hooks+'#include "actual-functions.h"')
(out/'test.c').write_text(model+(k/'test-tail.c').read_text())
(out/'test-host003.py').write_bytes(Path(__file__).read_bytes())
base='/mnt/e/Codex-archive/xbox-windows-native/unbound279-host003'
r=dict(passed=False,host_only=True,release_installed=False,guest_launched=False,texture_sha256=sha(src),actual_functions=names,models=['GL objects and errors','registers/source memory','observer callback reporting','CPU/context/worker admission fixture'],actual_worker_sequencing_tested=False)
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+base,base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({x:y for x,y in r.items() if x!='files'},indent=2));assert r['passed']
