#include <assert.h>
#include <stdio.h>
#include "lifetime.h"
static unsigned checks,cases,negatives;
#define CHECK(x) do{assert(x);checks++;}while(0)
static uint64_t identities[4]={100,101,102,103},names[4]={10,11,12,13},sizes[4]={32,32,32,32};
static uint8_t keys[4][G284_KEY];
static G284 fresh(unsigned mode)
{
 G284 g={0};CHECK(g284_arm(&g,17,mode,identities,names,keys,sizes));return g;
}
static void release(G284 *g)
{for(unsigned i=0;i<4;i++)CHECK(g284_decrement(g,17,i,i+1,identities[i],names[i],2));}
static void final_free(G284 *g)
{for(unsigned i=0;i<4;i++)CHECK(g284_decrement(g,17,i,i+1,identities[i],names[i],1));}
static void output(const char *name,const G284 *g)
{
 uint8_t b[G284_BYTES];CHECK(g284_encode(g,b,sizeof(b))==sizeof(b));FILE *f=fopen(name,"wb");CHECK(f);
 CHECK(fwrite(b,1,sizeof(b),f)==sizeof(b));CHECK(!fclose(f));
}
static G284 control(void)
{
 G284 g=fresh(0);release(&g);
 for(unsigned i=0;i<4;i++)CHECK(g284_bound(&g,17,i,i+1,identities[i],names[i],2));
 CHECK(g284_seal(&g,17));cases++;return g;
}
static G284 candidate(unsigned mask,const unsigned order[4],bool cross)
{
 G284 g=fresh(1);release(&g);final_free(&g);
 for(unsigned j=0;j<4;j++) {
  unsigned i=order[j],old=cross?(i+1)%4:i;
  uint64_t id=mask&(1u<<i)?identities[old]:1000+i;
  uint64_t name=mask&(1u<<(i+4))?names[old]:100+i;
  uint64_t generation=g284_created(&g,17,i,id,name,1,keys[i],sizes[i]);CHECK(generation==5+j);
  CHECK(g284_bound(&g,17,i,generation,id,name,2));
  CHECK(g.unit[i].old_free && g.unit[i].old_refs==0 && g.unit[i].new_refs==2);
 }
 CHECK(g284_seal(&g,17));cases++;return g;
}
static void refusals(void)
{
 for(unsigned n=0;n<15;n++) {
  G284 g=fresh(n==5?0:1);bool result=true;unsigned slot=0;
  switch(n) {
  case 0:result=g284_decrement(&g,18,0,1,100,10,2);break;
  case 1:result=g284_decrement(&g,17,4,1,100,10,2);break;
  case 2:result=g284_decrement(&g,17,0,99,100,10,2);break;
  case 3:result=g284_decrement(&g,17,0,1,999,10,2);break;
  case 4:result=g284_decrement(&g,17,0,1,100,10,1);break;
  case 5:release(&g);result=g284_decrement(&g,17,0,1,100,10,1);break;
  case 6:result=g284_created(&g,17,0,100,10,1,keys[0],32)!=0;break;
  case 7:release(&g);final_free(&g);result=g284_created(&g,17,0,100,10,1,keys[1],32)!=0;break;
  case 8:release(&g);final_free(&g);result=g284_bound(&g,17,0,5,100,10,2);break;
  case 9:release(&g);CHECK(g284_decrement(&g,17,0,1,100,10,1));result=g284_created(&g,17,0,101,10,1,keys[0],32)!=0;break;
  case 10:release(&g);final_free(&g);CHECK(g284_created(&g,17,0,100,10,1,keys[0],32)==5);result=g284_created(&g,17,1,100,11,1,keys[1],32)!=0;break;
  case 11:release(&g);final_free(&g);CHECK(g284_created(&g,17,0,100,10,1,keys[0],32)==5);result=g284_bound(&g,17,0,1,100,10,2);break;
  case 12:release(&g);final_free(&g);g.next_generation=UINT64_MAX;result=g284_created(&g,17,0,100,10,1,keys[0],32)!=0;break;
  case 13:result=g284_arm(&g,17,1,identities,names,keys,sizes);break;
  case 14:release(&g);CHECK(g284_decrement(&g,17,0,1,100,10,1));result=g284_created(&g,17,0,1000,100,1,keys[0],32)!=0;break;
  }
  (void)slot;CHECK(!result&&g.errors);CHECK(!g284_seal(&g,17));negatives++;
 }
 G284 g=fresh(1);CHECK(!g284_decrement(&g,18,0,1,100,10,2));
 CHECK(!g284_decrement(&g,17,0,1,100,10,2));CHECK(!g284_decrement(&g,17,0,1,100,10,1));
 CHECK(g.unit[0].old_free&&g.unit[0].event[1].identity==100);negatives++;
 g=fresh(1);g.sequence=UINT64_MAX;g.calls=UINT64_MAX;
 CHECK(!g284_decrement(&g,17,0,1,100,10,2));CHECK(!g284_decrement(&g,17,0,1,100,10,1));
 CHECK(g.unit[0].old_free&&g.unit[0].event[1].kind==2&&g.unit[0].event[1].seq==0);
 CHECK(g.calls==UINT64_MAX&&g.sequence==UINT64_MAX);CHECK(!g284_seal(&g,17));output("failed-saturation.bin",&g);negatives++;
 g=control();CHECK(!g284_seal(&g,17));CHECK(g.errors);negatives++;
}
int main(void)
{
 for(unsigned u=0;u<4;u++)for(unsigned j=0;j<32;j++)keys[u][j]=(uint8_t)(u*31+j);
 G284 g=control();output("control.bin",&g);
 unsigned order[4]={0,1,2,3};g=candidate(255,order,false);output("reuse.bin",&g);
 g=candidate(0,order,false);output("fresh.bin",&g);g=candidate(255,order,true);output("cross-reuse.bin",&g);
 for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)for(unsigned c=0;c<4;c++)for(unsigned d=0;d<4;d++) {
  if(a==b||a==c||a==d||b==c||b==d||c==d)continue;
  unsigned perm[4]={a,b,c,d};
  /* Each lifetime independently chooses reused pointer and/or reused GL name. */
  for(unsigned mask=0;mask<256;mask++)candidate(mask,perm,false);
 }
 refusals();g=control();uint8_t out[G284_BYTES];memset(out,0xa5,sizeof(out));
 for(unsigned n=0;n<G284_BYTES;n++) {
  CHECK(g284_encode(&g,out,n)==0);
  for(unsigned j=0;j<sizeof(out);j++)CHECK(out[j]==0xa5);
 }
 CHECK(g284_encode(&g,out,sizeof(out))==sizeof(out));
 printf("PASS %u generation/ABA scenarios, %u refusal groups, %u checks; no actual renderer callbacks or GL\n",cases,negatives,checks);
}
