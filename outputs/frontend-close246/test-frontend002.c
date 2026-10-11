#define _GNU_SOURCE
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include "qemu/atomic.h"
typedef unsigned GLuint, GLenum;
typedef int GLint;
typedef void *GLsync;
enum {GL_SYNC_GPU_COMMANDS_COMPLETE=0x9117,GL_SYNC_FLUSH_COMMANDS_BIT=1,
 GL_ALREADY_SIGNALED=0x911a,GL_CONDITION_SATISFIED=0x911c,GL_NO_ERROR=0,
 GL_TEXTURE_BINDING_2D=0x8069,GL_CURRENT_PROGRAM=0x8b8d,
 GL_ARRAY_BUFFER_BINDING=0x8894,GL_ELEMENT_ARRAY_BUFFER_BINDING=0x8895,
 GL_DRAW_FRAMEBUFFER_BINDING=0x8ca6,GL_VERTEX_ARRAY_BINDING=0x85b5,GL_ACTIVE_TEXTURE=0x84e0};
enum {QEMU_CLOCK_REALTIME};
struct xemu_console {void *real_window,*winctx;};
static int mode,gl_calls,renderer_calls,checks;
static bool worker_stop;
static uint64_t qemu_clock_get_ns(int ignored){(void)ignored;return 999;}
static uint64_t qemu_get_thread_id(void){return (uintptr_t)pthread_self();}
static bool bql_locked(void){return mode==1;}
static bool SDL_GL_MakeCurrent(void *w,void *c){(void)w;(void)c;return mode!=2;}
static void *SDL_GL_GetCurrentContext(void){return (void *)7;}
static int nv2a_frontend246_loan(void){++renderer_calls;return mode==3?-1:mode==4?1:0;}
static bool xwn_frontend246_request(bool close);
static GLsync glFenceSync(GLenum condition,GLuint flags){assert(condition==0x9117&&flags==0);++gl_calls;return mode==5?NULL:(void*)8;}
static GLenum glClientWaitSync(GLsync s,GLuint flags,uint64_t timeout){assert(s==(void*)8&&flags==1&&timeout==100000000);++gl_calls;if(mode==8){assert(xwn_frontend246_request(false));}return mode==6?0x911b:GL_CONDITION_SATISFIED;}
static void glDeleteSync(GLsync s){assert(s==(void*)8);++gl_calls;}
static void glGetIntegerv(GLenum n,GLint *v){assert(n);++gl_calls;*v=13;}
static bool glIsTexture(GLuint n){++gl_calls;return n==42;}
static GLenum glGetError(void){++gl_calls;return mode==7?0x502:0;}
static char *g_strdup_printf(const char *fmt,...){va_list v;va_start(v,fmt);char *p=NULL;assert(vasprintf(&p,fmt,v)>=0);va_end(v);return p;}
static void trace_nv2a_lifecycle244(int p,uint64_t t,uint64_t th,uint64_t ref,uint64_t a,uint64_t b){(void)t;(void)th;(void)ref;(void)a;(void)b;assert(p>=60&&p<=68);}
#include "frontend-actual.inc"
static void check(bool v){assert(v);++checks;}
static void reset(void){frontend246_state=0;frontend246_ready=false;memset(&frontend246_record,0,sizeof(frontend246_record));frontend246_last_texture=42;frontend246_last_fallback=false;gl_calls=renderer_calls=0;worker_stop=false;}
static void *actor(void *arg){struct xemu_console *s=arg;while(!qatomic_load_acquire(&worker_stop)){frontend246_gate(s);sched_yield();}return NULL;}
int main(void){struct xemu_console s={0};
 for(int round=0;round<256;++round){
  for(mode=0;mode<=8;++mode){reset();check(!frontend246_gate(&s));check(!xwn_frontend246_request(false));check(xwn_frontend246_request(true));check(!xwn_frontend246_request(true));check(frontend246_gate(&s));check(frontend246_ready);
   int expect=mode==0?2:mode==8?4:3;check(frontend246_state==expect);
   if(mode==1){check(gl_calls==0&&renderer_calls==0);}else if(mode==2){check(gl_calls==0);}else if(mode==3||mode==4){check(gl_calls==0);}
   int count=gl_calls;
   if(mode!=8){check(frontend246_gate(&s));check(gl_calls==count);check(xwn_frontend246_request(false));}
   check(!frontend246_gate(&s));check(frontend246_state==5);check(!xwn_frontend246_request(false));check(!xwn_frontend246_request(true));check(!frontend246_gate(&s));
   char *r=xwn_frontend246_report();check(strstr(r,"state=5 ready=1")!=NULL);free(r);
  }
  mode=0;reset();pthread_t thread;check(pthread_create(&thread,NULL,actor,&s)==0);check(xwn_frontend246_request(true));
  unsigned i=0;while(qatomic_load_acquire(&frontend246_state)==1){check(++i<10000000);sched_yield();}
  check(qatomic_load_acquire(&frontend246_state)==2);char *r=xwn_frontend246_report();check(strstr(r,"loan=0 bql=0 error=0 texture=42")!=NULL);free(r);
  check(xwn_frontend246_request(false));i=0;while(qatomic_load_acquire(&frontend246_state)==4){check(++i<10000000);sched_yield();}
  check(qatomic_load_acquire(&frontend246_state)==5);qatomic_store_release(&worker_stop,true);check(pthread_join(thread,NULL)==0);
 }
 printf("PASS 2304 fresh logic lifecycles,256 joined actor races,%d checks\n",checks);return 0;
}
