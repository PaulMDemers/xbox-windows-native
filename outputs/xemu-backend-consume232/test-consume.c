#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#define qemu_build_assert(condition) _Static_assert(condition, "atomic width")
#include "qemu/atomic.h"
static unsigned ctz32(uint32_t x) { assert(x); return __builtin_ctz(x); }
#include "nv2a_regs.h"
#define MIN(a,b) ((a)<(b)?(a):(b))
#define NV2A_DPRINTF(...) ((void)0)
#define QEMU_CLOCK_REALTIME 0
typedef uint64_t hwaddr;
typedef struct {
    struct {unsigned state,consume_stop,consume_steps,consume_words,wait_before,wait_after;int64_t deadline;} preserve227;
    struct {uint32_t regs[0x2000];} pfifo;
    struct {uint32_t regs_[0x3000];bool waiting_for_nop,waiting_for_flip,waiting_for_context_switch;} pgraph;
} NV2AState;
static NV2AState d;
static uint32_t dma[32768];
static int64_t now;
static int puller_mode;
static uint64_t checks;
static int64_t qemu_clock_get_ns(int clock) { assert(clock==0);return now; }
static uint32_t ldl_le_p(void *p) { uint32_t word;memcpy(&word,p,4);return word; }
static uint8_t *nv_dma_map(NV2AState *p,hwaddr instance,hwaddr *len) {
    assert(p==&d && instance==0);*len=sizeof(dma);return (uint8_t*)dma;
}
/* Explicit PGRAPH adapter: return the requested batch count or a chosen failure.
 * Actual DMA parser/register masks/atomic macros and bounded wrapper are used. */
static ssize_t pfifo_run_puller(NV2AState *p,uint32_t method,uint32_t parameter,
                               uint32_t *parameters,size_t words,size_t lookahead) {
    (void)method;(void)parameter;assert(p==&d);assert(words<=lookahead && words>0);
    assert(parameters>=(uint32_t*)dma && parameters+lookahead<=dma+32768);
    if(puller_mode==1)return -1;
    if(puller_mode==2)return 0;
    if(puller_mode==3)return lookahead+1;
    return words;
}
#include "pusher-actual.inc"
static void check(bool good) { assert(good);checks++; }
static void reset(void) {
    memset(&d,0,sizeof(d));memset(dma,0,sizeof(dma));now=99;puller_mode=0;
    d.preserve227.state=1;d.preserve227.deadline=100;
    d.pgraph.regs_[NV_PGRAPH_FIFO]=NV_PGRAPH_FIFO_ACCESS;
    d.pfifo.regs[NV_PFIFO_CACHE1_PUSH0]=NV_PFIFO_CACHE1_PUSH0_ACCESS;
    d.pfifo.regs[NV_PFIFO_CACHE1_PUSH1]=NV_PFIFO_CACHE1_PUSH1_MODE;
    d.pfifo.regs[NV_PFIFO_MODE]=1;
    d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUSH]=NV_PFIFO_CACHE1_DMA_PUSH_ACCESS;
    d.pfifo.regs[NV_PFIFO_CACHE1_PULL0]=NV_PFIFO_CACHE1_PULL0_ACCESS;
}
static void packet(unsigned count) {
    dma[0]=(count<<18)|0x100;
    for(unsigned i=1;i<=count;i++)dma[i]=i+100;
    d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]=(count+1)*4;
}
static PFIFOConsume232 run(unsigned steps,unsigned words) {
    PFIFOConsume232 b={.steps_left=steps,.words_left=words,.deadline=100};pfifo_run_pusher(&d,&b);return b;
}
int main(void) {
    reset();nv2a_preserve232_consume(&d);check(!d.preserve227.consume_stop && !d.preserve227.consume_words);
    for(unsigned bit=0;bit<4;bit++) {
        reset();packet(10);
        if(bit==0)d.pgraph.regs_[NV_PGRAPH_FIFO]=0;
        if(bit==1)d.pgraph.waiting_for_nop=true;
        if(bit==2)d.pgraph.waiting_for_flip=true;
        if(bit==3)d.pgraph.waiting_for_context_switch=true;
        nv2a_preserve232_consume(&d);
        check(d.preserve227.consume_stop==4 && d.preserve227.consume_words==0 && d.preserve227.consume_steps==0);
        check(d.preserve227.wait_before==(1u<<bit) && d.preserve227.wait_after==(1u<<bit));
        check(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==0);
    }
    reset();dma[0]=1;d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]=4;
    PFIFOConsume232 b=run(7,100);check(b.stop==3 && b.steps==7 && b.words==7 && !d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]);
    reset();dma[0]=1;d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]=4;
    b=run(100,3);check(b.stop==2 && b.steps==3 && b.words==3 && !d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]);
    for(unsigned cause=0;cause<3;cause++) {
        reset();packet(10);
        if(cause==0)d.pfifo.regs[NV_PFIFO_CACHE1_PUSH0]=0;
        if(cause==1)d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUSH]=0;
        if(cause==2)d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUSH]|=NV_PFIFO_CACHE1_DMA_PUSH_STATUS;
        b=run(100,100);check(b.stop==5 && b.words==0 && !d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]);
    }
    reset();packet(10);now=100;b=run(100,100);check(b.stop==1 && b.words==0);
    reset();packet(10);d.preserve227.state=5;b=run(100,100);check(b.stop==1 && b.words==0);
    reset();packet(10);d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]=2;b=run(100,100);check(b.stop==7 && b.words==0);
    reset();packet(10);SET_MASK(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE],NV_PFIFO_CACHE1_DMA_STATE_ERROR,3);
    b=run(100,100);check(b.stop==6 && b.words==0 && GET_MASK(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE],NV_PFIFO_CACHE1_DMA_STATE_ERROR)==3);
    for(unsigned mode=1;mode<=3;mode++) {
        reset();packet(10);puller_mode=mode;b=run(100,100);
        check(b.stop==(mode==1?4:8) && b.words==1 && d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==4);
    }
    reset();dma[0]=(3<<18)|0x100;d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]=4;
    nv2a_preserve232_consume(&d);check(d.preserve227.consume_stop==9 && d.preserve227.consume_words==1);
    for(unsigned round=0;round<10000;round++) {
        unsigned count=1+round%1000,budget=1+(round*37)%1500;
        reset();packet(count);b=run(32768,budget);
        unsigned expected=MIN(budget,count+1);
        check(b.words==expected && b.words<=budget && b.steps<=32768);
        check(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==expected*4);
        check(GET_MASK(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE],NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT)==count-(expected-1));
        check(b.stop==(budget<count+1?2:0));
        if(budget>=count+1) {
            uint32_t state=d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE],dcount=d.pfifo.regs[NV_PFIFO_CACHE1_DMA_DCOUNT];
            reset();packet(count);pfifo_run_pusher(&d,NULL);
            check(d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==(count+1)*4 && d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]==state && d.pfifo.regs[NV_PFIFO_CACHE1_DMA_DCOUNT]==dcount);
        }
    }
    printf("checks=%llu packet_cases=10000 ordinary_comparisons=covered jump_budgets=covered native_grants=0\n",(unsigned long long)checks);
}
