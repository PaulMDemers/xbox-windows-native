/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "signal672.h"
struct code672 classify672(const struct record669 *r){
 struct code672 c={INVALID672,1};
 if(!r || r->phase!=HELD669 || r->status> SENT669 ||
    r->result.admission>5 || r->result.used>1 || r->result.safe>1 ||
    r->result.completed>3 || r->result.error>11 ||
    r->result.cleanup_error>11 || r->send_error>11 || r->faults>31)return c;
 c.kind=WRAPPER672;c.value=r->status;
 /* Report an exact field only when the lifecycle classified that category.
  * Contradictory or incomplete outcomes remain the exact wrapper status. */
 if(r->status==UNSAFE669 && r->result.used && r->result.cleanup_error){
  c.kind=CLEANUP672;c.value=r->result.cleanup_error;
 }else if(r->status==ADMISSION669 && !r->faults && r->result.admission && !r->result.used){
  c.kind=ADMISSION672;c.value=r->result.admission;
 }else if(r->status==SEND_FAILED669 && !r->faults){
  if(r->send_error){c.kind=SEND672;c.value=r->send_error;}
  else if(r->result.error){c.kind=NATIVE672;c.value=r->result.error;}
 }else if(r->status==SENT669){
  if(r->faults || !r->enter_called || !r->send_called || !r->flags_valid ||
     r->enter_error || r->send_error || r->result.admission ||
     r->result.used!=1 || r->result.safe!=1 || r->result.completed!=3 ||
     r->result.error || r->result.cleanup_error || (r->final_flags&512)){
   c.kind=INVALID672;c.value=2;
  }else{c.kind=SUCCESS672;c.value=0;}
 }
 return c;
}
static unsigned claim(const struct smc658 *io,struct emission672 *r){
 if(!r || !io || !io->in || !io->out || !io->delay)return 5;
 if(!__sync_bool_compare_and_swap(&r->used,0,1))return 6;
 return 0;
}
static unsigned led(const struct smc658 *io,struct emission672 *r,unsigned reg,unsigned value){
 r->steps++;r->error=write658(io,reg,value,&r->smc);return r->error;
}
static unsigned pause_ms(const struct smc658 *io,struct emission672 *r,unsigned ms){
 unsigned i;r->pauses++;
 /* delay656 accepts at most 1000us; never ask it for a long interval. */
 for(i=0;i<ms;i++){
  r->milliseconds++;
  if(io->delay(io->p,1000)){r->error=1;return 1;}
 }
 return 0;
}
#define TRY672(x) do{unsigned e=(x);if(e)return e;}while(0)
unsigned marker672(const struct smc658 *io,struct emission672 *r){
 TRY672(claim(io,r));
 TRY672(led(io,r,8,0));TRY672(led(io,r,7,1));
 TRY672(pause_ms(io,r,2000));TRY672(led(io,r,8,0x05));
 TRY672(pause_ms(io,r,8000));TRY672(led(io,r,8,0));
 r->complete=1;return 0;
}
unsigned report672(const struct smc658 *io,struct emission672 *r,struct code672 c){
 static const unsigned masks[]={0x50,0xa5,0x55,0x5f,0xf5,0x0f,0xf0};
 unsigned round,i;
 /* No saturation: an out-of-range code is rejected without any I/O. */
 if(c.kind>INVALID672 || c.value>11 || (c.kind==SUCCESS672 && c.value))return 5;
 TRY672(claim(io,r));
 TRY672(led(io,r,8,0));TRY672(led(io,r,7,1));
 for(round=0;round<2;round++){
  TRY672(pause_ms(io,r,2000));TRY672(led(io,r,8,masks[c.kind]));
  TRY672(pause_ms(io,r,6000));TRY672(led(io,r,8,0));
  TRY672(pause_ms(io,r,2000));
  /* Slow solid-red pulses: count minus one is the exact selected value. */
  for(i=0;i<=c.value;i++){
   TRY672(led(io,r,8,0xf0));TRY672(pause_ms(io,r,500));
   TRY672(led(io,r,8,0));TRY672(pause_ms(io,r,500));
  }
 }
 TRY672(led(io,r,8,masks[c.kind]));r->complete=1;return 0;
}
