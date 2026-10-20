#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "dib_header.h"
typedef struct {DIBU data[10],available,calls,bytes,max,base;int mutate,partial;} MEM;
static int read604(void*ctx,DIBU addr,void*dest,DIBU bytes) {
 MEM*m=ctx;m->calls++;m->bytes+=bytes;if(bytes>m->max)m->max=bytes;
 assert(bytes==4||bytes==40);assert(addr==m->base);
 if(bytes>m->available){if(m->partial)memset(dest,0xab,20);return 0;}
 memcpy(dest,m->data,bytes);if(m->mutate&&bytes==40)((DIBU*)dest)[0]=124;
 return 1;
}
static void reset604(MEM*m) {memset(m,0,sizeof(*m));m->available=40;m->base=0x1000;m->data[0]=40;m->data[1]=8;m->data[2]=0xfffffff8;m->data[3]=0x200001;}
static DIBSNAP test604(MEM*m,DIBU addr,DIBU expected) {DIBSNAP s;dib_snapshot604(read604,m,addr,&s);assert(s.status==expected);assert(m->calls<=2&&m->bytes<=44&&m->max<=40);return s;}
int main(void) {
 MEM m;DIBSNAP s;DIBU bpp;reset604(&m);s=test604(&m,0x1000,0);assert(s.count==10&&s.stride==32&&s.bytes==256);
 reset604(&m);m.data[2]=8;s=test604(&m,0x1000,0);assert(s.bytes==256);
 reset604(&m);test604(&m,0,1);assert(m.calls==0);
 reset604(&m);test604(&m,0xffffffff,2);assert(m.calls==0);
 reset604(&m);m.available=0;test604(&m,0x1000,3);
 reset604(&m);m.available=4;m.partial=1;s=test604(&m,0x1000,3);assert(s.count==1&&s.words[0]==40&&s.words[1]==0);
 reset604(&m);m.base=0xfffffff0;test604(&m,m.base,2);assert(m.calls==1);
 reset604(&m);m.data[0]=124;s=test604(&m,0x1000,4);assert(m.calls==1&&s.count==1);
 reset604(&m);m.mutate=1;test604(&m,0x1000,4);
 reset604(&m);m.data[1]=0;test604(&m,0x1000,5);
 reset604(&m);m.data[1]=0xffffffff;test604(&m,0x1000,5);
 reset604(&m);m.data[2]=0;test604(&m,0x1000,5);
 reset604(&m);m.data[2]=0x80000000;test604(&m,0x1000,5);
 reset604(&m);m.data[3]=0x200002;test604(&m,0x1000,6);
 reset604(&m);m.data[3]=0x30001;test604(&m,0x1000,7);
 reset604(&m);m.data[4]=1;test604(&m,0x1000,8);
 reset604(&m);m.data[1]=16385;test604(&m,0x1000,9);
 reset604(&m);m.data[1]=16384;m.data[2]=16384;test604(&m,0x1000,9);
 reset604(&m);m.data[5]=1;test604(&m,0x1000,10);
 reset604(&m);m.data[5]=67108865;test604(&m,0x1000,10);
 reset604(&m);m.data[8]=257;test604(&m,0x1000,11);
 for(bpp=1;bpp<=32;bpp*=2){reset604(&m);m.data[1]=3;m.data[3]=(bpp<<16)|1;if(bpp==2)continue;s=test604(&m,0x1000,0);assert(s.stride==((3*bpp+31)/32)*4);}
 reset604(&m);m.data[1]=3;m.data[3]=0x180001;s=test604(&m,0x1000,0);assert(s.stride==12);
 puts("DIB604 PASS: 19 rejection controls, signed heights, supported bpp, bounded reads");return 0;
}
