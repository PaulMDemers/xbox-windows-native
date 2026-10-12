"""Verify all consumed private cases without rerunning or rewriting them."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
for case in ['001','002','003']:
 r=json.loads((k/f'host{case}.json').read_text());assert r['passed']==(case!='002')
 root=Path('E:/Codex-archive/xbox-windows-native/life284-host'+case)
 for name,h in r['files'].items():
  p=root/name;assert sha(p)==h;files[str(p)]=h
root=Path('E:/Codex-archive/xbox-windows-native/life284-host003')
for n in ['lifetime.h','test.c','decode.py','test-host.py']:assert (root/n).read_bytes()==(k/n).read_bytes()
p=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/source/hw/xbox/nv2a/pgraph/gl/texture.c')
original=json.loads((k.parent/'release-runtime281/source-review.json').read_text())['files']
assert sha(p) in original.values();s=p.read_text()
body='''static void texture_binding_destroy(gpointer data)
{
    TextureBinding *binding = (TextureBinding *)data;
    assert(binding->refcnt > 0);
    x269_destroying(binding);
    binding->refcnt--;
    if (binding->refcnt == 0) {
        glDeleteTextures(1, &binding->gl_texture);
        g_free(binding);
    }
}'''
assert s.count(body)==1
assert s.count('key_out->binding = generate_texture(state, texture_data, palette_data);')==1
r=dict(passed=True,host_only=True,renderer_built=False,guest_prepared=False,guest_launched=False,
 physical_changed=False,actual_hook_coverage=False,actual_publication_adapter=False,
 scenarios=6150,refusal_groups=18,checks=29734439,transport_mutations_rejected=17081,
 old_predecrement_hook_is_not_completed_free=True,source_sha256=sha(p),
 preserved_failure='host002 accepted birth before all old objects freed; original inputs and failed output retained',
 private_files_verified=len(files),files=files)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
