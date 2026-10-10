/* MIT. Independent accounting oracle; no GDI or guest rendering simulation. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef uint32_t ULONG;
typedef uint64_t ULONGLONG;
#include "upload_account.h"
static unsigned checks;
#define CHECK(v) do {++checks;if(!(v)){fprintf(stderr,"line %u\n",__LINE__);exit(1);}}while(0)
int main(void)
{
 XWA_STATS s={0};XWA_COPY c={0};ULONG out[XWA_WORDS],i,j;
 uint64_t bytes[15]={0},null_bytes[15]={0};uint32_t boxes[15]={0},req[15]={0},nulls[15]={0};
 CHECK(XWA_WORDS==158);XwaSnapshot(&s,out);
 CHECK(out[0]==0x41555758&&out[1]==119&&out[2]==632&&out[3]==XWN_UPLOAD_ACCOUNTING&&out[4]==15);
 for(i=5;i<158;i++)CHECK(out[i]==0);
 for(i=0;i<4096;i++) {
  ULONG kind=(i*7)%15,explicit_rect=i&1,n=(i%9)+1;
  c=(XWA_COPY){0};
  for(j=0;j<n;j++)XwaBox(&c,(uint64_t)(i+1)*(j+3)*4);
  if(i%17==0)XwaFallback(&c);
  XwaRecord(&s,kind,explicit_rect,&c);
  req[kind]++;nulls[kind]+=!explicit_rect;boxes[kind]+=n;
  for(j=0;j<n;j++)bytes[kind]+=(uint64_t)(i+1)*(j+3)*4;
  if(!explicit_rect)for(j=0;j<n;j++)null_bytes[kind]+=(uint64_t)(i+1)*(j+3)*4;
  XwaSnapshot(&s,out);CHECK(out[5]==0&&out[6]==0&&out[7]==0);
  for(j=0;j<15;j++) {
   ULONG a=8+j*10;uint64_t b=(uint64_t)out[a+4]|((uint64_t)out[a+5]<<32);
   uint64_t z=(uint64_t)out[a+6]|((uint64_t)out[a+7]<<32);
   CHECK(out[a+9]==0);
#if XWN_UPLOAD_ACCOUNTING
   CHECK(out[a]==req[j]&&out[a+1]==req[j]-nulls[j]&&out[a+2]==nulls[j]);
   CHECK(out[a+3]==boxes[j]&&b==bytes[j]&&z==null_bytes[j]);
#else
   CHECK(out[a]==0&&out[a+1]==0&&out[a+2]==0&&out[a+3]==0&&b==0&&z==0&&out[a+8]==0);
#endif
  }
 }
#if XWN_UPLOAD_ACCOUNTING
 XwaRecord(&s,15,0,&c);CHECK(s.errors==1);s.errors=0;
 XwaRecord(&s,0,2,&c);CHECK(s.errors==1);s.errors=0;
 c=(XWA_COPY){0};XwaBox(&c,UINT64_MAX);XwaBox(&c,1);
 CHECK(c.bytes==UINT64_MAX&&c.overflow==1&&c.boxes==2);
 c.boxes=UINT32_MAX;XwaBox(&c,0);CHECK(c.boxes==UINT32_MAX&&c.overflow==1);
 c.fallbacks=UINT32_MAX;XwaFallback(&c);CHECK(c.fallbacks==UINT32_MAX);
 s=(XWA_STATS){0};c=(XWA_COPY){1,1,0,UINT64_MAX};XwaRecord(&s,0,0,&c);
 CHECK(s.overflow==0&&s.row[0].null_bytes==UINT64_MAX);XwaRecord(&s,0,0,&c);
 CHECK(s.overflow==1&&s.row[0].bytes==UINT64_MAX&&s.row[0].null_bytes==UINT64_MAX);
 s=(XWA_STATS){0};s.row[0].requests=UINT32_MAX;s.row[0].null_rect=UINT32_MAX;
 XwaRecord(&s,0,0,&c);CHECK(s.overflow==1&&s.row[0].requests==UINT32_MAX);
 XwaSnapshot(&s,out);CHECK(out[6]==1);
#endif
 puts("accounting host oracle PASS");printf("checks=%u mode=%u\n",checks,XWN_UPLOAD_ACCOUNTING);return 0;
}
