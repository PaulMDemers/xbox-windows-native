/* Exact new worker and scalar adapter with explicit GL/job/live-graph models. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "admission.h"
#include "fixture.h"
#include "release.h"
#include "boundary.h"
#include "link.h"
#include "resume.h"
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
typedef struct X280Transaction X280Transaction;
typedef struct X265State {X260Slot boundary;X265Rows ledger;unsigned accounting_error,shader_jobs_unknown,contexts274,seal274,admission278;bool textures278;uint64_t allocations278[4];X277Proof proof278;struct X265State *end274;X280Transaction *transaction280;} X265State;
#include "transaction.h"
typedef struct {unsigned report_queue,gl_zpass_pixel_count_query_count;} PGRAPHGLState;
typedef struct {Lock renderer_lock,lock;PGRAPHGLState *gl_renderer_state;unsigned framebuffer_in_use,primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length;} PGRAPHState;
typedef struct {X265State *ledger265;PGRAPHState pgraph;void *vram;struct{Lock lock;unsigned halt,regs[3];} pfifo;} NV2AState;
typedef unsigned GloContext;
static GloContext rc=1,dc=2,*g_nv2a_context_render=&rc,*g_nv2a_context_display=&dc;
static struct{unsigned stopped;} cpu={1};
#define qemu_get_cpu(i) ((void)(i),&cpu)
static NV2AState device;static PGRAPHGLState renderer;static X265State initial,post,ending;static X280Transaction transaction;
static unsigned requested,fault_stage,active_stage;
#define fault ((fault_stage==active_stage)?requested:0)
static unsigned cpu_calls,fences,graph_calls,arm_calls,seal_calls,enabled,current;
static unsigned attempts[4][4],checks,release_calls,post_calls,mutated;static uint64_t now;
#define CHECK(x) do{assert(x);checks++;}while(0)
enum {F_CPU0=1,F_CPU1,F_RENDER,F_DISPLAY,F_LOCK1,F_LOCK2,F_LATE1,F_LATE2,
 F_COLLECT,F_GRAPH0,F_GRAPH1,F_QUERY,F_CONTEXT,F_ACCT,F_SHADER,F_GET,F_PENDING,
 F_CLOCK,F_BETWEEN_CLOCK,F_CPU_TUPLE,F_GRAPH_CHANGE,F_CTX_MATCH,F_ACTUAL_CTX,F_ARM,F_SEAL,F_ERROR,
 F_AFTER_ACTION,F_PUBLISH,F_METHOD,F_OWNER,F_FOREIGN_CLOCK,F_UNBOUND,F_RELEASE,F_POST,F_REFSTATE,F_RETAINED,F_END_KEY,F_LAST};
static uint64_t qemu_get_thread_id(void){return fault==F_OWNER?92:91;}
static uint64_t qemu_clock_get_ns(unsigned v){(void)v;return ++now;}
static bool bql_locked(void){return false;}
static bool xwn_frontend246_closed(void){return true;}
static uint64_t memory_region_size(void *v){(void)v;return fixture.ram_bytes;}
static uint64_t memory_region_get_ram_addr(void *v){(void)v;return fixture.ram_base;}
static bool x260_alive(NV2AState *d,X260Slot *v){(void)d;active_stage=v->stage;return !(fault==F_AFTER_ACTION && (arm_calls||seal_calls));}
static unsigned x274_pending(NV2AState *d){(void)d;return fault==F_PENDING;}
static int qemu_mutex_trylock(Lock *l){
 attempts[active_stage][l->id]++;
 if((l->id==2&&((fault==F_LOCK1&&attempts[active_stage][2]==1)||(fault==F_LATE1&&attempts[active_stage][2]==2)))||
    (l->id==3&&((fault==F_LOCK2&&attempts[active_stage][3]==1)||(fault==F_LATE2&&attempts[active_stage][3]==2))))return 1;
 CHECK(!l->locked);l->locked=1;return 0;
}
static void qemu_mutex_lock(Lock *l){CHECK(!l->locked);l->locked=1;}
static void qemu_mutex_unlock(Lock *l){CHECK(l->locked);l->locked=0;}
static bool x260_cpu_boundary(NV2AState *d,X260Slot *v,unsigned phase){
 CHECK(d->pfifo.lock.locked&&!d->pgraph.lock.locked&&!d->pgraph.renderer_lock.locked);cpu_calls++;
 if((phase==0&&fault==F_CPU0)||(phase==1&&fault==F_CPU1))return false;
 X260CPU *a=&v->cpu[phase];a->done=1;a->epoch=v->stage*2-1+phase;a->thread=77;a->when=++now;
 a->count=4;a->clock278=100+(phase&&fault==F_CLOCK?2:0)+(fault==F_BETWEEN_CLOCK?1:0);a->clock_error278=fault==F_FOREIGN_CLOCK;
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
 for(unsigned i=0;i<4;i++) {
  const X277Texture *t=&fixture.textures[i];unsigned released=transaction.candidate && s->boundary.stage==2;
  x265_add(&s->ledger,3,i,released?0:t->identity,0,1,0,0,0);
  x265_add(&s->ledger,4,t->identity,released?1:2,t->name,0x0de1,0,0,0);
  x265_add(&s->ledger,5,t->identity,released?1:2,1,released?0:1,0,0,0);
 }
 x265_add(&s->ledger,1,900,77,65536,4096,22,1,fault==F_RETAINED);
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
 CHECK(cpu_calls==2&&graph_calls==2&&initial.admission278==0);CHECK(!transaction.release.observer_armed);
 arm_calls++;enabled=1;return fault!=F_ARM;
}
static bool pgraph_gl_reuse269_seal(void){
 CHECK(!device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
 CHECK(cpu_calls==6&&graph_calls==6&&ending.admission278==0);
 seal_calls++;enabled=0;return fault!=F_SEAL;
}
static unsigned pgraph_gl_reuse269_error(void){return fault==F_ERROR;}
static bool x280_graph(NV2AState *d,X280Transaction *tx,X265State *s,unsigned phase){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);graph_calls++;
 if((phase==0&&fault==F_GRAPH0)||(phase==1&&fault==F_GRAPH1))return false;
 s->proof278.graph[phase]=fixture.graph[0];
 if(!phase) {
  memcpy(s->proof278.textures,fixture.textures,sizeof(fixture.textures));
  if(tx->candidate&&s->boundary.stage==2)for(unsigned i=0;i<4;i++){s->proof278.textures[i].refs=1;s->proof278.textures[i].unit_edges=0;}
  if(fault==F_REFSTATE)s->proof278.textures[0].refs++;
  if(fault==F_END_KEY)s->proof278.textures[0].name++;
 }
 if(phase&&fault==F_GRAPH_CHANGE)s->proof278.graph[1].surfaces[0].flags=0;
 return true;
}

static bool x280_unbound(NV2AState *d,X265State *s,X279Proof *p){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
 CHECK(s==&initial&&s->boundary.state==5&&s->admission278==0);
 *p=(X279Proof){.observation=s->proof278,.operation=X279_RELEASE,.complete_graph=1,.locks_held=1,.owner_current=1,.contexts_current=1,.cache_count=4,.target={0x0de1,0x0de1,0x0de1,0x0de1}};
 return fault!=F_UNBOUND;
}
static X279Result pgraph_gl_release280(NV2AState *d,const X279Proof *p){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
 CHECK(!x279_admit(p)&&cpu_calls==2&&arm_calls==1);release_calls++;
 mutated=fault==F_RELEASE?3:15;
 return (X279Result){fault==F_RELEASE?X279_QUARANTINE:X279_OK,mutated};
}
static bool pgraph_gl_reuse280_post(NV2AState *d){
 CHECK(d->pfifo.lock.locked&&d->pgraph.lock.locked&&d->pgraph.renderer_lock.locked);
 CHECK(cpu_calls==4&&post.boundary.state==5&&transaction.state==2);post_calls++;return fault!=F_POST;
}
/* ACTUAL_FUNCTIONS */
static void setup(unsigned candidate){
 memset(&device,0,sizeof(device));memset(&renderer,0,sizeof(renderer));memset(&initial,0,sizeof(initial));memset(&post,0,sizeof(post));memset(&ending,0,sizeof(ending));memset(&transaction,0,sizeof(transaction));
 memset(attempts,0,sizeof(attempts));now=100;requested=fault_stage=active_stage=0;
 cpu_calls=fences=graph_calls=arm_calls=seal_calls=release_calls=post_calls=mutated=0;enabled=0;current=1;
 device.ledger265=&initial;device.vram=&renderer;device.pgraph.gl_renderer_state=&renderer;device.pgraph.primitive_mode=PRIM_TYPE_INVALID;
 device.pfifo.lock=(Lock){1,1};device.pgraph.renderer_lock.id=2;device.pgraph.lock.id=3;device.pfifo.halt=1;
 initial.transaction280=&transaction;transaction=(X280Transaction){.pre=&initial,.post=&post,.end=&ending,.state=1,.candidate=candidate};
 initial.ledger.rows=initial.ledger.storage;post.ledger.rows=post.ledger.storage;ending.ledger.rows=ending.ledger.storage;
}
static void verify(bool success,unsigned expected){
 CHECK(device.pfifo.lock.locked&&!device.pgraph.lock.locked&&!device.pgraph.renderer_lock.locked);
 CHECK(transaction.state==(success?expected:6));CHECK(device.pfifo.halt==!success);
 unsigned a=arm_calls,b=seal_calls,c=cpu_calls,r=release_calls;
 CHECK(!x280_worker(&device));CHECK(a==arm_calls&&b==seal_calls&&c==cpu_calls&&r==release_calls);
 for(unsigned n=0;n<3;n++){
  X265State *s=n==0?&initial:n==1?&post:&ending;unsigned scalar=0;
  for(unsigned i=0;i<s->ledger.count;i++)scalar+=s->ledger.rows[i][0]==64;
  CHECK(scalar<=1); /* Failed publication never repeats rows. */
 }
}
static bool relevant(unsigned f,unsigned stage,unsigned candidate){
 if(f==F_GET||f==F_METHOD)return false; /* separately exercise direct state below */
 if(f==F_SEAL||f==F_ERROR)return stage==3;
 if(f==F_ARM||f==F_UNBOUND)return stage==1;
 if(f==F_RELEASE)return stage==1&&candidate;
 if(f==F_POST||f==F_BETWEEN_CLOCK||f==F_RETAINED)return stage==2;
 if(f==F_CTX_MATCH||f==F_OWNER)return stage>1;
 if(f==F_END_KEY)return stage==3;
 if(f==F_AFTER_ACTION)return true;
 return true;
}
int main(int argc,char **argv){
 unsigned paths=0;
 for(unsigned mode=0;mode<2;mode++)for(unsigned stage=1;stage<=3;stage++)for(unsigned f=0;f<F_LAST;f++){
  if(!relevant(f,stage,mode))continue;
  setup(mode);
  if(stage==3){CHECK(x280_worker(&device));verify(true,3);transaction.state=4;device.pfifo.halt=1;}
  requested=f;fault_stage=stage;
  CHECK(x280_worker(&device));verify(f==0,stage==3?5:3);paths++;
  if(mode&&stage==2)CHECK(mutated==15&&release_calls==1);
  if(stage==3)CHECK(arm_calls==1&&release_calls==mode);
  if(!f&&stage==3&&argc==2){
   char path[512];snprintf(path,sizeof(path),"%s/mode%u.bin",argv[1],mode);FILE *o=fopen(path,"wb");CHECK(o);
   CHECK(fwrite(transaction.records,sizeof(transaction.records),1,o)==1);
   X265State *slots[]={&initial,&post,&ending};
   for(unsigned i=0;i<3;i++){uint64_t count=slots[i]->ledger.count;CHECK(fwrite(&count,8,1,o)==1);CHECK(fwrite(slots[i]->ledger.rows,64,(size_t)count,o)==count);}
   CHECK(!fclose(o));
  }
 }
 for(unsigned mode=0;mode<2;mode++)for(unsigned which=0;which<5;which++){
  setup(mode);if(which==0)transaction.pre=NULL;if(which==1)transaction.post=transaction.pre;
  if(which==2)transaction.candidate=2;
  if(which==3)device.pfifo.regs[0]=4;
  if(which==4)device.pfifo.regs[2]=0x10;
  CHECK(x280_worker(&device));verify(false,0);CHECK(!release_calls);paths++;
 }
 /* Publication failure after the full post-release proof still forbids resume. */
 setup(1);transaction.published[0]=1;CHECK(x280_worker(&device));verify(false,0);CHECK(mutated==15&&transaction.reason==13);paths++;
 printf("PASS %u actual orchestration/capture paths, %u assertions; explicit CPU/GL/graph/release models; no runtime claim\n",paths,checks);return 0;
}
