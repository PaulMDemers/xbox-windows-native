"""Original114 bounded DIB upload adapter on frozen112; no guest access."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent; old=k.parent/'video-clip-upload'; d=k/'display'
assert not d.exists(); shutil.copytree(old/'display',d)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=json.loads((old/'patch-review.json').read_text())
for n,h in parent['source_files'].items(): assert sha(d/n)==h,n
shutil.copyfile(k/'dib_plan.h',d/'dib_plan.h')
def update(name,before,after):
 p=d/name; text=p.read_text(); assert text.count(before)==1,(name,before)
 p.write_bytes(text.replace(before,after).encode())
update('framebuf.h','typedef struct _PDEV','#include "dib_plan.h"\n\ntypedef struct _PDEV')
update('framebuf.h','   ULONG ShadowUploads;','   ULONG DibCounts[8];\n   ULONGLONG DibBytes;\n   ULONG ShadowUploads;')
update('framebuf.h','#endif /* _FRAMEBUF_PCH_ */','VOID XwnDibRecord(PPDEV p, ULONG result, ULONGLONG bytes);\nVOID XwnDibSnapshot(PPDEV p, ULONG *out);\n#endif /* _FRAMEBUF_PCH_ */')
update('CMakeLists.txt','    ownership.c','    ownership.c\n    dib_plan.h')
with (d/'CMakeLists.txt').open('a') as f: f.write('''
option(XWN_DIB_FASTPATH "Bounded standard32bpp DIB to RAM-primary copy" OFF)
if(XWN_DIB_FASTPATH)
 target_compile_definitions(xwnown PRIVATE XWN_DIB_FASTPATH=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_DIB_FASTPATH=0)
endif()
''')
update('enable.c','   if (Escape == 0x58574431 && OutBytes == 32)','''   if (Escape == 0x58574434 && OutBytes == sizeof(Data))
   {
      XwnDibSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;
   }
   if (Escape == 0x58574431 && OutBytes == 32)''')
with (d/'ownership.c').open('a') as f: f.write('''
/* Existing membership lock protects counters only. GDI retains the submitted
 * PDEV/bitmap for its DDI call. Never hold this lock across render or memcpy. */
VOID XwnDibRecord(PPDEV p, ULONG result, ULONGLONG bytes)
{
    if(result<1 || result>7) return;
    EngAcquireSemaphore(XwnOwnerLock);
    if(p->DibCounts[0]!=0xffffffff) ++p->DibCounts[0];
    if(p->DibCounts[result]!=0xffffffff) ++p->DibCounts[result];
    if((~(ULONGLONG)0)-p->DibBytes<bytes) p->DibBytes=~(ULONGLONG)0;
    else p->DibBytes+=bytes;
    EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnDibSnapshot(PPDEV p, ULONG *out)
{
    ULONG i;
    RtlZeroMemory(out,128);
    EngAcquireSemaphore(XwnOwnerLock);
    out[0]=0x42445758;out[1]=114;out[2]=128;out[3]=XWN_DIB_FASTPATH;
    for(i=0;i<8;i++) out[4+i]=p->DibCounts[i];
    out[12]=(ULONG)p->DibBytes;out[13]=(ULONG)(p->DibBytes>>32);
    EngReleaseSemaphore(XwnOwnerLock);
}
''')
adapter='''
/* Only standard system-memory32bpp SRCCOPY into our owned primary. Anything
 * requiring translation, a complex clip, foreign ownership or aliasing still
 * uses Eng. No framebuffer cache, mode, scanout or lifetime policy changes. */
static BOOL XwnDibCopy(PPDEV p, SURFOBJ *source, CLIPOBJ *clip,
                       XLATEOBJ *xlate, const RECTL *rect, const POINTL *point)
{
#if XWN_DIB_FASTPATH
    XD_SURFACE a,b; XD_RECT r,c; XD_PLAN plan;
    SURFOBJ *target=p->ShadowObject; ULONG reason,y;
    BYTE *from,*to;
    if(!source || source->iType!=STYPE_BITMAP || source->iBitmapFormat!=BMF_32BPP ||
       (source->fjBitmap&BMF_NOTSYSMEM) || !source->pvBits || !source->pvScan0 ||
       !target || target->iType!=STYPE_BITMAP || target->iBitmapFormat!=BMF_32BPP ||
       (target->fjBitmap&BMF_NOTSYSMEM) || target->pvBits!=p->ShadowBits ||
       !target->pvScan0 || (xlate && xlate->flXlate!=XO_TRIVIAL) || !rect || !point)
    { XwnDibRecord(p,XD_FORMAT,0);return FALSE; }
    if(clip && clip->iDComplexity!=DC_TRIVIAL && clip->iDComplexity!=DC_RECT)
    { XwnDibRecord(p,XD_CLIP,0);return FALSE; }
    a.base=(XD_U32)(ULONG_PTR)target->pvBits;a.size=target->cjBits;
    a.scan=(XD_U32)(ULONG_PTR)target->pvScan0;a.stride=target->lDelta;
    a.width=target->sizlBitmap.cx;a.height=target->sizlBitmap.cy;
    b.base=(XD_U32)(ULONG_PTR)source->pvBits;b.size=source->cjBits;
    b.scan=(XD_U32)(ULONG_PTR)source->pvScan0;b.stride=source->lDelta;
    b.width=source->sizlBitmap.cx;b.height=source->sizlBitmap.cy;
    r.left=rect->left;r.top=rect->top;r.right=rect->right;r.bottom=rect->bottom;
    if(clip && clip->iDComplexity==DC_RECT) {
        c.left=clip->rclBounds.left;c.top=clip->rclBounds.top;
        c.right=clip->rclBounds.right;c.bottom=clip->rclBounds.bottom;
    }
    reason=XdPlan(&a,&b,r,point->x,point->y,
                   clip && clip->iDComplexity==DC_RECT?&c:NULL,&plan);
    if(reason==XD_HIT) {
        from=(BYTE*)source->pvBits+plan.source;to=(BYTE*)target->pvBits+plan.target;
        for(y=0;y<plan.rows;y++) {
            memcpy(to,from,plan.bytes);
            /* Do not form a pointer outside either allocation after last row. */
            if(y+1<plan.rows) {from+=plan.source_step;to+=plan.target_step;}
        }
        XwnDibRecord(p,XD_HIT,(ULONGLONG)plan.bytes*plan.rows);return TRUE;
    }
    XwnDibRecord(p,reason,0);return reason==XD_EMPTY;
#else
    XwnDibRecord(p,XD_DISABLED,0);return FALSE;
#endif
}
'''
update('shadow.c','BOOL APIENTRY XwnBitBlt(',adapter+'\nBOOL APIENTRY XwnBitBlt(')
update('shadow.c',' ok=EngBitBlt(',' if (XwnOwner(psoTrg)==p && rop4==0xcccc && !psoMask &&\n     XwnDibCopy(p,psoSrc,pco,pxlo,prclTrg,pptlSrc)) ok=TRUE;\n else ok=EngBitBlt(')
update('shadow.c',' ok=EngCopyBits(',' if (XwnOwner(psoDest)==p &&\n     XwnDibCopy(p,psoSrc,pco,pxlo,prclDest,pptlSrc)) ok=TRUE;\n else ok=EngCopyBits(')
for p in d.iterdir():
 if p.is_file():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
r=dict(parent_tree=json.loads((old/'build-report.json').read_text())['source_tree'],original_files=parent['source_files'],source_files={p.name:sha(p) for p in d.iterdir() if p.is_file()},private_escape='0x58574434',escape_version=114,identity112_retained=True,physical_access=False,runtime_qualified=False)
(k/'source-review.json').write_text(json.dumps(r,indent=2)+'\n')
print('Original114 sources generated; no build or runtime qualification')
