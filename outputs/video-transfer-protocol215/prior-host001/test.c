/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent packet/pixel/transition oracle, not a GPU emulator qualification.
 */
#include "protocol.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned long long checks;static uint32_t seed=215;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(1);}}while(0)
static uint32_t random32(void){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed;}
static X215Input good(void)
{
 X215Input r={0};unsigned i;
 for(i=0;i<4;i++){r.range[i].base=0x200000+i*0x10000;r.range[i].bytes=4096;}
 r.source_offset=16;r.dest_offset=32;r.source_pitch=80;r.dest_pitch=96;r.width=16;r.height=8;
 r.ramht_base=0x12000;r.objects_base=0x18000;r.channel=1;r.token=0x215001;return r;
}
static int valid(const X215Input *r)
{
 unsigned i,j;uint64_t s,d;
 if(!r->token || r->width<1 || r->width>16 || r->height<1 || r->height>8 || r->channel>3)return 0;
 for(i=0;i<4;i++) {
  uint64_t b=r->range[i].base,z=b+r->range[i].bytes;
  if(b%4096 || r->range[i].bytes%4096 || r->range[i].bytes<4096 || r->range[i].bytes>65536 || z>62914560)return 0;
  for(j=0;j<i;j++)if(b<(uint64_t)r->range[j].base+r->range[j].bytes && r->range[j].base<z)return 0;
 }
 if(r->source_offset<16 || r->dest_offset<16 || r->source_offset%4 || r->dest_offset%4 ||
    r->source_pitch%4 || r->dest_pitch%4 || r->source_pitch>65535 || r->dest_pitch>65535 ||
    r->source_pitch<4*r->width || r->dest_pitch<4*r->width)return 0;
 s=r->source_offset;d=r->dest_offset;
 for(i=0;i<r->height;i++) {
  if(s+4*r->width+16>r->range[0].bytes || d+4*r->width+16>r->range[1].bytes)return 0;
  s+=r->source_pitch;d+=r->dest_pitch;
 }
 if(r->ramht_base%4096 || r->ramht_base>126976 || r->objects_base%16 ||
    (uint64_t)r->objects_base+112>1048576 ||
    (r->objects_base<r->ramht_base+4096 && r->ramht_base<(uint64_t)r->objects_base+112))return 0;
 return 1;
}
static void exact(const X215Input *r,const X215Plan *p)
{
 /* Fixed known method headers independently decoded from the pinned source. */
 uint32_t golden[27]={0x40000,0x97,0x401a4,8,0x41d6c,16,0x42000,0x62,
  0x82184,3,4,0x102300,10,0,0,0,0x44000,0x9f,0x4419c,0x62,
  0x1042fc,3,0,0,0,0x41d70,0};
 static const uint32_t handles[7]={0x97,0x62,0x9f,3,4,8,6};unsigned i,j;
 golden[13]=r->source_pitch+r->dest_pitch*65536;golden[14]=r->source_offset;golden[15]=r->dest_offset;
 golden[24]=r->width+r->height*65536;golden[26]=r->token;
 CHECK(p->packet_bytes==108);for(i=0;i<27;i++)CHECK(p->words[i]==golden[i]);
 CHECK(p->source_end==r->source_offset+(r->height-1)*r->source_pitch+r->width*4);
 CHECK(p->dest_end==r->dest_offset+(r->height-1)*r->dest_pitch+r->width*4);
 for(i=0;i<7;i++) {
  uint32_t slot=handles[i]^(r->channel*128);
  CHECK(p->entry[i].address==r->ramht_base+slot*8);CHECK(p->entry[i].handle==handles[i]);
  CHECK((p->entry[i].context&65535)*16==r->objects_base+i*16);
  CHECK((p->entry[i].context>>24&31)==r->channel);
  CHECK((p->entry[i].context>>16&3)==(i<3));CHECK(p->entry[i].context>>31);
 }
 for(i=0;i<3;i++){CHECK(p->graphics[i][0]==handles[i]);for(j=1;j<4;j++)CHECK(p->graphics[i][j]==0);}
 for(i=0;i<4;i++) {
  CHECK(p->dma[i][0]==0xb000u+(i==0 || i==3?2u:3u));CHECK(p->dma[i][1]==r->range[i].bytes-1);
  CHECK((p->dma[i][2]&0xfffff000u)==r->range[i].base);CHECK(p->dma[i][2]==p->dma[i][3]);
 }
}
static void pixels(const X215Input *r,const X215Plan *p)
{
 unsigned char memory[4][4096],expected[4096];uint32_t cls[8]={0},sp=0,dp=0,so=0,doff=0,w=0,h=0;
 uint32_t format=0,op=0,semaphore=0,si=0,di=0,surface=0,points=0;unsigned i,j;
 memset(memory,0xa5,sizeof(memory));
 for(i=0;i<4096;i++)memory[0][i]=(unsigned char)(i*37+i/13);
 memset(memory[2]+16,0,4);memcpy(expected,memory[1],4096);
 for(i=0;i<r->height;i++)for(j=0;j<r->width*4;j++)expected[r->dest_offset+i*r->dest_pitch+j]=memory[0][r->source_offset+i*r->source_pitch+j];
 i=0;
 while(i<27) {
  uint32_t word=p->words[i++],count=word>>18&2047,sub=word>>13&7,method=word&8191;
  CHECK((word&0xe0030003u)==0 && count>0 && i+count<=27);
  while(count--) {
   uint32_t value=p->words[i++];
   if(method==0){cls[sub]=value;CHECK((sub==0 && value==0x97)||(sub==1 && value==0x62)||(sub==2 && value==0x9f));}
   else if(cls[sub]==0x97 && method==0x1a4)CHECK(value==8);
   else if(cls[sub]==0x97 && method==0x1d6c)semaphore=value;
   else if(cls[sub]==0x62 && method==0x184)si=value;
   else if(cls[sub]==0x62 && method==0x188)di=value;
   else if(cls[sub]==0x62 && method==0x300)format=value;
   else if(cls[sub]==0x62 && method==0x304){sp=value%65536;dp=value/65536;}
   else if(cls[sub]==0x62 && method==0x308)so=value;
   else if(cls[sub]==0x62 && method==0x30c)doff=value;
   else if(cls[sub]==0x9f && method==0x19c)surface=value;
   else if(cls[sub]==0x9f && method==0x2fc)op=value;
   else if(cls[sub]==0x9f && (method==0x300 || method==0x304)){CHECK(value==0);points++;}
   else if(cls[sub]==0x9f && method==0x308) {
    w=value%65536;h=value/65536;CHECK(format==10 && op==3 && si==3 && di==4 && surface==0x62 && points==2);
    for(j=0;j<h;j++){CHECK(so+j*sp+w*4<4096 && doff+j*dp+w*4<4096);memcpy(memory[1]+doff+j*dp,memory[0]+so+j*sp,w*4);}
   } else if(cls[sub]==0x97 && method==0x1d70) {
    CHECK(w && h && semaphore==16 && value==r->token);
    for(j=0;j<4;j++)memory[2][16+j]=(unsigned char)(value>>(j*8));
   } else CHECK(0);
   method+=4;
  }
 }
 for(i=0;i<4096;i++){CHECK(memory[1][i]==expected[i]);CHECK(memory[0][i]==(unsigned char)(i*37+i/13));
  CHECK(memory[3][i]==0xa5);CHECK(memory[2][i]==(i>=16 && i<20?(unsigned char)(r->token>>((i-16)*8)):0xa5));}
}
static void lifetime(void)
{
 unsigned s,e;X215Context c;int result;uint32_t expected;int ok;
 /* Table oracle covers every state and rejected transitions, not just a happy path. */
 for(s=0;s<8;s++)for(e=0;e<18;e++) {
  c=(X215Context){s,215,100,200};expected=s;ok=0;
  switch(e) {
  case 0:result=x215_prepare(&c,216,100,100);if(s==0){expected=1;ok=1;}break;
  case 1:result=x215_expose(&c,63,110);if(s==1){expected=2;ok=1;}break;
  case 2:result=x215_expose(&c,31,110);break;
  case 3:result=x215_submit(&c);if(s==2){expected=3;ok=1;}break;
  case 4:result=x215_observe(&c,215,0,110,0);break;
  case 5:result=x215_observe(&c,215,215,110,0);if(s==3){expected=4;ok=1;}break;
  case 6:result=x215_observe(&c,215,214,110,0);if(s==3)expected=6;break;
  case 7:result=x215_observe(&c,214,215,110,0);break;
  case 8:result=x215_observe(&c,215,215,200,0);if(s==3)expected=6;break;
  case 9:result=x215_observe(&c,215,0,99,0);if(s==3)expected=6;break;
  case 10:result=x215_observe(&c,215,215,110,1);if(s==3)expected=6;break;
  case 11:result=x215_drain(&c,215,7);if(s==4){expected=5;ok=1;}break;
  case 12:result=x215_drain(&c,214,7);break;
  case 13:result=x215_drain(&c,215,3);break;
  case 14:result=x215_release(&c);if(s==1 || s==5){expected=7;ok=1;}break;
  case 15:result=x215_abort(&c);if(s==1){expected=7;ok=1;}else if(s>=2 && s<=4)expected=6;break;
  case 16:result=x215_expose(&c,63,200);break;
  default:result=x215_prepare(&c,215,UINT64_MAX,100);break;
  }
  CHECK(result==ok);CHECK(c.state==expected);
 }
 c=(X215Context){0};CHECK(!x215_prepare(&c,0,0,100));CHECK(!x215_prepare(&c,1,0,0));CHECK(!x215_prepare(&c,1,0,1000001));
 CHECK(x215_prepare(&c,215,0,100));CHECK(x215_expose(&c,63,1));CHECK(x215_submit(&c));
 CHECK(!x215_observe(&c,215,0,100,0));CHECK(c.state==6);
 CHECK(!x215_observe(&c,215,215,101,0));CHECK(!x215_drain(&c,215,7));CHECK(!x215_release(&c));CHECK(!x215_prepare(&c,216,102,100));
 for(e=0;e<6;e++){c=(X215Context){0};CHECK(x215_prepare(&c,215,0,100));CHECK(!x215_expose(&c,63^(1u<<e),1));CHECK(c.state==1);}
}
int main(void)
{
 X215Input r;X215Plan p,before;unsigned w,h,pad,off,i,accepted=0;
 for(w=1;w<=16;w++)for(h=1;h<=8;h++)for(pad=0;pad<4;pad++)for(off=16;off<=32;off+=16) {
  r=good();r.width=w;r.height=h;r.source_pitch=w*4+pad*4;r.dest_pitch=w*4+(3-pad)*4;r.source_offset=off;
  CHECK(x215_plan(&r,&p));exact(&r,&p);pixels(&r,&p);
 }
 for(i=0;i<100000;i++) {
  r=good();r.width=random32()%19;r.height=random32()%11;r.channel=random32()%7;
  r.source_pitch=random32()%128;r.dest_pitch=random32()%128;r.source_offset=random32()%4200;r.dest_offset=random32()%4200;
  switch(i%8) {
   case 0:r=good();r.channel=i%4;break;
   case 1:r.range[1]=r.range[0];break;
   case 2:r.range[0].base=random32();break;
   case 3:r.objects_base=random32();break;
   case 4:r.ramht_base=random32();break;
   case 5:r.token=0;break;
   case 6:r.source_offset=UINT32_MAX;break;
   default:break;
  }
  memset(&p,0xcc,sizeof(p));before=p;int want=valid(&r),actual=x215_plan(&r,&p);CHECK(actual==want);
  if(actual){accepted++;exact(&r,&p);}else CHECK(!memcmp(&p,&before,sizeof(p)));
 }
 r=good();memset(&p,0xcc,sizeof(p));before=p;CHECK(!x215_plan(NULL,&p));CHECK(!memcmp(&p,&before,sizeof(p)));CHECK(!x215_plan(&r,NULL));
 lifetime();printf("checks=%llu pixel_cases=1024 descriptor_cases=100000 accepted=%u transition_cases=144 quarantine_terminal=1\n",checks,accepted);return 0;
}
