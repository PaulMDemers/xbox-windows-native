/* Explicit primary-surface ownership. GPL-2.0-or-later. */
#include "framebuf.h"

/* More than one PDEV may exist during a mode transition. Bounded admission
 * fails DrvEnableSurface cleanly; never evict a live registration. */
#define XWN_OWNER_LIMIT 32
typedef struct {
    PPDEV Owner;
    HSURF Surface;
    HDEV Device;
} XWN_OWNER;
static XWN_OWNER XwnOwners[XWN_OWNER_LIMIT];
static HSEMAPHORE XwnOwnerLock;

BOOL XwnOwnershipInit(VOID)
{
    /* GDI calls driver enable before any PDEV callbacks, and disable only
     * after the last PDEV. Initialization is not a lazy rendering operation. */
    if (XwnOwnerLock) return FALSE;
    XwnOwnerLock = EngCreateSemaphore();
    return XwnOwnerLock != NULL;
}

VOID APIENTRY XwnOwnershipDisable(VOID)
{
    if (XwnOwnerLock) {
        EngDeleteSemaphore(XwnOwnerLock);
        XwnOwnerLock = NULL;
    }
    RtlZeroMemory(XwnOwners, sizeof(XwnOwners));
}

BOOL XwnRegisterPrimary(PPDEV p)
{
    ULONG i, vacant = XWN_OWNER_LIMIT;
    BOOL ok = FALSE;
    if (!XwnOwnerLock || !p || !p->hSurfEng || !p->hDevEng ||
        !p->ShadowObject) return FALSE;
    EngAcquireSemaphore(XwnOwnerLock);
    for (i = 0; i < XWN_OWNER_LIMIT; ++i) {
        if (XwnOwners[i].Owner == p ||
            XwnOwners[i].Surface == p->hSurfEng) goto Exit;
        if (!XwnOwners[i].Owner && vacant == XWN_OWNER_LIMIT) vacant = i;
    }
    if (vacant != XWN_OWNER_LIMIT) {
        XwnOwners[vacant].Surface = p->hSurfEng;
        XwnOwners[vacant].Device = p->hDevEng;
        XwnOwners[vacant].Owner = p;
        ok = TRUE;
    }
Exit:
    EngReleaseSemaphore(XwnOwnerLock);
    return ok;
}

VOID XwnUnregisterPrimary(PPDEV p)
{
    ULONG i;
    if (!XwnOwnerLock || !p) return;
    EngAcquireSemaphore(XwnOwnerLock);
    for (i = 0; i < XWN_OWNER_LIMIT; ++i) {
        if (XwnOwners[i].Owner == p) {
            RtlZeroMemory(&XwnOwners[i], sizeof(XwnOwners[i]));
            break;
        }
    }
    EngReleaseSemaphore(XwnOwnerLock);
}

PPDEV XwnOwner(SURFOBJ *s)
{
    ULONG i;
    PPDEV p = NULL;
    if (!s || s->iType != STYPE_DEVICE || !s->dhpdev ||
        s->dhsurf != (DHSURF)s->dhpdev || !XwnOwnerLock) return NULL;
    EngAcquireSemaphore(XwnOwnerLock);
    for (i = 0; i < XWN_OWNER_LIMIT; ++i) {
        if ((DHPDEV)XwnOwners[i].Owner == s->dhpdev &&
            XwnOwners[i].Surface == s->hsurf &&
            XwnOwners[i].Device == s->hdev) {
            p = XwnOwners[i].Owner;
            break;
        }
    }
    EngReleaseSemaphore(XwnOwnerLock);
    /* No dereference of a SURFOBJ-provided private pointer. GDI must retain
     * the submitted surface/PDEV for its DDI call. This membership lock is
     * not a replacement for that lifetime contract or a rendering lock. */
    return p;
}

BOOL XwnSelectOwner(PPDEV *selected, SURFOBJ *s)
{
    PPDEV p;
    if (!s || s->iType == STYPE_BITMAP) return TRUE;
    p = XwnOwner(s);
    /* Unsupported foreign/device-bitmap or cross-PDEV operations must not
     * enter Eng with an opaque surface it could route recursively to us. */
    if (!p || (*selected && *selected != p)) return FALSE;
    *selected = p;
    return TRUE;
}

/* Accounting only: never hold membership lock across render/copy. */
VOID XwnRowRecord(PPDEV p, ULONG fast, ULONG slow, ULONG bytes)
{
    ULONGLONG total=(ULONGLONG)bytes*(fast+slow), quick=(ULONGLONG)bytes*fast;
    EngAcquireSemaphore(XwnOwnerLock);
    if(p->RowBoxes!=0xffffffff)++p->RowBoxes;
    p->RowFast=0xffffffff-p->RowFast<fast?0xffffffff:p->RowFast+fast;
    p->RowSlow=0xffffffff-p->RowSlow<slow?0xffffffff:p->RowSlow+slow;
    p->RowBytes=(~(ULONGLONG)0)-p->RowBytes<total?~(ULONGLONG)0:p->RowBytes+total;
    p->RowFastBytes=(~(ULONGLONG)0)-p->RowFastBytes<quick?~(ULONGLONG)0:p->RowFastBytes+quick;
    EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnRowSnapshot(PPDEV p, ULONG *out)
{
    RtlZeroMemory(out,128);EngAcquireSemaphore(XwnOwnerLock);
    out[0]=0x57525758;out[1]=115;out[2]=128;out[3]=XWN_UC_STORES;
    out[4]=p->RowBoxes;out[5]=p->RowFast;out[6]=p->RowSlow;
    out[7]=(ULONG)p->RowBytes;out[8]=(ULONG)(p->RowBytes>>32);
    out[9]=(ULONG)p->RowFastBytes;out[10]=(ULONG)(p->RowFastBytes>>32);
    EngReleaseSemaphore(XwnOwnerLock);
}

/* Separate elapsed diagnostic. Never hold membership lock across an Eng render
 * call, clock query or framebuffer copy. It only protects64bit accounting and
 * snapshots; it remains no replacement for GDI's submitted-PDEV lifetime. */
VOID XwnProfileInit(PPDEV p)
{
    ULONG i; LONGLONG a,b;
    p->Profile.Enabled=XWN_BODY_PROFILE;
    p->Profile.Minimum=~(ULONGLONG)0;
    EngQueryPerformanceFrequency(&p->Profile.Frequency);
    if (p->Profile.Frequency<=0) ++p->Profile.Errors;
    for(i=0;i<128;i++) {
        a=b=-1;EngQueryPerformanceCounter(&a);EngQueryPerformanceCounter(&b);
        XwnProfileCalibration(&p->Profile,a,b);
    }
}
LONGLONG XwnProfileStart(VOID)
{
#if XWN_BODY_PROFILE
    LONGLONG tick=-1;EngQueryPerformanceCounter(&tick);return tick;
#else
    return 0;
#endif
}
VOID XwnProfileEnd(PPDEV p, ULONG kind, LONGLONG begin)
{
    LONGLONG end=XwnProfileStart();
    EngAcquireSemaphore(XwnOwnerLock);
    XwnProfileAccumulate(&p->Profile,kind,begin,end);
    EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnProfileSnapshot(PPDEV p, ULONG *out)
{
    ULONG i,at;
    RtlZeroMemory(out,128);
    EngAcquireSemaphore(XwnOwnerLock);
    out[0]=0x544d5758;out[1]=113;out[2]=128;out[3]=p->Profile.Enabled;
    out[4]=(ULONG)p->Profile.Frequency;out[5]=(ULONG)((ULONGLONG)p->Profile.Frequency>>32);
    out[6]=p->Profile.Samples;
    out[7]=(ULONG)p->Profile.Minimum;out[8]=(ULONG)(p->Profile.Minimum>>32);
    out[9]=(ULONG)p->Profile.Maximum;out[10]=(ULONG)(p->Profile.Maximum>>32);
    out[11]=p->Profile.Errors;out[12]=p->Profile.Overflows;
    for(i=0;i<4;i++) {
        at=14+i*3;out[at]=p->Profile.Count[i];
        out[at+1]=(ULONG)p->Profile.Ticks[i];out[at+2]=(ULONG)(p->Profile.Ticks[i]>>32);
    }
    out[26]=p->Profile.Reads;
    EngReleaseSemaphore(XwnOwnerLock);
}

/* Actual per-call copied bytes, published only after copy, lock never spans Eng/copy. */
VOID XwnTextRecord(PPDEV p,ULONG reason,ULONG glyphs,const XWT_RECT *bound,const XWT_COPY *copied,const RECTL *clip,ULONG complexity)
{
 EngAcquireSemaphore(XwnOwnerLock);
 XwtRecord(&p->TextStats,XWN_TEXT_BOUNDS,reason,glyphs,bound,copied);
 p->TextHasClip=clip!=NULL;p->TextComplexity=complexity;
 if(clip)p->TextInputClip=*clip;else RtlZeroMemory(&p->TextInputClip,sizeof(p->TextInputClip));
 EngReleaseSemaphore(XwnOwnerLock);
}
VOID XwnTextSnapshot(PPDEV p,ULONG *out)
{
 ULONG i;XWT_STATS *s=&p->TextStats;
 RtlZeroMemory(out,128);EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x54585758;out[1]=117;out[2]=128;out[3]=XWN_TEXT_BOUNDS;
 out[4]=s->calls;out[5]=s->bounded;out[6]=s->fallback;out[7]=s->empty;
 out[8]=s->boxes;out[9]=(ULONG)s->bytes;out[10]=(ULONG)(s->bytes>>32);
 out[11]=s->overflow;
 for(i=0;i<7;i++)out[12+i]=s->reasons[i];
 out[19]=s->last_glyphs;out[20]=s->last_reason;out[21]=s->last_mode;
 out[22]=s->last.left;out[23]=s->last.top;out[24]=s->last.right;out[25]=s->last.bottom;
 out[26]=s->copied.boxes;out[27]=(ULONG)s->copied.bytes;out[28]=(ULONG)(s->copied.bytes>>32);
 out[29]=s->copied.overflow;
 EngReleaseSemaphore(XwnOwnerLock);
}

/* Atomic118 snapshot: actual input clip plus the same117 last-call accounting. */
VOID XwnTextExtended(PPDEV p,ULONG *out)
{
 ULONG i;XWT_STATS *s=&p->TextStats;
 RtlZeroMemory(out,160);EngAcquireSemaphore(XwnOwnerLock);
 out[0]=0x54585758;out[1]=118;out[2]=160;out[3]=XWN_TEXT_BOUNDS;
 out[4]=s->calls;out[5]=s->bounded;out[6]=s->fallback;out[7]=s->empty;
 out[8]=s->boxes;out[9]=(ULONG)s->bytes;out[10]=(ULONG)(s->bytes>>32);
 out[11]=s->overflow;
 for(i=0;i<7;i++)out[12+i]=s->reasons[i];
 out[19]=s->last_glyphs;out[20]=s->last_reason;out[21]=s->last_mode;
 out[22]=s->last.left;out[23]=s->last.top;out[24]=s->last.right;out[25]=s->last.bottom;
 out[26]=s->copied.boxes;out[27]=(ULONG)s->copied.bytes;out[28]=(ULONG)(s->copied.bytes>>32);
 out[29]=s->copied.overflow;
 out[32]=p->TextInputClip.left;out[33]=p->TextInputClip.top;out[34]=p->TextInputClip.right;out[35]=p->TextInputClip.bottom;
 out[36]=p->TextComplexity;out[37]=p->TextHasClip;
 EngReleaseSemaphore(XwnOwnerLock);
}
