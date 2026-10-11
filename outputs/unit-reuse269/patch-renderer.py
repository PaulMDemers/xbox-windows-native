"""Observation-only child of exact267; do not install the268 release helper."""
from pathlib import Path
k=Path(__file__).resolve().parent
def replace(p,old,new):
    t=p.read_text();assert t.count(old)==1,(str(p),old);p.write_text(t.replace(old,new))
def apply(root):
    gl=root/'hw/xbox/nv2a/pgraph/gl'
    replace(gl/'renderer.h','void pgraph_gl_bind_textures(NV2AState *d);','void pgraph_gl_bind_textures(NV2AState *d);\nbool pgraph_gl_reuse269_arm(NV2AState *d);\nunsigned pgraph_gl_reuse269_error(void);\nbool pgraph_gl_reuse269_seal(void);')
    anchor='static TextureBinding* generate_texture(const TextureShape s, const uint8_t *texture_data, const uint8_t *palette_data);'
    replace(gl/'texture.c',anchor,(k/'watch.c').read_text()+'\n'+anchor)
    replace(gl/'texture.c','                                         max_anisotropy);\n                continue;',
        '                                         max_anisotropy);\n                x269_bound(d,i,r->texture_binding[i],1);\n                continue;')
    replace(gl/'texture.c','        pg->texture_dirty[i] = false;','        pg->texture_dirty[i] = false;\n        x269_bound(d,i,binding,2);')
    replace(gl/'texture.c','    assert(binding->refcnt > 0);','    assert(binding->refcnt > 0);\n    x269_destroying(binding);')
    replace(gl/'renderer.c','    if (!context_ok) {reason=9;goto finish;}','''    if (!context_ok) {reason=9;goto finish;}
    /*269 Watch only after the immutable graph and context observations. */
    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count ||
        !pgraph_gl_reuse269_arm(d)) {reason=14;goto finish;}''')
    replace(gl/'renderer.c','pending=%u native_grant=0 retirement=0",','pending=%u native_grant=0 retirement=0 reuse269_error=%u",')
    replace(gl/'renderer.c','cpu1,cpu1?v->cpu[1].reason:UINT_MAX,v->pending_mask);','cpu1,cpu1?v->cpu[1].reason:UINT_MAX,v->pending_mask,pgraph_gl_reuse269_error());')
    anchor='void pgraph_gl_ledger265_request(NV2AState *d,const char *value,Error **errp)\n{'
    replace(gl/'renderer.c',anchor,anchor+'''
    /*269 One-way observation seal; does not reset any existing actor. */
    if (!strcmp(value,"seal269")) {
        X265State *s=qatomic_load_acquire(&d->ledger265);
        if (runstate_is_running() || !s || qatomic_load_acquire(&s->boundary.state)!=5 ||
            !pgraph_gl_reuse269_seal()) error_setg(errp,"269 seal requires stopped CPU and completed observer entry");
        return;
    }''')
