#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "large_oracle.h"
int main(int argc,char **argv) {
    uint32_t cw=0,ch=0,bytes=0,w,h,kind,count,x,y,v;
    if(argc==1) {
        static const uint32_t bad[][2]={{0,0},{256,129},{640,540},{960,360},{UINT32_MAX,540},{960,UINT32_MAX}};
        for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);++i) {
            cw=7;ch=9;bytes=11;
            if(lg_layout(bad[i][0],bad[i][1],&cw,&ch,&bytes)||cw!=7||ch!=9||bytes!=11)return 2;
        }
        puts("six invalid layouts refused without output mutation");return 0;
    }
    if(argc!=5)return 3;
    w=(uint32_t)strtoul(argv[1],NULL,10);h=(uint32_t)strtoul(argv[2],NULL,10);
    kind=(uint32_t)strtoul(argv[3],NULL,10);count=(uint32_t)strtoul(argv[4],NULL,10);
    if(kind>5||!lg_layout(w,h,&cw,&ch,&bytes))return 4;
    for(y=0;y<ch;++y)for(x=0;x<cw;++x) {
        v=kind==5?lg_pixel(x,y):lg_expected(kind,count,w,h,x,y);
        if(fwrite(&v,sizeof(v),1,stdout)!=1)return 5;
    }
    return fflush(stdout)?6:0;
}
