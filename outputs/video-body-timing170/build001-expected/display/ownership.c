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
