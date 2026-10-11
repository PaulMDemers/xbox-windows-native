"""Publish exact pending refusal predicates; no gate or operation is relaxed."""
from pathlib import Path
def apply(root):
    p=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=p.read_text()
    anchor='typedef struct X260Slot {';assert s.count(anchor)==1
    s=s.replace(anchor,Path(__file__).with_name('pending-mask.c').read_text()+'\n'+anchor)
    anchor='    unsigned state,stage,reason,stage_result,ref_count,age_count;';assert s.count(anchor)==1
    s=s.replace(anchor,anchor+'\n    unsigned pending_mask; /*263 immutable after terminal release publication */')
    old='''    if(pg->waiting_for_nop||pg->waiting_for_flip||pg->waiting_for_context_switch||
       pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE||qatomic_read(&pg->flush_pending)||
       qatomic_read(&pg->sync_pending)||qatomic_read(&r->downloads_pending)||
       qatomic_read(&r->download_dirty_surfaces_pending)||qatomic_read(&r->shader_cache_writeback_pending)){
        reason=7;goto finish;
    }'''
    new='''    v->pending_mask=x263_pending_mask(pg->waiting_for_nop,pg->waiting_for_flip,
       pg->waiting_for_context_switch,pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE,
       qatomic_read(&pg->flush_pending),qatomic_read(&pg->sync_pending),qatomic_read(&r->downloads_pending),
       qatomic_read(&r->download_dirty_surfaces_pending),qatomic_read(&r->shader_cache_writeback_pending));
    if(v->pending_mask){reason=7;goto finish;}'''
    assert s.count(old)==1;s=s.replace(old,new)
    anchor='        /* CPU copies may finish after timeout. Publish them only after acquire';assert s.count(anchor)==1
    s=s.replace(anchor,'        g_string_append_printf(out," slot%u_pending_mask=%u",n+1,v->pending_mask);\n'+anchor)
    p.write_text(s)
