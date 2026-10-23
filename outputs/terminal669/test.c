/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "phase.h"
struct model {struct record669 *r;struct ops669 *ops;unsigned mode,initial,flags,enter,sends,reads,nested;};
static unsigned count;
static int enter(void *p,uint32_t *before,uint32_t *after){
 struct model *m=p;m->enter++;assert(m->r->phase==CLAIMED669);
 *before=m->initial;*after=m->initial&~512u;m->flags=*after;
 if(m->mode==1)return -1;
 if(m->mode==2)*after^=1;
 if(m->mode==3)m->flags|=512;
 if(m->mode==4)m->r->transport[0]^=1;
 if(m->mode==5){assert(run669(m->r,m->ops)==BUSY669);m->nested++;}
 return 0;
}
static uint32_t flags(void *p){struct model *m=p;m->reads++;return m->flags;}
static int send(void *p,const uint8_t *b,unsigned n,struct outcome669 *o){
 struct model *m=p;m->sends++;assert(!(m->flags&512) && n==772 && b==m->r->transport);
 assert(m->r->phase==CLAIMED669 && m->r->flags_valid && !m->r->faults);
 o->used=1;o->safe=1;o->completed=3;
 switch(m->mode){
 case 6:o->used=0;o->safe=0;o->completed=0;o->admission=2;return 1;
 case 7:o->used=0;o->safe=0;o->completed=0;return 1;
 case 8:o->error=3;return 3;
 case 9:o->completed=2;break;
 case 10:o->safe=0;o->cleanup_error=5;return 5;
 case 11:m->r->transport[771]^=1;break;
 case 12:m->flags|=512;break;
 case 13:o->safe=0;o->cleanup_error=5;m->flags|=512;m->r->transport[1]^=1;return 5;
 case 14:o->used=2;break;
 case 15:o->admission=1;break;
 case 16:assert(run669(m->r,m->ops)==BUSY669);m->nested++;break;
 case 17:o->used=0;o->safe=1;o->completed=0;break;
 case 18:o->completed=4;break;
 case 19:o->safe=1;o->cleanup_error=5;break;
 }
 return 0;
}
int main(void){
 uint8_t input[772],original[772];unsigned i,mode,ifbit;
 for(i=0;i<772;i++)input[i]=original[i]=(uint8_t)(i*17+3);
 for(ifbit=0;ifbit<2;ifbit++)for(mode=0;mode<20;mode++){
  struct record669 r={0},saved;struct model m={0};struct ops669 ops={&m,enter,flags,send};unsigned expected,status;
  m.r=&r;m.ops=&ops;m.mode=mode;m.initial=0x46|(ifbit<<9);m.flags=m.initial;
  assert(seal669(&r,input,772,1)==OK669);assert(r.phase==READY669);
  status=run669(&r,&ops);
  expected=mode>=1&&mode<=4?GUARD669:mode==6?ADMISSION669:mode==7?NO_USE669:
   mode==8||mode==9?SEND_FAILED669:mode==10||mode==13||mode==19?UNSAFE669:mode==11?PACKET_CHANGED669:
   mode==12?IF_CHANGED669:mode==14||mode==15||mode==17||mode==18?INCONSISTENT669:SENT669;
  assert(status==expected && r.status==expected && r.phase==HELD669);
  assert(m.enter==1 && m.sends==(mode>=1&&mode<=4?0u:1u));
  assert(m.nested==(mode==5||mode==16?1u:0u));
  assert(r.original_flags==m.initial && !memcmp(r.original,original,772) && !memcmp(input,original,772));
  if(mode==13)assert((r.faults&(F_IF669|F_PACKET669|F_UNSAFE669))==(F_IF669|F_PACKET669|F_UNSAFE669));
  saved=r;assert(run669(&r,&ops)==BUSY669 && seal669(&r,input,772,1)==BUSY669);assert(!memcmp(&saved,&r,sizeof(r)));count++;
 }
 {
  struct record669 r={0};struct model m={0};struct ops669 ops={&m,enter,flags,send};unsigned state;
  m.r=&r;m.ops=&ops;
  assert(seal669(0,input,772,1)==ARG669 && seal669(&r,0,772,1)==ARG669);
  assert(seal669(&r,input,771,1)==ARG669 && seal669(&r,input,773,1)==ARG669);
  assert(seal669(&r,input,772,0)==ARG669 && seal669(&r,input,772,2)==ARG669);
  assert(run669(0,&ops)==ARG669 && run669(&r,0)==ARG669);
  for(state=0;state<=HELD669;state++)if(state!=READY669){r.phase=state;assert(run669(&r,&ops)==BUSY669);}
  r.phase=READY669;ops.enter=0;assert(run669(&r,&ops)==ARG669);ops.enter=enter;
  ops.flags=0;assert(run669(&r,&ops)==ARG669);ops.flags=flags;ops.send=0;assert(run669(&r,&ops)==ARG669);
  assert(!m.enter && !m.sends);
 }
 printf("{\"passed\":true,\"lifecycle_cases\":%u,\"argument_and_phase_checks\":15}\n",count);return 0;
}
