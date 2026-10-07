"""Generate an NT5 RAM-primary correctness prototype over the qualified0107 source."""
from pathlib import Path
import re,json,hashlib,difflib
k=Path(__file__).resolve().parent;old=k.parent/'video-direct-ddi';out=k/'display';assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();review=json.loads((old/'patch-review.json').read_text());original={}
for n,h in review['source_files'].items():
 p=old/'display'/n;assert sha(p)==h;original[n]=p.read_text();(out/n).write_text(original[n],newline='\n')
def edit(n,a,b):
 p=out/n;s=p.read_text();assert s.count(a)==1,(n,a);p.write_text(s.replace(a,b),newline='\n')
edit('CMakeLists.txt','    surface.c','    surface.c\n    shadow.c')
p=out/'CMakeLists.txt';p.write_text(p.read_text().replace('xwndir','xwnram'),newline='\n')
edit('framebuf.h','L"xwndir"','L"xwnram"')
edit('framebuf.h','   HSURF hSurfEng;','''   HSURF hSurfEng;
   HSURF ShadowSurface;
   SURFOBJ *ShadowObject;
   PVOID ShadowBits;
   BOOL ShadowActive;
   ULONG ShadowCalls[14];
   ULONG ShadowUploads;
   ULONGLONG ShadowBytes;''')
header=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/video-direct-ddi-002/source/sdk/include/psdk/winddi.h');text=header.read_text()
names=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
protos=[];bodies=[]
for index,name in enumerate(names):
 params=re.search(r'\(APIENTRY FN_Drv'+name+r'\)\((.*?)\);',text,re.S)[1]
 params=re.sub(r'_When_\([^\n]*?\)', '',params)
 params=re.sub(r'__[a-z_]+\([^)]*\)', '',params)
 params=re.sub(r'_[A-Za-z0-9]+_\([^)]*\)', '',params)
 params=re.sub(r'_[A-Za-z0-9]+_', '',params)
 params=' '.join(params.split());pieces=[p.strip() for p in params.split(',')];args=[re.search(r'(\w+)$',p)[1] for p in pieces]
 surfaces=[a for p,a in zip(pieces,args) if 'SURFOBJ' in p];dst=surfaces[0]
 callargs=[('XwnSub(p, '+a+')') if a in surfaces else a for a in args]
 proto='BOOL APIENTRY Xwn'+name+'('+params+')';protos.append(proto+';')
 # An entire framebuffer upload is conservative for complex bounds. Copy/fill
 # target rectangles are intersected with screen and clip bounds before copying.
 rect=next((a for a in args if a in ['prclTrg','prclDest','prclDst']),None) if name in ['BitBlt','CopyBits','AlphaBlend','TransparentBlt'] else None
 bodies.append(proto+'\n{\n PPDEV p=NULL; BOOL ok;\n'+''.join(' if (!p) p=XwnOwner('+a+');\n' for a in surfaces)+
  ' if (!p || !p->ShadowActive) return FALSE;\n if (p->ShadowCalls['+str(index)+'] != 0xffffffff) ++p->ShadowCalls['+str(index)+'];\n'+
  ' ok=Eng'+name+'('+', '.join(callargs)+');\n'+
  ' if (XwnOwner('+dst+')) XwnUpload(p, '+(rect or 'NULL')+', pco);\n return ok;\n}\n')
# Upload even after failure: engine may have partially drawn. Never report success
# when engine failed, and never leave an unflushed partial change solely on RAM.
shadow='''/* RAM-primary prototype. GPL-2.0-or-later, as the containing framebuf driver. */
#include "framebuf.h"
static PPDEV XwnOwner(SURFOBJ *s)
{
 PPDEV p;
 if (!s || s->iType != STYPE_DEVICE || !s->dhpdev || s->dhsurf != (DHSURF)s->dhpdev) return NULL;
 p=(PPDEV)s->dhpdev;
 return p->hSurfEng==s->hsurf && p->ShadowObject ? p : NULL;
}
static SURFOBJ *XwnSub(PPDEV p, SURFOBJ *s)
{
 return s && s->hsurf==p->hSurfEng ? p->ShadowObject : s;
}
VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)
{
 RECTL r; LONG y; ULONG bytes;
 if (!p->ShadowActive || !p->ScreenPtr || !p->ShadowBits) return;
 r.left=0;r.top=0;r.right=p->ScreenWidth;r.bottom=p->ScreenHeight;
 if(rect) {r.left=max(r.left,rect->left);r.top=max(r.top,rect->top);r.right=min(r.right,rect->right);r.bottom=min(r.bottom,rect->bottom);}
 if(clip) {r.left=max(r.left,clip->rclBounds.left);r.top=max(r.top,clip->rclBounds.top);r.right=min(r.right,clip->rclBounds.right);r.bottom=min(r.bottom,clip->rclBounds.bottom);}
 if(r.left>=r.right || r.top>=r.bottom) return;
 bytes=(r.right-r.left)*4;
 for(y=r.top;y<r.bottom;y++) memcpy((BYTE*)p->ScreenPtr+y*p->ScreenDelta+r.left*4,(BYTE*)p->ShadowBits+y*p->ScreenDelta+r.left*4,bytes);
 if(p->ShadowUploads!=0xffffffff) ++p->ShadowUploads;
 p->ShadowBytes+=(ULONGLONG)bytes*(r.bottom-r.top);
}
ULONG XwnCheckScanout(PPDEV p)
{
 ULONG i,n=p->ScreenDelta*p->ScreenHeight/4,bad=0;
 volatile ULONG *screen=(volatile ULONG*)p->ScreenPtr; ULONG *ram=(ULONG*)p->ShadowBits;
 for(i=0;i<n;i++) if ((screen[i]&0xffffff)!=(ram[i]&0xffffff)) ++bad;
 return bad;
}
'''+ '\n'.join(bodies)
(out/'shadow.c').write_text(shadow,newline='\n')
p=out/'framebuf.h';p.write_text(p.read_text()+'\nVOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip);\nULONG XwnCheckScanout(PPDEV p);\n'+'\n'.join(protos)+'\n',newline='\n')
hooks=' | '.join('HOOK_'+n.upper() for n in names)
edit('enable.c','   ULONG Data[8];','   ULONG Data[32]; ULONG i;')
a=original['enable.c'][original['enable.c'].index('   if (Escape !='):original['enable.c'].index('static DRVFN')]
b='''   if (InBytes || In || !Surface || !Out || !Surface->dhpdev) return 0;
   p = (PPDEV)Surface->dhpdev;
   if (!p->ScreenPtr || !p->hSurfEng || !p->ShadowObject || !p->ShadowActive) return 0;
   if (Escape == 0x58574431 && OutBytes == 32)
   {
      Data[0]=0x44525758;Data[1]=108;Data[2]=p->ScreenWidth;Data[3]=p->ScreenHeight;
      Data[4]=p->ScreenDelta;Data[5]=p->BitsPerPixel;Data[6]=p->ScreenDelta*p->ScreenHeight;Data[7]=1;
      memcpy(Out,Data,32);return 1;
   }
   if (Escape != 0x58574432 || OutBytes != sizeof(Data)) return 0;
   RtlZeroMemory(Data,sizeof(Data));Data[0]=0x53525758;Data[1]=108;
   for(i=0;i<14;i++) Data[2+i]=p->ShadowCalls[i];
   Data[16]=p->ShadowUploads;Data[17]=(ULONG)p->ShadowBytes;Data[18]=(ULONG)(p->ShadowBytes>>32);
   Data[19]=XwnCheckScanout(p);Data[20]=p->ShadowActive;
   memcpy(Out,Data,sizeof(Data));return 1;
}

'''
edit('enable.c',a,b)
edit('enable.c','   {INDEX_DrvEscape, (PFN)XwnDirectEscape},','   {INDEX_DrvEscape, (PFN)XwnDirectEscape},\n'+''.join('   {INDEX_Drv'+n+', (PFN)Xwn'+n+'},\n' for n in names))
edit('enable.c','    /* We don\'t support any optional callback */\n\n    return TRUE;','    /* No direct access may bypass the private RAM primary. */\n    return FALSE;')
a='''   hSurface = (HSURF)EngCreateBitmap(ScreenSize, ppdev->ScreenDelta, BitmapType,
                                     (ppdev->ScreenDelta > 0) ? BMF_TOPDOWN : 0,
                                     ppdev->ScreenPtr);'''
b='''   ppdev->ShadowBits=EngAllocMem(FL_ZERO_MEMORY, ppdev->ScreenDelta*ppdev->ScreenHeight, ALLOC_TAG);
   if(!ppdev->ShadowBits) goto FailMapping;
   ppdev->ShadowSurface=(HSURF)EngCreateBitmap(ScreenSize, ppdev->ScreenDelta, BitmapType, BMF_TOPDOWN, ppdev->ShadowBits);
   if(!ppdev->ShadowSurface) goto FailMapping;
   if(!EngAssociateSurface(ppdev->ShadowSurface, ppdev->hDevEng, 0)) goto FailMapping;
   ppdev->ShadowObject=EngLockSurface(ppdev->ShadowSurface);
   if(!ppdev->ShadowObject) goto FailMapping;
   hSurface=EngCreateDeviceSurface((DHSURF)ppdev, ScreenSize, BitmapType);'''
edit('surface.c',a,b)
edit('surface.c','EngAssociateSurface(hSurface, ppdev->hDevEng, 0)','EngAssociateSurface(hSurface, ppdev->hDevEng, '+hooks+')')
edit('surface.c','   ppdev->hSurfEng = hSurface;','   ppdev->hSurfEng = hSurface;\n   ppdev->ShadowActive=TRUE;\n   XwnUpload(ppdev,NULL,NULL);')
cleanup='''   ppdev->ShadowActive=FALSE;
   if(ppdev->ShadowObject) EngUnlockSurface(ppdev->ShadowObject);
   ppdev->ShadowObject=NULL;
   if(ppdev->ShadowSurface) EngDeleteSurface(ppdev->ShadowSurface);
   ppdev->ShadowSurface=NULL;
   if(ppdev->ShadowBits) EngFreeMem(ppdev->ShadowBits);
   ppdev->ShadowBits=NULL;
'''
edit('surface.c','FailMapping:\n','FailMapping:\n'+cleanup)
edit('surface.c','   ppdev->hSurfEng = NULL;','   ppdev->hSurfEng = NULL;\n'+cleanup)
edit('surface.c','   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);','   ppdev->ShadowActive=FALSE;\n   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);')
edit('surface.c','      return TRUE;','      ppdev->ShadowActive=TRUE;\n      XwnUpload(ppdev,NULL,NULL);\n      return TRUE;')
edit('surface.c','      return !EngDeviceIoControl','      ppdev->ShadowActive=FALSE;\n      return !EngDeviceIoControl')
# New patch applies strictly after0107; preserve original notices and bytes.
patch=''
for p in sorted(out.iterdir()):
 n=p.name;before=original.get(n,'');after=p.read_text()
 if before!=after:patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/win32ss/drivers/displays/framebuf/'+n if n in original else '/dev/null',tofile='b/win32ss/drivers/displays/framebuf/'+n))
(k/'0108-ram-primary.patch').write_text(patch,newline='\n')
r=dict(parent_tree='3c664be8842518eac9dd18d92f6a3e2f78d36f73',original_files=review['source_files'],source_files={p.name:sha(p) for p in out.iterdir()},patch_sha256=sha(k/'0108-ram-primary.patch'),header_sha256=sha(header),callbacks=names,physical_access=False)
(k/'patch-review.json').write_text(json.dumps(r,indent=2)+'\n')
