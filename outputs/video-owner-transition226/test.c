/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic obligations only. No MMIO, GPU launch or host-issued native grant.
 */
#include "owner.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint32_t checks;
#define CHECK(x) do { checks++;assert(x); } while(0)
static X226Plan plan(uint32_t g)
{
 X226Plan p={0};p.generation=g;p.channel=2;p.old_count=1;p.new_count=2;
 p.census_complete=p.backing_verified=p.backend_supported=p.context_supported=1;
 p.budget=1000;p.old_range[0]=(X226Range){0x10000,0x5000};
 /* Synthetic RAMIN allocation, NOT a proposed physical instance allocation. */
 p.new_range[0]=(X226Range){0x20000,0x1000};p.new_range[1]=(X226Range){0x22000,0x100};return p;
}
static X226Receipt receipt(const X226Owner *o)
{
 X226Receipt r={0};r.generation=o->generation;r.action=o->pending_action;
 r.sequence=o->sequence;r.producers_revoked=r.queue_consumed=1;
 r.backend_finished=r.references_ended=r.exact_private_install=1;
 r.trapped_channel=r.context_channel=o->channel;r.context_valid=r.irq_serviced=1;
 r.owner_restored=1;return r;
}
static void step(X226Owner *o,uint32_t action,uint64_t time)
{
 X226Receipt r;
 CHECK(x226_begin(o,action,time)==X226_ACCEPTED);
 CHECK(o->exposed==1 && o->pending_action==action);
 r=receipt(o);CHECK(x226_receipt(o,&r,time)==X226_ACCEPTED);
 CHECK(o->pending_action==0);
}
static X226Owner ready(uint32_t g)
{
 X226Owner o={0};X226Plan p=plan(g);
 CHECK(x226_prepare(&o,&p,100)==X226_ACCEPTED);
 p.new_range[0].start=0;CHECK(o.plan.new_range[0].start==0x20000);
 step(&o,X226_REVOKE,101);step(&o,X226_RETIRE_OLD,102);
 step(&o,X226_INSTALL,103);step(&o,X226_SERVICE_CONTEXT,104);
 CHECK(o.state==X226_READY);return o;
}
int main(void)
{
 uint32_t i,j;X226Owner o;X226Plan p;X226Receipt r,bad;
 /* Actual225 facts cannot prepare: no complete census/backing/backend service.
  * Twenty-two intact handles and equal pointers do not supply those facts. */
 for(i=0;i<4;i++) {
  o=(X226Owner){0};p=plan(1);
  if(i==0)p.census_complete=0;if(i==1)p.backing_verified=0;
  if(i==2)p.backend_supported=0;if(i==3)p.context_supported=0;
  CHECK(x226_prepare(&o,&p,100)==X226_REFUSED);
  CHECK(o.state==X226_EMPTY && !o.exposed);
 }
 for(i=0;i<100000;i++) {
  o=(X226Owner){0};p=plan(i+1);
  /* Every aligned point inside the entire inherited20KiB is prohibited. */
  p.new_range[0]=(X226Range){0x10000+(i%1280)*16,16};
  CHECK(x226_prepare(&o,&p,100)==X226_REFUSED);
  o=(X226Owner){0};p=plan(i+1);p.new_range[1]=p.new_range[0];
  CHECK(x226_prepare(&o,&p,100)==X226_REFUSED);
 }
 for(i=0;i<8;i++) {
  o=(X226Owner){0};p=plan(1);
  switch(i) {
   case 0:p.generation=0;break;case 1:p.channel=32;break;
   case 2:p.old_count=17;break;case 3:p.new_count=17;break;
   case 4:p.new_range[0]=(X226Range){0xfffffff0u,0x1000};break;
   case 5:p.new_range[0].start++;break;case 6:p.budget=0;break;
   case 7:p.budget=1000001;break;
  }
  CHECK(x226_prepare(&o,&p,100)==X226_REFUSED);
 }
 o=(X226Owner){0};p=plan(1);CHECK(!x226_prepare(&o,&p,UINT64_MAX-500));
 for(i=1;i<=4096;i++) {
  o=ready(i);
  CHECK(!x226_begin(&o,X226_RESTORE,105));
  step(&o,X226_SUBMIT,105);
  CHECK(x226_completion(&o,i,0,106,0)==X226_WAITING);
  CHECK(!x226_completion(&o,i-1,i,107,0));
  CHECK(o.state==X226_SUBMITTED);
  CHECK(x226_completion(&o,i,i,108,0)==X226_ACCEPTED);
  CHECK(o.state==X226_COMPLETED); /* Completion alone cannot release. */
  CHECK(!x226_begin(&o,X226_RESTORE,109));
  step(&o,X226_RETIRE_NEW,109);step(&o,X226_RESTORE,110);
  CHECK(o.state==X226_RELEASED && o.exposed);
  CHECK(!x226_begin(&o,X226_REVOKE,111));CHECK(!x226_cancel(&o));
 }
 /* Every action is marked exposed before any adapter call. Abort or deadline
  * in any pending action is terminal; late exact receipts cannot free it. */
 for(i=1;i<=7;i++)for(j=0;j<3;j++) {
  o=(X226Owner){0};p=plan(55);CHECK(x226_prepare(&o,&p,100));
  if(i>=2)step(&o,X226_REVOKE,101);
  if(i>=3)step(&o,X226_RETIRE_OLD,102);
  if(i>=4)step(&o,X226_INSTALL,103);
  if(i>=5)step(&o,X226_SERVICE_CONTEXT,104);
  if(i>=6) {step(&o,X226_SUBMIT,105);CHECK(x226_completion(&o,55,55,106,0));}
  if(i>=7)step(&o,X226_RETIRE_NEW,107);
  CHECK(x226_begin(&o,i,108));r=receipt(&o);
  if(j==0)CHECK(!x226_cancel(&o));
  if(j==1)CHECK(!x226_tick(&o,1100));
  if(j==2)CHECK(!x226_tick(&o,107));
  CHECK(o.state==X226_QUARANTINED);
  CHECK(!x226_receipt(&o,&r,109));CHECK(!x226_cancel(&o));
 }
 /* Test missing individual retirement obligations separately. */
 for(i=0;i<4;i++) {
  o=(X226Owner){0};p=plan(5);CHECK(x226_prepare(&o,&p,100));
  step(&o,X226_REVOKE,101);CHECK(x226_begin(&o,X226_RETIRE_OLD,102));
  r=receipt(&o);
  if(i==0)r.producers_revoked=0;if(i==1)r.queue_consumed=0;
  if(i==2)r.backend_finished=0;if(i==3)r.references_ended=0;
  CHECK(!x226_receipt(&o,&r,103));CHECK(o.state==X226_QUARANTINED);
 }
 for(i=0;i<5;i++) {
  o=(X226Owner){0};p=plan(5);CHECK(x226_prepare(&o,&p,100));
  step(&o,X226_REVOKE,101);step(&o,X226_RETIRE_OLD,102);step(&o,X226_INSTALL,103);
  CHECK(x226_begin(&o,X226_SERVICE_CONTEXT,104));r=receipt(&o);
  if(i==0)r.trapped_channel++;if(i==1)r.context_channel++;
  if(i==2)r.context_valid=0;if(i==3)r.irq_serviced=0;if(i==4)r.status=1;
  CHECK(!x226_receipt(&o,&r,105));CHECK(o.state==X226_QUARANTINED);
 }
 o=(X226Owner){0};p=plan(9);CHECK(x226_prepare(&o,&p,100));
 CHECK(x226_begin(&o,X226_REVOKE,101));r=receipt(&o);
 for(i=0;i<3;i++) {bad=r;if(i==0)bad.generation++;if(i==1)bad.sequence++;if(i==2)bad.action++;
  CHECK(!x226_receipt(&o,&bad,102));CHECK(o.state==X226_REVOKING && o.pending_action);}
 CHECK(x226_receipt(&o,&r,103));CHECK(!x226_receipt(&o,&r,104));
 o=ready(9);step(&o,X226_SUBMIT,105);CHECK(!x226_completion(&o,9,8,106,0));
 CHECK(o.state==X226_QUARANTINED);CHECK(!x226_completion(&o,9,9,107,0));
 o=ready(9);step(&o,X226_SUBMIT,105);CHECK(!x226_completion(&o,9,9,106,1));
 CHECK(o.state==X226_QUARANTINED);
 o=(X226Owner){0};p=plan(9);CHECK(x226_prepare(&o,&p,100));
 CHECK(x226_cancel(&o));CHECK(o.state==X226_RELEASED && !o.exposed);
 printf("checks=%u synthetic_cycles=4096 inherited_overlap_cases=100000 private_overlap_cases=100000 native_grants=0\n",checks);
 return 0;
}
