/*260 opt-in host diagnostic. One allocation of metadata per emulator process;
 * four immutable epoch slots. No guest-visible register or native GPU grant.
 * Each slot is published only after actual CPU-exclusive before/after audits.
 */
#include "qemu/cutils.h"
typedef struct X260CPU {
    NV2AState *d;
    unsigned done,reason,count;
    uint64_t epoch,thread,when,rows[X260_CALLBACKS][4];
} X260CPU;
typedef struct X260Slot {
    unsigned state,stage,reason,stage_result,ref_count,age_count;
    bool old_halt;
    int64_t deadline;
    uint64_t started,finished,worker_thread;
    X259Admission admission;
    X259Ref refs[X259_MAX_REFS];
    int64_t ages[128];
    X260CPU cpu[2];
    uint64_t vertex[16][4];
    unsigned unknown_vertex,callback_result;
    uintptr_t surface,callback;
    uint32_t texture;
} X260Slot;
typedef struct X260State {
    unsigned current; /* monitor-owned, release-published once per fresh slot */
    X259RendererState renderer;
    X260Slot slots[4];
} X260State;

static void x260_cpu_audit(CPUState *cpu,run_on_cpu_data data)
{
    X260CPU *a=data.host_ptr;NV2AState *d=a->d;
    a->thread=qemu_get_thread_id();a->when=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    if(!qemu_cpu_is_self(cpu)||!cpu_in_exclusive_context(cpu)||!qatomic_read(&cpu->stopped)||
       !xwn_frontend246_closed()||!qatomic_read(&d->pfifo.halt)){a->reason=1;goto done;}
    /* This job executes AFTER earlier queued insert/remove jobs. Merely seeing
     * work_list empty on another thread would not establish this boundary. */
    if(qemu_mutex_trylock(&cpu->work_mutex)){a->reason=2;goto done;}
    bool empty=QSIMPLEQ_EMPTY(&cpu->work_list);qemu_mutex_unlock(&cpu->work_mutex);
    if(!empty){a->reason=3;goto done;}
    MemAccessCallback *cb;
    QTAILQ_FOREACH(cb,&cpu->mem_access_callbacks,entry){
        if(a->count==X260_CALLBACKS){a->reason=4;break;}
        if(!pgraph_gl_pattern260_callback_owned(d,cb)){a->reason=5;break;}
        ram_addr_t base=memory_region_get_ram_addr(d->vram);
        if(base==RAM_ADDR_INVALID||cb->addr<base){a->reason=6;break;}
        uint64_t *row=a->rows[a->count++];
        row[0]=(uintptr_t)cb;row[1]=cb->addr-base;row[2]=cb->len;row[3]=(uintptr_t)cb->opaque;
    }
done:
    qatomic_store_release(&a->done,1);
}
static bool x260_alive(NV2AState *d,X260Slot *v)
{
    return qemu_clock_get_ns(QEMU_CLOCK_REALTIME)<v->deadline &&
        !qatomic_read(&d->exiting)&&xwn_frontend246_closed()&&qatomic_read(&qemu_get_cpu(0)->stopped);
}
static bool x260_cpu_boundary(NV2AState *d,X260Slot *v,unsigned index)
{
    X260CPU *a=&v->cpu[index];a->d=d;a->epoch=2*(v->stage-1)+index+1;
    /* FIFO lock is released by every timed wait. CPU audit takes no graphics
     * lock and signals no other actor. Metadata remains alive after timeout. */
    async_safe_run_on_cpu(qemu_get_cpu(0),x260_cpu_audit,RUN_ON_CPU_HOST_PTR(a));
    while(!qatomic_load_acquire(&a->done) && x260_alive(d,v))
        qemu_cond_timedwait(&d->pfifo.fifo_cond,&d->pfifo.lock,10);
    return qatomic_load_acquire(&a->done)&&!a->reason&&x260_alive(d,v);
}
static bool x260_ref(X260Slot *v,unsigned family,uint64_t identity,uint64_t begin,uint64_t length)
{
    if(v->ref_count==X259_MAX_REFS||family>=X259_FAMILIES||!identity||!length)return false;
    v->refs[v->ref_count++]=(X259Ref){begin,length,identity,family};
    v->admission.expected[family]++;return true;
}
static bool x260_collect(NV2AState *d,X260State *c,X260Slot *v)
{
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    X259Admission *a=&v->admission;SurfaceBinding *s;unsigned walked=0,owned=0;
    bool color_found=!r->color_binding,zeta_found=!r->zeta_binding;
    a->ram_bytes=memory_region_size(d->vram);a->frame_time=pg->frame_time;
    a->producer_halted=qatomic_read(&d->pfifo.halt)==true;
    a->cpu_stopped=qatomic_read(&qemu_get_cpu(0)->stopped)==true;
    a->frontend_closed=xwn_frontend246_closed();a->worker_joined=1;
    a->pending_reports=!QSIMPLEQ_EMPTY(&r->report_queue)||r->gl_zpass_pixel_count_query_count;
    a->active_primitives=pg->primitive_mode!=PRIM_TYPE_INVALID||pg->draw_arrays_length||
        pg->inline_array_length||pg->inline_elements_length||pg->inline_buffer_length;
    a->pending_cpu_jobs=v->cpu[0].reason!=0||!qatomic_load_acquire(&v->cpu[0].done);
    QTAILQ_FOREACH(s,&r->surfaces,entry){
        if(++walked>128)return false;
        color_found|=s==r->color_binding;zeta_found|=s==r->zeta_binding;
        if(v->stage==3&&(uintptr_t)s==c->renderer.surface){
            if(s->vram_addr!=a->physical+4096||s->size!=704||
               (uintptr_t)s->access_cb!=c->renderer.callback||
               s==r->color_binding||s==r->zeta_binding)return false;
            owned++;continue;
        }
        if(v->age_count==128||!x260_ref(v,X259_SURFACE,(uintptr_t)s,s->vram_addr,s->size))return false;
        v->ages[v->age_count++]=s->frame_time;
    }
    if(owned!=(v->stage==3)||!color_found||!zeta_found)return false;
    a->complete_families|=1u<<X259_SURFACE;
    LruNode *node;walked=0;unsigned used=0;
    bool bound[NV2A_MAX_TEXTURES]={0};
    QTAILQ_FOREACH(node,&r->texture_cache.global,next_global){
        if(++walked>512)return false;
        if(!lru_is_node_in_use(&r->texture_cache,node))continue;
        used++;TextureLruNode *t=container_of(node,TextureLruNode,node);
        if(!t->binding||!t->binding->refcnt||!x260_ref(v,X259_TEXTURE,(uintptr_t)t,
            t->key.texture_vram_offset,t->key.texture_length))return false;
        if(t->key.palette_length&&!x260_ref(v,X259_PALETTE,(uintptr_t)t,
            t->key.palette_vram_offset,t->key.palette_length))return false;
        for(unsigned j=0;j<NV2A_MAX_TEXTURES;j++)if(r->texture_binding[j]==t->binding)bound[j]=true;
    }
    if(r->texture_cache.num_used<0||used!=(unsigned)r->texture_cache.num_used)return false;
    for(unsigned j=0;j<NV2A_MAX_TEXTURES;j++)if(r->texture_binding[j]&&!bound[j])return false;
    a->complete_families|=(1u<<X259_TEXTURE)|(1u<<X259_PALETTE);
    walked=used=0;
    QTAILQ_FOREACH(node,&r->element_cache.global,next_global){
        if(++walked>51200)return false;
        if(!lru_is_node_in_use(&r->element_cache,node))continue;
        used++;VertexLruNode *t=container_of(node,VertexLruNode,node);
        if(!t->initialized||!t->key.count||!t->key.stride||t->key.count>UINT64_MAX/t->key.stride||
           !x260_ref(v,X259_VERTEX,(uintptr_t)t,t->key.addr,t->key.count*t->key.stride))return false;
    }
    if(r->element_cache.num_used<0||used!=(unsigned)r->element_cache.num_used)return false;
    /* Vertex attributes backed by a full-RAM GL COPY have no recorded complete
     * draw span here. Capture the actual binding and REFUSE unknown range;
     * never pretend an empty primitive makes that ownership proof complete. */
    for(unsigned j=0;j<NV2A_VERTEXSHADER_ATTRIBUTES;j++){
        GLint enabled=0,buffer=0,stride=0;void *pointer=NULL;
        glGetVertexAttribiv(j,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
        glGetVertexAttribiv(j,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
        glGetVertexAttribiv(j,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
        glGetVertexAttribPointerv(j,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
        v->vertex[j][0]=enabled;v->vertex[j][1]=(unsigned)buffer;
        v->vertex[j][2]=stride;v->vertex[j][3]=(uintptr_t)pointer;
        if(!enabled)continue;
        bool inline_copy=buffer&&((GLuint)buffer==r->gl_inline_array_buffer);
        for(unsigned n=0;n<NV2A_VERTEXSHADER_ATTRIBUTES;n++)inline_copy|=buffer&&((GLuint)buffer==r->gl_inline_buffer[n]);
        if(!inline_copy){a->unclassified++;v->unknown_vertex++;}
    }
    if(glGetError()!=GL_NO_ERROR)return false;
    a->complete_families|=1u<<X259_VERTEX;
    /* Conservative tail reservation includes every scanout stride/interlace
     * read without guessing a pitch. Invalid start is UNKNOWN, not zero bytes. */
    if(d->pcrtc.start>=a->ram_bytes||!x260_ref(v,X259_SCANOUT,1,d->pcrtc.start,a->ram_bytes-d->pcrtc.start))return false;
    a->complete_families|=1u<<X259_SCANOUT;
    uint32_t vb=d->pvideo.regs[NV_PVIDEO_BUFFER];
    if(vb&~NV_PVIDEO_BUFFER_0_USE)return false;
    if((vb&NV_PVIDEO_BUFFER_0_USE)&&d->pvideo.regs[NV_PVIDEO_SIZE_IN]!=UINT32_MAX){
        uint64_t begin=(uint64_t)d->pvideo.regs[NV_PVIDEO_BASE]+d->pvideo.regs[NV_PVIDEO_OFFSET];
        if(begin>=a->ram_bytes||!x260_ref(v,X259_OVERLAY,1,begin,a->ram_bytes-begin))return false;
    }
    a->complete_families|=1u<<X259_OVERLAY;
    owned=0;
    for(unsigned j=0;j<v->cpu[0].count;j++){
        uint64_t *row=v->cpu[0].rows[j];
        if(v->stage==3&&row[0]==c->renderer.callback){
            if(row[1]!=a->physical+4096||row[2]!=704)return false;
            owned++;continue;
        }
        if(!x260_ref(v,X259_CALLBACK,row[0],row[1],row[2]))return false;
    }
    if(owned!=(v->stage==3))return false;
    a->complete_families|=1u<<X259_CALLBACK;a->count=v->ref_count;
    return true;
}
static bool x260_context_fence(NV2AState *d,X260Slot *v,GloContext *ctx)
{
    if(!ctx||bql_locked()||!x260_alive(d,v))return false;
    glo_set_current(ctx);if(glGetError()!=GL_NO_ERROR)return false;
    GLsync fence=glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE,0);if(!fence)return false;
    GLenum result=glClientWaitSync(fence,GL_SYNC_FLUSH_COMMANDS_BIT,100000000);
    glDeleteSync(fence);
    return glGetError()==GL_NO_ERROR&&(result==GL_ALREADY_SIGNALED||result==GL_CONDITION_SATISFIED)&&x260_alive(d,v);
}
bool pgraph_gl_pattern260_worker(NV2AState *d)
{
    X260State *c=qatomic_load_acquire(&d->pattern260);if(!c)return false;
    unsigned number=qatomic_load_acquire(&c->current);if(!number||number>4)return false;
    X260Slot *v=&c->slots[number-1];
    if(qatomic_cmpxchg(&v->state,1,2)!=1)return false;
    v->worker_thread=qemu_get_thread_id();PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0;bool locked=false;
    if(!x260_alive(d,v)||!r||bql_locked()||!d->pfifo.halt||pg->framebuffer_in_use){reason=1;goto finish;}
    if(d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]!=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]||
       (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]&(NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR))){reason=2;goto finish;}
    if(!x260_cpu_boundary(d,v,0)){reason=3;goto finish;}
    /* Both finite GL waits run with NO BQL/FIFO/PG/renderer lock held. */
    qemu_mutex_unlock(&d->pfifo.lock);
    bool render=x260_context_fence(d,v,g_nv2a_context_render);
    bool display=render&&x260_context_fence(d,v,g_nv2a_context_display);
    glo_set_current(g_nv2a_context_render);
    qemu_mutex_lock(&d->pfifo.lock);
    if(!render||!display){reason=4;goto finish;}
    v->admission.render_fenced=render;v->admission.display_fenced=display;
    if(qemu_mutex_trylock(&pg->renderer_lock)){reason=5;goto finish;}
    if(qemu_mutex_trylock(&pg->lock)){qemu_mutex_unlock(&pg->renderer_lock);reason=6;goto finish;}
    locked=true;
    if(pg->waiting_for_nop||pg->waiting_for_flip||pg->waiting_for_context_switch||
       pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE||qatomic_read(&pg->flush_pending)||
       qatomic_read(&pg->sync_pending)||qatomic_read(&r->downloads_pending)||
       qatomic_read(&r->download_dirty_surfaces_pending)||qatomic_read(&r->shader_cache_writeback_pending)){
        reason=7;goto finish;
    }
    if(!x260_collect(d,c,v)){reason=8;goto finish;}
    v->stage_result=x259_admit(&v->admission,v->refs,v->ages,v->age_count);
    if(v->stage_result){reason=9;goto finish;}
    /* No FIFO lock while publishing callbacks/TLB work. Guest/producer/UI are
     * stopped and this worker is the sole renderer, so no new graphics epoch. */
    qemu_mutex_unlock(&d->pfifo.lock);
    v->stage_result=pgraph_gl_pattern259_stage(d,&c->renderer,&v->admission,v->refs,v->ages,v->stage);
    qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);locked=false;
    qemu_mutex_lock(&d->pfifo.lock);
    if(v->stage_result){reason=10;goto finish;}
    if(!x260_cpu_boundary(d,v,1)){reason=11;goto finish;}
    v->callback_result=x260_callbacks_check(v->cpu[0].rows,v->cpu[0].count,
        v->cpu[1].rows,v->cpu[1].count,c->renderer.callback,
        v->admission.physical+4096,(uintptr_t)d,v->stage);
    if(v->callback_result)reason=12;
finish:
    if(locked){qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if(!x260_alive(d,v)&&!reason)reason=14;
    v->reason=reason;v->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    v->surface=c->renderer.surface;v->callback=c->renderer.callback;v->texture=c->renderer.texture;
    /* Failure keeps producer halted. Controller MUST quit the sacrificial
     * process; it cannot acquire another stage or recycle metadata. */
    if(!reason)qatomic_set(&d->pfifo.halt,v->old_halt);else c->renderer.failed=true;
    qatomic_store_release(&v->state,reason?6:5);return true;
}
void pgraph_gl_pattern260_request(NV2AState *d,const char *value,Error **errp)
{
    uint64_t input[8];g_auto(GStrv) parts=g_strsplit(value,",",-1);
    if(g_strv_length(parts)!=8){error_setg(errp,"260 needs stage,physical,owner,virtual,p0,p1,p2,p3");return;}
    for(unsigned i=0;i<8;i++)if(qemu_strtou64(parts[i],NULL,0,&input[i])){error_setg(errp,"260 invalid integer");return;}
    if(input[0]<1||input[0]>4||runstate_is_running()||!xwn_frontend246_closed()||
       !d->pgraph.renderer||d->pgraph.renderer->type!=CONFIG_DISPLAY_RENDERER_OPENGL||
       qatomic_load_acquire(&d->worker247.state)!=0||qatomic_load_acquire(&d->preserve227.state)!=0){error_setg(errp,"260 needs stopped CPU/closed UI/OpenGL and unused legacy actors");return;}
    X260State *c=qatomic_load_acquire(&d->pattern260);
    unsigned current=c?qatomic_load_acquire(&c->current):0;
    if(input[0]!=current+1||(current&&(qatomic_load_acquire(&c->slots[current-1].state)!=5||c->renderer.failed))){error_setg(errp,"260 fresh sequential slot required");return;}
    if(qemu_mutex_trylock(&d->pfifo.lock)){error_setg(errp,"260 FIFO busy, not accepted");return;}
    if(!c){c=g_new0(X260State,1);c->renderer.next_stage=1;qatomic_store_release(&d->pattern260,c);}
    X260Slot *v=&c->slots[current];v->stage=input[0];v->admission.physical=input[1];v->admission.owner=input[2];
    v->admission.virtual_base=input[3];for(unsigned i=0;i<4;i++)v->admission.pages[i]=input[4+i];
    /* These immutable driver-contract values must also be attested in the host
     * runtime record; arbitrary caller claims are not a qualification result. */
    v->admission.generation=1;v->admission.attempted=1;
    v->started=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);v->deadline=v->started+5000000000LL;
    v->old_halt=qatomic_read(&d->pfifo.halt);qatomic_set(&d->pfifo.halt,true);
    qatomic_store_release(&v->state,1);qatomic_store_release(&c->current,current+1);
    qemu_cond_broadcast(&d->pfifo.fifo_cond);qemu_mutex_unlock(&d->pfifo.lock);
}
char *pgraph_gl_pattern260_report(NV2AState *d)
{
    X260State *c=qatomic_load_acquire(&d->pattern260);if(!c)return g_strdup("version=260 current=0");
    unsigned current=qatomic_load_acquire(&c->current);GString *out=g_string_new(NULL);
    g_string_append_printf(out,"version=260 current=%u",current);
    for(unsigned n=0;n<current;n++){
        X260Slot *v=&c->slots[n];unsigned state=qatomic_load_acquire(&v->state);
        g_string_append_printf(out," slot%u_state=%u",n+1,state);if(state!=5&&state!=6)continue;
        g_string_append_printf(out," slot%u_result=%u slot%u_reason=%u slot%u_refs=%u slot%u_unknown_vertex=%u slot%u_worker=%"PRIu64" slot%u_surface=%"PRIuPTR" slot%u_callback=%"PRIuPTR,
            n+1,v->stage_result,n+1,v->reason,n+1,v->ref_count,n+1,v->unknown_vertex,n+1,v->worker_thread,n+1,v->surface,n+1,v->callback);
        g_string_append_printf(out," slot%u_callback_result=%u slot%u_started=%"PRIu64" slot%u_finished=%"PRIu64,
            n+1,v->callback_result,n+1,v->started,n+1,v->finished);
        /* CPU copies may finish after timeout. Publish them only after acquire
         * observes done; no mutable partial arrays escape through QOM. */
        for(unsigned i=0;i<2;i++){
            X260CPU *a=&v->cpu[i];unsigned done=qatomic_load_acquire(&a->done);
            g_string_append_printf(out," slot%u_cpu%u_done=%u",n+1,i,done);if(!done)continue;
            g_string_append_printf(out," slot%u_cpu%u_reason=%u slot%u_cpu%u_count=%u slot%u_cpu%u_thread=%"PRIu64,
                n+1,i,a->reason,n+1,i,a->count,n+1,i,a->thread);
            for(unsigned j=0;j<a->count;j++)for(unsigned z=0;z<4;z++)g_string_append_printf(out," s%u_c%u_r%u_%u=%"PRIu64,n+1,i,j,z,a->rows[j][z]);
        }
        for(unsigned j=0;j<v->ref_count;j++){
            X259Ref *ref=&v->refs[j];g_string_append_printf(out," s%u_ref%u=%u:%"PRIu64":%"PRIu64":%"PRIu64,n+1,j,ref->family,ref->identity,ref->begin,ref->length);
        }
        for(unsigned j=0;j<16;j++)for(unsigned z=0;z<4;z++)g_string_append_printf(out," s%u_vertex%u_%u=%"PRIu64,n+1,j,z,v->vertex[j][z]);
    }
    return g_string_free(out,false);
}
