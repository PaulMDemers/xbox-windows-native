/* Exact new worker and scalar adapter with explicit GL/job/live-graph models. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "admission.h"
#include "fixture.h"
#define qatomic_load_acquire(p) (*(p))
#define qatomic_store_release(p,v) (*(p)=(v))
#define qatomic_read(p) (*(p))
#define qatomic_set(p,v) (*(p)=(v))
#define qatomic_cmpxchg(p,a,b) compare((p),(a),(b))
static unsigned compare(unsigned *p,unsigned a,unsigned b){unsigned old=*p;if(old==a)*p=b;return old;}
enum {QEMU_CLOCK_REALTIME,PRIM_TYPE_INVALID=99,NV_PFIFO_CACHE1_DMA_GET=0,NV_PFIFO_CACHE1_DMA_PUT=1,NV_PFIFO_CACHE1_DMA_STATE=2};
#define NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT 0x10
#define NV_PFIFO_CACHE1_DMA_STATE_ERROR 0x20
#define QSIMPLEQ_EMPTY(p) (!*(p))
typedef struct {unsigned locked,id;} Lock;
typedef struct {uint64_t epoch,thread,when,clock278,rows[128][4],detail276[128][3];unsigned done,reason,count,clock_error278;} X260CPU;
typedef struct {unsigned state,stage,reason,old_halt,pending_mask;uint64_t worker_thread,started,finished,deadline;X260CPU cpu[2];struct{unsigned render_fenced,display_fenced;} admission;} X260Slot;
typedef struct {uint64_t storage[2048][8];uint64_t (*rows)[8];unsigned count,overflow;} X265Rows;
typedef struct X265State {X260Slot boundary;X265Rows ledger;unsigned accounting_error,shader_jobs_unknown,contexts274,seal274,admission278;bool textures278;uint64_t allocations278[4];X277Proof proof278;struct X265State *end274;} X265State;
typedef struct {unsigned report_queue,gl_zpass_pixel_count_query_count;} PGRAPHGLState;
typedef struct {Lock renderer_lock,lock;PGRAPHGLState *gl_renderer_state;unsigned framebuffer_in_use,primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length;} PGRAPHState;
typedef struct {X265State *ledger265;PGRAPHState pgraph;void *vram;struct{Lock lock;unsigned halt,regs[3];} pfifo;} NV2AState;
typedef unsigned GloContext;
static GloContext rc=1,dc=2,*g_nv2a_context_render=&rc,*g_nv2a_context_display=&dc;
static struct{unsigned stopped;} cpu={1};
#define qemu_get_cpu(i) ((void)(i),&cpu)
static NV2AState device;static PGRAPHGLState renderer;static X265State initial,ending;
static unsigned fault,cpu_calls,fences,graph_calls,validate_calls,arm_calls,seal_calls,enabled,current;
static unsigned attempts[4],checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
enum {F_CPU0=1,F_CPU1,F_RENDER,F_DISPLAY,F_LOCK1,F_LOCK2,F_LATE1,F_LATE2,
 F_COLLECT,F_GRAPH0,F_GRAPH1,F_QUERY,F_CONTEXT,F_ACCT,F_SHADER,F_GET,F_PENDING,
 F_CLOCK,F_CPU_TUPLE,F_GRAPH_CHANGE,F_CTX_MATCH,F_ACTUAL_CTX,F_ARM,F_SEAL,F_ERROR,
 F_AFTER_ACTION,F_PUBLISH,F_METHOD,F_OWNER,F_FOREIGN_CLOCK,F_LAST};
static uint64_t qemu_get_thread_id(void){return fault==F_OWNER?92:91;}
static uint64_t qemu_clock_get_ns(unsigned v){(void)v;return 17;}
static bool bql_locked(void){return false;}
static bool xwn_frontend246_closed(void){return true;}
static uint64_t memory_region_size(void *v){(void)v;return fixture.ram_bytes;}
static uint64_t memory_region_get_ram_addr(void *v){(void)v;return fixture.ram_base;}
static bool x260_alive(NV2AState *d,X260Slot *v){(void)d;(void)v;return !(fault==F_AFTER_ACTION && (arm_calls||seal_calls));}
static unsigned x274_pending(NV2AState *d){(void)d;return fault==F_PENDING;}
static int qemu_mutex_trylock(Lock *l){
 attempts[l->id]++;
 if((l->id==2&&((fault==F_LOCK1&&attempts[2]==1)||(fault==F_LATE1&&attempts[2]==2)))||
    (l->id==3&&((fault==F_LOCK2&&attempts[3]==1)||(fault==F_LATE2&&attempts[3]==2))))return 1;
 CHECK(!l->locked);l->locked=1;return 0;
}
static void qemu_mutex_lock(Lock *l){CHECK(!l->locked);l->locked=1;}
static void qemu_mutex_unlock(Lock *l){CHECK(l->locked);l->locked=0;}
static bool x260_cpu_boundary(NV2AState *d,X260Slot *v,unsigned phase){
 CHECK(d->pfifo.lock.locked&&!d->pgraph.lock.locked&&!d->pgraph.renderer_lock.locked);cpu_calls++;
 if((phase==0&&fault==F_CPU0)||(phase==1&&fault==F_CPU1))return false;
 X260CPU *a=&v->cpu[phase];a->done=1;a->epoch=v->stage*2-1+phase;a->thread=77;a->when=4+phase;
 a->count=4;a->clock278=100+(phase&&fault==F_CLOCK?2:0);a->clock_error278=fault==F_FOREIGN_CLOCK;
 for(unsigned i=0;i<4;i++){
  X277Callback b=fixture.cpu[0].callbacks[i];b.opaque=(uintptr_t)d;b.region=(uintptr_t)d->vram;
  a->rows[i][0]=b.identity;a->rows[i][1]=b.begin;a->rows[i][2]=b.bytes;a->rows[i][3]=b.opaque;
  a->detail276[i][0]=b.function;a->detail276[i][1]=b.region;a->detail276[i][2]=b.absolute;
 }if(phase&&fault==F_CPU_TUPLE)a->rows[0][0]++;
 return true;
}
static void glo_set_current(GloContext *c){current=*c;}
static bool x260_context_fence(NV2AState *d,X260Slot *v,GloContext *c){
 (void)v;CHECK(!d->pfifo.lock.locked&&!d->pgraph.lock.locked&&!d->pgraph.renderer_lock.locked);fences++;
 current=*c;return !((*c==1&&fault==F_RENDER)||(*c==2&&fault==F_DISPLAY));
}
static bool x265_add(X265Rows *r,uint64_t k,uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g){
 if(fault==F_PUBLISH&&k==64){r->overflow=1;return false;}
 CHECK(r->count<2048);uint64_t row[]={k,a,b,c,d,e,f,g};memcpy(r->rows[r->count++],row,sizeof(row));return true;
}
static bool x265_collect(NV2AState *d,X265State *s){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
 s->accounting_error=fault==F_ACCT;s->shader_jobs_unknown=fault==F_SHADER;return fault!=F_COLLECT;
}
static bool x265_context(X265Rows *r,unsigned role,uint64_t limit){(void)r;(void)limit;CHECK(current==role);return fault!=F_QUERY;}
static bool x267_context(X265Rows *r,PGRAPHGLState *state,unsigned role,uint64_t limit){
 (void)state;(void)limit;CHECK(current==role);x265_add(r,51,role,100+role,200+role,200+role,300+role,300+role,1);return fault!=F_CONTEXT;
}
static bool glo_context_observe267(GloContext *c,uintptr_t ids[4]){
 CHECK(current==*c);ids[0]=200+*c;ids[1]=ids[0];ids[2]=300+*c;ids[3]=ids[2];return fault!=F_ACTUAL_CTX;
}
static bool x274_context_match(X265State *a,X265State *b){
 CHECK(a!=b);return fault!=F_CTX_MATCH;
}
static bool pgraph_gl_reuse274_ready(uint64_t owner){return owner==91&&enabled;}
static bool pgraph_gl_reuse269_arm(NV2AState *d){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
 CHECK(cpu_calls==2&&graph_calls==2&&validate_calls==1&&initial.admission278==0);
 arm_calls++;enabled=1;return fault!=F_ARM;
}
static bool pgraph_gl_reuse269_seal(void){
 CHECK(!device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
 CHECK(cpu_calls==2&&graph_calls==2&&validate_calls==1&&ending.admission278==0);
 seal_calls++;enabled=0;return fault!=F_SEAL;
}
static unsigned pgraph_gl_reuse269_error(void){return fault==F_ERROR;}
static bool x278_graph(NV2AState *d,X265State *s,unsigned phase){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);graph_calls++;
 if((phase==0&&fault==F_GRAPH0)||(phase==1&&fault==F_GRAPH1))return false;
 s->proof278.graph[phase]=fixture.graph[0];
 if(!phase)memcpy(s->proof278.textures,fixture.textures,sizeof(fixture.textures));
 if(phase&&fault==F_GRAPH_CHANGE)s->proof278.graph[1].surfaces[0].flags=0;
 return true;
}
/* ACTUAL_FUNCTIONS */
static void reset_counts(void){cpu_calls=fences=graph_calls=validate_calls=arm_calls=seal_calls=0;memset(attempts,0,sizeof(attempts));}
static void setup(void){
 memset(&device,0,sizeof(device));memset(&renderer,0,sizeof(renderer));memset(&initial,0,sizeof(initial));memset(&ending,0,sizeof(ending));
 reset_counts();fault=0;enabled=0;current=1;device.ledger265=&initial;device.vram=&renderer;
 device.pgraph.gl_renderer_state=&renderer;device.pgraph.primitive_mode=PRIM_TYPE_INVALID;
 device.pfifo.lock=(Lock){1,1};device.pgraph.renderer_lock.id=2;device.pgraph.lock.id=3;device.pfifo.halt=1;
 initial.textures278=true;initial.boundary.state=1;initial.boundary.stage=1;initial.boundary.started=1;initial.boundary.deadline=100;
 initial.ledger.rows=initial.ledger.storage;ending.ledger.rows=ending.ledger.storage;
}
static void inject(unsigned f){fault=f;if(f==F_GET)device.pfifo.regs[0]=4;if(f==F_METHOD)device.pfifo.regs[2]=0x10;}
static void verify_closed(X265State *s,bool success){
 CHECK(device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
 CHECK(s->boundary.state==(success?5:6));CHECK(device.pfifo.halt==!success);
 unsigned a=arm_calls,b=seal_calls,c=cpu_calls;CHECK(!x278_worker(&device));CHECK(a==arm_calls&&b==seal_calls&&c==cpu_calls);
}
int main(int argc,char **argv){
 unsigned paths=0;
 for(unsigned f=0;f<F_LAST;f++){
  if(f==F_SEAL||f==F_ERROR||f==F_CTX_MATCH||f==F_OWNER)continue;
  setup();inject(f);CHECK(x278_worker(&device));verify_closed(&initial,f==0);paths++;
 }
 for(unsigned f=0;f<F_LAST;f++){
  if(f==F_ARM)continue;
  setup();CHECK(x278_worker(&device));CHECK(initial.boundary.state==5);
  X265State saved=initial;reset_counts();enabled=1;device.pfifo.halt=1;
  initial.end274=&ending;ending.textures278=true;ending.boundary.state=1;ending.boundary.stage=2;
  ending.boundary.started=1;ending.boundary.deadline=100;inject(f);
  CHECK(x278_worker(&device));verify_closed(&ending,f==0);CHECK(!arm_calls);
  initial.end274=NULL;CHECK(!memcmp(&initial,&saved,sizeof(saved)));paths++;
  if(!f&&argc==2){FILE *out=fopen(argv[1],"wb");CHECK(out!=NULL);CHECK(fwrite(ending.ledger.rows,8*sizeof(uint64_t),ending.ledger.count,out)==ending.ledger.count);CHECK(!fclose(out));}
 }
 printf("PASS %u actual worker paths, %u assertions; CPU/GL/live-graph models, actual scalar validation/transport; no rearm, locks balanced\n",paths,checks);return 0;
}
