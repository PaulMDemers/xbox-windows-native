/* SPDX-License-Identifier: MIT. Same tests run with ASan/UBSan and on NT5. */
#include "resources.h"
#include "vectors.h"
#include "../constraints.h"
static unsigned cases;
static void copy_bytes(unsigned char *d,const unsigned char *s,unsigned n)
{ while(n--)*d++=*s++; }
static int equal_bytes(const unsigned char *a,const unsigned char *b,unsigned n)
{ while(n--)if(*a++!=*b++)return 0;return 1; }
#define CHECK(x) do { ++cases; if(!(x))return __LINE__; } while(0)
static int only_pinned(const unsigned char *a,const unsigned char *b,unsigned n,unsigned kind)
{
    unsigned i;
    for(i=0;i<n;++i) {
        unsigned d=i>=40 ? (i-40)/32 : 999,field=i>=40 ? (i-40)%32 : 0;
        if(field>=12 && ((kind==XWN_PROFILE_PHYSICAL && (d==2||d==3||d==5||d==6)) ||
                        (kind==XWN_PROFILE_XEMU && (d==0||d==1))))continue;
        if(a[i]!=b[i])return 0;
    }
    return 1;
}
static int run_tests(void)
{
    /* Single-threaded test process; avoid CRT stack probing on NT5. */
    static unsigned char b[4096],before[4096],pinned[4096];
    unsigned kind,profile,n,i;int rc;
    /* Reproducer: old policy leaves BAR2's relocation alternative unrestricted. */
    copy_bytes(b,physical220_basic,sizeof(physical220_basic));
    CHECK(!xwn_pin_requirements(b,sizeof(physical220_basic)));
    CHECK(xwn_get32(b+40+6*32+16)==0 && xwn_get32(b+40+6*32+24)==0xffffffffU);
    for(kind=XWN_PROFILE_PHYSICAL;kind<=XWN_PROFILE_XEMU;++kind) {
        const unsigned char *original=kind==XWN_PROFILE_PHYSICAL ? physical220_basic : emulator004_basic;
        const unsigned char *boot=kind==XWN_PROFILE_PHYSICAL ? physical220_boot : emulator004_boot;
        unsigned boot_size=kind==XWN_PROFILE_PHYSICAL ? sizeof(physical220_boot) : sizeof(emulator004_boot);
        n=kind==XWN_PROFILE_PHYSICAL ? sizeof(physical220_basic) : sizeof(emulator004_basic);
        copy_bytes(b,original,n);profile=99;
        CHECK(!xwn_pin_resources(b,n,&profile) && profile==kind);
        CHECK(only_pinned(original,b,n,kind));
        copy_bytes(pinned,b,n);
        CHECK(!xwn_pin_resources(b,n,&profile) && equal_bytes(b,pinned,n));
        CHECK(!xwn_check_resources(boot,boot_size,kind));
        CHECK(xwn_check_resources(boot,boot_size,3-kind));
        for(i=0;i<n;++i) {
            copy_bytes(b,original,n);xwn_w32(b,i);copy_bytes(before,b,n);profile=99;
            CHECK(xwn_pin_resources(b,i,&profile) && profile==99 && equal_bytes(b,before,n));
        }
        for(i=0;i<n*8;++i) {
            copy_bytes(b,original,n);b[i/8]^=(unsigned char)(1U<<(i%8));
            copy_bytes(before,b,n);profile=99;rc=xwn_pin_resources(b,n,&profile);
            if(rc)CHECK(profile==99 && equal_bytes(b,before,n));
            else {
                CHECK(profile==kind && only_pinned(before,b,n,kind));
                CHECK(xwn_r32(b+40+(kind==XWN_PROFILE_PHYSICAL ? 3 : 1)*32+16)==0xc000);
                if(kind==XWN_PROFILE_PHYSICAL)CHECK(xwn_r32(b+40+6*32+16)==0xc200 && xwn_r32(b+40+6*32+24)==0xc21f);
            }
        }
        for(i=0;i<boot_size;++i)CHECK(xwn_check_resources(boot,i,kind));
        copy_bytes(b,boot,boot_size);xwn_w32(b+24,0xc100);
        CHECK(xwn_check_resources(b,boot_size,kind));
    }
    /* Valid first list, invalid second: reject without partially pinning first. */
    n=sizeof(physical220_basic);copy_bytes(b,physical220_basic,n);
    copy_bytes(b+n,physical220_basic+32,n-32);xwn_w32(b,2*n-32);xwn_w32(b+28,2);
    copy_bytes(before,b,2*n-32);profile=99;
    CHECK(!xwn_pin_resources(b,2*n-32,&profile) && profile==XWN_PROFILE_PHYSICAL);
    copy_bytes(b,before,2*n-32);b[n+8+6*32+20]=1;copy_bytes(before,b,2*n-32);profile=99;
    CHECK(xwn_pin_resources(b,2*n-32,&profile) && profile==99 && equal_bytes(b,before,2*n-32));
    /* C200 cannot be omitted, moved, widened, or duplicated. */
    copy_bytes(b,physical220_boot,sizeof(physical220_boot));xwn_w32(b+16,1);
    CHECK(xwn_check_resources(b,36,XWN_PROFILE_PHYSICAL));
    copy_bytes(b,physical220_boot,sizeof(physical220_boot));xwn_w32(b+40,0xc300);
    CHECK(xwn_check_resources(b,52,XWN_PROFILE_PHYSICAL));
    copy_bytes(b,physical220_boot,sizeof(physical220_boot));xwn_w32(b+48,64);
    CHECK(xwn_check_resources(b,52,XWN_PROFILE_PHYSICAL));
    copy_bytes(b,physical220_boot,sizeof(physical220_boot));copy_bytes(b+52,b+36,16);xwn_w32(b+16,3);
    CHECK(xwn_check_resources(b,68,XWN_PROFILE_PHYSICAL));
    /* One separate physical BAR0 allocation is allowed; overlap or two are not. */
    xwn_w32(b+56,0xc100);xwn_w32(b+64,16);
    CHECK(!xwn_check_resources(b,68,XWN_PROFILE_PHYSICAL));
    copy_bytes(b+68,b+52,16);xwn_w32(b+16,4);
    CHECK(xwn_check_resources(b,84,XWN_PROFILE_PHYSICAL));
    xwn_w32(b+16,3);xwn_w32(b+56,0xc008);
    CHECK(xwn_check_resources(b,68,XWN_PROFILE_PHYSICAL));
    return 0;
}
