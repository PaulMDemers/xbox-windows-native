# Test741 CLOSED: native preservation prefix passes

All15 native full-value checks passed, with cleanup mask0 (all20 saved-value
comparisons matched) and selectors restored. Actual native CR0/CR3/CR4 are
4001003b/0/610. This matches kernel740 preservation success, across different
CPU contexts. It does not establish identical timing or fix the original full
mode sequence. CR1b/CR22/CR33 were not data-written; no bit7 mask or guessed
readback semantics were introduced. No geometry or encoder programming ran.

One launch was accepted2026-10-27T22:20:30.516954UTC. User observed green/holding.
First photo glare prevented a complete decode; failure and partial known fields
are retained. Second photo independently decoded all416 bits with five sample
offsets, three threshold policies and adjacent-row checks; known fields agree.
The native result comes from that photo, not the kernel preparation files.

After the user's confirmed manual power cycle, nine preparation reports were
collected once. Audit passed22:27:37UTC: exact source/binary/stage pins, double
readback, independently checked memory ownership and unrelated E entries.
PCI/CRTC/sequencer, geometry and allocation plan match closed738 preparation.
Pre-arm kernel CPU remains separate: flags646,CR0=8001003b,CR3=f000,CR4=610.
Last persisted phase is handoff_armed; this was not a Windows boot/shutdown.

No hook or owned host process/VM remains. Console authenticated at dashboard.
All741/prior runtimes CLOSED: never relaunch, recollect or parent them. No new
collection or audit failure. Earlier build/index/photo failures remain intact.

Next is a source-level review of the first geometry block after the now-tested
preservation prefix. Define bounded writes, readback contracts, owned buffer
limits and recovery before a fresh diagnostic. Original704 failure attribution
and CR22/CR33 write contracts remain unresolved. No full-mode repeat, predicate
waiver, firmware-state replay, functional driver patch or Windows qualification.

---

Retained preparation history follows; the CLOSED status above supersedes its
prelaunch status statements.

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
