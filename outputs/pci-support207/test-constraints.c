/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "constraints.h"
int main(int argc,char **argv)
{
    unsigned char original[4096],data[4096],before[4096];
    FILE *f;size_t size;unsigned i,cases=0;int result;
    assert(argc==2);f=fopen(argv[1],"rb");assert(f);size=fread(original,1,sizeof(original),f);assert(feof(f));fclose(f);
    assert(size==328);memcpy(data,original,size);assert(xwn_pin_requirements(data,(unsigned)size)==0);
    for(i=0;i<size;++i) {
        /* Only BAR1's preferred+alternative port alignment/min/max fields. */
        if((i>=40+2*32+12 && i<40+3*32) || (i>=40+3*32+12 && i<40+4*32))continue;
        assert(data[i]==original[i]);
    }
    for(i=2;i<=3;++i) {
        unsigned char *p=data+40+i*32;
        assert(xwn_get32(p+8)==16 && xwn_get32(p+12)==1 && xwn_get32(p+16)==0xc000 && xwn_get32(p+24)==0xc00f);
    }
    memcpy(before,data,size);assert(xwn_pin_requirements(data,(unsigned)size)==0);assert(!memcmp(before,data,size));cases+=2;
    /* Every truncation fails with no write, even when its recorded size is edited. */
    for(i=0;i<size;++i) {
        memcpy(data,original,size);xwn_put32(data,i);memcpy(before,data,size);
        assert(xwn_pin_requirements(data,i)!=0 && !memcmp(before,data,size));++cases;
    }
    /* All individual byte mutations: any rejection is atomic; successes still
       pin both controller alternatives and retain unrelated bytes. */
    for(i=0;i<size*8;++i) {
        memcpy(data,original,size);data[i/8]^=(unsigned char)(1U<<(i%8));memcpy(before,data,size);
        result=xwn_pin_requirements(data,(unsigned)size);
        if(result)assert(!memcmp(before,data,size));
        else {
            assert(xwn_get32(data+40+2*32+16)==0xc000 && xwn_get32(data+40+3*32+16)==0xc000);
        }
        ++cases;
    }
    printf("{\"cases\":%u,\"passed\":true,\"scope\":\"actual physical189 requirements and malformed-input atomicity\"}\n",cases);
    return 0;
}
