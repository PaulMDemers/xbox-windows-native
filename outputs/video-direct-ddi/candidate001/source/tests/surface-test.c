#include "framebuf.h"
#include <assert.h>
#include <stdio.h>
static int Fault, Maps, Unmaps, Bitmaps, Deletes, Associates, Cases;
static unsigned char Pixels[16];
static unsigned char Surface;
ULONG EngDeviceIoControl(HANDLE h,ULONG op,PVOID in,ULONG ni,PVOID out,ULONG no,ULONG *returned)
{
    (void)h;(void)ni;(void)no;
    if(op==IOCTL_VIDEO_SET_CURRENT_MODE) return Fault==1;
    if(op==IOCTL_VIDEO_RESET_DEVICE) return Fault==8;
    if(op==IOCTL_VIDEO_MAP_VIDEO_MEMORY) {
        VIDEO_MEMORY_INFORMATION *v=out;
        if(Fault==2)return 1;
        assert(((VIDEO_MEMORY*)in)->RequestedVirtualAddress==NULL);
        Maps++;v->VideoRamBase=Pixels;v->FrameBufferBase=Pixels;
        v->VideoRamLength=0x400000;v->FrameBufferLength=Fault==4?16:0x400000;
        *returned=Fault==3?0:sizeof(*v);return 0;
    }
    assert(op==IOCTL_VIDEO_UNMAP_VIDEO_MEMORY);
    assert(((VIDEO_MEMORY*)in)->RequestedVirtualAddress==Pixels);
    Unmaps++;assert(Unmaps<=Maps);return 0;
}
BOOL IntSetPalette(DHPDEV d,PVOID p,ULONG a,ULONG b){(void)d;(void)p;(void)a;(void)b;return TRUE;}
HSURF EngCreateBitmap(SIZEL s,LONG delta,ULONG format,ULONG flags,PVOID bits)
{
    assert(s.cx==1024&&s.cy==576&&delta==4096&&format==BMF_32BPP&&flags==BMF_TOPDOWN&&bits==Pixels);
    if(Fault==5)return NULL;
    Bitmaps++;return &Surface;
}
BOOL EngAssociateSurface(HSURF s,HANDLE d,ULONG hooks){(void)d;assert(s==&Surface&&hooks==0);Associates++;return Fault!=6;}
BOOL EngDeleteSurface(HSURF s){assert(s==&Surface);Deletes++;assert(Deletes<=Bitmaps);return TRUE;}
static PDEV fresh(int fault)
{
    PDEV p;memset(&p,0,sizeof(p));p.ScreenWidth=1024;p.ScreenHeight=576;p.ScreenDelta=4096;p.BitsPerPixel=32;
    Fault=fault;Maps=Unmaps=Bitmaps=Deletes=Associates=0;return p;
}
int main(void)
{
    int f;PDEV p;
    for(f=0;f<=6;f++){
        p=fresh(f);
        if(f==0){
            assert(DrvEnableSurface(&p)==&Surface&&Maps==1&&Unmaps==0);
            assert(!DrvEnableSurface(&p)&&Maps==1&&Bitmaps==1);
            assert(DrvAssertMode(&p,TRUE)&&DrvAssertMode(&p,FALSE));
        }else assert(!DrvEnableSurface(&p));
        DrvDisableSurface(&p);DrvDisableSurface(&p);
        assert(!p.ScreenPtr&&!p.hSurfEng&&Maps==Unmaps&&Bitmaps==Deletes);Cases++;
    }
    for(f=0;f<9;f++){
        p=fresh(0);
        switch(f){case 0:p.ScreenWidth=0;break;case 1:p.ScreenWidth=0xffffffff;break;case 2:p.ScreenHeight=0;break;
          case 3:p.ScreenHeight=1081;break;case 4:p.ScreenDelta=0;break;case 5:p.ScreenDelta=4095;break;
          case 6:p.BitsPerPixel=24;break;case 7:p.ScreenWidth=1920;p.ScreenDelta=7680;p.ScreenHeight=1080;break;
          default:p.ScreenHeight=0xffffffff;break;}
        assert(!DrvEnableSurface(&p)&&Maps==1&&Unmaps==1&&Bitmaps==0);
        DrvDisableSurface(&p);assert(Unmaps==1&&!p.ScreenPtr&&!p.hSurfEng);Cases++;
    }
    p=fresh(8);assert(!DrvAssertMode(&p,FALSE));Cases++;
    printf("{\"passed\":true,\"cases\":%d,\"scope\":\"Actual surface.c with host API faults; not NT5 lifecycle or generic PnP proof\"}\n",Cases);
    return 0;
}
