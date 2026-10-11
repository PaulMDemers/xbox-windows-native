#include "callback-check.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do {checks++;assert(x);} while(0)
static uint64_t a[X260_CALLBACKS][4],b[X260_CALLBACKS][4];
static unsigned check(unsigned nb,unsigned na,unsigned stage)
{return x260_callbacks_check(a,nb,b,na,999,0x201000,0x12345678,stage);}
static void reset(unsigned n)
{
    memset(a,0,sizeof(a));memset(b,0,sizeof(b));
    for(unsigned j=0;j<n;j++){
        uint64_t row[4]={j+1,4096*(j+1),1024,0x12345678};
        memcpy(a[j],row,sizeof(row));memcpy(b[n-j-1],row,sizeof(row));
    }
}
static void owned(uint64_t r[4])
{r[0]=999;r[1]=0x201000;r[2]=704;r[3]=0x12345678;}
int main(void)
{
    for(unsigned n=0;n<=256;n++){
        reset(n);CHECK(check(n,n,1)==0);CHECK(check(n,n,4)==0);
        if(n<256){
            owned(b[n]);CHECK(check(n,n+1,2)==0);
            owned(a[n]);CHECK(check(n+1,n+1,3)==0);
            CHECK(check(n+1,n,3)!=0);CHECK(check(n,n,2)!=0);
            CHECK(check(n+1,n+1,1)!=0);CHECK(check(n+1,n+1,4)!=0);
            for(unsigned field=0;field<4;field++){
                uint64_t old=b[n][field];b[n][field]++;CHECK(check(n+1,n+1,3)!=0);b[n][field]=old;
            }
        }
        if(n){
            reset(n);CHECK(check(n,n-1,1)!=0);
            for(unsigned field=0;field<4;field++){
                uint64_t old=b[0][field];b[0][field]++;CHECK(check(n,n,1)!=0);b[0][field]=old;
            }
            if(n>1){memcpy(b[0],b[1],sizeof(b[0]));CHECK(check(n,n,1)!=0);}
        }
    }
    reset(1);
    CHECK(check(257,1,1)!=0);CHECK(check(1,257,1)!=0);
    CHECK(check(1,1,0)!=0);CHECK(check(1,1,5)!=0);
    CHECK(x260_callbacks_check(NULL,1,b,1,999,0x201000,1,1)!=0);
    CHECK(x260_callbacks_check(a,1,NULL,1,999,0x201000,1,1)!=0);
    CHECK(x260_callbacks_check(a,1,b,1,0,0x201000,1,1)!=0);
    CHECK(x260_callbacks_check(a,1,b,1,999,UINT64_MAX,1,1)!=0);
    CHECK(x260_callbacks_check(a,1,b,1,999,0x201000,0,1)!=0);
    for(unsigned field=0;field<4;field++){
        if(field==1)continue;
        reset(1);a[0][field]=b[0][field]=0;CHECK(check(1,1,1)!=0);
    }
    reset(1);a[0][1]=b[0][1]=UINT64_MAX;CHECK(check(1,1,1)!=0);
    puts("260 acknowledged callback tuple comparison: PASS");
    printf("checks=%u capacity=256 exact_order_independent=1\n",checks);
    return 0;
}
