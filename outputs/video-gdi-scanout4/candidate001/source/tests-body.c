#include "framebuf.h"
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
/* Include exact authored implementations, exposing only static helpers to tests. */
#include "surface.c"
#include "shadow.c"
#include "ownership.c"
#include "semaphore-shim.inc"
static int Fault,Maps,Unmaps,Bitmaps,Devices,Deletes,Allocations,Frees,Locks,Unlocks,Cases;
static ULONG Storage[16+1024*576+16];
static ULONG *Pixels=Storage+16;
static BYTE BitmapToken,PrimaryToken;
static SURFOBJ Shadow,Primary,Other,*ExpectedDest,*ExpectedOther;
static PPDEV Active;
static BOOL EngineResult=TRUE,WritePixel;
ULONG EngDeviceIoControl(HANDLE h,ULONG op,PVOID in,ULONG ni,PVOID out,ULONG no,ULONG *returned)
{
 (void)h;(void)ni;(void)no;
 if(op==IOCTL_VIDEO_SET_CURRENT_MODE)return Fault==1;
 if(op==IOCTL_VIDEO_RESET_DEVICE)return Fault==12;
 if(op==IOCTL_VIDEO_MAP_VIDEO_MEMORY){
  VIDEO_MEMORY_INFORMATION *v=out;if(Fault==2)return 1;
  assert(!((VIDEO_MEMORY*)in)->RequestedVirtualAddress);Maps++;
  v->VideoRamBase=Pixels;v->FrameBufferBase=Pixels;v->VideoRamLength=0x400000;
  v->FrameBufferLength=Fault==4?16:0x400000;*returned=Fault==3?0:sizeof(*v);return 0;
 }
 assert(op==IOCTL_VIDEO_UNMAP_VIDEO_MEMORY);
 assert(((VIDEO_MEMORY*)in)->RequestedVirtualAddress==Pixels);
 assert(!Active->ShadowSurface&&!Active->ShadowBits&&!Active->ShadowObject);
 Unmaps++;assert(Unmaps<=Maps);return 0;
}
BOOL IntSetPalette(DHPDEV d,PVOID p,ULONG a,ULONG b){(void)d;(void)p;(void)a;(void)b;return TRUE;}
PVOID EngAllocMem(ULONG flags,ULONG bytes,ULONG tag)
{
 assert(flags==FL_ZERO_MEMORY&&tag==ALLOC_TAG&&bytes==1024*576*4);
 if(Fault==5)return NULL;Allocations++;return calloc(1,bytes);
}
VOID EngFreeMem(PVOID p){assert(!Active->ShadowSurface&&!Active->ShadowObject);Frees++;free(p);}
HSURF EngCreateBitmap(SIZEL s,LONG delta,ULONG format,ULONG flags,PVOID bits)
{
 assert(s.cx==1024&&s.cy==576&&delta==4096&&format==BMF_32BPP&&flags==BMF_TOPDOWN&&bits==Active->ShadowBits);
 if(Fault==6)return NULL;Bitmaps++;return &BitmapToken;
}
HSURF EngCreateDeviceSurface(DHSURF p,SIZEL size,ULONG format)
{
 assert(p==Active&&size.cx==1024&&size.cy==576&&format==BMF_32BPP);
 if(Fault==9)return NULL;Devices++;return &PrimaryToken;
}
BOOL EngAssociateSurface(HSURF s,HANDLE d,ULONG hooks)
{
 (void)d;
 if(s==&BitmapToken){assert(!hooks);return Fault!=7;}
 assert(s==&PrimaryToken&&hooks==0x3fff);return Fault!=10;
}
SURFOBJ *EngLockSurface(HSURF s){assert(s==&BitmapToken);if(Fault==8)return NULL;Locks++;return &Shadow;}
VOID EngUnlockSurface(SURFOBJ *s){assert(s==&Shadow&&!Active->ShadowActive);Unlocks++;}
BOOL EngDeleteSurface(HSURF s)
{
 assert(s==&BitmapToken||s==&PrimaryToken);
 if(s==&BitmapToken)assert(!Active->ShadowObject);
 if(s==&PrimaryToken)assert(!XwnOwner(&Primary));
 Deletes++;assert(Deletes<=Bitmaps+Devices);return TRUE;
}
#include "engine-stubs.inc"
static void fresh(PPDEV p,int fault)
{
 memset(p,0,sizeof(*p));p->ScreenWidth=1024;p->ScreenHeight=576;p->ScreenDelta=4096;p->BitsPerPixel=32;
 p->hDevEng=p;Fault=fault;Active=p;Maps=Unmaps=Bitmaps=Devices=Deletes=Allocations=Frees=Locks=Unlocks=0;
 memset(Storage,0x5a,sizeof(Storage));memset(&Shadow,0,sizeof(Shadow));memset(&Primary,0,sizeof(Primary));
 Primary.hdev=p;Primary.iType=STYPE_DEVICE;Primary.dhpdev=p;Primary.dhsurf=p;Primary.hsurf=&PrimaryToken;
}
static void cleanup(PPDEV p)
{
 int i;DrvDisableSurface(p);DrvDisableSurface(p);
 assert(!p->ScreenPtr&&!p->hSurfEng&&!p->ShadowBits&&!p->ShadowObject&&!p->ShadowSurface&&!p->ShadowActive);
 assert(Maps==Unmaps&&Bitmaps+Devices==Deletes&&Allocations==Frees&&Locks==Unlocks);
 for(i=0;i<16;i++)assert(Storage[i]==0x5a5a5a5a&&Storage[16+1024*576+i]==0x5a5a5a5a);
}
int main(void)
{
 PDEV p;int f,x,y;ULONG rop;RECTL Full={0,0,1024,576};
 assert(XwnOwnershipInit());
 for(f=0;f<=10;f++){
  fresh(&p,f);
  if(!f){assert(DrvEnableSurface(&p)==&PrimaryToken);assert(!DrvEnableSurface(&p));assert(XwnCheckScanout(&p)==0);}
  else assert(!DrvEnableSurface(&p));cleanup(&p);Cases++;
 }
 for(f=0;f<9;f++){
  fresh(&p,0);
  switch(f){case 0:p.ScreenWidth=0;break;case 1:p.ScreenWidth=0xffffffff;break;case 2:p.ScreenHeight=0;break;
   case 3:p.ScreenHeight=1081;break;case 4:p.ScreenDelta=0;break;case 5:p.ScreenDelta=4095;break;
   case 6:p.BitsPerPixel=24;break;case 7:p.ScreenWidth=1920;p.ScreenDelta=7680;p.ScreenHeight=1080;break;
   default:p.ScreenHeight=0xffffffff;break;}
  assert(!DrvEnableSurface(&p)&&Maps==1&&Unmaps==1&&!Allocations);cleanup(&p);Cases++;
 }
 fresh(&p,0);assert(DrvEnableSurface(&p));
 ((ULONG*)p.ShadowBits)[0]=0xabcdef;assert(XwnCheckScanout(&p)==1);
 assert(DrvAssertMode(&p,FALSE));XwnUpload(&p,NULL,NULL);assert(Pixels[0]==0);
 assert(DrvAssertMode(&p,TRUE));assert(Pixels[0]==0xabcdef);Cases++;
 Fault=12;assert(!DrvAssertMode(&p,FALSE)&&!p.ShadowActive);Fault=1;
 assert(!DrvAssertMode(&p,TRUE)&&!p.ShadowActive);Fault=0;assert(DrvAssertMode(&p,TRUE));Cases++;
 for(f=0;f<7;f++){
  RECTL r={-10,-10,1029,580};CLIPOBJ c={{2,3,5,7}};ULONG previous=p.ShadowUploads;
  memset(Pixels,0,1024*576*4);memset(p.ShadowBits,0x77,1024*576*4);
  switch(f){case 1:r.right=1;break;case 2:r.bottom=2;break;case 3:r.left=1025;break;
   case 4:r.top=577;break;case 5:r.left=r.right;break;case 6:r.top=r.bottom;break;}
  XwnUpload(&p,&r,&c);
  for(y=0;y<576;y++)for(x=0;x<1024;x++)assert(Pixels[y*1024+x]==(!f&&x>=2&&x<5&&y>=3&&y<7?0x77777777:0));
  assert(p.ShadowUploads==previous+(!f));Cases++;
 }
 /* Exhaustive independent truth-table dependency tests for all 65,536 ROP4s. */
 for(rop=0;rop<65536;rop++){
  BOOL src=FALSE,mask=FALSE;int m,b,d,s;
  for(m=0;m<2;m++)for(b=0;b<2;b++)for(d=0;d<2;d++)
   src|=((rop>>(m*8+b*4+d))&1)!=((rop>>(m*8+b*4+2+d))&1);
  for(b=0;b<2;b++)for(s=0;s<2;s++)for(d=0;d<2;d++)
   mask|=((rop>>(b*4+s*2+d))&1)!=((rop>>(8+b*4+s*2+d))&1);
  assert(XwnRopUsesSource(rop)==src&&XwnRopUsesMask(rop)==mask);
 }
 ExpectedDest=ExpectedOther=&Shadow;WritePixel=TRUE;
#include "callback-calls.inc"
 /* Source-only primary substitution: reading the primary cannot upload to it. */
 ExpectedDest=&Other;ExpectedOther=&Shadow;{ULONG uploads=p.ShadowUploads;assert(XwnCopyBits(&Other,&Primary,NULL,NULL,&Full,NULL));assert(p.ShadowUploads==uploads);}Cases++;
 /* An unused source/mask is deliberately an invalid pointer. Engine never sees it. */
 ExpectedDest=&Shadow;ExpectedOther=NULL;assert(XwnBitBlt(&Primary,(SURFOBJ*)1,(SURFOBJ*)1,NULL,NULL,&Full,NULL,NULL,NULL,NULL,0xf0f0));Cases++;
 /* Preserve a partial engine change even when the engine reports failure. */
 EngineResult=FALSE;Pixels[0]=0;assert(!XwnBitBlt(&Primary,NULL,NULL,NULL,NULL,&Full,NULL,NULL,NULL,NULL,0xf0f0));assert(Pixels[0]==0x345678);Cases++;
 cleanup(&p);
 XwnOwnershipDisable();
 printf("{\"passed\":true,\"cases\":%d,\"rop_truth_tables\":65536,\"callbacks\":14,\"scope\":\"Actual source with fault/engine shim; not real Eng rendering, cursor or NT5 lifetime proof\"}\n",Cases);
 return 0;
}
