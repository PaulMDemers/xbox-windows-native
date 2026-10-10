/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "owner.h"
static int valid_range(X226Range r)
{
 return r.bytes && !(r.start & 15u) && !(r.bytes & 15u) &&
        (uint64_t)r.start+r.bytes <= 0x100000u;
}
static int overlap(X226Range a, X226Range b)
{
 return a.start < (uint64_t)b.start+b.bytes &&
        b.start < (uint64_t)a.start+a.bytes;
}
static int deadline(X226Owner *o, uint64_t now)
{
 if(now<o->last_time || now>=o->deadline) {
  if(o->exposed)o->state=X226_QUARANTINED;
  return 0;
 }
 o->last_time=now;return 1;
}
int x226_prepare(X226Owner *o, const X226Plan *p, uint64_t now)
{
 uint32_t i,j;
 if(!o || !p || o->state!=X226_EMPTY || !p->generation || p->channel>31 ||
    p->census_complete!=1 || p->backing_verified!=1 ||
    p->backend_supported!=1 || p->context_supported!=1 ||
    !p->budget || p->budget>1000000 || now>UINT64_MAX-p->budget ||
    !p->old_count || p->old_count>X226_MAX_RANGES ||
    !p->new_count || p->new_count>X226_MAX_RANGES)return X226_REFUSED;
 for(i=0;i<p->old_count;i++)if(!valid_range(p->old_range[i]))return X226_REFUSED;
 for(i=0;i<p->new_count;i++) {
  if(!valid_range(p->new_range[i]))return X226_REFUSED;
  for(j=0;j<p->old_count;j++)if(overlap(p->new_range[i],p->old_range[j]))return X226_REFUSED;
  for(j=0;j<i;j++)if(overlap(p->new_range[i],p->new_range[j]))return X226_REFUSED;
 }
 o->state=X226_PREPARED;o->generation=p->generation;o->channel=p->channel;
 o->pending_action=0;o->sequence=0;o->exposed=0;
 o->plan=*p;
 o->last_time=now;o->deadline=now+p->budget;return X226_ACCEPTED;
}
int x226_begin(X226Owner *o, uint32_t action, uint64_t now)
{
 uint32_t expected,next;
 if(!o || o->pending_action || o->state==X226_QUARANTINED ||
    o->state==X226_RELEASED || o->state==X226_EMPTY)return X226_REFUSED;
 switch(action) {
 case X226_REVOKE:expected=X226_PREPARED;next=X226_REVOKING;break;
 case X226_RETIRE_OLD:expected=X226_REVOKING;next=X226_RETIRING;break;
 case X226_INSTALL:expected=X226_RETIRING;next=X226_INSTALLING;break;
 case X226_SERVICE_CONTEXT:expected=X226_INSTALLING;next=X226_CONTEXT;break;
 case X226_SUBMIT:expected=X226_READY;next=X226_SUBMITTED;break;
 case X226_RETIRE_NEW:expected=X226_COMPLETED;next=X226_DRAINING;break;
 case X226_RESTORE:expected=X226_DRAINING;next=X226_RESTORING;break;
 default:return X226_REFUSED;
 }
 if(o->state!=expected || !deadline(o,now))return X226_REFUSED;
 if(o->sequence==UINT32_MAX) {o->state=X226_QUARANTINED;return X226_REFUSED;}
 /* Record exposure BEFORE the adapter's first producer/configuration store.
  * Even a failed/uncertain first write can retain references. */
 o->exposed=1;o->state=next;o->sequence++;o->pending_action=action;
 return X226_ACCEPTED;
}
int x226_receipt(X226Owner *o, const X226Receipt *r, uint64_t now)
{
 int valid=0;
 if(!o || !r || !o->pending_action || o->state==X226_QUARANTINED)return X226_REFUSED;
 /* A stale unrelated reply cannot satisfy or destroy a current request. */
 if(r->generation!=o->generation || r->sequence!=o->sequence ||
    r->action!=o->pending_action)return X226_REFUSED;
 if(!deadline(o,now))return X226_REFUSED;
 if(r->status) {o->state=X226_QUARANTINED;return X226_REFUSED;}
 switch(r->action) {
 case X226_REVOKE:valid=r->producers_revoked==1;break;
 case X226_RETIRE_OLD:
 case X226_RETIRE_NEW:
  valid=r->producers_revoked==1 && r->queue_consumed==1 &&
        r->backend_finished==1 && r->references_ended==1;break;
 case X226_INSTALL:valid=r->exact_private_install==1;break;
 case X226_SERVICE_CONTEXT:
  valid=r->trapped_channel==o->channel && r->context_valid==1 &&
        r->context_channel==o->channel && r->irq_serviced==1;break;
 case X226_SUBMIT:valid=1;break;
 case X226_RESTORE:valid=r->owner_restored==1 && r->references_ended==1;break;
 default:break;
 }
 if(!valid) {o->state=X226_QUARANTINED;return X226_REFUSED;}
 o->pending_action=0;
 if(r->action==X226_SERVICE_CONTEXT)o->state=X226_READY;
 if(r->action==X226_RESTORE)o->state=X226_RELEASED;
 return X226_ACCEPTED;
}
int x226_completion(X226Owner *o, uint32_t generation, uint32_t token,
                    uint64_t now, int fault)
{
 if(!o || o->state!=X226_SUBMITTED || o->pending_action ||
    generation!=o->generation)return X226_REFUSED;
 if(!deadline(o,now))return X226_REFUSED;
 if(fault || (token && token!=o->generation)) {
  o->state=X226_QUARANTINED;return X226_REFUSED;
 }
 if(!token)return X226_WAITING;
 o->state=X226_COMPLETED;return X226_ACCEPTED;
}
int x226_tick(X226Owner *o, uint64_t now)
{
 if(!o || o->state==X226_EMPTY || o->state==X226_RELEASED ||
    o->state==X226_QUARANTINED)return X226_REFUSED;
 return deadline(o,now)?X226_WAITING:X226_REFUSED;
}
int x226_cancel(X226Owner *o)
{
 if(!o || o->state==X226_EMPTY || o->state==X226_RELEASED)return X226_REFUSED;
 if(o->state==X226_PREPARED && !o->exposed) {
  o->state=X226_RELEASED;return X226_ACCEPTED;
 }
 o->state=X226_QUARANTINED;return X226_REFUSED;
}
