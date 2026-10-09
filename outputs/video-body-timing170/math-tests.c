/* Tests the actual diagnostic header with exact32/64bit NT type widths. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t ULONG;typedef uint64_t ULONGLONG;typedef int64_t LONGLONG;
#include "display/profile_math.h"
int main(void)
{
 XWN_PROFILE s; unsigned kind,i,checks=0;
 memset(&s,0,sizeof(s));s.Minimum=UINT64_MAX;s.Enabled=1;
 for(i=0;i<128;i++) {XwnProfileCalibration(&s,INT64_C(0x100000000)+i,INT64_C(0x100000000)+i+(i%7));checks++;}
 assert(s.Samples==128 && s.Reads==256 && s.Minimum==0 && s.Maximum==6 && s.Errors==0);checks++;
 for(kind=0;kind<4;kind++) {
  for(i=0;i<1000;i++) {XwnProfileAccumulate(&s,kind,INT64_C(0x1fffffff0),INT64_C(0x200000000));checks++;}
  assert(s.Ticks[kind]==16000 && s.Count[kind]==1000);checks++;
 }
 assert(s.Reads==8256 && s.Errors==0 && s.Overflows==0);checks++;
 XwnProfileAccumulate(&s,0,INT64_MAX-7,INT64_MAX);assert(s.Ticks[0]==16007);checks++;
 XwnProfileAccumulate(&s,0,10,9);XwnProfileAccumulate(&s,0,-1,10);
 assert(s.Errors==2 && s.Ticks[0]==16007);checks++;
 XwnProfileAccumulate(&s,4,0,1);assert(s.Errors==3 && s.Count[0]==1003);checks++;
 s.Ticks[1]=UINT64_MAX-1;XwnProfileAccumulate(&s,1,0,2);assert(s.Ticks[1]==UINT64_MAX && s.Overflows==1);checks++;
 s.Count[2]=UINT32_MAX;s.Reads=UINT32_MAX;XwnProfileAccumulate(&s,2,0,3);
 assert(s.Count[2]==UINT32_MAX && s.Reads==UINT32_MAX && s.Overflows==4);checks++;
 s.Errors=s.Overflows=UINT32_MAX;XwnProfileAccumulate(&s,4,0,1);
 assert(s.Errors==UINT32_MAX && s.Overflows==UINT32_MAX);checks++;
 memset(&s,0,sizeof(s));s.Minimum=UINT64_MAX;XwnProfileCalibration(&s,-1,-1);XwnProfileCalibration(&s,10,9);
 assert(s.Errors==2 && s.Samples==2 && s.Minimum==UINT64_MAX);checks++;
 memset(&s,0,sizeof(s));s.Enabled=0;XwnProfileAccumulate(&s,0,-1,-1);
 assert(s.Count[0]==1 && s.Ticks[0]==0 && s.Reads==0 && s.Errors==0);checks++;
 printf("%u actual-header checks passed\n",checks);return 0;
}
