#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <inttypes.h>
#include <stdatomic.h>
#include <pthread.h>
#define X260_CALLBACKS 256u
#define qatomic_load_acquire(p) atomic_load_explicit(p,memory_order_acquire)
#define g_malloc malloc
#define g_free free
static char *g_strdup_printf(const char *f,...) {
    char *p=malloc(65536);assert(p);va_list a;va_start(a,f);int n=vsnprintf(p,65536,f,a);va_end(a);assert(n>=0&&n<65536);return p;
}
typedef struct { _Atomic unsigned done;unsigned reason,count;uint64_t epoch,thread,when,rows[256][4],detail276[256][3]; } X260CPU;
typedef struct { _Atomic unsigned state;unsigned stage,reason;uint64_t worker_thread,started,finished;int64_t deadline;X260CPU cpu[2]; } X260Slot;
typedef struct {X260Slot boundary;} X265State;
typedef struct {_Atomic(X265State *) ledger265;} NV2AState;
/* ACTUAL_GETTER */
static X265State record;static NV2AState device;
static void fill(unsigned count) {
    record.boundary.stage=1;record.boundary.reason=14;record.boundary.worker_thread=7;
    record.boundary.started=10;record.boundary.finished=13;record.boundary.deadline=14;
    X260CPU *a=&record.boundary.cpu[0];a->epoch=1;a->thread=8;a->when=11;a->reason=0;a->count=count;
    for(unsigned i=0;i<count&&i<256;i++) {
        a->rows[i][0]=1000+i;a->rows[i][1]=4096*i;a->rows[i][2]=4096;a->rows[i][3]=(uintptr_t)&device;
        a->detail276[i][0]=123456;a->detail276[i][1]=234567;a->detail276[i][2]=4096*i;
    }
}
static void result(bool available) {
    X265State copy=record;char *p=pgraph_gl_callbacks276_report(&device);
    assert((strstr(p,"available=1")!=NULL)==available);free(p);assert(!memcmp(&copy,&record,sizeof(record)));
}
static void *publish(void *unused) {
    (void)unused;fill(4);atomic_store_explicit(&record.boundary.cpu[0].done,1,memory_order_release);
    atomic_store_explicit(&record.boundary.state,6,memory_order_release);return NULL;
}
int main(int argc,char **argv) {
    assert(argc==2);result(false);atomic_store(&device.ledger265,&record);result(false);
    fill(4);atomic_store(&record.boundary.state,6);result(false);
    atomic_store(&record.boundary.cpu[0].done,1);result(true);
    unsigned checks=4;
    for(unsigned state=0;state<9;state++){atomic_store(&record.boundary.state,state);result(state==6);checks++;}
    atomic_store(&record.boundary.state,6);
    for(unsigned count=0;count<259;count++){fill(count);result(count<=256);checks++;}
    fill(4);record.boundary.cpu[0].reason=5;result(false);checks++;
    fill(4);record.boundary.cpu[0].epoch=3;result(false);checks++;
    fill(4);record.boundary.cpu[0].thread=7;result(false);checks++;
    fill(4);record.boundary.cpu[0].when=15;result(false);checks++;
    fill(4);record.boundary.reason=7;result(false);checks++;
    fill(4);record.boundary.stage=2;result(false);checks++;
    fill(4);record.boundary.deadline=13;result(false);checks++;
    char *buffer=malloc(65536);memset(buffer,0xa5,65536);size_t used=65535;
    assert(!x276_append(buffer,&used,"long") && used==65535);free(buffer);checks++;
    for(unsigned run=0;run<1024;run++) {
        memset(&record,0,sizeof(record));pthread_t worker;assert(!pthread_create(&worker,NULL,publish,NULL));
        for(unsigned poll=0;poll<16;poll++) {
            char *p=pgraph_gl_callbacks276_report(&device);
            assert(strstr(p,"available=0") || (strstr(p,"available=1") && strstr(p,"count=4") && strstr(p,"c3=1003:")));free(p);
        }
        assert(!pthread_join(worker,NULL));result(true);checks+=17;
    }
    fill(256);char *p=pgraph_gl_callbacks276_report(&device);FILE *f=fopen(argv[1],"wb");assert(f);
    assert(fwrite(p,strlen(p),1,f)==1);assert(!fclose(f));free(p);
    printf("PASS %u actual getter checks,1024 release/acquire publication races; no real QEMU jobs\n",checks);
    return 0;
}
