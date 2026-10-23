/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "phase.h"
static int same(const uint8_t *a,const uint8_t *b){
 unsigned i;for(i=0;i<BYTES669;i++)if(a[i]!=b[i])return 0;return 1;
}
unsigned seal669(struct record669 *r,const uint8_t *packet,unsigned n,unsigned encoded){
 unsigned i;
 if(!r || !packet || n!=BYTES669 || encoded!=1)return ARG669;
 if(!__sync_bool_compare_and_swap(&r->phase,EMPTY669,SEALING669))return BUSY669;
 /* No callback, allocator or I/O while the original record is sealed. */
 for(i=0;i<BYTES669;i++)r->original[i]=r->transport[i]=packet[i];
 __sync_lock_test_and_set(&r->phase,READY669);return OK669;
}
unsigned run669(struct record669 *r,const struct ops669 *o){
 unsigned status;
 if(!r || !o || !o->enter || !o->flags || !o->send)return ARG669;
 if(!__sync_bool_compare_and_swap(&r->phase,READY669,CLAIMED669))return BUSY669;
 r->enter_called=1;
 r->enter_error=(unsigned)o->enter(o->p,&r->original_flags,&r->transport_flags);
 if(!r->enter_error && r->transport_flags==(r->original_flags&~0x200u))r->flags_valid=1;
 else r->faults|=F_GUARD669;
 r->final_flags=o->flags(o->p);
 if(r->final_flags&0x200u)r->faults|=F_IF669;
 if(!same(r->original,r->transport))r->faults|=F_PACKET669;
 if(r->faults){status=GUARD669;goto held;}
 r->send_called=1;
 r->send_error=(unsigned)o->send(o->p,r->transport,BYTES669,&r->result);
 r->final_flags=o->flags(o->p);
 if(r->final_flags&0x200u)r->faults|=F_IF669;
 if(!same(r->original,r->transport))r->faults|=F_PACKET669;
 if(r->result.used && (!r->result.safe || r->result.cleanup_error))r->faults|=F_UNSAFE669;
 if(r->result.used>1 || r->result.safe>1 || r->result.completed>3 ||
    (r->result.admission && r->result.used) ||
    (!r->result.used && (r->result.safe || r->result.completed || r->result.cleanup_error)))r->faults|=F_RESULT669;
 if(r->faults&F_UNSAFE669)status=UNSAFE669;
 else if(r->faults&F_IF669)status=IF_CHANGED669;
 else if(r->faults&F_PACKET669)status=PACKET_CHANGED669;
 else if(r->faults&F_RESULT669)status=INCONSISTENT669;
 else if(r->result.admission)status=ADMISSION669;
 else if(!r->result.used)status=NO_USE669;
 else if(r->send_error || r->result.error || r->result.completed!=3)status=SEND_FAILED669;
 else status=SENT669;
held:
 r->status=status;__sync_lock_test_and_set(&r->phase,HELD669);return status;
}
