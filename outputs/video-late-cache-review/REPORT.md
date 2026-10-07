# Late cache transition: fixed-buffer handoff rejected

Keep the tested0106 permanent uncached mapping. The reviewed NT5 primitives do
not provide the in-place, continuously valid cache transition required by this
design. No driver, fixture, registry or physical console was changed, and no
Windows/xemu guest was launched. This is a bounded design decision about the
current fixed physical framebuffer, not a claim that every possible WC design
is impossible.

## Actual kernel evidence

`inventory.json` pins the owned kernel SHA256
`84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152`,
its public symbols and the existing closed shared-trace002 desktop RAM capture.
Eighteen function windows were inspected. Seventeen were read from captured
resident memory: sixteen match the relocated PE exactly; the remaining helper
has the active CR4.PGE variant described below. The INIT routine was inspected
only on disk, never called.

| Candidate operation | Evidence | Decision |
| --- | --- | --- |
| MmMapIoSpace | Exported; allocates another mapping and can return NULL | Does not change the existing boot pointer atomically |
| MmMapLockedPagesWithReservedMapping | Exported in this owned kernel; checks all reserved PTEs are unused | Reusing an occupied range calls KeBugCheckEx(DA,107,...) |
| MmUnmapReservedMapping then map | Clears existing PTEs before the next map | Preserving the virtual address does not preserve continuous accessibility |
| MmProtectMdlSystemAddress | Absent from the actual export table | Not an available solution here; current Microsoft documentation starts at XP and does not list cache-policy flags |
| MmSetPageProtection | Nonexported, in discardable INIT | Not a supported resident driver entry point |
| InbvCheckDisplayOwnership | Reads the ownership state | Does not establish renderer or mapping exclusion |
| InbvAcquireDisplayOwnership | Calls the registered reset callback when needed, then changes ownership state | Not a provider reference drain or atomic cache transition |

Current Microsoft documentation describes reserved mapping as a reserve/map/
unmap API and lists XP as its supported minimum. Its presence in this particular
NT5 binary is an observation, not a general Windows2000 support guarantee.
[Reserved mapping](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmaplockedpageswithreservedmapping),
[MDL protection](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmprotectmdlsystemaddress).

Keeping the old UC alias while creating a WC alias is not a fallback: Microsoft
requires matching cache behavior for aliases of the same physical memory.
[MEMORY_CACHING_TYPE](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_memory_caching_type).

## Actual-code replay

`replay.json` records fifteen passing *analysis cases*, not fifteen guest tests.
Unicorn executes pinned NT5 mapping instructions against synthetic MDLs/PTEs;
allocation, cache/TLB helper effects and the bugcheck endpoint are modeled.

- Seven MmMapIoSpace cases reproduce early UC success, early WC rejection,
  desktop UC/WC PTE construction, and three allocation failures. Failed
  allocations publish no PTEs. These are not effective-cache measurements.
- Eight reserved-map cases cover1,14,15 and1024 pages with initial UC or WC.
  Every live replacement attempt reaches the actual DA/107 rejection without
  changing any PTE. After unmap, every mapped page is nonpresent; remapping at
  the same address works in the model. Restoring the original cache type works
  only through a second inaccessible interval. Surrounding guards remain intact.
- No renderer was executed in a live gap, no Windows guest crashed, and no
  actual cache/TLB transition was tested. The demonstrated PTE gap is enough
  to reject this proposed continuous-pointer protocol.

The earlier successful controlled crash rendered at IRQL31 through the permanent
UC pointer. MmMapIoSpace's documented ceiling is DISPATCH_LEVEL; a crash-time
attempt to allocate a replacement mapping is not a valid repair for the gap.
[MmMapIoSpace](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospace).

## Corrections and retained host failures

The historical `video-cache-handoff/replay-map.py` labels at two helper addresses
were reversed. Actual symbols and instructions identify:

1. RVA69098: **KeFlushCurrentTb**, no arguments.
2. RVA63D14: **KeInvalidateAllCaches(1)**.

The late-WC MmMapIoSpace path calls them in that order. The old replay's byte
pins, addresses, early rejection and resulting PTEs remain valid; its names and
description of the order were wrong. The historical script/JSON remain unchanged;
the corrected seven-case replay and hashes are here. Neither replay executes
the cache/TLB side effects on hardware.

The first read-only inspection assumed every function window matched the PE.
It stopped on KeFlushCurrentTb. The captured resident entry contains the20-byte
CR4.PGE clear/set sequence that appears at offset7 in the disk window, replacing
the disk entry's CR3 reload sequence. The final inventory records this variant
explicitly and never labels it a full-window PE match. The initial source and
failure record are preserved as `inspect-initial.py` and
`initial-inspection-failure.json`. This is not evidence of driver corruption.
The initial tool filename `inspect.py` also shadowed Python's standard-library
module during Unicorn import. Renaming it to `inventory.py` resolved that host
import failure before any replay ran. No guest was involved in either failure.

## Next direction

`shadow-contract.json` pins ten files from the existing ReactOS framebuffer
source lead and verifies32 proposed engine exports in the actual owned
win32k.sys. All engine names referenced by that source are exported too. This
establishes availability only, not an ABI-correct or tested replacement driver.
The installed, tested display driver remains Microsoft framebuf.

Use `SHADOW-PLAN.md` for a new isolated prototype. Keep the shared UC provider,
storage/network stack and boot renderer fixed. First qualify a direct-drawing
replacement display driver; then compare an opaque device surface backed by
RAM against that control. Previous emulator timings did not demonstrate a
convincing shadow speed advantage, so performance remains an open question.
Original physical111-byte non-ASCII damage/restart remains unresolved.
