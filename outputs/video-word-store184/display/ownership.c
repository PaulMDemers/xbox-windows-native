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
