#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include "qemu/atomic.h"
#include "qemu/queue.h"
typedef unsigned GLenum;typedef int GLint;typedef void *GLsync;typedef int GloContext;
enum {GL_TEXTURE_BINDING_2D=1,GL_CURRENT_PROGRAM,GL_ARRAY_BUFFER_BINDING,
GL_ELEMENT_ARRAY_BUFFER_BINDING,GL_DRAW_FRAMEBUFFER_BINDING,GL_VERTEX_ARRAY_BINDING,GL_ACTIVE_TEXTURE,
GL_SYNC_GPU_COMMANDS_COMPLETE,GL_SYNC_FLUSH_COMMANDS_BIT,GL_ALREADY_SIGNALED=0x911a,GL_CONDITION_SATISFIED=0x911c};
enum {QEMU_CLOCK_REALTIME,PRIM_TYPE_INVALID=0,PGRAPH_RENDERER_SWITCH_PHASE_IDLE=0,
NV_PFIFO_CACHE1_DMA_GET=0,NV_PFIFO_CACHE1_DMA_PUT=1,NV_PFIFO_CACHE1_DMA_STATE=2,
NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT=1,NV_PFIFO_CACHE1_DMA_STATE_ERROR=2};
typedef struct {int id;} Mutex;
typedef struct SurfaceBinding {uint64_t vram_addr,size;unsigned gl_buffer;
bool draw_dirty,download_pending,cpu_write_evict_pending,upload_pending;void *access_cb;
QTAILQ_ENTRY(SurfaceBinding) entry;} SurfaceBinding;
typedef struct {bool downloads_pending,download_dirty_surfaces_pending,shader_cache_writeback_pending;
QTAILQ_HEAD(,SurfaceBinding) surfaces;} PGRAPHGLState;
typedef struct {Mutex renderer_lock,lock;PGRAPHGLState *gl_renderer_state;
bool framebuffer_in_use,waiting_for_nop,waiting_for_flip,waiting_for_context_switch,flush_pending,sync_pending;
int primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length,renderer_switch_phase;} PGRAPHState;
typedef struct NV2AState {PGRAPHState pgraph;struct {Mutex lock;bool halt;uint32_t regs[3];int fifo_cond;} pfifo;
struct {unsigned state,reason,count,dirty,error;bool release,ready,old_halt;int64_t deadline;
uint64_t when,thread,context[2],surfaces[128][6];int bindings[2][7];unsigned fence[2];} worker247;} NV2AState;
static int mode,held[3],calls,waits,checks;static int64_t now;
static NV2AState *active;static GloContext render=1,display=2;
static GloContext *g_nv2a_context_render=&render,*g_nv2a_context_display=&display;
static int64_t qemu_clock_get_ns(int n){(void)n;return now;}
static uint64_t qemu_get_thread_id(void){return 12;}
static bool bql_locked(void){return mode==3;}
static bool xwn_frontend246_closed(void){return mode!=10;}
static int qemu_mutex_trylock(Mutex *m){if((mode==1&&m->id==1)||(mode==2&&m->id==2))return 1;assert(!held[m->id]);held[m->id]=1;return 0;}
static void qemu_mutex_unlock(Mutex *m){assert(held[m->id]);held[m->id]=0;}
static void qemu_mutex_lock(Mutex *m){assert(!held[m->id]);held[m->id]=1;}
static void qemu_cond_timedwait(int *c,Mutex *m,int ms){(void)c;assert(ms==20&&held[0]&&!held[1]&&!held[2]);++waits;
qemu_mutex_unlock(m);now+=20000000;if(mode!=11){qatomic_store_release(&active->worker247.release,true);}qemu_mutex_lock(m);}
static void glo_set_current(GloContext *c){assert(c==&render||c==&display);}
static void glGetIntegerv(GLenum f,GLint *v){assert(f&&!held[0]&&!held[1]&&!held[2]);*v=13;calls++;}
static GLenum glGetError(void){assert(!held[0]&&!held[1]&&!held[2]);return mode==8?0x502:0;}
static GLsync glFenceSync(GLenum f,unsigned b){assert(f==GL_SYNC_GPU_COMMANDS_COMPLETE&&!b&&!held[0]&&!held[1]&&!held[2]);return mode==6?NULL:(void*)1;}
static GLenum glClientWaitSync(GLsync f,unsigned b,uint64_t t){assert(f==(void*)1&&b==GL_SYNC_FLUSH_COMMANDS_BIT&&t==100000000&&!held[0]&&!held[1]&&!held[2]);calls++;if(mode==9)qatomic_store_release(&active->worker247.release,true);return mode==7?0x911b:GL_CONDITION_SATISFIED;}
static void glDeleteSync(GLsync f){assert(f==(void*)1&&!held[0]&&!held[1]&&!held[2]);}
static void trace_nv2a_lifecycle244(unsigned p,uint64_t n,uint64_t th,uint64_t key,uint64_t a,uint64_t b){(void)n;(void)th;(void)key;(void)a;(void)b;assert(p>=71&&p<=80);}
#include "worker-actual.inc"
static void check(bool b){assert(b);checks++;}
int main(void){
 for(int round=0;round<256;round++)for(mode=0;mode<12;mode++){
  NV2AState d={0};PGRAPHGLState r={0};SurfaceBinding s={.vram_addr=4096,.size=8192,.gl_buffer=42,.draw_dirty=true};
  d.pgraph.gl_renderer_state=&r;d.pgraph.renderer_lock.id=1;d.pgraph.lock.id=2;d.pfifo.lock.id=0;QTAILQ_INIT(&r.surfaces);
  active=&d;now=0;calls=waits=0;memset(held,0,sizeof(held));held[0]=1;d.pfifo.halt=true;d.worker247.state=1;d.worker247.deadline=5000000000;
  if(mode==4)QTAILQ_INSERT_TAIL(&r.surfaces,&s,entry);if(mode==5)d.pgraph.flush_pending=true;
  check(pgraph_gl_worker247(&d));check(held[0]&&!held[1]&&!held[2]);check(!d.pfifo.halt&&d.worker247.ready);
  check(d.worker247.state==(mode==0?5:6));if(mode==0){check(!d.worker247.reason&&waits==1&&calls==16);}else if(mode==11){check(waits==250&&now==5000000000);}else{check(waits==0);}
  if(mode==4){check(d.worker247.count==1&&d.worker247.dirty==1&&s.draw_dirty&&s.gl_buffer==42&&calls==0);}
  if((mode>=1&&mode<=5)||mode==10){check(calls==0);}
  check(!pgraph_gl_worker247(&d));check(held[0]&&!held[1]&&!held[2]);
 }
 printf("PASS3072 fresh actual-helper paths,%d checks; fences held zero actor locks, finite parks, no dirty disposal\n",checks);return 0;
}
