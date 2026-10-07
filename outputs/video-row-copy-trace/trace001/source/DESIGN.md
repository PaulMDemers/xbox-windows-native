# Bounded first-row copy observation

Same compiled probe107 and fixed video0093/storage stack as prior transfer trace,
new child/attempt only. Four small/large upload/overlap brackets retain full
54-case/162-RGB workload and strict cold gates. Diagnostic timing is not ordinary
performance. No physical access or driver/settings/device-policy change.

Capture the actual descriptor passed to private row target win32kRVA117125.
Arm its two possible first-row callsites117172/117179 only for that paired outer
call; after one hit remove both so subsequent rows are not sampled. Capture
actual dst/src/length,56 descriptor bytes and source/destination surface-row
membership. Pin actual callee and kernel IAT target. For the optional optimized
helper, capture its first executed MMX/scalar/fallback path once and remove all
algorithm breakpoints. This identifies a first-row path, not every row/branch.

Resolve CR0/CR3/CR4 and validate NT recursive PDE against actual CR3; reject PAE.
Read current present PDE/PTE for every page intersecting the first-row ranges.
Record physical addresses and raw PWT/PCD/PAT bits. These bits alone are not a
complete effective-cache-type audit: PAT/MTRR policy remains outside this trace.

Same thread/frame/stack pairing, loaded-module identities and exact relocated
resident code pins,512 stops/600 seconds, all-breakpoint teardown and resume on
success/failure. No argument/return/register mutation or fake completion.
Independently verify actual row bounds, branch choice and pins after cold audit.
