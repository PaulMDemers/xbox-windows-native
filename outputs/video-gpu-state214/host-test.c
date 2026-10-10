/* Exact snapshot helper with independent approved-address/read-count oracle. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "host-shim/ntddk.h"
static ULONG checks,count,reads,irql,records[64][4];static PUCHAR memory;
static const ULONG allowed[22]={0,0x100,0x140,0x2210,0x2214,0x2218,0x2100,0x2140,
 0x3200,0x3204,0x3220,0x3228,0x3240,0x3244,0x3250,0x400100,0x400140,0x400148,0x400720,
 0x600100,0x600140,0x600800};
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"%u: %s\n",__LINE__,#x);exit(1);}}while(0)
ULONG KeGetCurrentIrql(void){return irql;}
LONG InterlockedCompareExchange(volatile LONG *p,LONG value,LONG expected)
{__atomic_compare_exchange_n(p,&expected,value,0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST);return expected;}
ULONG XgnRead(PULONG p)
{
 ULONG offset=(ULONG)((PUCHAR)p-memory),i;CHECK((PUCHAR)p>=memory && offset+4<=0x681000);
 for(i=0;i<22;i++) if(allowed[i]==offset) break;
 CHECK(i<22);reads++;return *p;
}
void XwnVideoTrace(ULONG e,ULONG a,ULONG b,ULONG c)
{CHECK(count<64);records[count][0]=e;records[count][1]=a;records[count][2]=b;records[count++][3]=c;}
#include "gpu_snapshot.c"
static void reset(void){memset(records,0,sizeof(records));count=reads=irql=0;XgnSeen[0]=XgnSeen[1]=0;}
static void *worker(void *unused){(void)unused;XgnSnapshot(memory,0x681000,0);return NULL;}
int main(void)
{
 ULONG i,phase,at,sum=0;pthread_t threads[32];memory=calloc(1,0x681000);CHECK(memory);
 for(i=0;i<22;i++){*(PULONG)(memory+allowed[i])=allowed[i]^0xa5000000u;sum^=0xa5000000u;}
 reset();for(phase=0;phase<2;phase++){XgnSnapshot(memory,0x681000,phase);XgnSnapshot(memory,0x681000,phase);}
 CHECK(reads==(XWN_GPU_SNAPSHOT?44u:0u));CHECK(count==(XWN_GPU_SNAPSHOT?48u:2u));
 for(phase=0;phase<2;phase++) {
  at=phase*(XWN_GPU_SNAPSHOT?24u:1u);CHECK(records[at][0]==21400 && records[at][1]==phase && records[at][2]==XWN_GPU_SNAPSHOT && records[at][3]==0);
#if XWN_GPU_SNAPSHOT
  for(i=0;i<22;i++)CHECK(records[at+1+i][0]==21401 && records[at+1+i][1]==phase && records[at+1+i][2]==allowed[i] && records[at+1+i][3]==(allowed[i]^0xa5000000u));
  CHECK(records[at+23][0]==21402 && records[at+23][1]==phase && records[at+23][2]==22 && records[at+23][3]==sum);
#endif
 }
 reset();XgnSnapshot(memory,0x681000,2);CHECK(reads==0 && count==1 && records[0][0]==21403 && records[0][2]==1);
 reset();XgnSnapshot(NULL,0x681000,0);CHECK(reads==0 && count==1 && records[0][2]==2);
 reset();XgnSnapshot(memory+1,0x681000,0);CHECK(reads==0 && count==1 && records[0][2]==2);
 reset();XgnSnapshot(memory,0x680fff,0);CHECK(reads==0 && count==1 && records[0][2]==2);
 reset();irql=31;XgnSnapshot(memory,0x681000,0);CHECK(reads==0 && count==1 && records[0][2]==2);
 reset();for(i=0;i<32;i++)CHECK(!pthread_create(&threads[i],NULL,worker,NULL));
 for(i=0;i<32;i++)CHECK(!pthread_join(threads[i],NULL));
 CHECK(reads==(XWN_GPU_SNAPSHOT?22u:0u) && count==(XWN_GPU_SNAPSHOT?24u:1u));
 for(i=0;i<22;i++)CHECK(*(PULONG)(memory+allowed[i])==(allowed[i]^0xa5000000u));
 free(memory);printf("checks=%u mode=%u exact_phases=2 fault_cases=5 concurrent_callers=32\n",checks,XWN_GPU_SNAPSHOT);return 0;
}
