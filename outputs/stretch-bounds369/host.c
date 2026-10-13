/* Actual wrappers/upload code; modeled GDI engine and clip service. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef int BOOL;
typedef int32_t LONG;
typedef uint32_t ULONG,DWORD,ROP4;
typedef uint64_t ULONGLONG;
typedef int64_t LONGLONG;
typedef unsigned char BYTE;
typedef void VOID;
typedef struct { LONG left,top,right,bottom; } RECTL;
typedef struct { LONG x,y; } POINTL;
typedef struct { int token; } XLATEOBJ,COLORADJUSTMENT,BRUSHOBJ;
typedef struct { RECTL rclBounds; ULONG iDComplexity; RECTL parts[2]; int fault; } CLIPOBJ;
typedef struct PDEV PDEV,*PPDEV;
typedef struct { PPDEV owner; } SURFOBJ;
struct PDEV { BOOL ShadowActive; SURFOBJ *ShadowObject; void *ShadowBits,*ScreenPtr;
    LONG ScreenWidth,ScreenHeight,ScreenDelta; ULONG ShadowCalls[14],ShadowUploads;
    ULONGLONG ShadowBytes; };
typedef struct { ULONGLONG bytes; } XWT_COPY;
#define TRUE 1
#define FALSE 0
#define APIENTRY
#define DC_COMPLEX 3
#define CT_RECTANGLES 0
#define CD_ANY 0
#define XWN_UC_STORES 0
#define max(a,b) ((a)>(b)?(a):(b))
#define min(a,b) ((a)<(b)?(a):(b))
static unsigned checks,cases,eng_calls,enum_calls;
static int enabled,engine_ok,mutate_argument,reject_owner;
#define XWN_STRETCH_BOUNDS enabled
static PDEV dev;
static SURFOBJ target,source,shadow,mask;
static RECTL original;
static RECTL *argument;
static void need(int ok) { ++checks; if(!ok) {fprintf(stderr,"check %u case %u\n",checks,cases);abort();} }
static PPDEV XwnOwner(SURFOBJ *s) {return s?s->owner:NULL;}
static BOOL XwnSelectOwner(PPDEV *p,SURFOBJ *s) {
    if(reject_owner)return FALSE;
    if(s&&s->owner){if(*p&&*p!=s->owner)return FALSE;*p=s->owner;}return TRUE;
}
static LONGLONG XwnProfileStart(void) {return 1;}
static void XwnProfileEnd(PPDEV p,unsigned n,LONGLONG t) {(void)p;(void)n;(void)t;}
static void XwnRowRecord(PPDEV p,ULONG a,ULONG b,ULONG n){(void)p;(void)a;(void)b;(void)n;}
static void XwtCopy(XWT_COPY *c,ULONGLONG n){c->bytes+=n;}
static void CLIPOBJ_cEnumStart(CLIPOBJ*c,int a,int b,int d,int e){(void)c;(void)a;(void)b;(void)d;(void)e;enum_calls=0;}
static BOOL CLIPOBJ_bEnum(CLIPOBJ*c,ULONG size,ULONG *batch){
    RECTL *r=(RECTL*)(batch+1);(void)size;++enum_calls;
    if(c->fault==1){*batch=33;return FALSE;}
    if(c->fault==2){*batch=1;r[0]=(RECTL){4,0,2,3};return FALSE;}
    if(c->fault==3){*batch=0;return TRUE;}
    *batch=2;r[0]=c->parts[0];r[1]=c->parts[1];return FALSE;
}
static int inside(const RECTL*r,int x,int y){return x>=r->left&&x<r->right&&y>=r->top&&y<r->bottom;}
static int clipped(CLIPOBJ*c,int x,int y){
    if(!c)return 1;
    if(!inside(&c->rclBounds,x,y))return 0;
    return c->iDComplexity!=DC_COMPLEX||inside(&c->parts[0],x,y)||inside(&c->parts[1],x,y);
}
static BOOL engine(SURFOBJ*d,SURFOBJ*s,SURFOBJ*m,CLIPOBJ*c,RECTL*r){
    int x,y;uint32_t *ram=dev.ShadowBits;RECTL box;
    ++eng_calls;need(d==&shadow&&s==&source&&m==&mask);need(r==argument);
    if(r)need(!memcmp(r,&original,sizeof(*r)));
    /* Independent geometric oracle, not the candidate helper. */
    box=original;
    for(y=0;y<24;y++)for(x=0;x<32;x++){
        int inx=(x>=box.left&&x<box.right)||(x>=box.right&&x<box.left);
        int iny=(y>=box.top&&y<box.bottom)||(y>=box.bottom&&y<box.top);
        if(clipped(c,x,y)&&((r&&inx&&iny)||(!engine_ok&&x==7&&y==8)))
            ram[y*32+x]=(uint32_t)(0x12340000u+(unsigned)x*17u+(unsigned)y*29u);
    }
    if(r&&mutate_argument)*r=(RECTL){0,0,1,1};
    return engine_ok;
}
static BOOL EngStretchBlt(SURFOBJ*d,SURFOBJ*s,SURFOBJ*m,CLIPOBJ*c,XLATEOBJ*x,COLORADJUSTMENT*a,POINTL*h,RECTL*r,RECTL*src,POINTL*mp,ULONG mode){
    (void)x;(void)a;(void)h;(void)src;(void)mp;need(mode==3);return engine(d,s,m,c,r);
}
static BOOL EngStretchBltROP(SURFOBJ*d,SURFOBJ*s,SURFOBJ*m,CLIPOBJ*c,XLATEOBJ*x,COLORADJUSTMENT*a,POINTL*h,RECTL*r,RECTL*src,POINTL*mp,ULONG mode,BRUSHOBJ*b,DWORD rop){
    (void)x;(void)a;(void)h;(void)src;(void)mp;(void)b;need(mode==3&&rop==0xaacc);return engine(d,s,m,c,r);
}
#include "row_store.h"
#include "stretch_bounds.h"
#include "actual.inc"
static ULONGLONG run(int variant,int on,int success,int mutation,int null_rect,int clipkind,RECTL rect){
    uint32_t ram[32*24+32],screen[32*24+32];unsigned i;BOOL result;
    CLIPOBJ clip={{2,3,30,22},1,{{2,3,14,22},{19,3,30,22}},0};
    CLIPOBJ *cp=clipkind?&clip:NULL;
    RECTL arg=rect,src={0,0,16,8};
    ++cases;enabled=on;engine_ok=success;mutate_argument=mutation;eng_calls=0;
    for(i=0;i<32*24+32;i++)ram[i]=screen[i]=0xddeeff00u+i;
    memset(&dev,0,sizeof(dev));dev.ShadowActive=TRUE;dev.ShadowObject=&shadow;
    dev.ShadowBits=ram+16;dev.ScreenPtr=screen+16;dev.ScreenWidth=32;dev.ScreenHeight=24;dev.ScreenDelta=128;
    target.owner=&dev;source.owner=NULL;shadow.owner=NULL;mask.owner=NULL;
    if(clipkind>=2)clip.iDComplexity=DC_COMPLEX;
    if(clipkind>=3)clip.fault=clipkind-2;
    original=rect;argument=null_rect?NULL:&arg;
    if(variant)result=XwnStretchBltROP(&target,&source,&mask,cp,NULL,NULL,NULL,argument,&src,NULL,3,NULL,0xaacc);
    else result=XwnStretchBlt(&target,&source,&mask,cp,NULL,NULL,NULL,argument,&src,NULL,3);
    need(result==success);need(eng_calls==1);need(dev.ShadowCalls[variant?9:8]==1);
    for(i=0;i<32*24+32;i++)need(ram[i]==screen[i]);
    for(i=0;i<16;i++){need(ram[i]==0xddeeff00u+i);need(ram[32*24+16+i]==0xddeeff00u+32*24+16+i);}
    if(!mutation&&!null_rect)need(!memcmp(&arg,&rect,sizeof(arg)));
    return dev.ShadowBytes;
}
int main(void){
    RECTL caseset[]={{5,6,15,16},{15,6,5,16},{5,16,15,6},{15,16,5,6},
        {-100,-100,10,10},{20,18,100,100},{-30,2,-1,10},{32,24,40,30},
        {INT32_MIN,INT32_MIN,INT32_MAX,INT32_MAX},{INT32_MAX,INT32_MAX,INT32_MIN,INT32_MIN},
        {5,5,5,9},{5,5,9,5}};
    unsigned n,v,clip,ok,mut;ULONGLONG old,new;
    for(n=0;n<sizeof(caseset)/sizeof(caseset[0]);n++)for(v=0;v<2;v++)for(clip=0;clip<6;clip++)for(ok=0;ok<2;ok++)for(mut=0;mut<2;mut++){
        old=run(v,0,ok,mut,0,clip,caseset[n]);new=run(v,1,ok,mut,0,clip,caseset[n]);
        need(new<=old);if(!ok||n>=10)need(new==old);
    }
    for(v=0;v<2;v++)for(ok=0;ok<2;ok++){
        old=run(v,0,ok,0,1,0,caseset[0]);new=run(v,1,ok,0,1,0,caseset[0]);need(new==old);
    }
    old=run(0,0,1,0,0,0,caseset[0]);new=run(0,1,1,0,0,0,caseset[0]);need(old==3072&&new==400);
    reject_owner=1;eng_calls=0;need(!XwnStretchBlt(&target,&source,&mask,NULL,NULL,NULL,NULL,&original,NULL,NULL,3));need(eng_calls==0);
    printf("{\"cases\":%u,\"checks\":%u,\"modeled_full_clip_bytes\":%llu,\"modeled_bounded_bytes\":%llu}\n",cases,checks,(unsigned long long)old,(unsigned long long)new);
    return 0;
}
