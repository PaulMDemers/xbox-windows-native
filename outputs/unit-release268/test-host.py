"""Exact pinned bind/release/cache source with explicit modeled GL boundaries."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
arg=argparse.ArgumentParser();arg.add_argument('attempt');a=arg.parse_args();assert a.attempt in ['001','002','003']
out=Path('E:/Codex-archive/xbox-windows-native/unit-release268-host'+a.attempt)
assert not out.exists();out.mkdir(parents=True)
pins=json.loads((k.parent/'backend-actors267/renderer-source-pins001.json').read_text())
source=Path('E:/Codex-archive/xbox-windows-native/retirement264-source001')
sha=lambda b:hashlib.sha256(b).hexdigest()
n='hw/xbox/nv2a/pgraph/gl/texture.c';raw=(source/n).read_bytes();assert sha(raw)==pins[n]
text=raw.decode()
def function(name):
    m=re.search(r'(?m)^(?:static )?(?:void|bool) '+name+r'\([^)]*\)\s*\{',text);assert m,name
    depth=1;end=m.end()
    while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[m.start():end]
names=['texture_binding_destroy','texture_cache_entry_init','texture_cache_entry_post_evict','texture_cache_entry_compare','pgraph_gl_bind_textures']
(out/'actual-functions.h').write_text(text[:text.index('#include')]+ '\n\n'.join(function(n) for n in names)+'\n')
(out/'qemu').mkdir()
for relative,src in [('include/qemu/lru.h',source/'include/qemu/lru.h'),('include/qemu/queue.h',Path('E:/Codex-archive/xbox-windows-native/retirement264-host001/qemu/queue.h'))]:
    data=src.read_bytes();assert sha(data)==pins[relative];(out/'qemu'/src.name).write_bytes(data)
for name in ['test-rebind.c','release-core.h','proposed-release.c','test-host.py']:(out/name).write_bytes((k/name).read_bytes())
base='/mnt/e/Codex-archive/xbox-windows-native/unit-release268-host'+a.attempt
command=['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+base,base+'/test-rebind.c','-o',base+'/test']
r=dict(scope='Host original bind/cache/counting paths; modeled GL/register/VRAM interfaces, no renderer/guest integration',
    exact_function_sha256={n:sha(function(n).encode()) for n in names},texture_source_sha256=sha(raw),
    production_patch_applied=False,guest_executed=False,physical_access=False,real_gl=False,command=command)
c=subprocess.run(command,capture_output=True,timeout=60);r.update(compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'))
if c.returncode==0:
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60);r.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'))
r['passed']=r.get('test_exit')==0
r['files']={str(p.relative_to(out)):sha(p.read_bytes()) for p in out.rglob('*') if p.is_file()}
dest=k/('host-test'+a.attempt+'.json');assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['passed']
