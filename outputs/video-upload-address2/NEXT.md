# Next: test the emulator surface-access callback hypothesis

Read REPORT.md, trace-verification.json, verifier-tests.json and source-followup.json.
Both address kits are CLOSED; do not relaunch or recollect. First remains failed
capture/clean cold workload, second is diagnostic PASS with ordinary/timing FALSE.
No next fixture exists. Physical baseline and rollback are unchanged.

The actual guest copy branch and recorded paging flags do not change by screen
position. The previous ordinary 48x median difference remains unexplained.
Runtime first-row addresses are known; all96-row mappings are captured. The
display header was unreadable, explicitly recorded; resident code/loader identity
and cold hash corroborate the module. Do not claim effective cache-type auditing.

Investigate the existing xemu nv2a_pgraph_surface_cpu_read/write events, which
record GPU surface base and offset. First verify this pinned binary's trace backend
and output routing without launching another Windows workload. Then prepare a NEW
owned child with bounded marker-delimited draws at top/lower positions. Enable only
the selected events during those draws, cap records/log size, disable in finally,
and preserve exact event windows alongside actual guest copy ranges. No broad CPU
trace or unbounded per-access logging. Keep observer pauses out of speed claims.

Determine whether slow ranges overlap CPU-access-watched GPU surfaces, possibly
retained across dashboard-to-Windows handoff. That is a hypothesis, not an observed
fact. Do not remove callbacks, invalidate surfaces or alter cache settings merely
to obtain faster output. If runtime evidence supports a mechanism, design a focused
emulator/guest contract fix and matched ordinary regressions, including correctness
of GPU surface read/write synchronization and normal shutdown.

Keep physical0101/video0093,0088rollback,0.1.0 and all failed evidence. Recheck C:
capacity (~21GiB last seen); keep20GiB build guard and preserve QCOW backing chains.
