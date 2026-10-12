#include "framebuf.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "surface.c"
static PDEV *active;
static SURFOBJ shadow;
static unsigned char bitmap,device,storage[0x900000+64];
static unsigned char *pixels=storage+32;
static unsigned ram,frame,fail,allocated,freed,mapped,unmapped,created,deleted,locked,unlocked,cases,checks;
static int registered;
ULONG EngDeviceIoControl(HANDLE h,ULONG op,PVOID in,ULONG ni,PVOID out,ULONG no,ULONG *ret) {
 (void)h;(void)ni;(void)no;
 if(op==IOCTL_VIDEO_SET_CURRENT_MODE)return fail==1;
 if(op==IOCTL_VIDEO_RESET_DEVICE)return 0;
 if(op==IOCTL_VIDEO_MAP_VIDEO_MEMORY){VIDEO_MEMORY_INFORMATION *v=out;if(fail==2)return 1;
  assert(!((VIDEO_MEMORY*)in)->RequestedVirtualAddress);mapped++;v->VideoRamBase=pixels;
  v->FrameBufferBase=pixels;v->VideoRamLength=ram;v->FrameBufferLength=fail==4?0:frame;
  *ret=fail==3?0:sizeof(*v);return 0;}
 assert(op==IOCTL_VIDEO_UNMAP_VIDEO_MEMORY&&((VIDEO_MEMORY*)in)->RequestedVirtualAddress==pixels);
 assert(!active->ShadowBits&&!active->ShadowSurface&&!active->ShadowObject);unmapped++;return 0;
}
BOOL IntSetPalette(DHPDEV d,PVOID p,ULONG a,ULONG b){(void)d;(void)p;(void)a;(void)b;return TRUE;}
PVOID EngAllocMem(ULONG flags,ULONG bytes,ULONG tag){assert(flags==FL_ZERO_MEMORY&&tag==ALLOC_TAG);
 assert(bytes==(uint64_t)active->ScreenWidth*active->ScreenHeight*4&&bytes<=8294400);
 if(fail==5){return NULL;} allocated++;return calloc(1,bytes);}
VOID EngFreeMem(PVOID p){assert(!active->ShadowObject&&!active->ShadowSurface);freed++;free(p);}
HSURF EngCreateBitmap(SIZEL size,LONG stride,ULONG format,ULONG flags,PVOID bits){
 assert(size.cx==(LONG)active->ScreenWidth&&size.cy==(LONG)active->ScreenHeight&&stride==(LONG)active->ScreenDelta);
 assert(format==BMF_32BPP&&flags==BMF_TOPDOWN&&bits==active->ShadowBits);if(fail==6){return NULL;} created++;return &bitmap;}
HSURF EngCreateDeviceSurface(DHSURF p,SIZEL size,ULONG format){assert(p==active&&size.cx==(LONG)active->ScreenWidth&&size.cy==(LONG)active->ScreenHeight&&format==BMF_32BPP);
 if(fail==9){return NULL;} created++;return &device;}
BOOL EngAssociateSurface(HSURF s,HANDLE h,ULONG hooks){(void)h;
 if(s==&bitmap){assert(hooks==0);return fail!=7;}assert(s==&device&&hooks==0x3fff);return fail!=10;}
SURFOBJ *EngLockSurface(HSURF s){assert(s==&bitmap);if(fail==8){return NULL;} locked++;return &shadow;}
VOID EngUnlockSurface(SURFOBJ *s){assert(s==&shadow&&!active->ShadowActive);unlocked++;}
BOOL EngDeleteSurface(HSURF s){assert(s==&bitmap||s==&device);if(s==&bitmap)assert(!active->ShadowObject);deleted++;return TRUE;}
BOOL XwnRegisterPrimary(PPDEV p){assert(p==active);if(fail==11)return FALSE;assert(!registered);registered=1;return TRUE;}
VOID XwnUnregisterPrimary(PPDEV p){assert(p==active);registered=0;}
VOID XwnUpload(PPDEV p,const RECTL *rect,const CLIPOBJ *clip){(void)rect;(void)clip;
 assert(p==active&&registered&&p->ShadowActive&&p->ShadowBits);
 /* Explicit engine/upload model: this tests allocation and unwind, not drawing. */
 memcpy(pixels,p->ShadowBits,(size_t)p->ScreenDelta*p->ScreenHeight);}
static void fresh(PDEV *p,unsigned w,unsigned h,unsigned fault,unsigned rb,unsigned fb){
 memset(p,0,sizeof(*p));p->ScreenWidth=w;p->ScreenHeight=h;p->ScreenDelta=w*4;p->BitsPerPixel=32;p->hDevEng=p;
 active=p;fail=fault;ram=rb;frame=fb;allocated=freed=mapped=unmapped=created=deleted=locked=unlocked=0;
 assert(!registered);memset(storage,0xa5,sizeof(storage));
}
static void cleanup(PDEV *p){unsigned i;DrvDisableSurface(p);DrvDisableSurface(p);
 assert(!p->ScreenPtr&&!p->hSurfEng&&!p->ShadowBits&&!p->ShadowSurface&&!p->ShadowObject&&!p->ShadowActive&&!registered);
 assert(allocated==freed&&mapped==unmapped&&created==deleted&&locked==unlocked);
 for(i=0;i<32;i++)assert(storage[i]==0xa5&&storage[sizeof(storage)-1-i]==0xa5);
 cases++;
}
int main(void){PDEV p;unsigned modes[][2]={{720,480},{1024,576},{1280,720},{1920,1080}};unsigned i,f;
 for(i=0;i<4;i++)for(f=0;f<12;f++){
  unsigned w=modes[i][0],h=modes[i][1],bytes=w*h*4;int allow=(XWN_HD_SURFACE_BOUNDS||bytes<=0x400000);
  fresh(&p,w,h,f,0x900000,bytes);
  if(!f&&allow){assert(DrvEnableSurface(&p)==&device);assert(!DrvEnableSurface(&p));
   ((unsigned char*)p.ShadowBits)[0]=0x17;((unsigned char*)p.ShadowBits)[bytes-1]=0x39;
   assert(DrvAssertMode(&p,FALSE));assert(DrvAssertMode(&p,TRUE));assert(pixels[0]==0x17&&pixels[bytes-1]==0x39);
  }else {assert(!DrvEnableSurface(&p));} cleanup(&p);
 }
 {unsigned dim[]={0,1,480,720,1080,1280,1920,1921,0xffffffff};
  unsigned lengths[]={0,1,0x400000,8294400,0x900000,0x900001,0xffffffff};
  unsigned x,y,a,b;
  for(x=0;x<9;x++)for(y=0;y<9;y++)for(a=0;a<7;a++)for(b=0;b<7;b++){
   uint64_t bytes=(uint64_t)dim[x]*dim[y]*4;
   unsigned expected=(dim[x]&&dim[x]<=1920&&dim[y]&&dim[y]<=1080&&lengths[b]&&lengths[b]<=0x900000&&lengths[a]<=lengths[b]&&bytes<=lengths[a])?(unsigned)bytes:0;
   assert(XwnSurfaceBytes(dim[x],dim[y],dim[x]*4,32,lengths[a],lengths[b])==expected);checks++;
  }
 }
#if XWN_HD_SURFACE_BOUNDS
 for(i=0;i<7;i++){fresh(&p,1920,1080,0,0x900000,8294400);
  switch(i){case 0:p.ScreenDelta=0;break;case 1:p.ScreenDelta=0xffffffff;break;case 2:p.ScreenWidth=0xffffffff;break;
   case 3:p.BitsPerPixel=24;break;case 4:ram=8294399;break;case 5:frame=8294399;break;default:ram=0x900001;break;}
  assert(!DrvEnableSurface(&p)&&!allocated);cleanup(&p);
 }
#endif
 printf("cases=%u geometry_checks=%u profile=%u\n",cases,checks,(unsigned)XWN_HD_SURFACE_BOUNDS);return 0;
}
