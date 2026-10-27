# 741 native preservation control: prepared, no physical launch

740 passed all15 full-value checks and20 cleanup comparisons on physical1.6
in kernel context. This fresh native counterpart has the same probe body except
namespace, comment and explicit native CPU admission. It writes11 MMIO and3
CRTC entries, preserving CR1b/CR22/CR33 without data writes. CR1b is compared to
its actual admitted saved full byte85. No mask, firmware replay or status clear.
No geometry/encoder/full-mode programming, Windows or driver qualification.

The retained738 wrapper, bridge and frontend differ only by namespace/comments
and the exact relocation count. New payload has13 relocations:8 absolute and5
PC-relative. The host002 builder rejected its inherited15 count; host003 then
failed compilation because its host test retained a10-element memcpy for the
new8-element array. Both failures and exact source snapshots are retained.
Fresh host004 and page_tool003 correct those bounds. No physical access occurred.
The diskless alias capture length is corrected to73728 bytes (8x8192 plus two
4096-byte guards); this does not change the native handoff or page contents.

Validation:57 actualELF cases,12 fresh disklessCPU fixtures,53 relocated whole-
framebuffer cases,76 optical cases,27 nxdk page cases,372 nxdk ownership cases
and131379 host ownership cases pass. All CPU fixtures closed. Exact embedded
bridge/payload and compiled frontend object bytes checked inPE/XBE. Sources and
receipts frozen; historical attempts are never reopened or used as runtime parents.
Models test control flow and counterfactual responses, not physical NV2A semantics.

The13-row optical report exposes signature, phase, aggregate/forward status,
first mismatch, full expected/observed, cleanup mask, selector restore, actual
nativeCR0/3/4 and completed checks. Kernel preparation is written before handoff;
native results require a photo and are never claimed persisted to disk.

No startup hook. Unique E/Applications/XWNMode741. Once staged and watcher/reset
availability confirmed, one launch may deliberately hold for a photo. Collect
preparation files once only after manual power cycle back to dashboard.
No741 physical result exists yet. Console remains at dashboard after740.

Stage/readback complete. XBE SHA256: a34ceb359f71da751d4c076cc82b7e98ffec039dd761b13edd8474f6f5197e1b.
Awaiting watcher/photo/reset availability; no launch sent. Active physical002.py,
audit_collection002.py and review_prepare002.py supersede retained templates.
