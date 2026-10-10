/* Exact native probe under injectable host providers. No DMA/residency proof. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "host-shim/ntddk.h"
static ULONG fault,allocations,frees,queries,copies,count,checks;
static PUCHAR allocation;
static ULONG records[8][4];
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"%u: %s\n",__LINE__,#x);exit(1);}}while(0)
ULONG KeGetCurrentIrql(void){return fault==1?31:0;}
void XwnVideoTrace(ULONG e,ULONG a,ULONG b,ULONG c)
{CHECK(count<8);records[count][0]=e;records[count][1]=a;records[count][2]=b;records[count++][3]=c;}
void *MmAllocateContiguousMemorySpecifyCache(size_t n,PHYSICAL_ADDRESS low,PHYSICAL_ADDRESS high,PHYSICAL_ADDRESS boundary,int cache)
{
 allocations++;CHECK(n==16384 && low.QuadPart==0x100000 && high.QuadPart==0x03bfffff && !boundary.QuadPart && cache==0);
 if(fault==2)return NULL;
 allocation=aligned_alloc(4096,n);CHECK(allocation);return allocation;
}
void MmFreeContiguousMemorySpecifyCache(void *p,size_t n,int cache)
{CHECK(p==allocation && n==16384 && cache==0);frees++;free(p);allocation=NULL;}
PHYSICAL_ADDRESS MmGetPhysicalAddress(void *p)
{
 PHYSICAL_ADDRESS a;queries++;a.QuadPart=0x200000+((PUCHAR)p-allocation);
 if(fault==3)a.QuadPart+=1;
 if(fault==4 && queries==2)a.QuadPart+=4096;
 if(fault==5 && queries==6)a.QuadPart--;
 return a;
}
void RtlFillMemory(void *p,size_t n,UCHAR value){memset(p,value,n);}
void RtlCopyMemory(void *p,const void *q,size_t n)
{
 copies++;memcpy(p,q,n);
 if(copies==8) {
  if(fault==6)allocation[4224+2*272+12]^=1; /* Copied destination. */
  if(fault==7)allocation[64]^=1; /* Source unexpectedly changed. */
  if(fault==8)allocation[16383]^=1; /* Outer allocation guard. */
 }
}
#include "staging_probe.c"
int main(void)
{
 for(fault=0;fault<=8;fault++) {
  BOOLEAN passed;allocations=frees=queries=copies=count=0;memset(records,0,sizeof(records));
  passed=XgtNativeProbe();
#if XWN_STAGING_PROBE
  CHECK(passed==(fault==0));CHECK(records[0][0]==21300 && records[0][1]==1);
  if(fault==1) {CHECK(!allocations && !frees && count==1);continue;}
  if(fault==2) {CHECK(allocations==1 && !frees && count==2);CHECK(records[1][3]==1);continue;}
  CHECK(allocations==1 && frees==1 && !allocation && count==4);
  CHECK(records[3][0]==21303 && records[3][1]==passed && records[3][2]==16384);
  CHECK(records[2][3]==(fault==0?0:fault==3?2:fault==4?3:fault==5?4:fault==6?8:fault==7?9:10));
  if(!fault)fprintf(stderr,"observed checks=%u tiles=%u queries=%u copies=%u\n",records[2][1],records[2][2],queries,copies);
  if(!fault)CHECK(records[2][1]==15365 && records[2][2]==4 && queries==6 && copies==26);
#else
  CHECK(passed && !allocations && !frees && !queries && !copies && count==1);
  CHECK(records[0][0]==21300 && !records[0][1] && !records[0][2]);
#endif
 }
 printf("checks=%u mode=%u fault_cases=9\n",checks,XWN_STAGING_PROBE);return 0;
}
