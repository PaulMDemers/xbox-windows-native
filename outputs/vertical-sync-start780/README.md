# Test780 host-qualified: vertical-sync-start recovery

Fresh kernel-context test, source-only extension of closed778 after closed779.
Target489 derives from pinned704 GPU_PARAMETER and expected MMIO write; baseline
724 comes from retained physical records. Tests own saved-value restoration
724 ->489 ->724 with eight vertical/stride neighbors. Stops before NVVSYNCEND.
No full visible mode switch or Windows1.6/acceleration claim. E-only owned path,
no startup hook; automatic dashboard return intended after15seconds.

Host qualification:458 actual COFF fault cases,2353 layout cases,10 clock cases,
strict result/schema mutation checks and exact linked COFF/PE/XBE code checks PASS.
Preserve host-invocation-failure001 (missing lease before cases) and clock-model001
(stale stack offsets before cases); clock_model002 uses observed disassembly and
passes. Guest build unchanged after those harness failures.

No physical stage or launch yet. NEXT stage/readback exact build, one bounded SITE,
authenticated dashboard return, collect once/double, audit. Standing2026-10-28
watch/reset authorization applies; no new readiness question required. No owned
VM or running host process. All779/prior closed, never rerun/recollect/parent.
