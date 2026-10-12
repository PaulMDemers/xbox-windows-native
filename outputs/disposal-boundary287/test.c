#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include "boundary.h"
#include "fixture.h"
static unsigned checks;
#define CHECK(x) do {assert(x);checks++;}while(0)
static void make(X287Proof *p,unsigned mode,unsigned stage)
{
 memset(p,0,sizeof(*p));p->boundary=fixture;p->boundary.stage=stage;
 memset(p->boundary.textures,0,sizeof(p->boundary.textures));
 p->boundary.started=1000+stage*100;p->boundary.finished=p->boundary.started+50;p->boundary.deadline=p->boundary.finished+100;
 for(unsigned c=0;c<2;c++){p->boundary.cpu[c].epoch=2*stage-1+c;p->boundary.cpu[c].when=p->boundary.started+10+c;}
 p->candidate=mode;p->inventory_complete=1;
 for(unsigned i=0;i<4;i++) {
  X287Slot *s=&p->selected[i];s->anchor=fixture.textures[i];s->anchor.refs=2;s->anchor.cache_edges=s->anchor.unit_edges=1;
  s->current=s->anchor;s->old_generation=s->generation=i+1;s->key_bytes=32;
  for(unsigned j=0;j<32;j++)s->old_key[j]=s->current_key[j]=(uint8_t)(i*31+j);
  s->current_gl_alive=1;
  if(stage==2 || stage==3){s->current.refs=1;s->current.unit_edges=0;}
  if(mode&&stage>=3){s->old_completed_free=s->old_gl_deleted=1;}
  if(mode&&stage==3){memset(&s->current,0,sizeof(s->current));memset(s->current_key,0,1024);s->generation=s->current_gl_alive=0;}
  if(mode&&stage==4)s->generation=5+i; /* Address/name recycling is allowed. */
 }
}
int main(void)
{
 X287Proof *p=malloc(sizeof(*p)),*q=malloc(sizeof(*q));assert(p&&q);
 for(unsigned mode=0;mode<2;mode++)for(unsigned stage=1;stage<=4;stage++) {
  make(p,mode,stage);CHECK(!x287_validate(p));
  if(stage>1){make(q,mode,stage-1);CHECK(!x287_chain(q,p));}
  for(unsigned i=0;i<4;i++)for(unsigned field=0;field<11;field++) {
   make(p,mode,stage);uint64_t v[11];memcpy(v,&p->selected[i].current,sizeof(v));v[field]^=1;memcpy(&p->selected[i].current,v,sizeof(v));
   /* A changed replacement identity/name can be valid; the recorder must link it. */
   if(mode&&stage==4&&field<2)continue;
   CHECK(x287_validate(p));
  }
  for(unsigned i=0;i<4;i++) {
   make(p,mode,stage);p->selected[i].old_completed_free^=1;CHECK(x287_validate(p));
   make(p,mode,stage);p->selected[i].old_gl_deleted^=1;CHECK(x287_validate(p));
   make(p,mode,stage);p->selected[i].current_gl_alive^=1;CHECK(x287_validate(p));
   make(p,mode,stage);p->selected[i].current_key[0]^=1;CHECK(x287_validate(p));
   make(p,mode,stage);p->selected[i].old_key[1023]=1;CHECK(x287_validate(p));
   make(p,mode,stage);p->selected[i].generation=1; if(i || (mode&&stage>=3))CHECK(x287_validate(p));
  }
  make(p,mode,stage);p->inventory_complete=0;CHECK(x287_validate(p));
  make(p,mode,stage);p->boundary.textures[0]=fixture.textures[0];CHECK(x287_validate(p));
  make(p,mode,stage);p->boundary.cpu[1].epoch--;CHECK(x287_validate(p));
  make(p,mode,stage);p->boundary.cpu[1].clock++;CHECK(x287_validate(p));
  make(p,mode,stage);p->boundary.cpu_stopped=2;CHECK(x287_validate(p));
 }
 for(unsigned stage=2;stage<=4;stage++) {
  make(q,1,stage-1);make(p,1,stage);
  p->boundary.cpu[0].clock++;p->boundary.cpu[1].clock++;
  CHECK((x287_chain(q,p)==0)==(stage==4));
  make(p,1,stage);p->selected[0].old_key[0]^=1;
  if(stage!=3)p->selected[0].current_key[0]^=1;
  CHECK(x287_chain(q,p));
 }
 make(p,1,4);p->selected[1].generation=5;CHECK(x287_validate(p));
 make(p,1,3);p->selected[0].current=fixture.textures[0];CHECK(x287_validate(p));
 make(q,1,3);make(p,1,4);p->selected[0].generation=1;CHECK(x287_chain(q,p));
 make(q,1,3);make(p,1,4);CHECK(!x287_chain(q,p));
 make(q,1,3);make(p,1,4);p->boundary.cpu[0].clock--;p->boundary.cpu[1].clock--;CHECK(x287_chain(q,p));
 make(p,1,4);p->selected[0].current.name=UINT64_C(1)<<32;CHECK(x287_validate(p));
 free(p);free(q);printf("PASS %u four-boundary/absence/replacement scalar checks; all CPU/GL/graph facts modeled, no runtime provider\n",checks);
}
