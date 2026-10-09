/* Byte-for-byte copy oracle with redzones, signed rows and clip preservation.
 * SPDX-License-Identifier: GPL-2.0-or-later */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "dib_plan.h"
static unsigned checks, seed=0x1820114;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"failure line%d seed%x\n",__LINE__,seed);exit(1);}}while(0)
static unsigned next(void) {seed=seed*1664525U+1013904223U;return seed;}
static int surface_oracle(XD_SURFACE s)
{
    int y;int64_t at;
    if(!s.base || !s.size || s.width<=0 || s.height<=0 || !s.stride ||
       (uint64_t)s.base+s.size>0x100000000ULL ||
       (int64_t)s.width*4>llabs((int64_t)s.stride))return 0;
    /* Test fixture dimensions are bounded; extreme inputs separately tested. */
    for(y=0;y<s.height;y++) {
        at=(int64_t)s.scan+(int64_t)y*s.stride;
        if(at<s.base || at+(int64_t)s.width*4>(int64_t)s.base+s.size)return 0;
    }
    return 1;
}
static void testcase(unsigned id)
{
    unsigned char input[8192],actual[8192],expected[8192];
    XD_SURFACE a,b;XD_RECT r,c;XD_PLAN plan,before;
    int x,y,sx,sy,res,should,clipped=0;int64_t from,to;
    int w=1+(next()%29),h=1+(next()%23),stride=w*4+(next()%5)*4;
    a=(XD_SURFACE){0x10000,(unsigned)(stride*h),0x10000,stride,w,h};
    b=(XD_SURFACE){0x20000,(unsigned)(stride*h),0x20000,stride,w,h};
    if(next()&1){a.stride=-stride;a.scan+=(h-1)*stride;}
    if(next()&1){b.stride=-stride;b.scan+=(h-1)*stride;}
    r.left=next()%w;r.top=next()%h;r.right=r.left+1+next()%(w-r.left);
    r.bottom=r.top+1+next()%(h-r.top);sx=next()%(w-(r.right-r.left)+1);
    sy=next()%(h-(r.bottom-r.top)+1);
    c.left=(int)(next()%(w+10))-5;c.top=(int)(next()%(h+10))-5;
    c.right=c.left+next()%(w+10);c.bottom=c.top+next()%(h+10);
    if(id%9==0)b.size--;
    if(id%11==0)b.scan++;
    if(id%13==0)r.left=-1;
    if(id%17==0)sx=w;
    if(id%19==0){b.base=a.base+1;b.scan=b.base+(b.stride<0?(h-1)*stride:0);}
    if(id%23==0)c.right=c.left-1;
    if(id%29==0)a.stride=1;
    memset(&plan,0x5a,sizeof(plan));before=plan;
    res=XdPlan(&a,&b,r,sx,sy,id&1?&c:NULL,&plan);
    should=surface_oracle(a)&&surface_oracle(b)&&r.left>=0&&r.top>=0&&
           r.right>r.left&&r.bottom>r.top&&r.right<=w&&r.bottom<=h&&
           sx>=0&&sy>=0&&(int64_t)sx+r.right-r.left<=w&&
           (int64_t)sy+r.bottom-r.top<=h;
    if(should && (uint64_t)a.base<(uint64_t)b.base+b.size &&
       (uint64_t)b.base<(uint64_t)a.base+a.size) should=0;
    if(should&&(id&1)&&(c.left>c.right||c.top>c.bottom))should=0;
    if(should) {
        for(y=r.top;y<r.bottom;y++)for(x=r.left;x<r.right;x++)
            if(!(id&1)||(x>=c.left&&x<c.right&&y>=c.top&&y<c.bottom))++clipped;
        CHECK(res==(clipped?XD_HIT:XD_EMPTY));
    } else CHECK(res!=XD_HIT && res!=XD_EMPTY);
    if(res!=XD_HIT){CHECK(memcmp(&plan,&before,sizeof(plan))==0);return;}
    for(x=0;x<(int)sizeof(input);x++)input[x]=(unsigned char)(x*37+id);
    memset(actual,0xa5,sizeof(actual));memcpy(expected,actual,sizeof(actual));
    for(y=r.top;y<r.bottom;y++)for(x=r.left;x<r.right;x++) {
        if((id&1)&&!(x>=c.left&&x<c.right&&y>=c.top&&y<c.bottom))continue;
        from=(int64_t)b.scan-b.base+(int64_t)(sy+y-r.top)*b.stride+(sx+x-r.left)*4;
        to=(int64_t)a.scan-a.base+(int64_t)y*a.stride+x*4;
        CHECK(from>=0&&from+4<=b.size&&to>=0&&to+4<=a.size);
        memcpy(expected+64+to,input+64+from,4);
    }
    from=plan.source;to=plan.target;
    for(y=0;y<(int)plan.rows;y++) {
        CHECK(from>=0&&from+plan.bytes<=b.size&&to>=0&&to+plan.bytes<=a.size);
        memcpy(actual+64+to,input+64+from,plan.bytes);
        from+=plan.source_step;to+=plan.target_step;
    }
    CHECK(memcmp(actual,expected,sizeof(actual))==0);
}
int main(void)
{
    unsigned i;XD_PLAN p,before;XD_SURFACE a={0xfffff000,4096,0xfffff000,4096,1024,1};
    XD_SURFACE b={0x1000,4096,0x1000,4096,1024,1};XD_RECT r={0,0,1024,1};
    CHECK(XdPlan(&a,&b,r,0,0,NULL,&p)==XD_HIT);CHECK(p.bytes==4096&&p.rows==1);
    a.size=4097;CHECK(XdPlan(&a,&b,r,0,0,NULL,&p)==XD_GEOMETRY);
    a=(XD_SURFACE){0x10000,4096,0x10000,INT_MIN,1,INT_MAX};
    CHECK(XdPlan(&a,&b,r,0,0,NULL,&p)==XD_GEOMETRY);
    r=(XD_RECT){INT_MIN,INT_MIN,INT_MAX,INT_MAX};memset(&p,0xa5,sizeof(p));before=p;
    CHECK(XdPlan(&a,&b,r,INT_MAX,INT_MAX,NULL,&p)==XD_GEOMETRY);
    CHECK(memcmp(&p,&before,sizeof(p))==0);
    a=b;r=(XD_RECT){0,0,1,1};CHECK(XdPlan(&a,&b,r,0,0,NULL,&p)==XD_ALIAS);
    for(i=0;i<30000;i++)testcase(i);
    printf("PASS %u checks;30000 byte-oracle cases; signed rows, clipping, alias, padding, overflow/redzones\n",checks);
    return 0;
}
