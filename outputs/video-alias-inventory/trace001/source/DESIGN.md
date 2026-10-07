# Read-only desktop alias inventory

Fresh emulator child, unchanged probe107/drivers/settings/device policy. Arm
only the probe's first phase marker; at the first small upload precheck capture
the current CPU registers and one coherent 64MiB physical RAM snapshot while
stopped. Pin actual kernel/probe identities and resident code. Resume in finally
after removing every breakpoint; keep raw RAM private with SHA256 provenance.
No code/register/page/cache mutation or interactive input. 600-second bound.

Offline walk the current CR3 and all processes linked by the pinned NT5 active
process list. Decode present 4KiB and 4MiB translations, retaining raw entries
and rejecting out-of-RAM page tables or unsupported PAE/PSE36 layouts. Inventory
all mappings intersecting reserved RAM03C00000..04000000 or its NV2A aperture
F3C00000..F4000000. Include user and kernel virtual addresses, identify shared
CR3s, and report absent/nonpresent mappings as outside resident coverage.

Require coherent process list links and complete bounded directory traversal.
This is a point-in-time resident mapping inventory, not an exhaustive history,
inactive-process scan, TLB audit, PFN ownership proof or effective PAT/MTRR audit.
Reuse historical0094/0096 MSR evidence with its limits, not as current values.
Follow normal workload/restart and full cold/event/config/pagefile checks.
