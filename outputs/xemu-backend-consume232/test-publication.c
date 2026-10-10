#define _XOPEN_SOURCE 700
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <pthread.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <inttypes.h>
#define qemu_build_assert(condition) _Static_assert(condition, "QEMU atomic register width")
#include "qemu/atomic.h"

/* Host-only formatting adapter; the actual QEMU atomic headers stay intact. */
typedef struct { char *str; size_t len; } GString;
static GString *g_string_new(const char *unused) {
    assert(!unused);GString *s=calloc(1,sizeof(*s));assert(s);
    s->str=calloc(1,1);assert(s->str);return s;
}
static void g_string_append_printf(GString *s,const char *format,...) {
    va_list a,b;va_start(a,format);va_copy(b,a);
    int n=vsnprintf(NULL,0,format,a);va_end(a);assert(n>=0);
    s->str=realloc(s->str,s->len+(size_t)n+1);assert(s->str);
    assert(vsnprintf(s->str+s->len,(size_t)n+1,format,b)==n);va_end(b);s->len+=(size_t)n;
}
static char *g_string_free(GString *s,bool release) {
    assert(!release);char *p=s->str;free(s);return p;
}
#define g_free free
#define g_ascii_strtoull strtoull

typedef struct {
    struct {
        unsigned state, surfaces, dirty, downloaded, error, reason;
        unsigned consume_stop,consume_steps,consume_words,wait_before,wait_after;
        uint64_t bytes;
        uint32_t request_fifo[10], gate_fifo[10];
        int64_t deadline;
        bool old_halt;
    } preserve227;
    struct { bool halt; } pfifo;
} NV2AState;
typedef NV2AState Object;
typedef void Error;
#define NV2A_DEVICE(p) (p)
#define QEMU_CLOCK_REALTIME 0
static NV2AState d;
static int64_t now=99;
static uint64_t checks;
static pthread_barrier_t barrier;
static int64_t qemu_clock_get_ns(int clock) { assert(clock==0); return now; }
/* Actual model functions, with only surrounding QEMU object/clock adapters. */
#include "publication-actual.inc"
static void check(bool ok) { assert(ok); checks++; }
static uint64_t field(const char *s,const char *name) {
    char key[64];snprintf(key,sizeof(key),"%s=",name);
    const char *p=strstr(s,key);assert(p);return g_ascii_strtoull(p+strlen(key),NULL,10);
}
static void reset(unsigned state) {
    memset(&d,0,sizeof(d));d.preserve227.deadline=100;
    d.pfifo.halt=true;qatomic_store_release(&d.preserve227.state,state);
}
static void tuple(unsigned n) {
    qatomic_set(&d.preserve227.surfaces,n);
    qatomic_set(&d.preserve227.dirty,n+1);
    qatomic_set(&d.preserve227.downloaded,n+2);
    qatomic_set(&d.preserve227.bytes,((uint64_t)n<<32)+0x12345678);
    qatomic_set(&d.preserve227.error,n+3);
    qatomic_set(&d.preserve227.reason,n+4);
    qatomic_set(&d.preserve227.consume_stop,n+15);
    qatomic_set(&d.preserve227.consume_steps,n+16);
    qatomic_set(&d.preserve227.consume_words,n+17);
    qatomic_set(&d.preserve227.wait_before,n+18);
    qatomic_set(&d.preserve227.wait_after,n+19);
    for(unsigned i=0;i<10;i++) qatomic_set(&d.preserve227.gate_fifo[i],n+5+i);
}
static void verify(const char *s,unsigned n) {
    check(field(s,"tuple_published")==1);
    check(field(s,"surfaces")==n && field(s,"dirty")==n+1 && field(s,"downloaded")==n+2);
    check(field(s,"bytes")==((uint64_t)n<<32)+0x12345678);
    check(field(s,"error")==n+3 && field(s,"reason")==n+4);
    check(field(s,"consume_stop")==n+15 && field(s,"consume_steps")==n+16 && field(s,"consume_words")==n+17 && field(s,"wait_before")==n+18 && field(s,"wait_after")==n+19);
    for(unsigned i=0;i<10;i++) {char key[32];snprintf(key,sizeof(key),"gate%u",i);check(field(s,key)==n+5+i);}
}
static void hidden(const char *s) {
    check(field(s,"tuple_published")==0);
    for(const char **p=(const char *[]) {"surfaces","dirty","downloaded","bytes","error","reason","consume_stop","consume_steps","consume_words","wait_before","wait_after",NULL};*p;p++) check(field(s,*p)==0);
    for(unsigned i=0;i<10;i++) {char key[32];snprintf(key,sizeof(key),"gate%u",i);check(field(s,key)==0);}
}
static void *worker(void *unused) {
    (void)unused;
    for(unsigned i=0;i<100000;i++) {
        pthread_barrier_wait(&barrier);tuple(i+1);nv2a_preserve227_finish(&d,3);
        pthread_barrier_wait(&barrier);
    }
    return NULL;
}
static void *reader(void *unused) {
    (void)unused;
    for(unsigned i=0;i<100000;i++) {
        pthread_barrier_wait(&barrier);
        char *s=preserve227_report(&d,NULL);g_free(s);
        unsigned state=qatomic_load_acquire(&d.preserve227.state);
        if(state==1 || state==2) qatomic_cmpxchg(&d.preserve227.state,state,5);
        pthread_barrier_wait(&barrier);
    }
    return NULL;
}
static void *publication_reader(void *unused) {
    (void)unused;
    for(unsigned i=0;i<10000;i++) {
        pthread_barrier_wait(&barrier);
        while(qatomic_load_acquire(&d.preserve227.state)!=3) {}
        /* Actual report's acquire establishes visibility of the mutable tuple.
         * Main verifies contents after the reader saves the report. */
        char *s=preserve227_report(&d,NULL);
        assert(field(s,"bytes")==((uint64_t)(i+1)<<32)+0x12345678);
        assert(field(s,"request9")==i+9);
        g_free(s);pthread_barrier_wait(&barrier);
    }
    return NULL;
}
int main(void) {
    for(unsigned state=1;state<=2;state++) for(unsigned result=3;result<=6;result++)
    for(unsigned old=0;old<=1;old++) for(unsigned time=99;time<=101;time++) {
        reset(state);d.preserve227.old_halt=old;now=time;tuple(37);
        nv2a_preserve227_finish(&d,result);
        unsigned expected=time>=100?5:result;
        check(qatomic_load_acquire(&d.preserve227.state)==expected);
        check(qatomic_read(&d.pfifo.halt)==((expected==3 || expected==4)?old:true));
        char *s=preserve227_report(&d,NULL);
        if(expected==3 || expected==4 || expected==6) verify(s,37);else hidden(s);
        g_free(s);
    }
    for(unsigned state=0;state<=7;state++) if(state!=1 && state!=2) {
        reset(state);tuple(77);now=101;nv2a_preserve227_finish(&d,3);
        check(qatomic_load_acquire(&d.preserve227.state)==state && qatomic_read(&d.pfifo.halt));
        char *s=preserve227_report(&d,NULL);
        if(state==3 || state==4 || state==6) verify(s,77);else hidden(s);g_free(s);
    }
    reset(1);now=101;char *s=preserve227_report(&d,NULL);hidden(s);g_free(s);
    tuple(999);nv2a_preserve227_finish(&d,3);s=preserve227_report(&d,NULL);hidden(s);g_free(s);
    check(qatomic_load_acquire(&d.preserve227.state)==5 && qatomic_read(&d.pfifo.halt));
    now=99;assert(!pthread_barrier_init(&barrier,NULL,3));pthread_t a,b;
    assert(!pthread_create(&a,NULL,worker,NULL));assert(!pthread_create(&b,NULL,reader,NULL));
    unsigned completed=0,expired=0;
    for(unsigned i=0;i<100000;i++) {
        reset(1+i%2);pthread_barrier_wait(&barrier);pthread_barrier_wait(&barrier);
        unsigned state=qatomic_load_acquire(&d.preserve227.state);
        check((state==3 && !qatomic_read(&d.pfifo.halt)) || (state==5 && qatomic_read(&d.pfifo.halt)));
        s=preserve227_report(&d,NULL);if(state==3)verify(s,i+1);else hidden(s);g_free(s);
        completed+=state==3;expired+=state==5;
    }
    assert(!pthread_join(a,NULL) && !pthread_join(b,NULL));assert(!pthread_barrier_destroy(&barrier));
    assert(!pthread_barrier_init(&barrier,NULL,2));assert(!pthread_create(&a,NULL,publication_reader,NULL));
    for(unsigned i=0;i<10000;i++) {
        reset(0);pthread_barrier_wait(&barrier);
        for(unsigned j=0;j<10;j++)d.preserve227.request_fifo[j]=i+j;
        qatomic_store_release(&d.preserve227.state,1);
        tuple(i+1);nv2a_preserve227_finish(&d,3);pthread_barrier_wait(&barrier);checks+=2;
    }
    assert(!pthread_join(a,NULL));assert(!pthread_barrier_destroy(&barrier));
    printf("checks=%" PRIu64 " concurrent_pairs=100000 publication_pairs=10000 completed=%u timed_out=%u native_grants=0\n",checks,completed,expired);
}
