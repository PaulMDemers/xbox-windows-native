/* Actual transaction body, with explicit CPU/GL/graph/lock models. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define qatomic_load_acquire(p) (*(p))
#define qatomic_store_release(p,v) (*(p)=(v))
#define qatomic_read(p) (*(p))
#define qatomic_set(p,v) (*(p)=(v))
#define qatomic_cmpxchg(p,a,b) compare((p),(a),(b))
static unsigned compare(unsigned *p,unsigned a,unsigned b){unsigned old=*p;if(old==a)*p=b;return old;}
enum {QEMU_CLOCK_REALTIME,PRIM_TYPE_INVALID=99,NV_PFIFO_CACHE1_DMA_GET=0,NV_PFIFO_CACHE1_DMA_PUT=1,NV_PFIFO_CACHE1_DMA_STATE=2};
#define NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT 0x10
#define NV_PFIFO_CACHE1_DMA_STATE_ERROR 0x20
#define PGRAPH_RENDERER_SWITCH_PHASE_IDLE 0
#define QSIMPLEQ_EMPTY(p) (!*(p))
typedef struct {unsigned locked,id;} Lock;
typedef struct {uint64_t thread,epoch,when;unsigned done,reason,count;uint64_t rows[4][4];} CPU;
typedef struct {unsigned state,stage,reason,old_halt,pending_mask;uint64_t worker_thread,started,finished,deadline;CPU cpu[2];struct {unsigned render_fenced,display_fenced;} admission;} X260Slot;
typedef struct {uint64_t storage[64][8];uint64_t (*rows)[8];unsigned count,overflow;} Rows;
typedef struct X265State {X260Slot boundary;Rows ledger;unsigned accounting_error,shader_jobs_unknown,contexts274,seal274;struct X265State *end274;} X265State;
typedef struct {unsigned downloads_pending,download_dirty_surfaces_pending,shader_cache_writeback_pending,report_queue,gl_zpass_pixel_count_query_count;} PGRAPHGLState;
typedef struct {Lock renderer_lock,lock;PGRAPHGLState *gl_renderer_state;unsigned framebuffer_in_use,waiting_for_nop,waiting_for_flip,waiting_for_context_switch,renderer_switch_phase,flush_pending,sync_pending,primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length;} PGRAPHState;
typedef struct {X265State *ledger265;PGRAPHState pgraph;struct{Lock lock;unsigned halt,regs[3];} pfifo;} NV2AState;
typedef unsigned GloContext;
static GloContext render_context=1,display_context=2;
static GloContext *g_nv2a_context_render=&render_context,*g_nv2a_context_display=&display_context;
static NV2AState device;static X265State initial,ending;static PGRAPHGLState renderer;
static unsigned fault,seal_calls,arm_calls,cpu_calls,fences,current_context,enabled;
enum {BAD_OWNER=1,BAD_CPU0,BAD_CPU1,BAD_RENDER,BAD_DISPLAY,BAD_LOCK1,BAD_LOCK2,
    BAD_COLLECT,BAD_QUERY,BAD_CONTEXT,BAD_SHADER,BAD_ACCOUNTS,BAD_CALLBACKS,
    BAD_RESTORE,BAD_SEAL,BAD_ERROR,BAD_DEADLINE,BAD_CHANGED_CONTEXT,BAD_LATE_LOCK1,
    BAD_LATE_LOCK2,BAD_GET,BAD_PENDING,BAD_INVENTORY};
static uint64_t qemu_get_thread_id(void){return fault==BAD_OWNER?92:91;}
static uint64_t qemu_clock_get_ns(unsigned c){(void)c;return 17;}
static bool bql_locked(void){return false;}
static bool x260_alive(NV2AState *d,X260Slot *v){(void)d;(void)v;return !(fault==BAD_DEADLINE&&seal_calls);}
static unsigned renderer_attempts,pg_attempts;
static int qemu_mutex_trylock(Lock *l){
    if(l->id==2){renderer_attempts++;if((fault==BAD_LOCK1&&renderer_attempts==1)||(fault==BAD_LATE_LOCK1&&renderer_attempts==2))return 1;}
    if(l->id==3){pg_attempts++;if((fault==BAD_LOCK2&&pg_attempts==1)||(fault==BAD_LATE_LOCK2&&pg_attempts==2))return 1;}
    assert(!l->locked);l->locked=1;return 0;
}
static void qemu_mutex_lock(Lock *l){assert(!l->locked);l->locked=1;}
static void qemu_mutex_unlock(Lock *l){assert(l->locked);l->locked=0;}
static bool x260_cpu_boundary(NV2AState *d,X260Slot *v,unsigned index){
    assert(d->pfifo.lock.locked&&!d->pgraph.lock.locked&&!d->pgraph.renderer_lock.locked);cpu_calls++;
    if((index==0&&fault==BAD_CPU0)||(index==1&&fault==BAD_CPU1))return false;
    v->cpu[index].done=1;v->cpu[index].thread=77;v->cpu[index].epoch=2*(v->stage-1)+index+1;
    v->cpu[index].count=(fault==BAD_CALLBACKS&&index==0)||(fault==BAD_INVENTORY&&index==1);
    return true;
}
static void glo_set_current(GloContext *c){current_context=*c;}
static bool x260_context_fence(NV2AState *d,X260Slot *v,GloContext *c){
    (void)v;assert(!d->pfifo.lock.locked&&!d->pgraph.lock.locked&&!d->pgraph.renderer_lock.locked);fences++;current_context=*c;
    return !((*c==1&&fault==BAD_RENDER)||(*c==2&&fault==BAD_DISPLAY));
}
static unsigned x263_pending_mask(unsigned a,unsigned b,unsigned c,unsigned e,unsigned f,unsigned g,unsigned h,unsigned i,unsigned j){return a|b|c|e|f|g|h|i|j;}
static bool pgraph_gl_reuse274_ready(uint64_t owner){return owner==91&&enabled;}
static unsigned pgraph_gl_reuse269_error(void){return fault==BAD_ERROR;}
static bool pgraph_gl_reuse269_seal(void){
    assert(!device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
    seal_calls++;enabled=0;return fault!=BAD_SEAL;
}
static bool pgraph_gl_reuse269_arm(NV2AState *d){(void)d;arm_calls++;return true;}
static bool x265_add(Rows *r,uint64_t k,uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g){
    assert(r->count<64);uint64_t row[8]={k,a,b,c,d,e,f,g};memcpy(r->rows[r->count++],row,sizeof(row));return true;
}
static bool x265_collect(NV2AState *d,X265State *s){
    assert(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
    s->accounting_error=fault==BAD_ACCOUNTS;s->shader_jobs_unknown=fault==BAD_SHADER;return fault!=BAD_COLLECT;
}
static bool x265_context(Rows *r,unsigned role,uint64_t deadline){(void)r;(void)deadline;assert(current_context==role);return fault!=BAD_QUERY;}
static bool x267_context(Rows *r,PGRAPHGLState *state,unsigned role,uint64_t deadline){
    (void)state;(void)deadline;assert(current_context==role);
    x265_add(r,51,role,100+role,200+role,200+role,300+role,300+role,fault==BAD_CHANGED_CONTEXT?0:1);
    return fault!=BAD_CONTEXT;
}
static bool glo_context_observe267(GloContext *ctx,uintptr_t actual[4]){(void)actual;return *ctx==1&&current_context==1&&fault!=BAD_RESTORE;}
/* INSERT_ACTUAL_FUNCTIONS */
static void setup(unsigned failure){
    fault=failure;seal_calls=arm_calls=cpu_calls=fences=renderer_attempts=pg_attempts=0;enabled=1;current_context=1;
    memset(&initial,0,sizeof(initial));memset(&ending,0,sizeof(ending));memset(&device,0,sizeof(device));memset(&renderer,0,sizeof(renderer));
    device.ledger265=&initial;device.pgraph.gl_renderer_state=&renderer;
    device.pfifo.lock=(Lock){1,1};device.pgraph.renderer_lock.id=2;device.pgraph.lock.id=3;
    device.pfifo.halt=1;device.pgraph.primitive_mode=PRIM_TYPE_INVALID;
    initial.boundary.state=5;initial.boundary.worker_thread=91;initial.end274=&ending;
    initial.ledger.rows=initial.ledger.storage;ending.ledger.rows=ending.ledger.storage;
    x267_context(&initial.ledger,&renderer,1,100);current_context=2;x267_context(&initial.ledger,&renderer,2,100);current_context=1;
    /* Initial graph predates fault injection at the end capture. */
    initial.ledger.rows[0][7]=initial.ledger.rows[1][7]=1;
    ending.boundary.state=1;ending.boundary.stage=2;ending.boundary.old_halt=0;
    if(failure==BAD_GET)device.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]=4;
    if(failure==BAD_PENDING)device.pgraph.flush_pending=1;
}
int main(void){
    unsigned cases=0;
    for(unsigned f=0;f<=BAD_INVENTORY;f++){
        setup(f);Rows original=initial.ledger;
        assert(pgraph_gl_ledger265_worker(&device));
        assert(device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
        assert(!arm_calls&&!memcmp(&initial.ledger,&original,sizeof(original)));
        assert(ending.boundary.state==(f?6:5));
        if(!f){assert(seal_calls==1&&cpu_calls==2&&fences==2&&!device.pfifo.halt&&ending.seal274&&ending.contexts274);}
        else{assert(ending.boundary.reason&&device.pfifo.halt);}
        unsigned old_seals=seal_calls,old_cpu=cpu_calls;
        assert(!pgraph_gl_ledger265_worker(&device));assert(seal_calls==old_seals&&cpu_calls==old_cpu);
        cases++;
    }
    printf("PASS %u actual end-worker paths; locks balanced, original immutable, failure quarantine, no rearm/repeat; CPU/GL modeled\n",cases);
}
