/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "probe.h"
struct context675 {const struct ops675 *ops;struct record675 *r;};
static unsigned read_smc(void *p,unsigned port,unsigned width){
 struct context675 *c=p;return c->ops->in(c->ops->p,port,width);
}
static void write_smc(void *p,unsigned port,unsigned width,unsigned value){
 struct context675 *c=p;c->ops->out(c->ops->p,port,width,value);
}
static int refuse_wait(void *p,unsigned us){
 struct context675 *c=p;c->r->wait_refusals++;c->r->last_wait_us=us;
 return 1;
}
static uint32_t observe_tick(void *p){
 struct context675 *c=p;struct record675 *r=c->r;
 uint32_t value=c->ops->ticks(c->ops->p);
 if(r->stored_samples<SAMPLES675)r->samples[r->stored_samples++]=value;
 r->last_sample=value;r->total_samples++;return value;
}
unsigned probe675(const struct ops675 *o,struct record675 *r,unsigned us){
 struct context675 context={o,r};
 const struct smc658 smc={&context,read_smc,write_smc,refuse_wait};
 const struct io656 timer={&context,0,0,0,observe_tick,0};
 unsigned e;
 if(!o || !r || !o->flags || !o->ticks || !o->in || !o->out || !us || us>1000)return ARG675;
 if(!__sync_bool_compare_and_swap(&r->phase,ZERO675,CLAIMED675))return BUSY675;
 r->request_us=us;r->flags_before=o->flags(o->p);
 if(r->flags_before&512){r->error=IF675;return IF675;}
 /* A visible progress pattern replaces the old initial dark pause. Do not
  * time it in software: SMC hardware owns its alternating green/amber mask. */
 r->phase=ENTRY675;
 r->entry_error=write658(&smc,8,0x5f,&r->smc);
 if(!r->entry_error)r->entry_error=write658(&smc,7,1,&r->smc);
 if(r->entry_error){r->error=ENTRY_SMC675;return ENTRY_SMC675;}
 r->entry_complete=1;r->flags_after_entry=o->flags(o->p);
 if(r->flags_after_entry&512){r->error=IF675;return IF675;}
 r->phase=TIMER675;r->timer_called=1;
 r->timer_error=(unsigned)delay656(&timer,&r->timer_accounting,us);
 r->flags_after=o->flags(o->p);
 if(r->flags_after&512){r->error=IF675;return IF675;}
 /* Raw return retained even if final SMC signaling fails. An error here is
  * not permission to restart transport or change the timer implementation. */
 r->final_mask=r->timer_error==N656_OK?0x0f:r->timer_error==N656_TIMER?0xa5:0xf5;
 r->phase=FINAL675;
 e=write658(&smc,8,r->final_mask,&r->smc);r->final_error=e;
 if(e){r->error=FINAL_SMC675;return FINAL_SMC675;}
 r->final_complete=1;r->phase=DONE675;return OK675;
}
