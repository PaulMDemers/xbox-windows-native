# Rebuilt overlay: first emulator boot passed

The eight-component overlay from package-reconstruction-002 was installed in a
new owned child of the unbooted GDI v3 fixture. All eight previous hashes matched
the captured 0.1.0 components. Preparation read back the replacement bytes and
verified the parent stayed unchanged. No physical driver was replaced.

`nt5-rebuilt-overlay-001` launched once at 2026-10-05 21:06:41 UTC and returned
to dashboard at 21:08:12. [Cold audit](audit.json) verifies all eight rebuilt
files, the unchanged workload, four passing pixel checks and the normal-restart
request. New system events contain the known HID7000/Ftdisk49, startup markers
and EventLog6006. No new application or delayed-write events were found.

This qualifies one emulator boot and bounded GDI workload using the private
synthetic NV2A resource model. It does not establish physical equivalence,
network stress, full allocation integrity or general stability. No debugger
register/memory changes were used. A pause/capture/resume screenshot during the
shutdown screen is retained in the owned run; timings are not hardware evidence.

The rebuilt package and its manifest remain unchanged; this separate report
adds runtime evidence without rewriting the original compilation claims.
The installed physical 0.1.0 baseline and release tag remain the rollback source.

## Binary layout investigation

[Comparison](pe-layout-comparison.json) covers the HAL and rosload from the exact
tested ZIP against captured physical files. Section sizes, RVAs and entry RVAs
match. All 557 differing HAL .text bytes and all 126 INIT bytes occur in 32-bit
relocation slots. Examples reference identical diagnostic strings at moved
addresses. Pointed-to data has not been exhaustively normalized, so this is not
a byte-equivalence proof.

Rosload has ten differing .text bytes: eight lie in relocation slots, and two
change immediate values passed to DbgPrint in HalpPCIPin2ISALine and
HalpPCIISALine2Pin. Disassembly gives 685→728 and 696→739. The rebuilt pcibus.c
contains UNIMPLEMENTED_DBGBREAK at lines728/739, consistent with changed source
line-number diagnostics. INIT is identical. Export timestamps and other .rdata
differences still prevent a byte-identical build claim.

Next: full reconstructed-package storage/network tests and a controlled
physical promotion only when that coverage is sufficient. The physical video
benchmark uses the original baseline drivers, not this package.
