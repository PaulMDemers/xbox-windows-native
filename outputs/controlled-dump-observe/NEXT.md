# Next: make the proven shutdown-reachable NVNet helper resident

ALL owned sessions CLOSED. crash002 must never be relaunched/recollected.
Read REPORT.md, verification.json, callback-review.json and actual records.
Closed: prepare26220,runner44238,tracer34812,supervisor14139,audit78930;
post-timeout snapshot50986 completed,initial waiting observer22677 canceled before
guest access. Offload42428 completed; original paths preserved and hash-verified.
Previous controlled-dump/crash001 is a separate failed observer, pushed d670e00.

Exact diagnosis: intended E058D103 enters KiScanBugCheckCallbackList; active NDIS
miniport callback invokes nvnetnt5 MiniportShutdown RVA21f0. It calls pageable
NvNetIdleTransmitter RVA7800; absent PTE00720060 at VAf8d17800 causes nested
D1(f8d17800,1f,0,f8d17800), then HAL halt. Dump routine not reached. Post-timeout
RAM/page-table/callback/PE replay verifies this; no ordinary or dump recovery PASS.

Create a NEW source patch from frozen0103 tree3f7316b6079e28eab45c07d8abdf720b118aa90f,
removing CODE_SEG(PAGE) and PAGED_CODE from NvNetIdleTransmitter only. Review
shutdown's full HIGH_LEVEL-reachable call graph/data: other direct helpers are
already nonpaged, actual KeGetCurrentIrql skips the ordinary spin-lock pause at
HIGH_LEVEL; NdisStallExecution compiles to HAL stall. Preserve hardware stop,
reset, interrupt disable and power-state behavior; do not disable callback/NIC.
Build fresh matched NVNet control/candidate under build lease and compiler pins;
verify section/relocation/import/call-graph properties before staging anything.
Existing actual NVNet SHA d4aafead757f43c46ba161d2d034aafe05b7024ae693c39d224da42d485927d1.
No new network-driver build or patch exists yet. Keep candidate0103 FATX and0102
HAL exact; use unique normal and controlled-crash children. Require normal
workload/cold integrity and meaningful network/shutdown validation, then observe
genuine callback return, dump routine return and cold dump header/high-LBA writes.
Only then plan a separate recovery child preserving the crash image.

No settings/service/event suppression, fake success or gate waiver. Original
physical111nonASCII corruption/restart remains unresolved; this crash-path defect
is distinct. Preserve physical0101/video0093,0088rollback,immutable0.1.0 and all
failures/inherited emulator-only device policy. Emulator ONLY until13:00UTC,
check clock before work; no physicalFTP/deploy/test. At cutoff clean/preserve/
report/pause. C:about29.5GB after verified old standalone offload;20GiB guard stays.
