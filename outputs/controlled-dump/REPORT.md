# Intended crash confirmed; dump capture incomplete

crash001 is CLOSED and must never be relaunched/recollected. It launched once
at 11:01:08 UTC and reached the intended E058D103 bugcheck at 11:02:22 with all
four exact cookie parameters. The kernel entry and actual trigger.sys caller
were resident-byte pinned. The screenshot independently shows the intended code.

The observer then failed with GDB E14 while trying to pin a loaded driver's PE
entrypoint. That is an invalid residency assumption: initialization entrypoints
can be discarded after boot. The frozen trace records one event/two pins; it
does not establish whether IoWriteCrashDump was called. Every breakpoint was
removed, the guest resumed, and the supervisor waited30 seconds before capture
and owned cleanup. Do not repair or replace this failed capture's evidence.

Cold inspection confirms the exact flushed intent log, clean allocation
(324 directories,6756 files,325 directory clusters,zero errors/orphans), five
structurally readable hives and unchanged protected binaries/payloads. The
pagefile still has its96MiB/1536-cluster chain. Its first header is PAGEPAGE,
not the intended PAGEDUMP header. There is no qualified dump write or recovery.
Normal boot paging writes reached the high-LBA extent, but that is not proof of
crash-miniport writes. The28-bit alias region is unchanged and has no traced
writes. No warning/error event was flushed; normal-shutdown count is0, as
expected for a deliberate crash. No ordinary strict PASS is claimed.

The helper and demand driver were built with the pinned RosBE compiler; all
imports resolve in owned NT5 binaries and PE checksums verify. Early host-only
build failures (missing DDK include directory, then an unquoted PowerShell
include argument) were corrected before preparation/freezing. No guest retry.

Next use a NEW child and observer that pins resident dispatch/callback code,
not discarded entrypoints. Record the dump context at the actual bugcheck and
follow entry/return or the reason the kernel skips writing. No driver/dump-policy
patch is justified yet. No recovery boot has been attempted. Physical access
remains prohibited, and original corruption/restart history remains unresolved.
