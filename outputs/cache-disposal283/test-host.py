"""Freeze original281 normal functions and new helper in explicit GL/owner models."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt.isdecimal()
dest=k/('host'+attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/cache283-host'+attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/source/hw/xbox/nv2a/pgraph/gl/texture.c')
pins=json.loads((k.parent/'release-runtime281/source-review.json').read_text())['files'];assert sha(source) in pins.values()
text=source.read_text()
def function(name):
 m=re.search(r'(?m)^(?:static )?(?:void|bool) '+name+r'\([^)]*\)\s*\{',text);assert m,name
 depth=1;end=m.end()
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[m.start():end]
names=['texture_binding_destroy','texture_cache_entry_init','texture_cache_entry_post_evict','texture_cache_entry_compare','pgraph_gl_bind_textures']
(out/'actual-functions.h').write_bytes((text[:text.index('#include')]+'\n\n'.join(function(n) for n in names)+'\n').encode())
old=Path('E:/Codex-archive/xbox-windows-native/unbound279-host003');prior=json.loads((k.parent/'unbound-release279/host003.json').read_text())['files']
prior={n.replace('\\','/'):h for n,h in prior.items()}
for name in ['qemu/lru.h','qemu/queue.h','admission.h','release.h','fixture.h','proposed-release.c','test.c']:
 assert sha(old/name)==prior[name]
 if name=='test.c':continue
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((old/name).read_bytes())
(out/'boundary.h').write_bytes((k.parent/'release-worker280/boundary.h').read_bytes())
for name in ['disposal.h','proposed-disposal.c','test-tail.c','test-host.py']:(out/name).write_bytes((k/name).read_bytes())
model=(old/'test.c').read_text().split('static unsigned scenarios,refusals,quarantines;')[0]
model=model.replace('static unsigned active,','static unsigned ignore_name,event_refs[64];\nstatic unsigned active,')
model=model.replace('objects[*names].alive=false;deletes++;','if(*names==ignore_name)return;objects[*names].alive=false;deletes++;')
model=model.replace('assert(b->refcnt);event_count++;','assert(b->refcnt);assert(event_count<64);event_refs[event_count]=b->refcnt;event_count++;')
model=model.replace('#include "actual-functions.h"','static bool glIsTexture(unsigned name){return name<8192 && objects[name].alive;}\n#include "actual-functions.h"')
code=model+'\n#include "boundary.h"\n#include "disposal.h"\n#include "proposed-disposal.c"\n'+(k/'test-tail.c').read_text()
(out/'test.c').write_bytes(code.encode());base='/mnt/e/Codex-archive/xbox-windows-native/cache283-host'+attempt
r=dict(passed=False,host_only=True,guest_launched=False,release_or_disposal_installed=False,texture_sha256=sha(source),actual_functions=names,models=['GL namespace/pixels/errors','registers and source memory','observer events/final-free reporting','CPU/context/graph proof fixture; no actual runtime provider or worker'])
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+base,base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
