/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#define XGT_U32 uint32_t
#define XGT_U64 uint64_t
#define XGT_I32 int32_t
#include "transfer_plan.h"
static unsigned checks, cases, strips;
static uint32_t seed=0x212b1001;
static uint32_t rng(void) { seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed; }
#define CHECK(x) do { checks++; if(!(x)) { fprintf(stderr,"line %u: %s\n",__LINE__,#x);exit(1); } } while(0)
static void rejected(XGT_LAYOUT a, XGT_LAYOUT b, XGT_RECT r, uint32_t cap)
{
    XGT_PLAN p,zero={0};memset(&p,0x9b,sizeof(p));
    CHECK(!XgtPlan(&p,&a,&b,&r,cap));CHECK(!memcmp(&p,&zero,sizeof(p)));
}
static void pixels(XGT_LAYOUT a, XGT_LAYOUT b, XGT_RECT r, uint32_t cap)
{
    unsigned char *src=malloc(a.bytes+64),*dst=malloc(b.bytes+64);
    unsigned char *oracle=malloc(b.bytes),*saved=malloc(a.bytes);
    unsigned char *stage=malloc(cap+64);
    XGT_PLAN p;XGT_STRIP s,zero={0};uint32_t y,x,cursor=0;
    CHECK(src && dst && oracle && saved && stage);
    memset(src,0xac,a.bytes+64);memset(dst,0xb5,b.bytes+64);
    memset(oracle,0xb5,b.bytes);
    /* Independent full bitmap oracle, including alpha and all padding. */
    for(y=0;y<a.height;y++) for(x=0;x<a.width;x++) {
        unsigned char pixel[4]={(unsigned char)(x^y), (unsigned char)(x+3*y),
            (unsigned char)(7*x+y), (unsigned char)(0x41+(y%173))};
        memcpy(src+32+y*a.pitch+x*4,pixel,4);
        if(x>=(uint32_t)r.left && x<(uint32_t)r.right &&
           y>=(uint32_t)r.top && y<(uint32_t)r.bottom)
            memcpy(oracle+y*b.pitch+x*4,pixel,4);
    }
    memcpy(saved,src+32,a.bytes);
    CHECK(XgtPlan(&p,&a,&b,&r,cap));
    while(XgtStrip(&p,cursor,&s)) {
        strips++;CHECK(s.next_row>cursor && s.next_row<=p.height);
        CHECK(s.packed_bytes<=cap && s.rows && s.row_bytes);
        memset(stage,0xdc,cap+64);
        for(y=0;y<s.rows;y++) memcpy(stage+32+y*s.row_bytes,
                src+32+s.source_offset+y*a.pitch,s.row_bytes);
        for(y=0;y<s.rows;y++) memcpy(dst+32+s.destination_offset+y*b.pitch,
                stage+32+y*s.row_bytes,s.row_bytes);
        for(x=0;x<32;x++) CHECK(stage[x]==0xdc);
        for(x=s.packed_bytes+32;x<cap+64;x++) CHECK(stage[x]==0xdc);
        cursor=s.next_row;
        CHECK(strips<1000000); /* Fixed test process bound, not a GPU timeout. */
    }
    CHECK(cursor==p.height);CHECK(!memcmp(&s,&zero,sizeof(s)));
    CHECK(!memcmp(oracle,dst+32,b.bytes));CHECK(!memcmp(saved,src+32,a.bytes));
    for(x=0;x<32;x++) CHECK(src[x]==0xac && src[a.bytes+32+x]==0xac &&
        dst[x]==0xb5 && dst[b.bytes+32+x]==0xb5);
    cases++;free(src);free(dst);free(oracle);free(saved);free(stage);
}
int main(void)
{
    XGT_LAYOUT a={640,480,2560,1228800},b=a;
    XGT_RECT r={0,0,640,480};XGT_PLAN p,q;XGT_STRIP s,zero={0};
    unsigned i,j;
    pixels(a,b,r,65536);pixels(a,b,(XGT_RECT){639,479,640,480},4);
    b.pitch+=64;b.bytes=b.pitch*b.height;
    pixels(a,b,(XGT_RECT){13,17,623,477},2440);
    /* Different source/destination pitches and one-row/exact/remainder strips. */
    for(i=0;i<320;i++) {
        a.width=1+rng()%1920;a.height=1+rng()%256;
        a.pitch=(a.width+ rng()%33)*4;a.bytes=a.pitch*a.height;
        b=a;b.pitch=(a.width+rng()%33)*4;b.bytes=b.pitch*b.height;
        r.left=rng()%a.width;r.top=rng()%a.height;
        r.right=r.left+1+rng()%(a.width-r.left);
        r.bottom=r.top+1+rng()%(a.height-r.top);
        j=(r.right-r.left)*4;
        pixels(a,b,r,j+(rng()%(65537-j)));
    }
    a=(XGT_LAYOUT){640,480,2560,1228800};b=a;r=(XGT_RECT){0,0,640,480};
    rejected(a,b,r,0);rejected(a,b,r,2559);rejected(a,b,r,65537);
    rejected(a,b,(XGT_RECT){-1,0,640,480},65536);
    rejected(a,b,(XGT_RECT){0,-1,640,480},65536);
    rejected(a,b,(XGT_RECT){0,0,0,1},65536);
    rejected(a,b,(XGT_RECT){0,0,641,480},65536);
    rejected(a,b,(XGT_RECT){0,0,640,481},65536);
    rejected(a,b,(XGT_RECT){INT32_MIN,INT32_MIN,INT32_MAX,INT32_MAX},65536);
    b.width--;rejected(a,b,r,65536);b=a;b.bytes--;rejected(a,b,r,65536);
    b=a;b.pitch--;rejected(a,b,r,65536);b=a;b.bytes=UINT32_MAX;rejected(a,b,r,65536);
    b=a;b.height=UINT32_MAX;rejected(a,b,r,65536);
    a=(XGT_LAYOUT){1920,1080,7680,8294400};rejected(a,a,(XGT_RECT){0,0,1920,1080},65536);
    a=(XGT_LAYOUT){1920,540,7680,4147200};pixels(a,a,(XGT_RECT){0,0,1920,540},65536);
    a=(XGT_LAYOUT){640,480,2560,1228800};b=a;r=(XGT_RECT){0,0,640,480};
    CHECK(XgtPlan(&p,&a,&b,&r,65536));
    /* Every descriptor word is adversarially mutated. Tests exercise the actual
     * planner: accepted mutations must still have bounded monotonic strips. */
    for(i=0;i<100000;i++) {
        uint32_t words[sizeof(q)/4],cursor=0;
        memcpy(words,&p,sizeof(q));words[rng()%(sizeof(q)/4)]=rng();memcpy(&q,words,sizeof(q));
        while(XgtStrip(&q,cursor,&s)) {
            CHECK(s.rows && s.packed_bytes<=65536);
            CHECK((uint64_t)s.source_offset+(uint64_t)(s.rows-1)*q.source.pitch+s.row_bytes<=q.source.bytes);
            CHECK((uint64_t)s.destination_offset+(uint64_t)(s.rows-1)*q.destination.pitch+s.row_bytes<=q.destination.bytes);
            CHECK(s.next_row>cursor && s.next_row<=1080);
            cursor=s.next_row;
        }
        CHECK(!memcmp(&s,&zero,sizeof(s)));
    }
    CHECK(!XgtPlan(NULL,&a,&b,&r,65536));CHECK(!XgtStrip(&p,0,NULL));
    CHECK(!XgtStrip(&p,UINT32_MAX,&s));CHECK(!XgtStrip(NULL,0,&s));
    printf("checks=%u exact_pixel_cases=%u strips=%u malformed_plans=100000\n",checks,cases,strips);
    return 0;
}
