#include "callback-check.h"
/* Compare acknowledged CPU-owned copies, never a live list from the monitor.
 * Rows: identity, VRAM-relative begin, length, opaque. Ordering is immaterial.
 * Every unrelated callback must survive with its entire tuple unchanged. */
unsigned x260_callbacks_check(const uint64_t before[][4],unsigned nb,
    const uint64_t after[][4],unsigned na,uint64_t identity,
    uint64_t begin,uint64_t opaque,unsigned stage)
{
    if(stage<1||stage>4||!identity||!opaque||begin>UINT64_MAX-704||
       nb>X260_CALLBACKS||na>X260_CALLBACKS||(nb&&!before)||(na&&!after))return 1;
    unsigned own[2]={0,0};
    for(unsigned side=0;side<2;side++){
        const uint64_t (*rows)[4]=side?after:before;
        unsigned count=side?na:nb;
        for(unsigned j=0;j<count;j++){
            if(!rows[j][0]||!rows[j][2]||rows[j][1]>UINT64_MAX-rows[j][2]||!rows[j][3])return 2;
            for(unsigned k=0;k<j;k++)if(rows[k][0]==rows[j][0])return 3;
            if(rows[j][0]==identity){
                if(rows[j][1]!=begin||rows[j][2]!=704||rows[j][3]!=opaque)return 4;
                own[side]++;
            }
        }
    }
    if(own[0]!=(stage==3)||own[1]!=((stage==2||stage==3)?1u:0u))return 5;
    if(nb-own[0]!=na-own[1])return 6;
    for(unsigned j=0;j<nb;j++){
        if(before[j][0]==identity)continue;
        unsigned found=0;
        for(unsigned k=0;k<na;k++)if(after[k][0]==before[j][0]){
            for(unsigned z=1;z<4;z++)if(after[k][z]!=before[j][z])return 7;
            found++;
        }
        if(found!=1)return 8;
    }
    return 0;
}
