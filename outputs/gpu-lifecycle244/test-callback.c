/* Exact compiled callback bodies, actual QEMU queues/atomics, explicit CPU-work
 * and log adapters. This test is not actual CPU-thread or GPU completion. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include <qemu/atomic.h>
#include <qemu/queue.h>
typedef uint64_t hwaddr;
typedef struct {uint64_t base;} MemoryRegion;
typedef void (*MemAccessCallbackFunc)(void *, MemoryRegion *, hwaddr, hwaddr, bool);
#include "callback-struct.inc"
typedef struct {bool stopped;QTAILQ_HEAD(,MemAccessCallback) mem_access_callbacks;} CPUState;
typedef struct {void *host_ptr;} run_on_cpu_data;
#define RUN_ON_CPU_HOST_PTR(p) ((run_on_cpu_data){.host_ptr=(p)})
typedef void (*run_on_cpu_func)(CPUState *, run_on_cpu_data);
#define QEMU_CLOCK_REALTIME 0
static uint64_t clock244,actor,freed,allocation_count;
static unsigned checks,events_n,work_n,tlb_n;
static struct {int phase;uint64_t ref,addr,len,thread;int stopped;} events[64];
static struct {CPUState *cpu;run_on_cpu_func f;run_on_cpu_data data;} work[8];
static uint64_t qemu_clock_get_ns(int c){assert(!c);return ++clock244;}
static uint64_t qemu_get_thread_id(void){return actor;}
static void *g_malloc(size_t n){void *p=malloc(n);assert(p);allocation_count++;return p;}
static void g_free(void *p){freed=(uintptr_t)p;allocation_count--;free(p);}
static uint64_t memory_region_get_ram_addr(MemoryRegion *mr){return mr->base;}
static void async_safe_run_on_cpu(CPUState *cpu,run_on_cpu_func f,run_on_cpu_data data){
 assert(work_n<8);work[work_n].cpu=cpu;work[work_n].f=f;work[work_n].data=data;work_n++;
}
static void tlb_flush_all_cpus_synced(CPUState *cpu){(void)cpu;tlb_n++;}
static void trace_xwn_mem_callback244(int phase,uint64_t when,uint64_t thread,uint64_t ref,uint64_t addr,uint64_t len,int stopped){
 assert(events_n<64 && when==clock244);
 if(phase==5)assert(ref==freed); /* scalar only, ASan checks the actual body */
 events[events_n].phase=phase;events[events_n].ref=ref;events[events_n].addr=addr;
 events[events_n].len=len;events[events_n].thread=thread;events[events_n].stopped=stopped;events_n++;
}
#include "callback-actual.inc"
static void drain(void){
 unsigned n=work_n;actor=1;
 for(unsigned i=0;i<n;i++)work[i].f(work[i].cpu,work[i].data);
 work_n=0;
}
typedef struct {unsigned lifecycle244_marks;uint64_t ownership_canary;} NV2AState;
typedef NV2AState Object;
typedef bool Error;
#define NV2A_DEVICE(p) (p)
static unsigned marker_n;
static void error_setg(Error **p,const char *s){assert(s);**p=true;}
static void trace_nv2a_lifecycle244(int phase,uint64_t when,uint64_t thread,uint64_t ref,uint64_t a,uint64_t b){
 assert(phase==(int)(41+marker_n));assert(when==clock244 && thread==actor && !ref && !a && !b);marker_n++;
}
#include "marker-actual.inc"
static void callback(void *p,MemoryRegion *r,hwaddr a,hwaddr n,bool w){
 (void)p;(void)r;(void)a;(void)n;(void)w;
}
int main(void){
 for(unsigned i=0;i<4096;i++){
  CPUState cpu={0};QTAILQ_INIT(&cpu.mem_access_callbacks);cpu.stopped=!!(i&1);
  events_n=work_n=tlb_n=0;actor=2;
  MemoryRegion mr={.base=UINT64_C(0x100000000)};
  uint64_t offset=(i%32)*65536,len=i%2?65536:128;
  MemAccessCallback *cb=mem_access_callback_insert(&cpu,&mr,offset,len,callback,&cpu);
  uint64_t identity=(uintptr_t)cb;
  assert(QTAILQ_EMPTY(&cpu.mem_access_callbacks) && work_n==1 && events_n==1);checks++;
  if(i&2)drain();
  actor=2;mem_access_callback_remove_by_ref(&cpu,cb);
  assert(events[events_n-1].phase==3 && tlb_n==2);checks++;
  drain();assert(QTAILQ_EMPTY(&cpu.mem_access_callbacks) && !allocation_count && !work_n);checks++;
  assert(events_n==5);checks++;
  int order[5]={1,(i&2)?2:3,(i&2)?3:2,4,5};
  for(unsigned j=0;j<5;j++){
   assert(events[j].phase==order[j] && events[j].ref==identity);checks++;
   assert(events[j].addr==mr.base+offset && events[j].len==len);checks++;
   assert(events[j].stopped==cpu.stopped);checks++;
   assert(events[j].thread==((events[j].phase==1||events[j].phase==3)?2:1));checks++;
  }
  unsigned old=events_n;mem_access_callback_remove_by_ref(&cpu,NULL);
  assert(events_n==old && tlb_n==2 && !work_n);checks++;
 }
 NV2AState d={.ownership_canary=UINT64_C(0xabcd12345678)};
 bool error=false;Error *ep=&error;
 lifecycle244_mark_set(&d,false,&ep);assert(error && !d.lifecycle244_marks && !marker_n);checks++;
 error=false;lifecycle244_mark_set(&d,true,&ep);assert(!error && d.lifecycle244_marks==1 && marker_n==1);checks++;
 lifecycle244_mark_set(&d,true,&ep);assert(!error && d.lifecycle244_marks==2 && marker_n==2);checks++;
 lifecycle244_mark_set(&d,true,&ep);assert(error && d.lifecycle244_marks==2 && marker_n==2);checks++;
 assert(d.ownership_canary==UINT64_C(0xabcd12345678));checks++;
 printf("4096 callback cycles; %u checks; bounded markers; no adapter leaks\n",checks);
 return 0;
}
