# RAM0109 ownership boundary

The RAM0108 surface lookup compared `dhsurf == dhpdev` and then read that
address as our PDEV. Another driver can use the same convention. The new
lookup matches a live registration containing our PDEV, HSURF and HDEV before
returning our pointer. It never dereferences the private pointer supplied by
an unknown SURFOBJ. Escapes use the same lookup.

A 32-entry table permits overlapping PDEVs during a mode transition. Duplicate
owners or primary handles are rejected; exhaustion fails surface creation and
unwinds bitmap, mapping and allocation resources. Registration occurs after all
creation/association succeeds and before the primary is returned to GDI.
Unregistration precedes primary deletion and shadow destruction.

The driver creates an Eng semaphore at DrvEnableDriver and deletes it through
DrvDisableDriver. It protects table membership only; every Eng rendering call,
resource deletion and upload happens outside it. Rendering can reenter ownership
lookup. The lock is not held while calling back to the engine.

Required surface operands are checked before any rendering/counter updates.
Ordinary GDI bitmaps are accepted; their handle alone cannot cause substitution.
Unknown device surfaces, device bitmaps and two different owned PDEVs in one
operation fail before calling Eng. This explicitly bounds the prototype; it
does not implement printer, cross-adapter or multiple active display rendering.
Unused ROP source/mask operands remain unread and are passed to Eng as NULL.

The lookup does not manufacture a reference to a GDI-owned object. GDI must
keep each submitted SURFOBJ and its PDEV alive throughout its DDI invocation.
Tests exercise concurrent membership on independent objects, not illegal
simultaneous destruction of an object still submitted for rendering. No claim
of general render/teardown concurrency or NT5 mode-transition qualification.

Only display source, filename and read-only revision109 change. Miniport,
shared UC mapping, cache attributes, storage, dump, network, HID and device
policy remain pinned. No physical access. Performance is not inferred from
the extra host tests or emulator timing.

API references (reviewed alongside owned NT5 exports and pinned winddi.h):
- [SURFOBJ fields](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-surfobj)
- [EngCreateSemaphore; Windows 2000 availability](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engcreatesemaphore)
- [DrvDisableDriver resource teardown](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvdisabledriver)

Generator draft001 stopped on an incorrect expected replacement count27; actual
25 operand lookups were found. Draft output/script are preserved, not compiled.
