#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t ULONG;
typedef uint64_t ULONGLONG;
typedef void VOID;
#include "eligible.h"
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)) {fprintf(stderr,"failed line%d\n",__LINE__);exit(1);}} while(0)
int main(void) {
 ULONG s[12],before[8];unsigned i,j;uint64_t sum;
 for(i=0;i<10000;i++) {
  memset(s,0,sizeof(s));for(j=0;j<8;j++)s[j]=i*17+j;memcpy(before,s,sizeof(before));
  sum=0;
  for(j=0;j<32;j++) {uint64_t bytes=((uint64_t)i<<24)+j+1;
   XwnEligibleRecord(s,(j&1)?-2:1,bytes);sum+=bytes;
   CHECK((((uint64_t)s[9]<<32)|s[8])==sum);CHECK(s[10]==0);
   CHECK(memcmp(before,s,sizeof(before))==0);
  }
  XwnEligibleRecord(s,-1,0);XwnEligibleRecord(s,0,0);XwnEligibleRecord(s,-2,0);
  CHECK((((uint64_t)s[9]<<32)|s[8])==sum);CHECK(s[10]==0);
 }
 memset(s,0,sizeof(s));s[8]=UINT32_MAX-1;s[9]=UINT32_MAX;
 XwnEligibleRecord(s,-2,1);CHECK(s[8]==UINT32_MAX&&s[9]==UINT32_MAX&&!s[10]);
 XwnEligibleRecord(s,1,1);CHECK(s[8]==UINT32_MAX&&s[9]==UINT32_MAX&&s[10]==1);
 XwnEligibleRecord(s,-2,UINT64_MAX);CHECK(s[8]==UINT32_MAX&&s[9]==UINT32_MAX&&s[10]==1);
 XwnEligibleRecord(s,0,0);CHECK(s[10]==1);
 for(i=0;i<5;i++) {int r[]={-3,2,-1,0,1};uint64_t b[]={0,0,1,1,0};
  memset(s,0,sizeof(s));XwnEligibleRecord(s,r[i],b[i]);CHECK(s[10]==2&&!s[8]&&!s[9]);
  XwnEligibleRecord(s,-2,7);CHECK(s[10]==2&&s[8]==7);
 }
 printf("{\"checks\":%u,\"passed\":true}\n",checks);return 0;
}
