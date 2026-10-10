/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include "resource-tests.h"
#include "start-vector.h"
static int start_tests(void)
{
    unsigned char b[128];unsigned i,v;int rc;
    rc=run_tests();if(rc)return rc;
    CHECK(!xwn_check_resources(start_vector,sizeof(start_vector),XWN_PROFILE_XEMU));
    for(i=0;i<sizeof(start_vector);++i)CHECK(xwn_check_resources(start_vector,i,XWN_PROFILE_XEMU));
    /* The two independent compatibility changes, never a moved aperture. */
    copy_bytes(b,start_vector,sizeof(start_vector));xwn_w32(b+12,0x00010001);
    CHECK(!xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    xwn_w32(b+12,0);b[22]=1;
    CHECK(!xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    for(v=0;v<256;++v){
        copy_bytes(b,start_vector,sizeof(start_vector));b[22]=(unsigned char)v;
        CHECK((xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU)==0)==(v==1 || v==0x31));
    }
    copy_bytes(b,start_vector,sizeof(start_vector));xwn_w32(b+12,1);
    CHECK(xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    xwn_w32(b+12,0x10000);CHECK(xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    xwn_w32(b+12,0);xwn_w32(b+24,0xc100);CHECK(xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    xwn_w32(b+24,0xc000);xwn_w32(b+32,16);CHECK(xwn_check_resources(b,sizeof(start_vector),XWN_PROFILE_XEMU));
    /* Carry the allocation encoding through the physical two-window rules. */
    copy_bytes(b,physical220_boot,sizeof(physical220_boot));xwn_w32(b+12,0);b[22]=b[38]=0x31;
    CHECK(!xwn_check_resources(b,sizeof(physical220_boot),XWN_PROFILE_PHYSICAL));
    xwn_w32(b+40,0xc300);CHECK(xwn_check_resources(b,sizeof(physical220_boot),XWN_PROFILE_PHYSICAL));
    xwn_w32(b+40,0xc200);xwn_w32(b+48,64);CHECK(xwn_check_resources(b,sizeof(physical220_boot),XWN_PROFILE_PHYSICAL));
    xwn_w32(b+48,32);xwn_w32(b+16,1);CHECK(xwn_check_resources(b,36,XWN_PROFILE_PHYSICAL));
    return 0;
}
int main(void)
{
    int rc=start_tests();printf("{\"passed\":%s,\"cases\":%u,\"failure_line\":%d,\"captured_start_bytes\":%u}\n",rc?"false":"true",cases,rc,(unsigned)sizeof(start_vector));return rc!=0;
}
