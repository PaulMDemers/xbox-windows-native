#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "primary_copy.c"
static unsigned tests,cases,backward,forward,horizontal,empty,refused;
#define CHECK(x) do{++tests;if(!(x)){fprintf(stderr,"failed %d: %s\n",__LINE__,#x);abort();}}while(0)
static uint32_t seed=348;
static unsigned rnd(unsigned n){seed=seed*1664525U+1013904223U;return seed%n;}
static void run(unsigned w,unsigned h,RECTL r,POINTL s,CLIPOBJ *clip)
{
    unsigned bytes=w*h*4,i,x,y,k;ULONGLONG copied=99;int rc;unsigned expected=0;
    unsigned char *a=malloc(bytes+128),*orig=malloc(bytes+128),*want=malloc(bytes+128);
    SURFOBJ ram={0},primary={0};PDEV p={0};
    CHECK(a&&orig&&want);
    for(i=0;i<bytes+128;i++)a[i]=(unsigned char)rnd(256);
    memcpy(orig,a,bytes+128);memcpy(want,a,bytes+128);
    p.ShadowActive=1;p.BitsPerPixel=32;p.ScreenWidth=w;p.ScreenHeight=h;p.ScreenDelta=w*4;
    p.ShadowBits=a+64;p.ShadowObject=&ram;p.ShadowSurface=&ram;p.hDevEng=&p;
    ram.iType=STYPE_BITMAP;ram.iBitmapFormat=BMF_32BPP;ram.cjBits=bytes;
    ram.pvBits=ram.pvScan0=a+64;ram.hsurf=&ram;ram.hdev=&p;ram.lDelta=w*4;ram.sizlBitmap=(SIZEL){(LONG)w,(LONG)h};
    primary.owner=&p;primary.iBitmapFormat=BMF_32BPP;primary.sizlBitmap=ram.sizlBitmap;
    /* Independent oracle reads only the immutable preimage, pixel by pixel;
     * no planned offsets, chosen row order or row memmove reused. */
    for(y=0;y<h;y++)for(x=0;x<w;x++) {
        if((int)x<r.left || (int)x>=r.right || (int)y<r.top || (int)y>=r.bottom)continue;
        if(clip&&clip->iDComplexity==DC_RECT&&((int)x<clip->rclBounds.left || (int)x>=clip->rclBounds.right || (int)y<clip->rclBounds.top || (int)y>=clip->rclBounds.bottom))continue;
        for(k=0;k<4;k++)want[64+(y*w+x)*4+k]=orig[64+(((unsigned)s.y+y-r.top)*w+(unsigned)s.x+x-r.left)*4+k];
        expected+=4;
    }
    rc=XwnTryPrimaryCopy(&p,&primary,&primary,clip,NULL,&r,&s,&copied);
    CHECK(rc==(XWN_PRIMARY_COPY?(expected?1:0):-2));CHECK(copied==expected);
    CHECK(memcmp(a,XWN_PRIMARY_COPY?want:orig,bytes+128)==0);
    if(!expected)empty++;else if(r.top>s.y)backward++;else if(r.top<s.y)forward++;else horizontal++;
    ++cases;free(a);free(orig);free(want);
}
static void negatives(void)
{
    unsigned char a[1024],old[1024];XP_PLAN plan,oldplan;XP_RECT r={0,0,8,8},clip={1,1,4,4};unsigned i;
    SURFOBJ ram={0},target={0};PDEV p={0};RECTL dr={0,0,8,8};POINTL sp={0,0};CLIPOBJ c={DC_RECT,{0,0,8,8}};XLATEOBJ xl={XO_TRIVIAL};ULONGLONG b;
    memset(a,0x65,sizeof(a));memcpy(old,a,sizeof(a));memset(&plan,0x5b,sizeof(plan));oldplan=plan;
    for(i=0;i<11;i++) {
        XP_PTR base=(XP_PTR)a;unsigned n=1024,w=16,h=16,pitch=64;XP_RECT q=r,cl=clip;int sx=0,sy=0;
        switch(i){case 0:base=0;break;case 1:base++;break;case 2:base=(XP_PTR)-4;break;case 3:n--;break;case 4:w=1921;break;case 5:h=1081;break;case 6:pitch=68;break;case 7:q.left=INT32_MIN;break;case 8:q.right=INT32_MAX;break;case 9:sx=INT32_MAX;break;default:cl.left=5;break;}
        CHECK(XpPlan(base,n,w,h,pitch,&q,sx,sy,&cl,&plan)==0);CHECK(memcmp(&plan,&oldplan,sizeof(plan))==0);refused++;
    }
    for(i=0;i<24;i++) {
        memset(&p,0,sizeof(p));memset(&ram,0,sizeof(ram));memset(&target,0,sizeof(target));
        p.ShadowActive=1;p.BitsPerPixel=32;p.ScreenWidth=p.ScreenHeight=16;p.ScreenDelta=64;
        p.ShadowBits=a;p.ShadowObject=&ram;p.ShadowSurface=&ram;p.hDevEng=&p;
        ram.iType=STYPE_BITMAP;ram.iBitmapFormat=BMF_32BPP;ram.cjBits=1024;ram.pvBits=ram.pvScan0=a;ram.hsurf=&ram;ram.hdev=&p;ram.lDelta=64;ram.sizlBitmap=(SIZEL){16,16};
        target.owner=&p;target.iBitmapFormat=BMF_32BPP;target.sizlBitmap=ram.sizlBitmap;c.iDComplexity=DC_RECT;xl.flXlate=XO_TRIVIAL;dr=(RECTL){0,0,8,8};sp=(POINTL){0,0};
        switch(i){case 0:p.ShadowActive=0;break;case 1:target.owner=NULL;break;case 2:p.BitsPerPixel=24;break;case 3:target.iBitmapFormat=5;break;case 4:target.sizlBitmap.cx--;break;case 5:target.sizlBitmap.cy--;break;case 6:xl.flXlate=2;break;case 7:xl.flXlate=3;break;case 8:c.iDComplexity=DC_COMPLEX;break;case 9:p.ShadowObject=NULL;break;case 10:ram.iType=1;break;case 11:ram.iBitmapFormat=5;break;case 12:ram.fjBitmap=BMF_NOTSYSMEM;break;case 13:ram.pvBits=a+4;break;case 14:ram.pvScan0=a+4;break;case 15:ram.hsurf=NULL;break;case 16:ram.hdev=NULL;break;case 17:ram.sizlBitmap.cx--;break;case 18:ram.sizlBitmap.cy--;break;case 19:ram.lDelta=-64;break;case 20:ram.cjBits--;break;case 21:dr.left=-1;break;case 22:sp.x=10;break;default:sp.y=10;break;}
        b=123;CHECK(XwnTryPrimaryCopy(&p,&target,&target,&c,&xl,&dr,&sp,&b)==-1);CHECK(b==0);CHECK(memcmp(a,old,sizeof(a))==0);refused++;
    }
}
int main(void)
{
    unsigned i,w,h,rw,rh,dx,dy,sx,sy;
    /* Exhaust every relative displacement of a3x3 square inside8x8. */
    for(dy=0;dy<=5;dy++)for(dx=0;dx<=5;dx++)for(sy=0;sy<=5;sy++)for(sx=0;sx<=5;sx++) {
        RECTL r={(int)dx,(int)dy,(int)dx+3,(int)dy+3};POINTL s={(int)sx,(int)sy};run(8,8,r,s,NULL);
    }
    for(i=0;i<12000;i++) {
        CLIPOBJ c;RECTL r;POINTL s;
        w=1+rnd(64);h=1+rnd(48);rw=1+rnd(w);rh=1+rnd(h);dx=rnd(w-rw+1);dy=rnd(h-rh+1);sx=rnd(w-rw+1);sy=rnd(h-rh+1);
        r=(RECTL){(int)dx,(int)dy,(int)(dx+rw),(int)(dy+rh)};s=(POINTL){(int)sx,(int)sy};
        c.iDComplexity=i%3?DC_RECT:DC_TRIVIAL;c.rclBounds=(RECTL){(int)rnd(w+8)-4,(int)rnd(h+8)-4,0,0};c.rclBounds.right=c.rclBounds.left+(int)rnd(w+8);c.rclBounds.bottom=c.rclBounds.top+(int)rnd(h+8);
        run(w,h,r,s,i%4?&c:NULL);
    }
    run(1920,1080,(RECTL){1,1,961,541},(POINTL){0,0},NULL);
    run(1920,1080,(RECTL){0,0,960,540},(POINTL){1,1},NULL);
    run(1920,1080,(RECTL){960,540,1920,1080},(POINTL){0,0},NULL);
    negatives();CHECK(backward&&forward&&horizontal&&empty&&refused);
    printf("{\"enabled\":%d,\"checks\":%u,\"pixel_cases\":%u,\"downward\":%u,\"upward\":%u,\"same_row\":%u,\"empty\":%u,\"refusals\":%u}\n",XWN_PRIMARY_COPY,tests,cases,backward,forward,horizontal,empty,refused);return 0;
}
