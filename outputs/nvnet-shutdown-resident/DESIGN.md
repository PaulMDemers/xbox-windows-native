# Keep the existing shutdown helper resident

controlled-dump-observe/crash002 proves a nested D1 at IRQL31 when the NDIS
shutdown callback calls absent NVNet PAGE code. The actual cold symbol is
NvNetIdleTransmitter RVA7800. This is a demonstrated section-placement defect,
not a speculative storage fix. Physical behavior remains untested.

0104 removes that helper's PAGE annotation and PAGED_CODE assertion. Its MMIO
reads/writes, finite retry count and stall sequence stay identical. Registration
and execution of MiniportShutdown remain enabled. Other reviewed direct callees
(stop TX/RX, release sideband semaphore, power-state setter and the ordinary
pause helper) already reside in nonpaged .text. The HIGH_LEVEL branch skips
the ordinary lock-taking pause. Compiled call targets and section flags must
verify after both fresh builds. NdisStallExecution resolves to HAL stall in this
configuration; the crash path must not introduce waits, allocations or locks.

Fresh control and candidate use identical source base, target, flags, compiler
pins and build lease. Verify actual imports against owned NT5/NDIS/HAL binaries,
all shutdown-reachable sections and unchanged helper algorithm. Then use new
fixtures with unchanged FATX0103/HAL0102/video0093 and inherited device policy.
Require ordinary workload/cold integrity, meaningful local network and normal
shutdown validation, and a separate controlled crash that actually returns
from the callback and reaches dump writing. Preserve each failed attempt.

Configuration success alone still does not qualify a dump. Retain64-bit pagefile
offsets, require independent cold dump-header/high-LBA write evidence, and only
then use a separate recovery child preserving the crash disk. No physical
deployment, callback suppression, settings change or qualification waiver.
