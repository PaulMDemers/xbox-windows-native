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
