#define _XOPEN_SOURCE 700
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <inttypes.h>
#include <pthread.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include "qemu/atomic.h"
#include "nv2a_regs.h"
#define QEMU_CLOCK_REALTIME 0
#include "row-actual.inc"
typedef struct SurfaceBinding {
 struct SurfaceBinding *next;uint64_t vram_addr,size,dma_addr,dma_len;
 unsigned pitch,width,height,gl_buffer;
 bool draw_dirty,download_pending,cpu_write_evict_pending,upload_pending,cleared,color,swizzle;
 void *access_cb;
} SurfaceBinding;
#define QTAILQ_FOREACH(item,head,entry) for(item=*(head);item;item=item->next)
typedef struct {SurfaceBinding *surfaces,*color_binding,*zeta_binding;} PGRAPHGLState;
typedef struct {
 uint32_t regs_[0x3000],pending_interrupts,enabled_interrupts;
 bool waiting_for_nop,waiting_for_flip,waiting_for_context_switch;
 pthread_mutex_t lock,renderer_lock;
 unsigned primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length;
 bool framebuffer_in_use,flush_pending,sync_pending;
 uint64_t dma_color,dma_zeta;
 struct {uint64_t object_instance,dma_image_source,dma_image_dest;} context_surfaces_2d;
 struct {uint64_t context_surfaces;} image_blit;
 struct {unsigned type;} *renderer;
 PGRAPHGLState *gl_renderer_state;
} PGRAPHState;
typedef struct {
 PGRAPHState pgraph;
 struct {uint64_t total;unsigned count,next;NV2AWaitRow233 rows[256];} wait233;
 NV2AWaitSnapshot238 snapshot238;
 struct {pthread_mutex_t lock;bool halt,fifo_kick;uint32_t pending_interrupts,enabled_interrupts;} pfifo;
} NV2AState;
typedef NV2AState Object;
typedef unsigned Error;
#define NV2A_DEVICE(p) (p)
static uint64_t clock_value,checks,kicks;
static int64_t qemu_clock_get_ns(int kind) {assert(!kind);return qatomic_read(&clock_value);}
static uint32_t pgraph_reg_r(PGRAPHState *pg,uint32_t offset) {return pg->regs_[offset];}
static void nv2a_preserve231_snapshot(NV2AState *d,uint32_t w[10]) {
 assert(d);for(unsigned i=0;i<10;i++)w[i]=100+i;
}
/* Only surrounding host adapters; actual helpers unchanged below. */
static int qemu_mutex_trylock(pthread_mutex_t *m) {return pthread_mutex_trylock(m);}
static void qemu_mutex_lock(pthread_mutex_t *m) {assert(!pthread_mutex_lock(m));}
static void qemu_mutex_unlock(pthread_mutex_t *m) {assert(!pthread_mutex_unlock(m));}
static void pfifo_kick(NV2AState *d) {assert(d);kicks++;}
static void error_setg(Error **e,const char *s) {assert(s && e);*e=(Error*)1;}
typedef struct {char *str;size_t len;} GString;
static GString *g_string_new(const char *p) {assert(!p);GString*s=calloc(1,sizeof(*s));assert(s);s->str=calloc(1,1);assert(s->str);return s;}
static void g_string_append_printf(GString*s,const char*f,...) {
 va_list a,b;va_start(a,f);va_copy(b,a);int n=vsnprintf(NULL,0,f,a);va_end(a);assert(n>=0);
 s->str=realloc(s->str,s->len+n+1);assert(s->str);assert(vsnprintf(s->str+s->len,n+1,f,b)==n);va_end(b);s->len+=n;
}
static char *g_string_free(GString*s,bool release) {assert(!release);char*p=s->str;free(s);return p;}
#include "wait-actual.inc"
#include "snapshot-actual.inc"
#include "worker-actual.inc"
static NV2AState d;
static pthread_mutex_t pg_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_barrier_t barrier;
static void check(bool b) {assert(b);__atomic_fetch_add(&checks,1,__ATOMIC_RELAXED);}
static uint64_t field(const char*s,const char*n) {
 char key[64];snprintf(key,sizeof(key),"%s=",n);const char*p=strstr(s,key);assert(p);return strtoull(p+strlen(key),NULL,10);
}
static void hidden(const char*s) {
 check(!field(s,"tuple_published") && !field(s,"total") && !field(s,"count") && !field(s,"overwritten") && !strstr(s,"row="));
}
static void reset(unsigned state) {
 memset(&d,0,sizeof(d));assert(!pthread_mutex_init(&d.pfifo.lock,NULL));assert(!pthread_mutex_init(&d.pgraph.lock,NULL));assert(!pthread_mutex_init(&d.pgraph.renderer_lock,NULL));
 d.snapshot238.deadline=100;qatomic_store_release(&d.snapshot238.state,state);
 qatomic_set(&clock_value,99);
}
static void destroy(void) {assert(!pthread_mutex_destroy(&d.pfifo.lock));assert(!pthread_mutex_destroy(&d.pgraph.lock));assert(!pthread_mutex_destroy(&d.pgraph.renderer_lock));}
static void journal(unsigned n) {
 for(unsigned i=0;i<n;i++)nv2a_wait233_record(&d,i%2?4:2,i,i%2);
}
static void verify_copy(unsigned n) {
 check(d.snapshot238.total==n && d.snapshot238.count==(n<256?n:256));
 check(d.snapshot238.current.kind==9 && !d.snapshot238.current.seq && !d.snapshot238.current.fifo_valid);
 for(unsigned j=0;j<10;j++)check(!d.snapshot238.current.fifo[j]);
 for(unsigned i=0;i<d.snapshot238.count;i++) {
  NV2AWaitRow233*r=&d.snapshot238.rows[i];unsigned index=n-d.snapshot238.count+i;
  check(r->seq==index+1 && r->value==index && r->kind==(index%2?4:2) && r->fifo_valid==index%2);
  for(unsigned j=0;j<10;j++)check(r->fifo[j]==(index%2?100+j:0));
 }
}
static void *race_worker(void *unused) {
 (void)unused;
 for(unsigned i=0;i<20000;i++) {
  pthread_barrier_wait(&barrier);
  if(nv2a_snapshot238_claim(&d)) {
   assert(!pthread_mutex_lock(&pg_lock));nv2a_snapshot238_copy(&d);assert(!pthread_mutex_unlock(&pg_lock));
   nv2a_snapshot238_publish(&d);
  }
  pthread_barrier_wait(&barrier);
 }return NULL;
}
static void *race_reader(void *unused) {
 (void)unused;
 for(unsigned i=0;i<20000;i++) {
  pthread_barrier_wait(&barrier);qatomic_set(&clock_value,100);
  char*s=snapshot238_report(&d,NULL);if(!field(s,"tuple_published"))hidden(s);free(s);
  pthread_barrier_wait(&barrier);
 }return NULL;
}
static void *publish_reader(void *unused) {
 (void)unused;
 for(unsigned i=0;i<2000;i++) {
  pthread_barrier_wait(&barrier);
  while(qatomic_load_acquire(&d.snapshot238.state)!=3) {}
  char*s=snapshot238_report(&d,NULL);check(field(s,"total")==300 && field(s,"count")==256);verify_copy(300);free(s);
  pthread_barrier_wait(&barrier);
 }return NULL;
}
int main(void) {
 /* Request rejection, FIFO try-lock refusal, no halt mutation or repeat. */
 reset(0);Error*e=NULL;snapshot238_request(&d,false,&e);check(e && !d.snapshot238.state && !kicks);
 e=NULL;assert(!pthread_mutex_lock(&d.pfifo.lock));snapshot238_request(&d,true,&e);check(e && !d.snapshot238.state && !kicks);assert(!pthread_mutex_unlock(&d.pfifo.lock));
 e=NULL;d.pfifo.halt=true;snapshot238_request(&d,true,&e);check(!e && d.snapshot238.state==1 && kicks==1 && d.pfifo.halt && snapshot238_requested(&d,NULL));
 e=NULL;snapshot238_request(&d,true,&e);check(e && kicks==1);destroy();
 for(unsigned n=0;n<=1024;n++) {
  reset(1);journal(n);NV2AState old=d;check(nv2a_snapshot238_claim(&d));nv2a_snapshot238_copy(&d);nv2a_snapshot238_publish(&d);
  check(d.snapshot238.state==3);verify_copy(n);check(!memcmp(&old.pgraph,&d.pgraph,sizeof(d.pgraph)) && !memcmp(&old.wait233,&d.wait233,sizeof(d.wait233)));
  char*s=snapshot238_report(&d,NULL);qatomic_set(&clock_value,1000);journal(20);nv2a_snapshot238_publish(&d);char*t=snapshot238_report(&d,NULL);check(!strcmp(s,t));free(s);free(t);destroy();
 }
 /* Actual FIFO capture copies scalars without changing producer state. */
 reset(1);d.pfifo.halt=true;d.pfifo.fifo_kick=true;d.pfifo.pending_interrupts=42;d.pfifo.enabled_interrupts=13;
 nv2a_snapshot238_fifo(&d);check(d.snapshot238.fifo_when==99);
 check(d.snapshot238.fifo[0]==1 && d.snapshot238.fifo[1]==1 && d.snapshot238.fifo[2]==42 && d.snapshot238.fifo[3]==13);
 for(unsigned i=0;i<10;i++)check(d.snapshot238.fifo[i+4]==100+i);
 check(d.pfifo.halt && d.pfifo.fifo_kick && d.pfifo.pending_interrupts==42);destroy();
 /* Deadline on requested/copying, late copy and terminal tuple withholding. */
 for(unsigned state=1;state<=2;state++) {
  reset(state);journal(300);qatomic_set(&clock_value,100);char*s=snapshot238_report(&d,NULL);hidden(s);free(s);
  nv2a_snapshot238_copy(&d);nv2a_snapshot238_publish(&d);s=snapshot238_report(&d,NULL);hidden(s);check(d.snapshot238.state==5 && !nv2a_snapshot238_claim(&d));free(s);destroy();
 }
 for(unsigned state=0;state<=7;state++) if(state!=1 && state!=2) {
  reset(state);journal(10);check(!nv2a_snapshot238_claim(&d));nv2a_snapshot238_publish(&d);check(d.snapshot238.state==state);destroy();
 }
 reset(1);journal(100000);check(d.wait233.total==100000 && d.wait233.count==256);check(nv2a_snapshot238_claim(&d));nv2a_snapshot238_copy(&d);nv2a_snapshot238_publish(&d);verify_copy(100000);destroy();
 assert(!pthread_barrier_init(&barrier,NULL,3));pthread_t a,b;assert(!pthread_create(&a,NULL,race_worker,NULL));assert(!pthread_create(&b,NULL,race_reader,NULL));
 unsigned completed=0,expired=0;
 for(unsigned i=0;i<20000;i++) {
  reset(1);journal(300);pthread_barrier_wait(&barrier);pthread_barrier_wait(&barrier);
  unsigned state=qatomic_load_acquire(&d.snapshot238.state);check(state==3 || state==5);char*s=snapshot238_report(&d,NULL);
  if(state==3){verify_copy(300);completed++;}else{hidden(s);expired++;}free(s);destroy();
 }
 assert(!pthread_join(a,NULL) && !pthread_join(b,NULL));assert(!pthread_barrier_destroy(&barrier));
 assert(!pthread_barrier_init(&barrier,NULL,2));assert(!pthread_create(&a,NULL,publish_reader,NULL));
 for(unsigned i=0;i<2000;i++) {
  reset(0);journal(300);pthread_barrier_wait(&barrier);qatomic_store_release(&d.snapshot238.state,1);
  check(nv2a_snapshot238_claim(&d));nv2a_snapshot238_copy(&d);nv2a_snapshot238_publish(&d);
  /* Reader cannot observe new journal activity as part of immutable tuple. */
  journal(20);pthread_barrier_wait(&barrier);destroy();
 }
 assert(!pthread_join(a,NULL));assert(!pthread_barrier_destroy(&barrier));
 /* Actual worker block, with explicit surrounding lock/list/model adapters. */
 for(unsigned n=0;n<=129;n++) for(unsigned busy=0;busy<=1;busy++) {
  reset(1);SurfaceBinding surfaces[129]={0};PGRAPHGLState gl={0};typeof(*d.pgraph.renderer) renderer={.type=7};
  d.pgraph.renderer=&renderer;d.pgraph.gl_renderer_state=&gl;
  d.pgraph.framebuffer_in_use=true;d.pgraph.dma_color=12345;
  gl.surfaces=n?surfaces:NULL;gl.color_binding=n?surfaces:NULL;gl.zeta_binding=n?&surfaces[n-1]:NULL;
  for(unsigned i=0;i<n;i++) {
   surfaces[i]=(SurfaceBinding){.next=i+1<n?&surfaces[i+1]:NULL,.vram_addr=i*65536,.size=65536,.pitch=1024,.width=256,.height=64,.draw_dirty=true,.color=true,.access_cb=&gl,.dma_len=64*1024*1024};
  }
  SurfaceBinding oldsurfaces[129];memcpy(oldsurfaces,surfaces,sizeof(surfaces));
  if(busy)qemu_mutex_lock(&d.pgraph.renderer_lock);
  qemu_mutex_lock(&d.pfifo.lock);actual_worker(&d);qemu_mutex_unlock(&d.pfifo.lock);
  if(busy)qemu_mutex_unlock(&d.pgraph.renderer_lock);
  check(d.snapshot238.state==3 && d.snapshot238.renderer_valid==!busy);
  check(d.snapshot238.surface_count==(busy?0:(n>128?128:n)) && d.snapshot238.surface_truncated==(!busy && n>128));
  check(d.snapshot238.context[5]==!busy && d.snapshot238.context[10]==12345);
  check(!memcmp(oldsurfaces,surfaces,sizeof(surfaces)) && d.pgraph.framebuffer_in_use && gl.surfaces==(n?surfaces:NULL));
  if(!busy && n){check(d.snapshot238.surfaces[0][7]==1 && d.snapshot238.surfaces[0][5]==33 && d.snapshot238.surfaces[0][6]==1);}
  char *report=snapshot238_report(&d,NULL);check(field(report,"surface_count")==d.snapshot238.surface_count);free(report);destroy();
 }
 printf("checks=%" PRIu64 " race_pairs=20000 publication_pairs=2000 wrapped_records=100000 completion_winners=%u timeout_winners=%u immutable=covered late_completion=hidden fifo_validity=covered\n",checks,completed,expired);
}
