"""Add an exact refusal discriminator to227; no predicate relaxation."""
def replace(s,a,b):
 assert s.count(a)==1,a[:80]
 return s.replace(a,b)
def apply(root):
 n='hw/xbox/nv2a/nv2a_int.h';s=(root/n).read_text();s=replace(s,'unsigned state, surfaces, dirty, downloaded, error;','unsigned state, surfaces, dirty, downloaded, error, reason;');(root/n).write_text(s)
 n='hw/xbox/nv2a/nv2a.c';s=(root/n).read_text()
 s=replace(s,'" error=%u references_retired=0 native_grant=0",','" error=%u reason=%u references_retired=0 native_grant=0",')
 s=replace(s,'qatomic_read(&d->preserve227.bytes), qatomic_read(&d->preserve227.error));','qatomic_read(&d->preserve227.bytes), qatomic_read(&d->preserve227.error),\n        qatomic_read(&d->preserve227.reason));');(root/n).write_text(s)
 n='hw/xbox/nv2a/pgraph/gl/renderer.c';s=(root/n).read_text()
 s=replace(s,'        bool frontend_locked = !qemu_mutex_trylock(&pg->renderer_lock);','''        bool frontend_locked = !qemu_mutex_trylock(&pg->renderer_lock);
        if (!frontend_locked) { qatomic_set(&d->preserve227.reason, 2); }''')
 s=replace(s,'            if (queue_empty &&','''            if (!queue_empty) { qatomic_set(&d->preserve227.reason, 1); }
            if (queue_empty &&''');(root/n).write_text(s)
 n='hw/xbox/nv2a/pgraph/gl/surface.c';s=(root/n).read_text()
 a='''    if (pg->primitive_mode != PRIM_TYPE_INVALID || pg->draw_arrays_length ||
        pg->inline_array_length || pg->inline_elements_length ||
        pg->inline_buffer_length || pg->framebuffer_in_use ||
        pg->waiting_for_nop || pg->waiting_for_flip ||
        pg->waiting_for_context_switch || pg->flush_pending || pg->sync_pending) {
        return 4;
    }'''
 b='''    unsigned reason =
        pg->primitive_mode != PRIM_TYPE_INVALID ? 3 :
        pg->draw_arrays_length ? 4 : pg->inline_array_length ? 5 :
        pg->inline_elements_length ? 6 : pg->inline_buffer_length ? 7 :
        pg->framebuffer_in_use ? 8 : pg->waiting_for_nop ? 9 :
        pg->waiting_for_flip ? 10 : pg->waiting_for_context_switch ? 11 :
        pg->flush_pending ? 12 : pg->sync_pending ? 13 : 0;
    if (reason) { qatomic_set(&d->preserve227.reason, reason);return 4; }'''
 s=replace(s,a,b)
 s=replace(s,'s->size > memory_region_size(d->vram) - s->vram_addr) { return 4; }','s->size > memory_region_size(d->vram) - s->vram_addr) { qatomic_set(&d->preserve227.reason, 14);return 4; }')
 s=replace(s,'other->vram_addr < s->vram_addr + s->size) { return 4; }','other->vram_addr < s->vram_addr + s->size) { qatomic_set(&d->preserve227.reason, 15);return 4; }');(root/n).write_text(s)
