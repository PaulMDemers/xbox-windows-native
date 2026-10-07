"""Host ABI shim plus real-source lifecycle and upload tests, not an NT5 oracle."""
from pathlib import Path
import re
k=Path(__file__).resolve().parent;t=k/'tests';t.mkdir(exist_ok=False)
header='''#ifndef TEST_FRAMEBUF_H
#define TEST_FRAMEBUF_H
#include <stdint.h>
#include <string.h>
#include <stddef.h>
typedef uint32_t ULONG,DWORD,ROP4,MIX,FLONG;
typedef uint64_t ULONGLONG;
typedef int32_t LONG;
typedef unsigned char BYTE;
typedef int BOOL;
typedef void VOID,*PVOID,*HANDLE,*HSURF,*DHPDEV,*DHSURF;
typedef struct {LONG cx,cy;} SIZEL;
typedef struct {LONG x,y;} POINTL,POINTFIX;
typedef struct {LONG left,top,right,bottom;} RECTL;
typedef struct {RECTL rclBounds;} CLIPOBJ;
typedef struct {int unused;} XLATEOBJ,STROBJ,FONTOBJ,BRUSHOBJ,PATHOBJ,XFORMOBJ,LINEATTRS,COLORADJUSTMENT,BLENDOBJ,TRIVERTEX;
typedef struct {ULONG iType; DHPDEV dhpdev; DHSURF dhsurf; HSURF hsurf;} SURFOBJ;
typedef struct {PVOID RequestedVirtualAddress;} VIDEO_MEMORY;
typedef struct {PVOID VideoRamBase;ULONG VideoRamLength;PVOID FrameBufferBase;ULONG FrameBufferLength;} VIDEO_MEMORY_INFORMATION;
typedef struct {HANDLE hDriver,hDevEng;HSURF hSurfEng;PVOID ScreenPtr;ULONG ModeIndex,ScreenWidth,ScreenHeight,ScreenDelta,BitsPerPixel,iDitherFormat;PVOID PaletteEntries;
HSURF ShadowSurface;SURFOBJ *ShadowObject;PVOID ShadowBits;BOOL ShadowActive;ULONG ShadowCalls[14],ShadowUploads;ULONGLONG ShadowBytes;} PDEV,*PPDEV;
#define IN
#define APIENTRY
#define TRUE 1
#define FALSE 0
#define BMF_8BPP 3
#define BMF_16BPP 4
#define BMF_24BPP 5
#define BMF_32BPP 6
#define BMF_TOPDOWN 1
#define FL_ZERO_MEMORY 1
#define ALLOC_TAG 42
#define STYPE_DEVICE 1
#define IOCTL_VIDEO_SET_CURRENT_MODE 1
#define IOCTL_VIDEO_MAP_VIDEO_MEMORY 2
#define IOCTL_VIDEO_UNMAP_VIDEO_MEMORY 3
#define IOCTL_VIDEO_RESET_DEVICE 4
#define RtlZeroMemory(p,n) memset(p,0,n)
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
ULONG EngDeviceIoControl(HANDLE,ULONG,PVOID,ULONG,PVOID,ULONG,ULONG*);
BOOL IntSetPalette(DHPDEV,PVOID,ULONG,ULONG);
HSURF EngCreateBitmap(SIZEL,LONG,ULONG,ULONG,PVOID);
HSURF EngCreateDeviceSurface(DHSURF,SIZEL,ULONG);
BOOL EngAssociateSurface(HSURF,HANDLE,ULONG);
BOOL EngDeleteSurface(HSURF);
PVOID EngAllocMem(ULONG,ULONG,ULONG);
VOID EngFreeMem(PVOID);
SURFOBJ *EngLockSurface(HSURF);
VOID EngUnlockSurface(SURFOBJ*);
HSURF DrvEnableSurface(DHPDEV);
VOID DrvDisableSurface(DHPDEV);
BOOL DrvAssertMode(DHPDEV,BOOL);
VOID XwnUpload(PPDEV,const RECTL*,const CLIPOBJ*);
ULONG XwnCheckScanout(PPDEV);
'''
s=(k/'display/shadow.c').read_text();protos=re.findall(r'BOOL APIENTRY (Xwn(\w+)\(([^\n]+)\))',s)
stubs='';calls=[]
for i,(proto,name,params) in enumerate(protos):
 header+=f'#define HOOK_{name.upper()} (1u<<{i})\nBOOL APIENTRY {proto};\nBOOL APIENTRY {proto.replace("Xwn","Eng",1)};\n'
 pieces=params.split(',');args=[re.search(r'(\w+)$',p)[1] for p in pieces];surfaces=[a for p,a in zip(pieces,args) if 'SURFOBJ' in p]
 body=''.join(f' (void){a};\n' for a in args)
 body+=' assert('+surfaces[0]+'==ExpectedDest);\n'
 for a in surfaces[1:]:body+=' assert('+a+'==ExpectedOther);\n'
 body+=' if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;\n return EngineResult;\n'
 call=[]
 for p,a in zip(pieces,args):
  call.append('&Primary' if a in surfaces else ('0xcccc' if a=='rop4' else ('&Full' if a in ['prclTrg','prclDest','prclDst'] else '0')))
 if name in ['BitBlt','StretchBltROP']:
  call=[('NULL' if a=='psoMask' else c) for a,c in zip(args,call)]
  # These source-copy ROPs need source but not mask, so a shared assertion is unsuitable.
  body=body.replace('assert(psoMask==ExpectedOther);','assert(psoMask==NULL);')
 stubs+='BOOL APIENTRY '+proto.replace('Xwn','Eng',1)+'\n{\n'+body+'}\n'
 calls.append(f' assert(Xwn{name}('+','.join(call)+f')); assert(p.ShadowCalls[{i}]==1); assert(Pixels[0]==0x345678); Cases++;')
(t/'framebuf.h').write_text(header+'#endif\n',newline='\n')
(t/'engine-stubs.inc').write_text(stubs,newline='\n')
(t/'callback-calls.inc').write_text('\n'.join(calls)+'\n',newline='\n')
