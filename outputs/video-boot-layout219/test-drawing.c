/* SPDX-License-Identifier: GPL-2.0-or-later
 * Execute extracted actual drawing/reset bodies against independently guarded
 * memory. Host HAL/palette/font wrappers are models, not a guest boot. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
typedef uint32_t ULONG;typedef int32_t LONG;typedef uintptr_t ULONG_PTR;
typedef uint8_t UCHAR,*PUCHAR;typedef uint16_t USHORT;typedef char CHAR;
typedef uint32_t RGBQUAD,*PULONG;typedef int BOOLEAN;typedef void VOID;
#define TRUE 1
#define FALSE 0
#define NTAPI
#define _In_
#define _In_reads_(x)
#define _Out_writes_bytes_all_(x)
#define SCREEN_WIDTH 640u
#define SCREEN_HEIGHT 480u
#define BOOTCHAR_HEIGHT 13u
#define BOOTCHAR_WIDTH 8u
#define FONT_PTR_DELTA 1u
#define BV_COLOR_NONE 16u
#define BV_COLOR_BLACK 0u
#define NV2A_VIDEO_MEMORY_SIZE 0x400000u
#define BB_OFFSET(x,y) ((y)*640u+(x))
#define FB_OFFSET(x,y) (((PanV+(y))*FrameBufferWidth+PanH+(x))*BytesPerPixel)
#define RtlZeroMemory(p,n) memset(p,0,n)
#define RtlCopyMemory(p,q,n) memcpy(p,q,n)
#include "boot_layout.h"
static ULONG_PTR FrameBufferStart;
static ULONG FrameBufferWidth,FrameBufferHeight,PanH,PanV,BootWritableBytes;
static UCHAR BytesPerPixel=4;static RGBQUAD CachedPalette[16];static PUCHAR BackBuffer;
static struct {ULONG Left,Top,Right,Bottom;} VidpScrollRegion;
static unsigned hal_calls;
static void HalResetDisplay(void){hal_calls++;}
static const UCHAR *GetFontPtr(CHAR c){static const UCHAR font[13]={0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa};(void)c;return font;}
static void ApplyPalette(void);
static void InitializePalette(void){for(unsigned i=0;i<16;i++)CachedPalette[i]=i?0xff000000u+i:0;ApplyPalette();}
void VidSolidColorFill(ULONG,ULONG,ULONG,ULONG,UCHAR);
#include "actual-drawing.inc"
static unsigned checks;
#define CHECK(v) do{checks++;if(!(v)){fprintf(stderr,"line%d: %s\n",__LINE__,#v);abort();}}while(0)
static void guard(const unsigned char *p,size_t n,unsigned char value){for(size_t i=0;i<n;i++)CHECK(p[i]==value);}
int main(void){
    const unsigned dims[][2]={{640,480},{800,600},{1024,576},{1280,720}};
    XWN_BOOT_LAYOUT l={0},unchanged={1,2,3};
    for(unsigned width=0;width<9;width++){
        const ULONG values[]={0,639,640,1920,1921,0xffff,0x10000000,0x7fffffff,0xffffffff};
        l=unchanged;int ok=XwnBootLayout(0x03c00000,values[width],480,316160,&l);
        CHECK(ok==(values[width]>=640&&values[width]<=1920));
        if(!ok)CHECK(!memcmp(&l,&unchanged,sizeof(l)));
    }
    CHECK(!XwnBootLayout(0,640,480,316160,&l));CHECK(!XwnBootLayout(0x03c00000,640,480,0,&l));
    CHECK(!XwnBootLayout(0x03c00000,640,480,0xffffffff,&l));CHECK(!XwnBootLayout(0x03c00000,1920,1080,316160,&l));
    CHECK(!XwnBootLayout(0x03c00000,640,480,316160,0));
    for(unsigned ram=0;ram<2;ram++)for(unsigned d=0;d<4;d++)for(unsigned setmode=0;setmode<2;setmode++){
        CHECK(XwnBootLayout(ram?0x07c00000:0x03c00000,dims[d][0],dims[d][1],316160,&l));
        unsigned char *raw=malloc(0x402000);CHECK(raw!=NULL);memset(raw,0xa5,0x402000);
        unsigned char *mem=raw+4096;FrameBufferStart=(uintptr_t)mem;
        FrameBufferWidth=dims[d][0];FrameBufferHeight=dims[d][1];PanH=(FrameBufferWidth-640)/2;PanV=(FrameBufferHeight-480)/2;
        BootWritableBytes=l.WritableBytes;
#if CONTROL
        BackBuffer=mem+0x400000-316160;
#else
        BackBuffer=mem+l.HiddenOffset;
#endif
        unsigned before=hal_calls;ResetDisplay(setmode);CHECK(hal_calls==before+setmode);
#if CONTROL
        CHECK(mem[0x3eb000]==0);CHECK(mem[0x3fffff]==0);
#else
        guard(mem+0x3eb000,0x15000,0xa5);
        VidSolidColorFill(0,0,639,479,3);
        for(unsigned y=0;y<480;y++)for(unsigned x=0;x<640;x++){
            CHECK(BackBuffer[y*640+x]==3);CHECK(*(PULONG)(mem+FB_OFFSET(x,y))==CachedPalette[3]);
        }
        DisplayCharacter('X',632,467,7,1);
        PreserveRow(466,14,FALSE);VidSolidColorFill(0,466,639,479,5);PreserveRow(466,14,TRUE);
        VidpScrollRegion.Left=0;VidpScrollRegion.Right=639;VidpScrollRegion.Top=0;VidpScrollRegion.Bottom=465;DoScroll(14);
        unsigned char packed[640*480/2];VidScreenToBufferBlt(packed,0,0,640,480,320);
        for(unsigned y=0;y<480;y++)for(unsigned x=0;x<640;x+=2)
            CHECK(packed[y*320+x/2]==(unsigned char)((BackBuffer[y*640+x]&15)*16+(BackBuffer[y*640+x+1]&15)));
        InitPaletteWithTable(CachedPalette,16);guard(mem+0x3eb000,0x15000,0xa5);
        ResetDisplay(setmode);guard(mem+0x3eb000,0x15000,0xa5);
#endif
        guard(raw,4096,0xa5);guard(mem+0x400000,4096,0xa5);free(raw);
    }
    printf("{\"passed\":true,\"checks\":%u,\"profiles\":2,\"geometries\":4,\"control\":%d}\n",checks,CONTROL);
}
