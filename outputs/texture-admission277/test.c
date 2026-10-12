#include <assert.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "admission.h"
#include "queue.h"
#include "fixture.h"
static unsigned checks;
#define CHECK(x) do {assert(x);checks++;} while(0)
/* Exact actual insert/unlink bodies below; QEMU scheduling, trace and CPU
 * context are explicitly modeled. Queue macros are the pinned QEMU header. */
typedef uint64_t hwaddr;
typedef struct MemAccessCallback {
    void *mr;hwaddr addr,len;void *func,*opaque;
    QTAILQ_ENTRY(MemAccessCallback) entry;
} MemAccessCallback;
typedef struct CPUState {QTAILQ_HEAD(,MemAccessCallback) mem_access_callbacks;unsigned stopped;} CPUState;
typedef union {void *host_ptr;} run_on_cpu_data;
static _Thread_local CPUState *self;
static _Thread_local unsigned exclusive;
#define qemu_cpu_is_self(c) (self==(c))
#define cpu_in_exclusive_context(c) (self==(c) && exclusive)
#define qatomic_read(p) __atomic_load_n((p),__ATOMIC_SEQ_CST)
#define qatomic_fetch_or(p,v) __atomic_fetch_or((p),(v),__ATOMIC_SEQ_CST)
#define qatomic_cmpxchg(p,o,n) __extension__ ({__typeof__(*(p)) old_=(o); __atomic_compare_exchange_n((p),&old_,(n),0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST);old_;})
#define QEMU_CLOCK_REALTIME 0
#define qemu_clock_get_ns(x) ((uint64_t)(x))
#define qemu_get_thread_id() 1u
#define trace_xwn_mem_callback244(a,b,c,d,e,f,g) ((void)(a),(void)(b),(void)(c),(void)(d),(void)(e),(void)(f),(void)(g))
static unsigned frees;
static void g_free(void *p){CHECK(p!=NULL);frees++;free(p);}
/* ACTUAL_CLOCK */
/* ACTUAL_INSERT */
/* ACTUAL_REMOVE */
static CPUState cpu,foreign;
static void reset_clock_model(void)
{
    /* Test process models a fresh instance. No corresponding runtime API. */
    x277_clock_owner=NULL;x277_clock_value=0;x277_clock_error=0;
    self=&cpu;exclusive=1;QTAILQ_INIT(&cpu.mem_access_callbacks);
}
static void lifecycle(void)
{
    reset_clock_model();uint64_t clock;unsigned error;
    mem_access_callback_clock277(&cpu,&clock,&error);CHECK(clock==0 && error);
    for(unsigned round=0;round<4096;round++) {
        MemAccessCallback *cb=calloc(1,sizeof(*cb));CHECK(cb!=NULL);
        cb->addr=0x1000;cb->len=4096;
        do_mem_access_callback_insert(&cpu,(run_on_cpu_data){.host_ptr=cb});
        mem_access_callback_clock277(&cpu,&clock,&error);
        CHECK(!error && clock==round*2+1 && QTAILQ_FIRST(&cpu.mem_access_callbacks)==cb);
        do_mem_access_callback_remove_by_ref(&cpu,(run_on_cpu_data){.host_ptr=cb});
        mem_access_callback_clock277(&cpu,&clock,&error);
        CHECK(!error && clock==round*2+2 && QTAILQ_EMPTY(&cpu.mem_access_callbacks));
    }
    CHECK(frees==4096);
    /* Actual tuple can return byte-for-byte after remove/insert. Clock cannot. */
    X277Proof p=fixture;CHECK(x277_validate(&p)==0);
    p.cpu[1].clock+=2;CHECK(x277_validate(&p)==X277_LIFETIME);
    exclusive=0;mem_access_callback_clock277(&cpu,&clock,&error);CHECK(error);
    exclusive=1;self=&foreign;x277_clock_advance(&foreign);
    self=&cpu;mem_access_callback_clock277(&cpu,&clock,&error);CHECK(error&1);
    reset_clock_model();x277_clock_value=UINT64_MAX-1;
    x277_clock_advance(&cpu);CHECK(x277_clock_value==UINT64_MAX);
    x277_clock_advance(&cpu);CHECK(x277_clock_value==UINT64_MAX && (x277_clock_error&2));
}
typedef struct {X277CPU copy;unsigned published;} Publication;
static void *publish(void *arg)
{
    Publication *p=arg;self=&cpu;exclusive=1;
    p->copy=fixture.cpu[0];mem_access_callback_clock277(&cpu,&p->copy.clock,&p->copy.clock_error);
    __atomic_store_n(&p->published,1,__ATOMIC_RELEASE);return NULL;
}
static void publication(void)
{
    reset_clock_model();x277_clock_advance(&cpu);
    for(unsigned i=0;i<1024;i++) {
        Publication p={0};pthread_t thread;
        CHECK(!pthread_create(&thread,NULL,publish,&p));
        while(!__atomic_load_n(&p.published,__ATOMIC_ACQUIRE)) {}
        CHECK(p.copy.clock==1 && !p.copy.clock_error && p.copy.count==4);
        CHECK(!memcmp(p.copy.callbacks,fixture.cpu[0].callbacks,4*sizeof(X277Callback)));
        CHECK(!pthread_join(thread,NULL));
    }
}
static void rejects(void)
{
    X277Proof p=fixture;CHECK(x277_validate(&p)==0);
    /* Old276 evidence has neither a mutation clock nor second acknowledgment. */
    p.cpu[0].clock=0;memset(&p.cpu[1],0,sizeof(p.cpu[1]));memset(&p.graph[1],0,sizeof(p.graph[1]));
    CHECK(x277_validate(&p)!=0);
#define BAD(statement) do {p=fixture;statement;CHECK(x277_validate(&p)!=0);}while(0)
    BAD(p.release_requested=1);BAD(p.stage=0);BAD(p.stage=3);
    BAD(p.device=0);BAD(p.region=0);BAD(p.function=0);BAD(p.worker=0);
    BAD(p.ram_bytes=UINT64_MAX);BAD(p.ram_base=UINT64_MAX);
    BAD(p.cpu_stopped=0);BAD(p.frontend_closed=0);BAD(p.pfifo_halted=0);
    BAD(p.cpu_stopped=2);BAD(p.frontend_closed=2);BAD(p.pfifo_halted=2);
    BAD(p.render_fenced=0);BAD(p.display_fenced=0);BAD(p.get_equals_put=0);
    BAD(p.render_fenced=2);BAD(p.display_fenced=2);BAD(p.get_equals_put=2);
    BAD(p.render_context=0);BAD(p.display_context=p.render_context);
    BAD(p.pending=1);BAD(p.method_error=1);BAD(p.unknown_owners=1);
    BAD(p.started=p.finished+1);BAD(p.deadline=p.finished);
    for(unsigned phase=0;phase<2;phase++) {
        BAD(p.cpu[phase].done=0);BAD(p.cpu[phase].error=1);BAD(p.cpu[phase].clock_error=1);
        BAD(p.cpu[phase].epoch++);BAD(p.cpu[phase].thread=p.worker);
        BAD(p.cpu[phase].clock=0);BAD(p.cpu[phase].clock=UINT64_MAX);
        BAD(p.cpu[phase].when=p.deadline);BAD(p.cpu[phase].count=129);
        BAD(p.graph[phase].complete=0);BAD(p.graph[phase].error=1);
        BAD(p.graph[phase].complete=2);
        BAD(p.graph[phase].count=129);BAD(p.graph[phase].count=3);
        for(unsigned i=0;i<4;i++) {
            BAD(p.cpu[phase].callbacks[i].identity=0);
            BAD(p.cpu[phase].callbacks[i].identity=p.cpu[phase].callbacks[(i+1)%4].identity);
            BAD(p.cpu[phase].callbacks[i].begin=UINT64_MAX);
            BAD(p.cpu[phase].callbacks[i].bytes=0);
            BAD(p.cpu[phase].callbacks[i].bytes=UINT64_MAX);
            BAD(p.cpu[phase].callbacks[i].opaque++);BAD(p.cpu[phase].callbacks[i].function++);
            BAD(p.cpu[phase].callbacks[i].region++);BAD(p.cpu[phase].callbacks[i].absolute++);
            BAD(p.graph[phase].surfaces[i].identity=0);BAD(p.graph[phase].surfaces[i].callback=0);
            BAD(p.graph[phase].surfaces[i].identity=p.graph[phase].surfaces[(i+1)%4].identity);
            BAD(p.graph[phase].surfaces[i].callback=p.graph[phase].surfaces[(i+1)%4].callback);
            BAD(p.graph[phase].surfaces[i].begin++);BAD(p.graph[phase].surfaces[i].bytes--);
            BAD(p.graph[phase].surfaces[i].name=0);BAD(p.graph[phase].surfaces[i].flags=2);
            BAD(p.graph[phase].surfaces[i].flags=4);BAD(p.graph[phase].surfaces[i].flags=8);
            BAD(p.graph[phase].surfaces[i].roles=4);
        }
    }
    for(unsigned i=0;i<4;i++) {
        BAD(p.textures[i].identity=0);BAD(p.textures[i].name=0);
        BAD(p.textures[i].identity=p.textures[(i+1)%4].identity);
        BAD(p.textures[i].name=p.textures[(i+1)%4].name);
        BAD(p.textures[i].allocation++);BAD(p.textures[i].allocation_bytes=0);
        BAD(p.textures[i].source++);BAD(p.textures[i].source_bytes--);
        BAD(p.textures[i].palette=1);BAD(p.textures[i].palette_bytes=1);
        BAD(p.textures[i].refs=1);BAD(p.textures[i].cache_edges=0);BAD(p.textures[i].unit_edges=0);
        BAD(p.textures[i].allocation=p.graph[0].surfaces[0].begin;p.textures[i].source=p.textures[i].allocation+256);
        BAD(p.textures[i].name=p.graph[0].surfaces[0].name);
    }
    /* Guard-only overlap must fail, even when the 512 source bytes are outside. */
    p=fixture;for(unsigned j=0;j<2;j++) {
        p.cpu[j].callbacks[0].begin=p.textures[0].allocation+4095;
        p.cpu[j].callbacks[0].absolute=p.ram_base+p.cpu[j].callbacks[0].begin;
        p.cpu[j].callbacks[0].bytes=1;
        p.graph[j].surfaces[0].begin=p.cpu[j].callbacks[0].begin;p.graph[j].surfaces[0].bytes=1;
    }CHECK(x277_validate(&p)==X277_OVERLAP);
    /* Unrelated readback/dirty-state change is rejected within a transaction. */
    BAD(p.graph[1].surfaces[0].flags=0);
    BAD(p.graph[0].surfaces[0].roles=1;p.graph[1].surfaces[0].roles=1);
    BAD(p.cpu[1].clock+=2);
    /* Clock counts may differ across separate guest-resumed transactions. */
    p=fixture;p.stage=2;p.cpu[0].epoch=3;p.cpu[1].epoch=4;
    p.cpu[0].clock=p.cpu[1].clock=123456;CHECK(x277_validate(&p)==0);
#undef BAD
}
int main(void)
{ lifecycle();publication();rejects();printf("PASS %u checks; 4096 actual insert/unlink/free pairs; 1024 publication races\n",checks);return 0; }
