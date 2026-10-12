#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <errno.h>
#include "release.h"
#define X265_ROWS 180000u
#define X265_COLUMNS 8u
#define MIN(a,b) ((a)<(b)?(a):(b))
#define X265_PAGE 256u
typedef struct{uint64_t (*rows)[8];unsigned count,capacity,overflow;}X265Rows;
typedef struct X280Transaction X280Transaction;
typedef struct X265State{bool textures278;uint64_t allocations278[4];X265Rows ledger;struct{unsigned state,reason;uint64_t worker_thread;}boundary;X280Transaction *transaction280;unsigned page,accounting_error,shader_jobs_unknown;}X265State;
#include "transaction.h"
typedef struct{unsigned locked;}Lock;
typedef struct{unsigned type;}Renderer;
typedef struct{X265State *ledger265;unsigned exiting;void *pattern260;struct{unsigned state;}worker247,preserve227;struct{Renderer *renderer;}pgraph;struct{Lock lock;unsigned halt,fifo_cond;}pfifo;}NV2AState;
#define CONFIG_DISPLAY_RENDERER_OPENGL 1
#define qatomic_load_acquire(p) (*(p))
#define qatomic_store_release(p,v) (*(p)=(v))
#define qatomic_read(p) (*(p))
#define qatomic_set(p,v) (*(p)=(v))
#define g_new0(type,n) ((type*)calloc((n),sizeof(type)))
#define g_malloc0_n(n,s) calloc((n),(s))
#define g_free(p) free(p)
typedef struct{unsigned unused;}Error;
static Error error;
static void error_setg(Error **e,const char *text){assert(text&&*text);*e=&error;}
static bool running,frontend=true,armed=true;
static bool runstate_is_running(void){return running;}
static bool xwn_frontend246_closed(void){return frontend;}
static bool pgraph_gl_reuse274_ready(uint64_t worker){return worker&&armed;}
static int qemu_mutex_trylock(Lock *l){if(l->locked)return 1;l->locked=1;return 0;}
static void qemu_mutex_unlock(Lock *l){assert(l->locked);l->locked=0;}
static void qemu_cond_broadcast(unsigned *v){(*v)++;}
static int qemu_strtou64(const char *s,const char **end,int base,uint64_t *out){char *e;errno=0;*out=strtoull(s,&e,base);*end=e;return errno||e==s;}
static unsigned x265_page_count(unsigned n){return (n+255)/256;}
typedef struct{char *str;size_t len;}GString;
static GString *g_string_new(void *unused){(void)unused;GString *s=calloc(1,sizeof(*s));s->str=calloc(65536,1);return s;}
static void g_string_append_printf(GString *s,const char *fmt,...){va_list a;va_start(a,fmt);int n=vsnprintf(s->str+s->len,65536-s->len,fmt,a);va_end(a);assert(n>=0&&(size_t)n<65536-s->len);s->len+=n;}
static void g_string_append(GString *s,const char *v){g_string_append_printf(s,"%s",v);}
static char *g_string_free(GString *s,bool segment){assert(!segment);char *p=s->str;free(s);return p;}
static char *g_strdup(const char *s){return strdup(s);}
static char *g_strdup_printf(const char *fmt,...){char *s=calloc(65536,1);va_list a;va_start(a,fmt);int n=vsnprintf(s,65536,fmt,a);va_end(a);assert(n>=0&&n<65536);return s;}
/* ACTUAL_FUNCTIONS */
static NV2AState d;static Renderer renderer={1};static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static void setup(void){memset(&d,0,sizeof(d));d.pgraph.renderer=&renderer;running=false;frontend=armed=true;}
static void dispose(void){X280Transaction *t=d.ledger265->transaction280;X265State *s[]={t->pre,t->post,t->end};for(unsigned i=0;i<3;i++){free(s[i]->ledger.rows);free(s[i]);}free(t);d.ledger265=NULL;}
int main(void)
{
 const char *valid[]={"control281,0,4096,8192,12288","candidate281,0,4096,8192,12288"};
 for(unsigned mode=0;mode<2;mode++){
  setup();Error *e=NULL;CHECK(x281_request(&d,valid[mode],&e)&&!e);X280Transaction *t=d.ledger265->transaction280;
  CHECK(t&&t->state==1&&t->candidate==mode&&d.pfifo.halt==1&&d.pfifo.fifo_cond==1);
  CHECK(t->pre!=t->post&&t->pre!=t->end&&t->post!=t->end);
  CHECK(t->pre->ledger.capacity==X265_ROWS&&t->post->ledger.capacity==X265_ROWS&&t->end->ledger.capacity==X265_ROWS);
  for(unsigned i=0;i<4;i++)CHECK(t->pre->allocations278[i]==i*4096&&t->post->allocations278[i]==i*4096&&t->end->allocations278[i]==i*4096);
  const char *legacy[]={"capture,1","finish274","seal269","observe276",valid[mode],"finish281"};
  for(unsigned i=0;i<6;i++){e=NULL;CHECK(x281_request(&d,legacy[i],&e)&&e);CHECK(t->state==1);}
  char *text=x281_report(t);CHECK(!strcmp(text,"version=281 state=1"));free(text);
  text=x281_data(t);CHECK(strstr(text,"unavailable=1"));free(text);
  t->pre->boundary.state=t->post->boundary.state=5;t->pre->boundary.worker_thread=91;t->pre->ledger.count=t->post->ledger.count=257;
  t->post->ledger.rows[256][0]=72;t->state=3;d.pfifo.halt=0;
  e=NULL;CHECK(x281_page(&d,"stage281,2,1",&e)&&!e);text=x281_data(t);CHECK(strstr(text,"epoch=2")&&strstr(text,"page=1")&&strstr(text,"r256=72:"));free(text);
  const char *pages[]={"0","end274,0","stage281,0,0","stage281,4,0","stage281,3,0","stage281,2,2","stage281,2,0x","stage281,18446744073709551616,0"};
  for(unsigned i=0;i<8;i++){e=NULL;CHECK(x281_page(&d,pages[i],&e)&&e);}
  e=NULL;CHECK(x281_request(&d,"finish281",&e)&&!e&&t->state==4&&d.pfifo.halt==1&&d.pfifo.fifo_cond==2);
  e=NULL;CHECK(x281_request(&d,"finish281",&e)&&e&&t->state==4);
  t->state=2;text=x281_data(t);CHECK(strstr(text,"unavailable=1"));free(text);
  t->state=6;t->end->boundary.state=6;t->end->ledger.count=1;
  e=NULL;CHECK(x281_page(&d,"stage281,3,0",&e)&&!e);text=x281_data(t);CHECK(strstr(text,"epoch=3"));free(text);
  dispose();
 }
 const char *bad[]={"candidate281,0,0,8192,12288","control281,1,4096,8192,12288","control281,0,4096,8192","candidate281,0,4096,8192,12288x","control281,+0,4096,8192,12288","control281,0,4096,8192,67108864"};
 for(unsigned i=0;i<6;i++){setup();Error *e=NULL;CHECK(x281_request(&d,bad[i],&e)&&e&&!d.ledger265);}
 for(unsigned i=0;i<7;i++){setup();Error *e=NULL;if(i==0)running=true;if(i==1)frontend=false;if(i==2)d.exiting=1;if(i==3)d.pattern260=&d;if(i==4)d.worker247.state=1;if(i==5)d.preserve227.state=1;if(i==6)d.pfifo.lock.locked=1;CHECK(x281_request(&d,valid[0],&e)&&e&&!d.ledger265);}
 setup();Error *e=NULL;CHECK(!x281_request(&d,"capture,1",&e)&&!e);CHECK(!x281_page(&d,"0",&e)&&!e);
 printf("PASS %u actual request/getter/serializer checks; allocator and GLib formatting/locks modeled, no runtime request accepted\n",checks);return 0;
}
