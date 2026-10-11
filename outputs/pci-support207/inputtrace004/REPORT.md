# Input trace 004: verified kernel sites, incomplete input-path coverage

The corrected kernel arm address matched resident NT5 headers and relocated
instruction bytes. The observer recorded 151 hits each at IoGetDeviceObjectPointer
entry, after ZwOpenFile and final return. It classified no input-class calls
and reached its 240-second deadline. This does not identify the failed input
path or owner. Breakpoints were removed and execution resumed before bounded
host closure at 2026-10-11T01:03:39.473677Z. No normal shutdown is claimed.

Read-only module-observation001.json records loaded keyboard/mouse classes.
Import-observation001.json shows both imports targeting the verified kernel
entry. Two coverage issues motivated a fresh harness: cached module ranges
can become stale, and the class enable helpers also have a direct forwarding
path that bypasses IoGetDeviceObjectPointer. Neither issue is claimed as the
runtime explanation solely from this incomplete trace.

Cold E/F allocation, protected files, five hives and event/SetupAPI history
passed. Installation exited zero, target lifecycle, invalid-only HAL probes
and QUERY_REMOVE/CANCEL_REMOVE recovery completed. F had 319 directories and
6726 files with no errors/orphans. One Kbdclass9 and one Mouclass9 retain
CREATE / STATUS_SHARING_VIOLATION; Ftdisk49 remains, DHCP1005 did not recur.
Pending install258 held restart; there is no Event6006/dashboard return.

The original pnp-review.json and pipeline failed the INF comparison: text-mode
copying changed the *host reference* line endings, hash167c0e57..., while cold
installed bytes matched canonical d8b50e1f... exactly. reference-correction001.json
pins both references and the original review, verifies normalized text equality,
and recomputes the package result against the canonical bytes. Original failed
evidence remains intact. The guest source and payload were never changed for
this correction and the guest was not rerun.

All sessions and leases for this attempt are closed. The used runtime remains
private and must not be relaunched. No physical access, policy change or
other-owner integration occurred; functional input/network, SMBus transactions,
normal restart and repeated-boot persistence remain unqualified.
