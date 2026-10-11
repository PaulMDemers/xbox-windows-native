#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include "qemu/atomic.h"
#include "nv2a_regs.h"
#define QEMU_CLOCK_REALTIME 0
typedef struct {
 struct {uint32_t regs[0x3000];} pfifo;
 struct {bool waiting_for_nop,waiting_for_flip,waiting_for_context_switch;} pgraph;
 struct {unsigned state,wait_before,wait_after,consume_stop,consume_steps,consume_words;int64_t deadline;} preserve227;
} NV2AState;
#include "budget-actual.inc"
static int64_t clock_value;
static bool fifo_access;
static unsigned calls,delegate_stop;
static bool can_fifo_access(NV2AState *d) {(void)d;return fifo_access;}
static int64_t qemu_clock_get_ns(int clock) {assert(clock==0);return clock_value;}
static void pfifo_run_pusher(NV2AState *d,PFIFOConsume232 *budget) {
 (void)d;calls++;budget->stop=delegate_stop;
}
#include "wait-actual.inc"
#include "consume-actual.inc"
static NV2AState d;
int main(void) {
 uint64_t checks=0,cases=0,empty=0,delegated=0;
 uint32_t pairs[][2]={{0,0},{4,4},{0,4},{4,0},{0xfffffffcu,0xfffffffcu},{4,8}};
 uint32_t method=NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT;
 uint32_t error=NV_PFIFO_CACHE1_DMA_STATE_ERROR;
 uint32_t parser[]={0,method & (~method+1u),error & (~error+1u),0xffcu};
 for(unsigned state=0;state<8;state++)for(int clock=99;clock<=101;clock++)
 for(unsigned waits=0;waits<16;waits++)for(unsigned q=0;q<6;q++)
 for(unsigned p=0;p<4;p++)for(unsigned delegate=5;delegate<=6;delegate++) {
  memset(&d,0,sizeof(d));calls=0;clock_value=clock;delegate_stop=delegate;
  d.preserve227.state=state;d.preserve227.deadline=100;fifo_access=!(waits&1);
  d.pgraph.waiting_for_nop=!!(waits&2);d.pgraph.waiting_for_flip=!!(waits&4);d.pgraph.waiting_for_context_switch=!!(waits&8);
  d.pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]=pairs[q][0];d.pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT]=pairs[q][1];d.pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]=parser[p];
  uint32_t before[0x3000];memcpy(before,d.pfifo.regs,sizeof(before));
  bool alive=state==1 && clock<100;
  bool is_empty=pairs[q][0]==pairs[q][1] && !(parser[p]&(method|error));
  unsigned expected= !alive?1:waits?4:is_empty?0:delegate;
  nv2a_preserve232_consume(&d);
  assert(d.preserve227.consume_stop==expected);checks++;
  assert(calls==(unsigned)(alive && !waits && !is_empty));checks++;
  assert(d.preserve227.wait_before==waits && d.preserve227.wait_after==waits);checks++;
  assert(!d.preserve227.consume_steps && !d.preserve227.consume_words);checks++;
  assert(!memcmp(before,d.pfifo.regs,sizeof(before)));checks++;
  assert(d.preserve227.state==state && d.preserve227.deadline==100);checks++;
  cases++;empty+=alive&&!waits&&is_empty;delegated+=calls;
 }
 assert(empty && delegated);checks++;
 printf("checks=%llu cases=%llu empty_shortcuts=%llu delegated=%llu\n",(unsigned long long)checks,(unsigned long long)cases,(unsigned long long)empty,(unsigned long long)delegated);
 return 0;
}
